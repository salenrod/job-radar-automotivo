import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------------------
# PERFIL BRASIL - ENGENHARIA MECANICA / AUTOMOTIVA / PRODUTO / PROCESSOS
# -----------------------------------------------------------------------------
# Objetivo:
# - vagas remotas no Brasil inteiro;
# - vagas presenciais ou hibridas em Curitiba e eixo industrial da RMC;
# - sem restricao de senioridade;
# - ampliar para funcoes tecnicas que frequentemente aceitam Engenharia
#   Mecanica/Automotiva, mantendo exclusoes explicitas para reduzir ruido.

# Cargos bastante aderentes ao perfil. Podem passar diretamente pelo titulo.
KEYWORDS_CARGO_FORTE = [
    # Engenharia mecanica / automotiva
    "Engenheiro Mecanico",
    "Engenheira Mecanica",
    "Mechanical Engineer",
    "Automotive Engineer",
    "Engenheiro Automotivo",
    "Engenheira Automotiva",
    "Engenheiro de Engenharia Automotiva",

    # Produto / desenvolvimento / powertrain
    "Engenheiro de Produto",
    "Engenheira de Produto",
    "Product Engineer",
    "Product Development Engineer",
    "Engenheiro de Desenvolvimento de Produto",
    "Engenharia de Desenvolvimento de Produto",
    "Analista de Engenharia de Produto",
    "Analista de Produto Automotivo",
    "Analista de Produto Chassis",
    "Analista de Produto Powertrain",
    "Powertrain Engineer",
    "Vehicle Engineer",

    # Projetos / CAD
    "Projetista Mecanico",
    "Projetista Mecânica",
    "Mechanical Designer",
    "Mechanical Design Engineer",
    "CAD Designer",
    "CAD Engineer",
    "Design Engineer",
    "Engenheiro de Projetos Mecanicos",
    "Engenheiro de Projetos Mecânico",

    # Teste / validacao / homologacao
    "Piloto de Testes",
    "Piloto de Rodagem",
    "Testador de Veiculo",
    "Testador de Veículos",
    "Vehicle Test Driver",
    "Vehicle Test Engineer",
    "Automotive Test Engineer",
    "Validation Engineer",
    "Vehicle Validation Engineer",
    "Engenheiro de Validacao",
    "Engenheiro de Validação",
    "Engenheiro de Testes Veiculares",
    "Analista de Testes Automotivos",
    "Tecnico de Testes Veiculares",
    "Técnico de Testes Veiculares",
    "Homologation Engineer",
    "Engenheiro de Homologacao",
    "Engenheiro de Homologação",

    # Processos / manufatura / industrializacao
    "Engenheiro de Processos",
    "Engenheira de Processos",
    "Process Engineer",
    "Manufacturing Engineer",
    "Engenheiro de Manufatura",
    "Engenheira de Manufatura",
    "Industrialization Engineer",
    "Engenheiro de Industrializacao",
    "Engenheiro de Industrialização",
    "Analista de Engenharia de Processos",
    "Analista de Processos Automotivos",
    "Analista de Processos da Pintura Automotiva",
    "Analista de Manufatura",
    "Engenheiro de Metodos",
    "Engenheiro de Métodos",
    "Continuous Improvement Engineer",
    "Engenheiro de Melhoria Continua",
    "Engenheiro de Melhoria Contínua",

    # Manutencao / confiabilidade / frota / PCM
    "Maintenance Engineer",
    "Engenheiro de Manutencao",
    "Engenheiro de Manutenção",
    "Reliability Engineer",
    "Engenheiro de Confiabilidade",
    "Analista de Manutencao Automotiva",
    "Analista de Manutenção Automotiva",
    "Analista de Manutencao de Frotas",
    "Analista de Manutenção de Frotas",
    "Analista Tecnico Manutencao",
    "Analista Técnico Manutenção",
    "Analista de PCM",
    "Planejador de Manutencao",
    "Planejador de Manutenção",
    "Fleet Maintenance Analyst",
    "Fleet Analyst",
    "Analista de Frotas",

    # Qualidade / fornecedor
    "Quality Engineer",
    "Engenheiro de Qualidade",
    "Engenheira de Qualidade",
    "Supplier Quality Engineer",
    "Supplier Development Engineer",
    "Engenheiro de Desenvolvimento de Fornecedores",
    "Analista de Qualidade Fornecedor",
    "Analista de Qualidade de Fornecedores",
    "Analista de Qualidade Automotiva",

    # Aplicacao / campo / suporte tecnico
    "Application Engineer",
    "Applications Engineer",
    "Engenheiro de Aplicacao",
    "Engenheiro de Aplicação",
    "Field Engineer",
    "Field Service Engineer",
    "Engenheiro de Campo",
    "Product Support Engineer",
    "Engenheiro de Suporte ao Produto",
    "Technical Support Engineer",
    "Engenheiro de Suporte Tecnico",
    "Engenheiro de Suporte Técnico",
    "Sales Engineer",
    "Technical Sales Engineer",
    "Engenheiro de Vendas Tecnicas",
    "Engenheiro de Vendas Técnicas",

    # Garantia / pos-venda / assistencia tecnica
    "Warranty Analyst",
    "Warranty Engineer",
    "Analista de Garantia Automotiva",
    "Analista de Garantia",
    "Garantista Automotivo",
    "After Sales Analyst",
    "After Sales Engineer",
    "Analista de Pos-Venda",
    "Analista de Pós-Venda",
    "Analista de Pos Vendas",
    "Analista de Pós Vendas",
    "Analista de Assistencia Tecnica",
    "Analista de Assistência Técnica",
    "Consultor Tecnico Automotivo",
    "Consultor Técnico Automotivo",

    # Eletromobilidade
    "E-Mobility Engineer",
    "E-Mobility Analyst",
    "Electromobility Engineer",
    "Engenheiro de Eletromobilidade",
    "Analista de Eletromobilidade",
]

