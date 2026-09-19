"""Diagnóstico local do jobs.db sem alterar nenhum dado.

Uso:
  python scripts/auditar_estado.py
  python scripts/auditar_estado.py --job-id 4456333167 --job-id 4455491822
"""

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import DB_PATH
from job import Job
from perfis import PERFIS


def _job_da_linha(r: sqlite3.Row) -> Job:
    return Job(
        titulo=r["titulo"] or "",
        empresa=r["empresa"] or "",
        local=r["local"] or "",
        link=r["link"] or "",
        site=r["site"] or "",
        publicado_em=r["publicado_em"] or "",
        modalidade=r["modalidade"] or "",
        escopo_indefinido=(r["site"] or "").lower() == "we work remotely",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", action="append", default=[], help="ID numérico visível na URL da vaga")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print(f"DB: {DB_PATH}")
    print(f"Total de vagas: {conn.execute('SELECT COUNT(*) FROM vagas_vistas').fetchone()[0]}")

    for chave, perfil in PERFIS.items():
        rows = conn.execute(
            """
            SELECT id,titulo,empresa,local,link,site,publicado_em,modalidade,
                   relevancia,exploratoria
            FROM vagas_vistas
            WHERE perfil=? AND digest_pendente=1
            """,
            (chave,),
        ).fetchall()
        validas = 0
        obsoletas = 0
        for r in rows:
            exploratoria = bool(r["exploratoria"])
            if exploratoria and not perfil.eixo_secundario_ativo:
                obsoletas += 1
                continue
            regras = (
                perfil.regras_eixo_secundario
                if exploratoria and perfil.regras_eixo_secundario is not None
                else perfil.regras
            )
            if _job_da_linha(r).combina_com(regras):
                validas += 1
            else:
                obsoletas += 1
        print(f"{perfil.nome}: digest pendente={len(rows)}, válidas hoje={validas}, obsoletas={obsoletas}")

        for meta in (
            f"heartbeat_ultimo_dia_{chave}",
            f"digest_ultimo_dia_{chave}",
            f"baixa_frequencia_ultimo_dia_{chave}",
            f"termos_offset_rotativos_v2_{chave}",
            f"termos_offset_{chave}",
        ):
            row = conn.execute("SELECT valor FROM metadados WHERE chave=?", (meta,)).fetchone()
            if row:
                print(f"  {meta}={row[0]}")

    for job_id in args.job_id:
        rows = conn.execute(
            """
            SELECT titulo,empresa,link,encontrada_em,perfil,digest_pendente,relevancia
            FROM vagas_vistas
            WHERE link LIKE ?
            ORDER BY encontrada_em DESC
            """,
            (f"%{job_id}%",),
        ).fetchall()
        if not rows:
            print(f"Job ID {job_id}: NÃO encontrado no jobs.db")
        else:
            print(f"Job ID {job_id}: encontrado {len(rows)} vez(es)")
            for r in rows:
                print(" ", dict(r))


if __name__ == "__main__":
    main()
