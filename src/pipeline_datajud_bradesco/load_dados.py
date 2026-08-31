from pathlib import Path
from urllib.parse import quote_plus
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
load_dotenv(env_path)

USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASE = os.getenv('POSTGRES_DB')
HOST = os.getenv('POSTGRES_HOST')
PORT = os.getenv('POSTGRES_PORT')


def get_engine():
    return create_engine(f"postgresql+psycopg2://{USER}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DATABASE}")


def load_data(df_processos: pd.DataFrame, df_assuntos: pd.DataFrame, df_movimentos: pd.DataFrame, df_movimentos_tabelados: pd.DataFrame):

    engine = get_engine()

    try:
        # Carrega o dataframe de processos
        df_processos.to_sql(
            name="processos",
            con=engine,
            schema="datajud",
            if_exists="append",
            index=False
        )

        logging.info(f"Processos carregados: {len(df_processos)} registro(s)")

    except Exception:
        logging.exception("Erro durante a carga dos processos no PostgreSQL.")
        raise

    try:
        # Carrega o dataframe de assuntos
        df_assuntos.to_sql(
            name="assuntos",
            con=engine,
            schema="datajud",
            if_exists="append",
            index=False
        )

        logging.info(f"Assuntos carregados: {len(df_assuntos)} registro(s)")

    except Exception:
        logging.exception(
            "Erro durante a carga dos assuntos no PostgreSQL."
        )
        raise

    try:
        # Carrega o dataframe de movimentos
        df_movimentos.to_sql(
            name="movimentos",
            con=engine,
            schema="datajud",
            if_exists="append",
            index=False
        )

        logging.info(f"Movimentos carregados: {len(df_movimentos)} registro(s)")

    except Exception:
        logging.exception(
            "Erro durante a carga dos movimentos no PostgreSQL."
        )
        raise
    try:
        # Carrega o dataframe de movimentos
        df_movimentos_tabelados.to_sql(
            name="movimentos_tabelados",
            con=engine,
            schema="datajud",
            if_exists="append",
            index=False
        )

        logging.info(f"Movimentos Tabelados carregados: {len(df_movimentos_tabelados)} registro(s)")

    except Exception:
        logging.exception("Erro durante a carga dos movimentos_tabelados no PostgreSQL.")
        raise

    logging.info("Dados carregados com sucesso no PostgreSQL!")      