# Cargos mais amplos, mas ainda razoavelmente compativeis. Precisam conter
# tambem um qualificador tecnico no proprio titulo, salvo quando explicitamente
# permitido por futura alteracao de config.
KEYWORDS_CARGO_AMBIGUO = [
    "Engenheiro de Projetos",
    "Project Engineer",
    "Engenheiro de Testes",
    "Test Engineer",
    "Analista de Produto",
    "Product Analyst",
    "Analista de Processos",
    "Process Analyst",
    "Analista de Qualidade",
    "Quality Analyst",
    "Analista de Manutencao",
    "Analista de Manutenção",
    "Maintenance Analyst",
    "Analista Tecnico",
    "Analista Técnico",
    "Technical Analyst",
    "Consultor Tecnico",
    "Consultor Técnico",
    "Technical Consultant",
    "Especificador Tecnico",
    "Especificador Técnico",
]

# Mantemos o nome legado QUALIFICADORES_DADOS porque perfis.py/job.py esperam
# exatamente essa variavel. Aqui o conteudo e de engenharia, nao de dados.
QUALIFICADORES_DADOS = [
    "mecan", "mechanical", "automot", "automotive", "vehicle", "veicular",
    "produto", "product", "process", "processo", "manufactur", "manufatura",
    "industrial", "qualidade", "quality", "supplier", "fornecedor",
    "manutenc", "maintenance", "frota", "fleet", "pcm", "reliability",
    "confiabilidade", "teste", "test", "validation", "validacao", "validacao",
    "homolog", "application", "aplicacao", "campo", "field service",
    "garantia", "warranty", "after sales", "pos-venda", "pos venda",
    "powertrain", "chassis", "cad", "solidworks", "autocad", "catia",
    "e-mobility", "electromobility", "ev", "phev", "mobilidade eletrica",
]

# Exclusoes no TITULO. Vencem ate keyword forte para impedir que funcoes de
# software/IT/civil com nomes genericos de Engineer/Test/Product entrem por
# acidente.
KEYWORDS_EXCLUSAO_TITULO = [
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
    "Engenheiro de Dados",
    "Data Analyst",
    "Analista de Dados",
    "Machine Learning",
    "Cybersecurity",
    "Cyber Security",
    "Seguranca da Informacao",
    "Segurança da Informação",
    "Civil Engineer",
    "Engenheiro Civil",
    "Engenharia Civil",
    "Structural Engineer",
    "Engenheiro Estrutural",
    "Arquitetura",
    "Construction",
    "Obras",
    "Aircraft",
    "Aviation",
    "Aviacao",
    "Aviação",
    "Aeronautica",
    "Aeronáutica",
    "Drone",
    "Produto Digital",
    "Digital Product",
    "Recursos Humanos",
    "Financeiro",
    "Contabil",
    "Contábil",
    "Product Manager",
    "Product Owner",
    "Gerente de Produto",
]

PERMITIR_CARGO_AMBIGUO_SEM_QUALIFICADOR = False

FERRAMENTAS_TITULO = [
    "SolidWorks", "AutoCAD", "CATIA", "Creo", "Siemens NX", "NX", "CAD",
    "APQP", "FMEA",
]

