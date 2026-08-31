import requests
import json
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

URL = os.getenv("URL")
API_KEY = os.getenv("API_KEY")

def extract_datajud_dados(url: str, api_key: str) -> list:

    headers = {
    "Authorization": f"APIKey {api_key}",
    "Content-Type": "application/json" 
    }

    body = {
        "size": 1,
        "query": {
            "match_all": {}
        }
    }

    logging.info("Iniciando extração dos dados do DataJud")
        
    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    # Resposta da API
    data = response.json()

    if response.status_code != 200:
        logging.error(
            f"Erro na requisição. "
            f"Status: {response.status_code}. "
            f"Resposta: {response.text}"
        )
        response.raise_for_status()

    # Resultado da extração
    output_path = 'data/datajud_dados.json'
    output_dir = Path(output_path).parent
    output_dir.mkdir(
        parents=True,
        exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    logging.info(f"Extração concluída. Dados salvos em {output_path}")

    return data