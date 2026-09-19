"""Perfis Brasil e Internacional do JobRadar Automotivo."""

from dataclasses import dataclass, field

from config import (
    ATIVAR_EIXO_IBERICO_BR,
    CIDADES,
    CIDADES_EUROPA_IBERICA,
    FERRAMENTAS_TITULO,
    KEYWORDS,
    KEYWORDS_CARGO_AMBIGUO,
    KEYWORDS_CARGO_FORTE,
    KEYWORDS_EXCLUSAO_TITULO,
    MERCADOS_REMOTO_ACEITOS,
    PERMITIR_CARGO_AMBIGUO_SEM_QUALIFICADOR,
    QUALIFICADORES_CARGO,
    QUALIFICADORES_DADOS,
    TERMOS_BUSCA,
    TERMOS_CORE,
    TERMOS_POR_CICLO,
)
from config_intl import (
    ATIVAR_EIXO_IBERICO,
    CIDADES_INTL,
    DOMINIOS_INDEED_INTL,
    IDIOMAS_EXIGIDOS_INTL,
    KEYWORDS_EXCLUSAO_TITULO_INTL,
    KEYWORDS_INTL,
    LOCATIONS_INTL,
    MERCADOS_REMOTO_ACEITOS_INTL,
    TERMOS_BUSCA_INTL,
    TERMOS_CORE_INTL,
    TERMOS_POR_CICLO_INTL,
)
from job import RegrasFiltro
from scrapers.catho import CathoScraper
from scrapers.gupy import GupyScraper
from scrapers.indeed import IndeedScraper
from scrapers.indeed_intl import IndeedIntlScraper
from scrapers.jobs99 import Jobs99Scraper
from scrapers.linkedin import LinkedInScraper
from scrapers.linkedin_intl import LinkedInIntlScraper
from scrapers.solides import SolidesScraper
from scrapers.weworkremotely_intl import WeWorkRemotelyIntlScraper

FREQUENCIA_ALTA = "alta"
FREQUENCIA_BAIXA = "baixa"


@dataclass
class DefinicaoScraper:
    classe: type
    frequencia: str
    kwargs_extras: dict = field(default_factory=dict)


@dataclass
class Perfil:
    chave: str
    nome: str
    palavras_monitoradas: list[str]
    paises_pesquisados: list[str] | None
    regras: RegrasFiltro
    regras_eixo_secundario: RegrasFiltro | None
    eixo_secundario_ativo: bool
    eixo_secundario_rotulo: str
    termos_busca: list[str]
    termos_por_ciclo: int
    definicao_scrapers: list[DefinicaoScraper]
    termos_core: list[str] = field(default_factory=list)
    max_scrapers_concorrentes: int = 4


_REGRAS_BR = RegrasFiltro(
    keywords_forte=KEYWORDS_CARGO_FORTE,
    keywords_ambiguo=KEYWORDS_CARGO_AMBIGUO,
    qualificadores_dados=QUALIFICADORES_DADOS,
    ferramentas_titulo=FERRAMENTAS_TITULO,
    qualificadores_cargo=QUALIFICADORES_CARGO,
    cidades=CIDADES,
    mercados_remoto_aceitos=MERCADOS_REMOTO_ACEITOS,
    keywords_exclusao_titulo=KEYWORDS_EXCLUSAO_TITULO,
    permitir_ambiguo_sem_qualificador=PERMITIR_CARGO_AMBIGUO_SEM_QUALIFICADOR,
)

_REGRAS_BR_IBERIA = RegrasFiltro(
    keywords_forte=KEYWORDS_CARGO_FORTE,
    keywords_ambiguo=KEYWORDS_CARGO_AMBIGUO,
    qualificadores_dados=QUALIFICADORES_DADOS,
    ferramentas_titulo=FERRAMENTAS_TITULO,
    qualificadores_cargo=QUALIFICADORES_CARGO,
    cidades=CIDADES_EUROPA_IBERICA,
    keywords_exclusao_titulo=KEYWORDS_EXCLUSAO_TITULO,
    permitir_ambiguo_sem_qualificador=PERMITIR_CARGO_AMBIGUO_SEM_QUALIFICADOR,
)

