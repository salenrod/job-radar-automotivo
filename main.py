
import argparse
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone

from config import DIGEST_HORA_UTC, INTERVALO_MINUTOS, LIMIAR_DIGEST_IMEDIATO
from database.database import (
    BancoVazioSuspeito,
    definir_metadado,
    iniciar_db,
    ja_vista,
    marcar_digest_enviado,
    obter_metadado,
    obter_vagas_pendentes_digest_detalhadas,
    descartar_vagas_digest,
    salvar_vaga,
)
from notifier.telegram import (
    enviar_digest,
    enviar_mensagem,
    notificar_vaga,
    notificar_vaga_exploratoria,
    processar_feedback_pendente,
)
from perfis import FREQUENCIA_ALTA, PERFIS, Perfil
from job import Job
from utils.filtro import filtrar_vagas
from logger import get_logger

logger = get_logger()

FUSO_BRASILIA = timezone(timedelta(hours=-3))


def _agora_brasilia() -> datetime:
    return datetime.now(FUSO_BRASILIA)


def _hoje_brasilia() -> date:
    return _agora_brasilia().date()


def _fontes_baixa_frequencia_ja_rodaram_hoje(perfil: Perfil) -> bool:
    chave = f"baixa_frequencia_ultimo_dia_{perfil.chave}"
    return obter_metadado(chave) == _hoje_brasilia().isoformat()


# Não é mais uma lista fixa construída uma vez: os scrapers recebem só o
# BLOCO de termos do ciclo atual (ver _proximo_bloco_termos), e a lista de
# QUAIS fontes entram também varia por ciclo (fonte de baixa frequência só
# entra na primeira execução do dia) — então precisam ser (re)criados a
# cada ciclo, não guardados numa constante de módulo. Cada perfil tem sua
# própria chave de metadados (sufixo perfil.chave), pra rodar dois perfis
# na mesma execução sem um pisar na cadência do outro.
def _construir_scrapers(perfil: Perfil, termos_busca: list[str]):
    rodar_baixa_frequencia = not _fontes_baixa_frequencia_ja_rodaram_hoje(perfil)

    scrapers = [
        definicao.classe(termos_busca=termos_busca, **definicao.kwargs_extras)
        for definicao in perfil.definicao_scrapers
        if definicao.frequencia == FREQUENCIA_ALTA or rodar_baixa_frequencia
    ]

    if rodar_baixa_frequencia:
        # Marca ANTES de rodar (não depois): mesmo que uma fonte de baixa
        # frequência falhe nesse ciclo, ela "rodou" no sentido de já ter
        # sido tentada hoje — não deve ser tentada de novo no ciclo
        # seguinte só porque deu erro. Falha individual já é tratada e
        # logada normalmente em ciclo_de_busca(), como qualquer scraper.
        definir_metadado(f"baixa_frequencia_ultimo_dia_{perfil.chave}", _hoje_brasilia().isoformat())

    return scrapers


def _proximo_bloco_termos(perfil: Perfil) -> list[str]:
    """Retorna TERMOS CORE + um bloco rotativo.

    Os termos core rodam em todo ciclo; apenas o restante avanca pelo offset
    persistido no jobs.db. Assim uma vaga com titulo essencial nao precisa
    esperar toda a lista girar novamente para ser descoberta.
    """
    core = list(dict.fromkeys(perfil.termos_core))
    core_set = set(core)
    rotativos = [t for t in perfil.termos_busca if t not in core_set]

    if not rotativos:
        return core

    tamanho_bloco = min(perfil.termos_por_ciclo, len(rotativos))
    # Chave nova: nao reaproveita offset calculado quando core e rotativos
    # ainda faziam parte da mesma lista.
    chave_offset = f"termos_offset_rotativos_v2_{perfil.chave}"
    offset_salvo = obter_metadado(chave_offset)
    offset = int(offset_salvo) % len(rotativos) if offset_salvo else 0

    bloco = [rotativos[(offset + i) % len(rotativos)] for i in range(tamanho_bloco)]
    definir_metadado(chave_offset, str((offset + tamanho_bloco) % len(rotativos)))
    return core + bloco


