# Perfil INTERNACIONAL - Engenharia Mecanica / Automotiva e funcoes adjacentes.
# Somente vagas remotas. O candidato deve poder trabalhar a partir do Brasil,
# LATAM ou em vagas Worldwide/Anywhere sem restricao geografica explicita.

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    DB_PATH,
    CIDADES_EUROPA_IBERICA,
)  # noqa: F401

KEYWORDS_INTL = [
    # Core mechanical / automotive
    "Mechanical Engineer",
    "Automotive Engineer",
    "Mechanical Design Engineer",
    "Mechanical Designer",
    "CAD Engineer",
    "CAD Designer",
    "Product Engineer",
    "Product Development Engineer",
    "Vehicle Engineer",
    "Powertrain Engineer",

    # Testing / validation / homologation
    "Vehicle Test Engineer",
    "Automotive Test Engineer",
    "Vehicle Validation Engineer",
    "Validation Engineer",
    "Homologation Engineer",
    "Vehicle Test Driver",

    # Manufacturing / process / quality
    "Manufacturing Engineer",
    "Process Engineer",
    "Industrialization Engineer",
    "Continuous Improvement Engineer",
    "Quality Engineer",
    "Supplier Quality Engineer",
    "Supplier Development Engineer",

    # Maintenance / reliability / fleet
    "Maintenance Engineer",
    "Reliability Engineer",
    "Maintenance Planner",
    "Fleet Maintenance Analyst",
    "Fleet Analyst",

    # Applications / field / support / technical sales
    "Application Engineer",
    "Applications Engineer",
    "Field Engineer",
    "Field Service Engineer",
    "Product Support Engineer",
    "Technical Support Engineer",
    "Sales Engineer",
    "Technical Sales Engineer",

    # Warranty / aftersales
    "Warranty Analyst",
    "Warranty Engineer",
    "After Sales Analyst",
    "After Sales Engineer",

    # E-mobility
    "E-Mobility Engineer",
    "E-Mobility Analyst",
    "Electromobility Engineer",
]

KEYWORDS_EXCLUSAO_TITULO_INTL = [
    "Software",
    "Software Engineer",
    "Software Test",
    "Software Quality",
    "QA Automation",
    "Test Automation",
    "Automation QA",
    "SDET",
    "Frontend",
    "Backend",
    "Full Stack",
    "Mobile Developer",
    "DevOps",
    "SRE",
    "Site Reliability",
    "Cloud Engineer",
    "Data Engineer",
    "Machine Learning",
    "Cybersecurity",
    "Cyber Security",
    "Civil Engineer",
    "Structural Engineer",
    "Construction",
    "Aircraft",
    "Aviation",
    "Drone",
    "Product Manager",
    "Product Owner",
]

TERMOS_CORE_INTL = [
    "mechanical engineer",
    "mechanical design engineer",
    "automotive engineer",
    "product engineer",
    "manufacturing engineer",
    "vehicle test engineer",
]

TERMOS_BUSCA_INTL = sorted(set([
    "mechanical engineer remote",
    "mechanical design engineer remote",
    "mechanical designer remote",
    "automotive engineer remote",
    "product engineer mechanical remote",
    "product development engineer automotive remote",
    "cad engineer remote",
    "solidworks engineer remote",
    "catia engineer remote",
    "manufacturing engineer remote",
    "process engineer mechanical remote",
    "industrialization engineer remote",
    "quality engineer automotive remote",
    "supplier quality engineer automotive remote",
    "supplier development engineer remote",
    "vehicle test engineer remote",
    "automotive test engineer remote",
    "validation engineer automotive remote",
    "homologation engineer remote",
    "maintenance engineer remote",
    "reliability engineer mechanical remote",
    "fleet maintenance analyst remote",
    "application engineer mechanical remote",
    "field service engineer mechanical remote",
    "product support engineer automotive remote",
    "technical sales engineer mechanical remote",
    "warranty analyst automotive remote",
    "after sales engineer automotive remote",
    "e-mobility engineer remote",
    "electromobility engineer remote",
    "powertrain engineer remote",
    "mechanical engineering latam",
    "automotive engineering latam",
    "mechanical engineer latin america",
]))

TERMOS_POR_CICLO_INTL = 8
IDIOMAS_EXIGIDOS_INTL = None

# Busca internacional orientada a vagas que possam ser exercidas do Brasil.
# Worldwide/Anywhere e vagas sem restricao explicita continuam elegiveis pelo
# parser de mercado; Brazil/Latin America ajudam o LinkedIn a descobrir vagas.
LOCATIONS_INTL = [
    "Brazil",
    "Latin America",
]

CIDADES_INTL = ["Remote", "Remoto"]

# Aceita remoto explicitamente direcionado a Brasil/LATAM. Worldwide/Anywhere
# e tratado como sem restricao pelo job.py e tambem passa.
MERCADOS_REMOTO_ACEITOS_INTL = [
    "Brasil",
    "LATAM",
]

ATIVAR_EIXO_IBERICO = False

# Fonte de baixa frequencia. Inclui Brasil e dois mercados internacionais para
# ampliar descoberta, mas o filtro final continua exigindo remoto elegivel.
DOMINIOS_INDEED_INTL = {
    "Brasil": "br.indeed.com",
    "Portugal": "pt.indeed.com",
    "Espanha": "es.indeed.com",
}
