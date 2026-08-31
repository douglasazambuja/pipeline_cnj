import pandas as pd
import json
from pathlib import Path
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

path_name = Path(__file__).parent.parent.parent / 'data' / 'datajud_dados.json'

columns_names_to_rename = {
    "_source.id": "processos_id",
    "_source.tribunal": "processos_tribunal",
    "_source.grau": "processos_grau",
    "_source.numeroProcesso": "processos_numero_processo",
    "_source.dataAjuizamento": "processos_data_ajuizamento",
    "_source.nivelSigilo": "processos_nivel_sigilo",
    "_source.orgaoJulgador.codigo": "processos_orgao_julgador_codigo",
    "_source.orgaoJulgador.nome": "processos_orgao_julgador_nome",
    "_source.orgaoJulgador.codigoMunicipioIBGE": "processos_orgao_julgador_codigo_municipio_ibge",
    "_source.classe.codigo": "processos_classe_codigo",
    "_source.classe.nome": "processos_classe_nome",
    "_source.sistema.codigo": "processos_sistema_codigo",
    "_source.sistema.nome": "processos_sistema_nome",
    "_source.formato.codigo": "processos_formato_codigo",
    "_source.formato.nome": "processos_formato_nome",
    "_source.dataHoraUltimaAtualizacao": "processos_data_hora_ultima_atualizacao",
}

columns_datetime_to_normalize = [
    "processos_data_ajuizamento",
    "processos_data_hora_ultima_atualizacao"
]


def create_dataframe(path_name: str) -> pd.DataFrame:
    path = path_name

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado{path}")

    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logging.info(f"\n DataFrame criado com sucesso {len(df)} linha(s)")

    return df 


def normalize_dataframe_columns(df: pd.DataFrame)-> pd.DataFrame:

    df_datajud = pd.json_normalize(df['hits.hits'].apply(lambda x: x[0]))                       

    df = pd.concat([df,df_datajud], axis=1)

    print("\nColunas Normalizadas:")
    print(df.columns.tolist())
                               
    logging.info(f"\n Normalização concluída.")

    return df 


def rename_dataframe_columns(df: pd.DataFrame, columns_names:dict[str, str]) -> pd.DataFrame:

    # Mantém somente as colunas definidas
    df = df[list(columns_names.keys())]

    # Padroniza os nomes das colunas.
    df = df.rename(columns=columns_names)

    logging.info(f"\n Colunas renomeadas: {columns_names}")

    return df


def normalize_datatime_coluns(df: pd.DataFrame, columns_names: list[str]) -> pd.DataFrame:

    for column in columns_names:
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.tz_localize(None)

    logging.info(f"\n Colunas de data/hora normalizadas: {columns_names}")

    return df


def create_movimentos_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    movimentos = []

    for _, row in df.iterrows():

        processo_id = row["_source.id"]
        lista_movimentos = row.get("_source.movimentos", [])

        if not isinstance(lista_movimentos, list):
            continue

        for movimento in lista_movimentos:

            movimentos.append({
                "processo_id": processo_id,
                "movimentos_codigo": movimento.get("codigo"),
                "movimentos_nome": movimento.get("nome"),
                "movimentos_data_hora": movimento.get("dataHora"),
            })

    df_movimentos = pd.DataFrame(movimentos)

    if not df_movimentos.empty:
        df_movimentos["movimentos_data_hora"] = pd.to_datetime(
            df_movimentos["movimentos_data_hora"],
            errors="coerce"
        ).dt.tz_localize(None)

    logging.info(
        f"DataFrame movimentos criado com {len(df_movimentos)} registro(s)"
    )

    return df_movimentos


def create_movimentos_tabelados_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    movimentos_tabelados = []

    for _, row in df.iterrows():

        processo_id = row["_source.id"]
        lista_movimentos = row.get("_source.movimentos", [])

        if not isinstance(lista_movimentos, list):
            continue

        for movimento in lista_movimentos:

            movimentos_codigo = movimento.get("codigo")

            lista_movimentos_tabelados = movimento.get(
                "complementosTabelados",
                []
            )

            if not isinstance(lista_movimentos_tabelados, list):
                continue

            for complemento in lista_movimentos_tabelados:

                movimentos_tabelados.append({
                    "processo_id": processo_id,
                    "movimentos_codigo": movimentos_codigo,
                    "movimentostabelados_codigo": complemento.get("codigo"),
                    "movimentostabelados_descricao": complemento.get("descricao"),
                    "movimentostabelados_valor": complemento.get("valor"),
                    "movimentostabelados_nome": complemento.get("nome"),
                })

    df_movimentos_tabelados = pd.DataFrame(movimentos_tabelados)

    logging.info(
        f"DataFrame movimentos_tabelados criado com "
        f"{len(df_movimentos_tabelados)} registro(s)"
    )

    return df_movimentos_tabelados


def create_assuntos_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    assuntos = []

    for _, row in df.iterrows():

        processo_id = row["_source.id"]
        lista_assuntos = row.get("_source.assuntos", [])

        if not isinstance(lista_assuntos, list):
            continue

        for assunto in lista_assuntos:

            assuntos.append({
                "processo_id": processo_id,
                "assuntos_codigo": assunto.get("codigo"),
                "assuntos_nome": assunto.get("nome")
            })

    df_assuntos = pd.DataFrame(assuntos)

    logging.info(
        f"DataFrame assuntos criado com {len(df_assuntos)} registro(s)"
    )

    return df_assuntos


def data_transformations():

    logging.info("\n Iniciando transformações")

    # Criação do DataFrame
    df = create_dataframe(path_name)

    # Normalização dos dados do DataJud
    df = normalize_dataframe_columns(df)

    # Separação das estruturas 1:N
    df_assuntos = create_assuntos_dataframe(df)
    df_movimentos = create_movimentos_dataframe(df)
    df_movimentos_tabelados = create_movimentos_tabelados_dataframe(df)

    # Transformação dos dados de processos
    df_processos = rename_dataframe_columns(df, columns_names_to_rename)    
    df_processos = normalize_datatime_coluns(df_processos, columns_datetime_to_normalize)
    
    logging.info("\n Transformações concluídas")

    return df_processos, df_assuntos, df_movimentos, df_movimentos_tabelados
