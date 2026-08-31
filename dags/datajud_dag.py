from datetime import datetime, timedelta
from json import load
from airflow.sdk import dag, task
import os , sys 
import logging

sys.path.insert(0,'/opt/airflow/src/')

from pipeline_datajud_bradesco.extract_dados import extract_datajud_dados
from pipeline_datajud_bradesco.transform_dados import data_transformations
from pipeline_datajud_bradesco.load_dados import load_data

URL = os.getenv("URL")
API_KEY = os.getenv("API_KEY")

@dag(
    dag_id="datajud_dag",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retry_delay": timedelta(minutes=5),
        "retries": 3,
    },
    schedule="0 * * * *",
    start_date=datetime(2026, 8, 29),
    catchup=False,
    description="Pipeline ETL - Dados Juridicos do CNJ"
)

def datajud_pipeline():

    @task()
    def extract_data_task():
        extract_datajud_dados(url=URL, api_key=API_KEY)  

    @task()
    def transform_data_task():

        df_processos, df_assuntos, df_movimentos, df_movimentos_tabelados = data_transformations()

        df_processos.to_parquet(
            "/opt/airflow/data/processos.parquet",
            index=False
        )

        df_assuntos.to_parquet(
            "/opt/airflow/data/assuntos.parquet",
            index=False
        )

        df_movimentos.to_parquet(
            "/opt/airflow/data/movimentos.parquet",
            index=False
        )

        df_movimentos_tabelados.to_parquet(
            "/opt/airflow/data/movimentos_tabelados.parquet",
            index=False
        )

        logging.info(f"Processos: {len(df_processos)} registro(s)")

        logging.info(f"Assuntos: {len(df_assuntos)} registro(s)")

        logging.info(f"Movimentos: {len(df_movimentos)} registro(s)")

        logging.info(f"Movimentos Tabelados: {len(df_movimentos_tabelados)} registro(s)")

    @task()
    def load_data_task():

        import pandas as pd

        df_processos = pd.read_parquet("/opt/airflow/data/processos.parquet")

        df_assuntos = pd.read_parquet("/opt/airflow/data/assuntos.parquet")

        df_movimentos = pd.read_parquet("/opt/airflow/data/movimentos.parquet")   

        df_movimentos_tabelados = pd.read_parquet("/opt/airflow/data/movimentos_tabelados.parquet")

        load_data(df_processos=df_processos, df_assuntos=df_assuntos, df_movimentos=df_movimentos, df_movimentos_tabelados=df_movimentos_tabelados)

    extract_data_task() >> transform_data_task() >> load_data_task()

datajud_pipeline()