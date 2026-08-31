""" from pathlib import Path
from dotenv import load_dotenv
import logging
import os

from pipeline_datajud_bradesco.extract_dados import extract_datajud_dados
from pipeline_datajud_bradesco.transform_dados import data_transformations
from pipeline_datajud_bradesco.load_dados import load_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


env_path = Path(__file__).parent.parent.parent / "config" / ".env"

load_dotenv(env_path)

URL = os.getenv("URL")
API_KEY = os.getenv("API_KEY")


def main():

    logging.info("Iniciando pipeline DataJud")

    try:

        # Extract
        logging.info("Iniciando etapa de Extract")

        extract_datajud_dados(
            URL,
            API_KEY
        )

        # Transform
        logging.info("Iniciando etapa de Transform")

        df_processos, df_assuntos, df_movimentos = data_transformations()

        logging.info(
            f"Transform concluído: "
            f"{len(df_processos)} processos, "
            f"{len(df_assuntos)} assuntos, "
            f"{len(df_movimentos)} movimentos"
        )

        # Load
        logging.info("Iniciando etapa de Load")

        load_data(
            df_processos=df_processos,
            df_assuntos=df_assuntos,
            df_movimentos=df_movimentos
        )

        logging.info(
            "Pipeline DataJud concluído com sucesso."
        )

    except Exception:
        logging.exception(
            "Pipeline DataJud finalizado com erro."
        )
        raise


if __name__ == "__main__":
    main() """