def _enviar_heartbeat_diario(
    perfil: Perfil, total_novas: int, scrapers_com_problema: list[str], total_fontes: int
):
    """Envia no maximo um heartbeat por DIA DE BRASILIA e so marca como
    enviado quando o Telegram confirma sucesso.

    A versao anterior usava a data UTC do runner; por isso o heartbeat do
    dia seguinte podia aparecer ainda as 21h do dia anterior no Telegram.
    Alem disso, uma falha transitoria de envio era marcada como sucesso e
    impedia nova tentativa ate o dia seguinte.
    """
    chave = f"heartbeat_ultimo_dia_{perfil.chave}"
    hoje = _hoje_brasilia().isoformat()
    if obter_metadado(chave) == hoje:
        return

    agora_br = _agora_brasilia().strftime("%H:%M BRT")
    if scrapers_com_problema:
        status = f"{len(scrapers_com_problema)}/{total_fontes} fonte(s) com problema"
    else:
        status = "todas as fontes ok"

    sucesso = enviar_mensagem(
        f"💓 <b>JobRadar {perfil.nome} ativo</b>\n\n"
        f"Confirmação diária: o ciclo rodou agora ({agora_br}, {status}). "
        f"{total_novas} vaga(s) nova(s) neste ciclo.\n\n"
        "Se essa mensagem parar de chegar, o workflow parou de rodar — "
        "não que faltou vaga."
    )
    if sucesso:
        definir_metadado(chave, hoje)
        logger.info(f"[{perfil.nome}] Heartbeat diário enviado com sucesso ({hoje}).")
    else:
        logger.warning(
            f"[{perfil.nome}] Heartbeat diário falhou; não marcado como enviado e será "
            "tentado novamente no próximo ciclo."
        )


def _revalidar_pendencias_digest(perfil: Perfil) -> list[tuple]:
    """Reaplica as regras ATUAIS a tudo que ainda esta na fila do digest.

    Retorna apenas (titulo, empresa, link, relevancia, exploratoria) validos
    e limpa o flag digest_pendente de registros obsoletos. Nao apaga historico.
    """
    pendentes = obter_vagas_pendentes_digest_detalhadas(perfil.chave)
    validas: list[tuple] = []
    obsoletas: list[str] = []

    for item in pendentes:
        exploratoria = bool(item["exploratoria"])
        if exploratoria and not perfil.eixo_secundario_ativo:
            obsoletas.append(item["id"])
            continue

        regras = (
            perfil.regras_eixo_secundario
            if exploratoria and perfil.regras_eixo_secundario is not None
            else perfil.regras
        )
        vaga = Job(
            titulo=item["titulo"] or "",
            empresa=item["empresa"] or "",
            local=item["local"] or "",
            link=item["link"] or "",
            site=item["site"] or "",
            publicado_em=item["publicado_em"] or "",
            modalidade=item["modalidade"] or "",
            escopo_indefinido=(item["site"] or "").lower() == "we work remotely",
        )
        if not vaga.combina_com(regras):
            obsoletas.append(item["id"])
            continue

        vaga.relevancia = vaga.pontuar_relevancia(regras)
        validas.append((vaga.titulo, vaga.empresa, vaga.link, vaga.relevancia, exploratoria))

    if obsoletas:
        descartar_vagas_digest(obsoletas)
        logger.info(
            f"[{perfil.nome}] Digest: {len(obsoletas)} pendência(s) obsoleta(s) "
            "removida(s) da fila após revalidar as regras atuais."
        )

    validas.sort(key=lambda x: x[3] or 0, reverse=True)
    return validas


def _enviar_digest_diario(perfil: Perfil):
    """Envia o digest diário depois de REVALIDAR cada pendência contra as
    regras atuais do perfil.

    Isso fecha um bug de migração: vagas Data/BI antigas ficaram no mesmo
    jobs.db com digest_pendente=1 e continuavam sendo enviadas mesmo depois
    de o perfil ter sido convertido para Cybersecurity.
    """
    chave = f"digest_ultimo_dia_{perfil.chave}"
    hoje_br = _hoje_brasilia()
    agora_utc = datetime.now(timezone.utc)

    ultimo_envio_str = obter_metadado(chave)
    if ultimo_envio_str == hoje_br.isoformat():
        return

    horario_certo = agora_utc.hour == DIGEST_HORA_UTC
    atrasado = ultimo_envio_str is not None and (
        hoje_br - date.fromisoformat(ultimo_envio_str)
    ).days >= 2
    if not (horario_certo or atrasado):
        return

    validas = _revalidar_pendencias_digest(perfil)
    if not validas:
        definir_metadado(chave, hoje_br.isoformat())
        logger.info(f"[{perfil.nome}] Digest sem vagas válidas após revalidação.")
        return

    if enviar_digest(validas, perfil.nome):
        marcar_digest_enviado(perfil.chave)
        definir_metadado(chave, hoje_br.isoformat())
        logger.info(f"[{perfil.nome}] Digest diário enviado: {len(validas)} vaga(s) válida(s).")
    else:
        logger.warning(
            f"[{perfil.nome}] Falha ao enviar digest diário ({len(validas)} vaga(s) "
            "válida(s) pendentes) - tenta de novo no próximo ciclo."
        )



