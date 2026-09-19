from datetime import date, datetime, timezone, timedelta
from types import SimpleNamespace

import database.database as db
import main
from job import Job
from perfis import PERFIL_BR


def _job(titulo="Mechanical Engineer", link="https://example.invalid/1"):
    return Job(
        titulo=titulo,
        empresa="Empresa Teste",
        local="Brasil",
        link=link,
        site="Teste",
        modalidade="Remoto",
    )


def test_dedup_secundaria_recente_bloqueia_mas_antiga_nao(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "jobs.db"))
    monkeypatch.setattr(db, "JANELA_DEDUP_CHAVE_SECUNDARIA_DIAS", 14)
    db.iniciar_db()

    primeira = _job(link="https://example.invalid/vaga-antiga")
    db.salvar_vaga(primeira, perfil_chave="brasil")

    mesma_abertura_recente = _job(link="https://example.invalid/outro-link")
    assert db.ja_vista(mesma_abertura_recente) is True

    with db._conectar() as conn:
        conn.execute(
            "UPDATE vagas_vistas SET encontrada_em = datetime('now', '-30 days') WHERE id = ?",
            (primeira.id,),
        )

    reabertura_real = _job(link="https://example.invalid/nova-abertura")
    assert db.ja_vista(reabertura_real) is False
    assert db.ja_vista(primeira) is True


def test_digest_revalida_config_e_remove_vaga_de_outro_perfil(monkeypatch):
    pendentes = [
        {
            "id": "cyber-old",
            "titulo": "Cloud Security Engineer",
            "empresa": "Empresa Cyber",
            "local": "Brasil",
            "link": "https://example.invalid/cyber",
            "site": "LinkedIn",
            "publicado_em": "",
            "modalidade": "Remoto",
            "relevancia": 3,
            "exploratoria": 0,
        },
        {
            "id": "auto-ok",
            "titulo": "Engenheiro Mecânico Pleno",
            "empresa": "Empresa Auto",
            "local": "Curitiba, PR",
            "link": "https://example.invalid/auto",
            "site": "LinkedIn",
            "publicado_em": "",
            "modalidade": "Presencial",
            "relevancia": 0,
            "exploratoria": 0,
        },
    ]
    removidos = []
    monkeypatch.setattr(main, "obter_vagas_pendentes_digest_detalhadas", lambda _perfil: pendentes)
    monkeypatch.setattr(main, "descartar_vagas_digest", lambda ids: removidos.extend(ids))

    validas = main._revalidar_pendencias_digest(PERFIL_BR)
    assert [v[0] for v in validas] == ["Engenheiro Mecânico Pleno"]
    assert removidos == ["cyber-old"]


def test_heartbeat_falhou_nao_marca_como_enviado(monkeypatch):
    gravados = []
    monkeypatch.setattr(main, "_hoje_brasilia", lambda: date(2026, 9, 19))
    monkeypatch.setattr(
        main,
        "_agora_brasilia",
        lambda: datetime(2026, 9, 19, 12, 0, tzinfo=timezone(timedelta(hours=-3))),
    )
    monkeypatch.setattr(main, "obter_metadado", lambda _chave: None)
    monkeypatch.setattr(main, "enviar_mensagem", lambda _texto: False)
    monkeypatch.setattr(main, "definir_metadado", lambda chave, valor: gravados.append((chave, valor)))

    main._enviar_heartbeat_diario(PERFIL_BR, 0, [], 3)
    assert gravados == []


def test_heartbeat_sucesso_marca_dia_de_brasilia(monkeypatch):
    gravados = []
    monkeypatch.setattr(main, "_hoje_brasilia", lambda: date(2026, 9, 19))
    monkeypatch.setattr(
        main,
        "_agora_brasilia",
        lambda: datetime(2026, 9, 19, 12, 0, tzinfo=timezone(timedelta(hours=-3))),
    )
    monkeypatch.setattr(main, "obter_metadado", lambda _chave: None)
    monkeypatch.setattr(main, "enviar_mensagem", lambda _texto: True)
    monkeypatch.setattr(main, "definir_metadado", lambda chave, valor: gravados.append((chave, valor)))

    main._enviar_heartbeat_diario(PERFIL_BR, 0, [], 3)
    assert gravados == [("heartbeat_ultimo_dia_brasil", "2026-09-19")]


def test_termos_core_rodam_em_todo_ciclo(monkeypatch):
    estado = {}
    monkeypatch.setattr(main, "obter_metadado", lambda chave: estado.get(chave))
    monkeypatch.setattr(main, "definir_metadado", lambda chave, valor: estado.__setitem__(chave, valor))
    perfil = SimpleNamespace(
        chave="teste",
        termos_core=["mechanical engineer", "engenheiro de produto"],
        termos_busca=[
            "mechanical engineer",
            "engenheiro de produto",
            "process engineer",
            "vehicle test engineer",
            "maintenance engineer",
            "quality engineer",
        ],
        termos_por_ciclo=2,
    )

    ciclo1 = main._proximo_bloco_termos(perfil)
    ciclo2 = main._proximo_bloco_termos(perfil)

    assert ciclo1[:2] == ["mechanical engineer", "engenheiro de produto"]
    assert ciclo2[:2] == ["mechanical engineer", "engenheiro de produto"]
    assert ciclo1[2:] != ciclo2[2:]
