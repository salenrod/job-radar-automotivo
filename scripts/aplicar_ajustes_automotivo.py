"""Aplica pequenos ajustes no motor compartilhado sem substituir job.py inteiro.

Uso:
    python scripts/aplicar_ajustes_automotivo.py

O script e idempotente: pode ser executado novamente sem duplicar alteracoes.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "job.py"

texto = JOB.read_text(encoding="utf-8")
original = texto

# Senioridade continua sendo exibida, mas deixa de privilegiar/penalizar o score.
# Todos os niveis classificados recebem o mesmo peso neutro (+1). Estagio/Trainee
# permanece 0 no branch existente, mas nunca e filtrado por senioridade.
replacements = {
    "_PESO_SENIORIDADE_ALVO = 2": "_PESO_SENIORIDADE_ALVO = 1",
    "_PESO_SENIORIDADE_ACIMA_DO_ALVO = -2": "_PESO_SENIORIDADE_ACIMA_DO_ALVO = 1",
}

for antigo, novo in replacements.items():
    if antigo in texto:
        texto = texto.replace(antigo, novo)
    elif novo not in texto:
        raise SystemExit(f"Trecho esperado nao encontrado em job.py: {antigo}")

if texto != original:
    JOB.write_text(texto, encoding="utf-8")
    print("job.py atualizado: senioridade neutralizada no score.")
else:
    print("job.py ja estava ajustado; nenhuma alteracao necessaria.")