QUALIFICADORES_CARGO = [
    "analista", "analyst", "engenheiro", "engineer", "especialista", "specialist",
    "projetista", "designer", "consultor", "consultant", "tecnico", "technical",
    "piloto", "testador",
]

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

# -----------------------------------------------------------------------------
# BUSCA
# -----------------------------------------------------------------------------
# Core roda a cada ciclo para reduzir a chance de perder vagas novas de familias
# essenciais. O restante fica em rodizio.
TERMOS_CORE = [
    "engenheiro mecanico",
    "mechanical engineer",
    "engenheiro de produto",
    "engenheiro de processos",
    "engenharia automotiva",
    "manutencao automotiva",
    "piloto de testes",
    "vehicle test engineer",
]

TERMOS_BUSCA = sorted(set([
    # Formacao / busca exploratoria por requisitos
    "engenharia mecanica",
    "mechanical engineering",
    "engenharia automotiva",
    "automotive engineering",

    # Produto / projeto / CAD
    "engenheiro de produto",
    "product engineer",
    "product development engineer",
    "projetista mecanico",
    "mechanical design engineer",
    "mechanical designer",
    "cad engineer",
    "solidworks engineer",
    "catia engineer",

    # Processos / manufatura
    "engenheiro de processos",
    "process engineer",
    "manufacturing engineer",
    "engenheiro de manufatura",
    "industrialization engineer",
    "analista de processos automotivos",
    "analista de engenharia de processos",
    "continuous improvement engineer",

    # Teste / validacao / homologacao
    "piloto de testes",
    "piloto de rodagem",
    "testador de veiculo",
    "vehicle test engineer",
    "automotive test engineer",
    "validation engineer",
    "vehicle validation engineer",
    "homologation engineer",

    # Manutencao / frota / PCM / confiabilidade
    "analista de manutencao",
    "manutencao automotiva",
    "analista de frotas",
    "fleet maintenance analyst",
    "maintenance engineer",
    "reliability engineer",
    "analista pcm",

    # Qualidade / fornecedores
    "quality engineer",
    "supplier quality engineer",
    "analista de qualidade fornecedor",
    "supplier development engineer",

    # Aplicacoes / campo / vendas tecnicas
    "application engineer",
    "engenheiro de aplicacao",
    "field service engineer",
    "product support engineer",
    "technical support engineer",
    "sales engineer mechanical",

    # Garantia / pos-venda
    "analista de garantia automotiva",
    "warranty analyst automotive",
    "after sales engineer",
    "analista pos venda automotivo",
    "consultor tecnico automotivo",

    # Eletromobilidade
    "e-mobility engineer",
    "electromobility engineer",
    "engenheiro eletromobilidade",
    "powertrain engineer",
    "ev vehicle engineer",
]))

TERMOS_POR_CICLO = 10

# -----------------------------------------------------------------------------
# LOCALIZACAO
# -----------------------------------------------------------------------------
# Presencial/hibrido: Curitiba + eixo industrial da RMC.
# Remoto: Brasil inteiro.
CIDADES = [
    "Remoto",
    "Curitiba",
    "Sao Jose dos Pinhais",
    "Araucaria",
    "Pinhais",
    "Fazenda Rio Grande",
    "Campo Largo",
    "Quatro Barras",
    "Campina Grande do Sul",
    "Colombo",
]

# Mantidos apenas por compatibilidade da arquitetura. O eixo iberico presencial
# fica desligado.
CIDADES_EUROPA_IBERICA = [
    "Portugal", "Lisboa", "Porto", "Braga", "Espanha", "Espana", "Spain",
    "Madrid", "Barcelona", "Valencia",
]
ATIVAR_EIXO_IBERICO_BR = False

# LinkedIn: busca completa focada em Curitiba (que normalmente inclui a RMC)
# e uma segunda localizacao apenas remota para o Brasil inteiro.
LOCATIONS_LINKEDIN = ["Curitiba, Paraná, Brazil"]
LOCATIONS_LINKEDIN_REMOTO_APENAS = ["Brazil"]

MERCADOS_REMOTO_ACEITOS = ["Brasil", "LATAM"]

# Mesma empresa+titulo so bloqueia reabertura recente; URL identica continua
# duplicata permanente.
JANELA_DEDUP_CHAVE_SECUNDARIA_DIAS = int(
    os.getenv("JANELA_DEDUP_CHAVE_SECUNDARIA_DIAS", 14)
)

# -----------------------------------------------------------------------------
# EXECUCAO / DIGEST / TELEGRAM
# -----------------------------------------------------------------------------
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))
LIMIAR_DIGEST_IMEDIATO = 6
DIGEST_HORA_UTC = 0

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.db")