def ciclo_de_busca(perfil: Perfil):
    total_novas = 0
    total_brutas = 0
    total_filtradas = 0
    scrapers_com_problema = []
    descartes_escopo_ciclo: Counter = Counter()

    termos_do_ciclo = _proximo_bloco_termos(perfil)
    logger.info(
        f"[{perfil.nome}] Termos deste ciclo: {len(termos_do_ciclo)} total "
        f"({len(perfil.termos_core)} core + até {perfil.termos_por_ciclo} rotativos) — "
        f"{', '.join(termos_do_ciclo)}"
    )
    scrapers = _construir_scrapers(perfil, termos_do_ciclo)

    # A parte lenta (abrir navegador, navegar, esperar seletor) roda em
    # paralelo aqui. Tudo que segue (filtrar, checar dedup, notificar,
    # salvar) continua rodando só na thread principal, um scraper de cada
    # vez, conforme a future dele termina — nunca duas threads escrevendo
    # no SQLite ou chamando o Telegram ao mesmo tempo. Cada scraper já é
    # auto-contido (cria e fecha seu(s) próprio(s) browser(s) Playwright
    # dentro de buscar_vagas()), então dá pra rodar vários ao mesmo tempo em
    # threads sem risco — nenhum compartilha Browser/Page com outro.
    with ThreadPoolExecutor(max_workers=perfil.max_scrapers_concorrentes) as executor:
        futures = {executor.submit(scraper.buscar_vagas): scraper for scraper in scrapers}

        for future in as_completed(futures):
            scraper = futures[future]
            nome = scraper.__class__.__name__

            try:
                vagas = future.result()
            except Exception as e:
                logger.error(f"[{perfil.nome}] Erro no scraper {nome}: {e}")
                scrapers_com_problema.append(nome)
                continue

            # Cada scraper trata timeout por termo internamente (só loga e
            # segue pro próximo termo), então um site totalmente bloqueado
            # não lança exceção pra cá — só devolve lista vazia. Por isso
            # também contamos "0 vaga bruta nessa fonte" como problema, não
            # só exceção.
            if not vagas:
                logger.warning(f"[{perfil.nome}] {nome} não retornou nenhuma vaga bruta neste ciclo.")
                scrapers_com_problema.append(nome)
                continue

            total_brutas += len(vagas)
            vagas_filtradas, descartes = filtrar_vagas(vagas, perfil.regras)
            descartes_escopo_ciclo.update(descartes)

            # Eixo secundário (Ibéria, quando ligado): mesma regra de cargo,
            # cidade diferente — sem duplicar o que já bateu na regra
            # primária.
            vagas_secundarias = []
            if perfil.eixo_secundario_ativo and perfil.regras_eixo_secundario is not None:
                ids_filtradas = {v.id for v in vagas_filtradas}
                candidatas, descartes_secundario = filtrar_vagas(vagas, perfil.regras_eixo_secundario)
                descartes_escopo_ciclo.update(descartes_secundario)
                vagas_secundarias = [v for v in candidatas if v.id not in ids_filtradas]

            total_filtradas += len(vagas_filtradas) + len(vagas_secundarias)

            novas_da_fonte = 0
            for vaga in vagas_filtradas:
                if ja_vista(vaga):
                    continue

                # Item 08: só notifica na hora quando a relevância passa do
                # limiar (ver LIMIAR_DIGEST_IMEDIATO em config.py) — abaixo
                # disso, vai pra fila do digest diário sem mensagem
                # individual (ver _enviar_digest_diario). Fila é salvar com
                # digest_pendente=True: não tem "notificação que pode
                # falhar" nesse caminho (a mensagem só sai no digest, depois),
                # então salvar direto não arrisca perder a vaga do jeito que
                # salvar ANTES de notificar arriscava no caminho imediato.
                #
                # MEDIDO: vaga com Job.publicacao_antiga (publicado_em "há X
                # meses/anos" — ver job.py) nunca vai pra notificação
                # imediata, mesmo com relevância alta — score mede "bate com
                # o que você procura", não "é recente". Site com pouco
                # volume pra um termo deixa vaga de meses atrás na página
                # visível (confirmado ao vivo: Sólides ordena por data, mas
                # sem volume novo suficiente a antiga não sai da 1ª página).
                # Não é descartada (mesma vaga ainda pode estar aberta) — só
                # sai do caminho "🚨 urgente" e vai pro digest em lote.
                if vaga.relevancia >= LIMIAR_DIGEST_IMEDIATO and not vaga.publicacao_antiga:
                    # Notifica ANTES de salvar. Se salvasse primeiro e o
                    # Telegram falhasse, a vaga ficava marcada como "vista"
                    # pra sempre — o próximo ciclo pulava ela em ja_vista()
                    # e a vaga se perdia sem nunca ter sido notificada de
                    # verdade.
                    if not notificar_vaga(vaga):
                        logger.warning(
                            f"[{perfil.nome}] Falha ao notificar '{vaga.titulo}' - não marcada "
                            "como vista, tenta de novo no próximo ciclo."
                        )
                        continue
                    salvar_vaga(vaga, perfil_chave=perfil.chave)
                    logger.info(f"[{perfil.nome}] Nova vaga: {vaga.titulo} - {vaga.empresa}")
                else:
                    salvar_vaga(vaga, perfil_chave=perfil.chave, digest_pendente=True)
                    motivo_digest = "vaga antiga" if vaga.publicacao_antiga else f"relevância {vaga.relevancia}/10"
                    logger.info(
                        f"[{perfil.nome}] Nova vaga (digest, {motivo_digest}): "
                        f"{vaga.titulo} - {vaga.empresa}"
                    )

                total_novas += 1
                novas_da_fonte += 1

            for vaga in vagas_secundarias:
                if ja_vista(vaga):
                    continue

                # Mesma regra de vaga antiga do loop acima.
                if vaga.relevancia >= LIMIAR_DIGEST_IMEDIATO and not vaga.publicacao_antiga:
                    if not notificar_vaga_exploratoria(vaga):
                        logger.warning(
                            f"[{perfil.nome}] Falha ao notificar '{vaga.titulo}' (exploratória) - "
                            "não marcada como vista, tenta de novo no próximo ciclo."
                        )
                        continue
                    salvar_vaga(vaga, perfil_chave=perfil.chave)
                    logger.info(
                        f"[{perfil.nome}] Nova vaga exploratória ({perfil.eixo_secundario_rotulo}): "
                        f"{vaga.titulo} - {vaga.empresa}"
                    )
                else:
                    salvar_vaga(vaga, perfil_chave=perfil.chave, digest_pendente=True, exploratoria=True)
                    motivo_digest = "vaga antiga" if vaga.publicacao_antiga else f"relevância {vaga.relevancia}/10"
                    logger.info(
                        f"[{perfil.nome}] Nova vaga exploratória (digest, {motivo_digest}): "
                        f"{vaga.titulo} - {vaga.empresa}"
                    )

                total_novas += 1
                novas_da_fonte += 1

            # Funil por fonte: sem isso só dava pra ver bruta (por fonte) e
            # nova (só o total do ciclo) — o meio (quanto o filtro de
            # cargo/cidade descarta, fonte por fonte) ficava invisível.
            logger.info(
                f"[{perfil.nome}][{nome}] Funil: {len(vagas)} brutas → "
                f"{len(vagas_filtradas) + len(vagas_secundarias)} filtradas → {novas_da_fonte} novas"
            )

    logger.info(
        f"[{perfil.nome}] Ciclo concluído: {total_brutas} brutas → {total_filtradas} filtradas → "
        f"{total_novas} nova(s)."
    )

    # MEDIDO: descarte por escopo era invisível no log — o funil mostra
    # bruta → filtrada → nova, mas nunca QUAL escopo derrubou vaga nem
    # QUANTAS. Um escopo mal reconhecido (texto cru tipo "lagos nigeria",
    # não mapeado em _MERCADOS_REMOTO) barra do jeito certo, mas some sem
    # rastro — foi assim que um bug real (escopo virando allowlist) passou
    # despercebido até virar relato explícito. Loga só quando há descarte
    # (a maioria dos ciclos não tem nenhum), ordenado do que mais derrubou
    # vaga pro que menos derrubou.
    if descartes_escopo_ciclo:
        detalhe = "; ".join(
            f"{escopo} ({n})" for escopo, n in descartes_escopo_ciclo.most_common()
        )
        logger.info(f"[{perfil.nome}] Descarte por escopo: {detalhe}")

    # Alerta de saúde: se a maioria das fontes falhou/voltou vazia, avisa no
    # Telegram. Sem isso, um bloqueio geral ou mudança de layout passaria
    # despercebido — o workflow do GitHub Actions continuaria "verde" mesmo
    # com tudo quebrado.
    if scrapers and len(scrapers_com_problema) >= len(scrapers) / 2:
        enviar_mensagem(
            f"⚠️ <b>JobRadar {perfil.nome} com problema</b>\n\n"
            f"{len(scrapers_com_problema)}/{len(scrapers)} fontes falharam ou voltaram "
            f"vazias neste ciclo: {', '.join(scrapers_com_problema)}.\n\n"
            "Vale checar o log do GitHub Actions."
        )

    _enviar_heartbeat_diario(perfil, total_novas, scrapers_com_problema, len(scrapers))
    _enviar_digest_diario(perfil)


