import pytest

from job import Job, extrair_escopo_remoto
from perfis import PERFIL_BR, PERFIL_INTL


CASOS_ESCOPO = [
    ("br-remoto-curitiba", "Curitiba, PR", "Remoto", {"Brasil"}),
    ("br-remoto-sjp", "São José dos Pinhais, PR", "Remoto", {"Brasil"}),
    ("worldwide", "Remote - Worldwide", "Remoto", set()),
    ("anywhere", "Remote (Anywhere)", "Remoto", set()),
    ("us-only", "Remote — US only", "Remoto", {"Estados Unidos"}),
    ("brazil-based", "Remote, Brazil based", "Remoto", {"Brasil"}),
    ("latam-brazil", "Remote - LATAM + Brazil", "Remoto", {"Brasil", "LATAM"}),
]


@pytest.mark.parametrize(
    "nome,local,modalidade,esperado",
    CASOS_ESCOPO,
    ids=[c[0] for c in CASOS_ESCOPO],
)
def test_extrair_escopo_remoto(nome, local, modalidade, esperado):
    assert extrair_escopo_remoto(local, modalidade) == esperado


CASOS_BR = [
    # Diretos
    ("mecanico-curitiba", "Engenheiro Mecânico Pleno", "Curitiba, PR", "Presencial", True),
    ("produto-sjp", "Engenheiro de Produto II", "São José dos Pinhais, PR", "Presencial", True),
    ("processos-pinhais", "Analista de Engenharia de Processos II", "Pinhais, PR", "Híbrido", True),
    ("processos-araucaria", "Engenheiro de Processos", "Araucária, PR", "Presencial", True),
    ("testador-curitiba", "Testador de Veículo", "Curitiba, PR", "Presencial", True),
    ("piloto-testes-curitiba", "Piloto de Testes Automotivos", "Curitiba, PR", "Presencial", True),
    ("manutencao-frota", "Analista Técnico Manutenção PL (Frota Leves)", "Curitiba, PR", "Híbrido", True),
    ("qualidade-fornecedor", "Analista de Qualidade Fornecedor", "Curitiba, PR", "Presencial", True),
    ("aplicacao-remoto", "Engenheiro de Aplicação", "Brasil", "Remoto", True),
    ("garantia-remoto", "Analista de Garantia Automotiva", "Brasil", "Remoto", True),
    ("emobility-remoto", "E-Mobility Engineer", "Brasil", "Remoto", True),

    # RMC industrial
    ("campo-largo", "Mechanical Engineer", "Campo Largo, PR", "Presencial", True),
    ("quatro-barras", "Product Engineer", "Quatro Barras, PR", "Híbrido", True),
    ("colombo", "Manufacturing Engineer", "Colombo, PR", "Presencial", True),
    ("fazenda-rio-grande", "Quality Engineer", "Fazenda Rio Grande, PR", "Presencial", True),
    ("campina-grande-sul", "Maintenance Engineer", "Campina Grande do Sul, PR", "Presencial", True),

    # Fora da geografia local
    ("sp-presencial-barrado", "Engenheiro Mecânico", "São Paulo, SP", "Presencial", False),
    ("joinville-hibrido-barrado", "Product Engineer", "Joinville, SC", "Híbrido", False),

    # Falsos positivos por area
    ("software-barrado", "Software Test Engineer", "Curitiba, PR", "Presencial", False),
    ("qa-barrado", "QA Automation Test Engineer", "Curitiba, PR", "Remoto", False),
    ("civil-barrado", "Engenheiro de Projetos - Obras Civis", "Curitiba, PR", "Presencial", False),
    ("aviacao-barrada", "Piloto de Testes - Aviação", "Curitiba, PR", "Presencial", False),
    ("produto-digital-barrado", "Analista de Produto Digital", "Brasil", "Remoto", False),
    ("dados-barrado", "Data Engineer", "Brasil", "Remoto", False),
]


@pytest.mark.parametrize(
    "nome,titulo,local,modalidade,esperado",
    CASOS_BR,
    ids=[c[0] for c in CASOS_BR],
)
def test_combina_com_brasil(nome, titulo, local, modalidade, esperado):
    job = Job(
        titulo=titulo,
        empresa="Teste",
        local=local,
        link=f"https://teste.invalid/{nome}",
        site="Teste",
        modalidade=modalidade,
    )
    assert job.combina_com(PERFIL_BR.regras) == esperado


CASOS_INTL = [
    ("mechanical-worldwide", "Mechanical Engineer", "Remote - Worldwide", "Remoto", True),
    ("design-anywhere", "Mechanical Design Engineer", "Remote (Anywhere)", "Remoto", True),
    ("automotive-latam", "Automotive Engineer", "Remote - LATAM", "Remoto", True),
    ("product-brazil", "Product Development Engineer", "Remote - Brazil", "Remoto", True),
    ("manufacturing-brazil", "Manufacturing Engineer", "Brazil", "Remoto", True),
    ("us-only-barrado", "Mechanical Engineer", "Remote - US only", "Remoto", False),
    ("software-intl-barrado", "Software Quality Engineer", "Remote - Worldwide", "Remoto", False),
    ("civil-intl-barrado", "Civil Engineer", "Remote - Worldwide", "Remoto", False),
    ("presencial-intl-barrado", "Mechanical Engineer", "Lisbon, Portugal", "Presencial", False),
]


@pytest.mark.parametrize(
    "nome,titulo,local,modalidade,esperado",
    CASOS_INTL,
    ids=[c[0] for c in CASOS_INTL],
)
def test_combina_com_internacional(nome, titulo, local, modalidade, esperado):
    job = Job(
        titulo=titulo,
        empresa="Teste",
        local=local,
        link=f"https://teste.invalid/{nome}",
        site="Teste",
        modalidade=modalidade,
    )
    assert job.combina_com(PERFIL_INTL.regras) == esperado


def test_senioridade_nao_muda_prioridade_entre_junior_pleno_senior():
    scores = []
    for nivel in ["Júnior", "Pleno", "Sênior"]:
        job = Job(
            titulo=f"Engenheiro Mecânico {nivel}",
            empresa="Teste",
            local="Curitiba, PR",
            link=f"https://teste.invalid/{nivel}",
            site="Teste",
            modalidade="Presencial",
        )
        scores.append(job.pontuar_relevancia(PERFIL_BR.regras))
    assert len(set(scores)) == 1