# Fontes de maior utilidade em alta frequencia. Indeed/Catho/99Jobs ficam 1x/dia
# para reduzir custo e bloqueios.
_SCRAPERS_BR = [
    DefinicaoScraper(GupyScraper, FREQUENCIA_ALTA),
    DefinicaoScraper(LinkedInScraper, FREQUENCIA_ALTA),
    DefinicaoScraper(SolidesScraper, FREQUENCIA_ALTA),
    DefinicaoScraper(IndeedScraper, FREQUENCIA_BAIXA),
    DefinicaoScraper(CathoScraper, FREQUENCIA_BAIXA),
    DefinicaoScraper(Jobs99Scraper, FREQUENCIA_BAIXA),
]

PERFIL_BR = Perfil(
    chave="brasil",
    nome="Brasil",
    palavras_monitoradas=KEYWORDS,
    paises_pesquisados=None,
    regras=_REGRAS_BR,
    regras_eixo_secundario=_REGRAS_BR_IBERIA,
    eixo_secundario_ativo=ATIVAR_EIXO_IBERICO_BR,
    eixo_secundario_rotulo="Ibéria",
    termos_busca=TERMOS_BUSCA,
    termos_por_ciclo=TERMOS_POR_CICLO,
    definicao_scrapers=_SCRAPERS_BR,
    termos_core=TERMOS_CORE,
    max_scrapers_concorrentes=4,
)


_REGRAS_INTL = RegrasFiltro(
    keywords_forte=KEYWORDS_INTL,
    keywords_ambiguo=[],
    qualificadores_dados=[],
    ferramentas_titulo=[],
    qualificadores_cargo=[],
    cidades=CIDADES_INTL,
    mercados_remoto_aceitos=MERCADOS_REMOTO_ACEITOS_INTL,
    idiomas_exigidos=IDIOMAS_EXIGIDOS_INTL,
    keywords_exclusao_titulo=KEYWORDS_EXCLUSAO_TITULO_INTL,
)

_REGRAS_INTL_IBERIA = RegrasFiltro(
    keywords_forte=KEYWORDS_INTL,
    keywords_ambiguo=[],
    qualificadores_dados=[],
    ferramentas_titulo=[],
    qualificadores_cargo=[],
    cidades=CIDADES_EUROPA_IBERICA,
    keywords_exclusao_titulo=KEYWORDS_EXCLUSAO_TITULO_INTL,
)

_SCRAPERS_INTL = [
    DefinicaoScraper(LinkedInIntlScraper, FREQUENCIA_ALTA, {"locations": LOCATIONS_INTL}),
    DefinicaoScraper(IndeedIntlScraper, FREQUENCIA_BAIXA, {"dominios": DOMINIOS_INDEED_INTL}),
    DefinicaoScraper(WeWorkRemotelyIntlScraper, FREQUENCIA_BAIXA),
]

PERFIL_INTL = Perfil(
    chave="internacional",
    nome="Internacional",
    palavras_monitoradas=KEYWORDS_INTL,
    paises_pesquisados=LOCATIONS_INTL,
    regras=_REGRAS_INTL,
    regras_eixo_secundario=_REGRAS_INTL_IBERIA,
    eixo_secundario_ativo=ATIVAR_EIXO_IBERICO,
    eixo_secundario_rotulo="Ibéria",
    termos_busca=TERMOS_BUSCA_INTL,
    termos_por_ciclo=TERMOS_POR_CICLO_INTL,
    definicao_scrapers=_SCRAPERS_INTL,
    termos_core=TERMOS_CORE_INTL,
    max_scrapers_concorrentes=3,
)

PERFIS = {
    PERFIL_BR.chave: PERFIL_BR,
    PERFIL_INTL.chave: PERFIL_INTL,
}