def _rodar_um_ciclo_de_cada(perfis: list[Perfil]):
    # Uma vez por execução, não por perfil: o offset do getUpdates (ver
    # processar_feedback_pendente) é global — feedback de vaga não tem
    # perfil, e rodar duas vezes na mesma execução só gastaria uma chamada
    # de API à toa (a segunda sempre veria "nada novo desde a última vez").
    processar_feedback_pendente()

    for perfil in perfis:
        print(f"\n{'=' * 50}")
        print(f"PERFIL: {perfil.nome.upper()}")
        print("=" * 50)

        print("\nPalavras monitoradas:")
        for palavra in perfil.palavras_monitoradas:
            print(f"• {palavra}")

        if perfil.paises_pesquisados:
            print("\nPaíses pesquisados:")
            for pais in perfil.paises_pesquisados:
                print(f"• {pais}")

        ciclo_de_busca(perfil)


def main():
    parser = argparse.ArgumentParser(description="JobRadar - monitor de vagas")
    parser.add_argument(
        "--perfil",
        required=True,
        nargs="+",
        choices=sorted(PERFIS.keys()),
        help=(
            "Qual(is) mercado(s) rodar nesta execução — 'brasil', 'internacional', "
            "ou os dois (--perfil brasil internacional)."
        ),
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Roda um único ciclo de busca (de cada perfil selecionado) e encerra "
             "(usado no GitHub Actions, que já dispara o script periodicamente via cron).",
    )
    args = parser.parse_args()

    perfis_selecionados = [PERFIS[chave] for chave in args.perfil]

    if not args.once:
        print(f"\nIntervalo de checagem: {INTERVALO_MINUTOS} min\n")

    # Chamado UMA VEZ só, antes de qualquer perfil rodar — não por perfil.
    # A checagem de "banco suspeito" (ver database.py) compara se o arquivo
    # já existia ANTES desta execução; se cada perfil chamasse iniciar_db()
    # separadamente na mesma execução, o segundo perfil veria o arquivo que
    # o primeiro acabou de criar/popular momentos atrás e podia disparar
    # falso positivo (arquivo "já existia" só porque o perfil anterior já
    # rodou nesta mesma execução, não porque é run antigo de verdade).
    try:
        iniciar_db()
    except BancoVazioSuspeito as e:
        logger.error(str(e))
        nomes = ", ".join(p.nome for p in perfis_selecionados)
        enviar_mensagem(f"🛑 <b>JobRadar abortado</b>\n\nPerfis desta execução: {nomes}\n\n{e}")
        sys.exit(1)

    if args.once:
        _rodar_um_ciclo_de_cada(perfis_selecionados)
        return

    while True:
        _rodar_um_ciclo_de_cada(perfis_selecionados)
        logger.info(f"Aguardando {INTERVALO_MINUTOS} minutos até a próxima checagem...")
        time.sleep(INTERVALO_MINUTOS * 60)


if __name__ == "__main__":
    main()
