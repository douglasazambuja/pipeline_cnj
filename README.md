# Pipeline de Dados Jurídicos — DataJud

Pipeline de Engenharia de Dados desenvolvido para extração, transformação e armazenamento de dados processuais disponibilizados pela API pública **DataJud, do Conselho Nacional de Justiça (CNJ)**.

O projeto implementa um fluxo ETL orquestrado pelo **Apache Airflow**, com os dados estruturados e armazenados em **PostgreSQL**.

## 🏗️ Arquitetura

```text
                    ┌─────────────────┐
                    │   API DataJud   │
                    │       CNJ       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Extract     │
                    │     Python      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Transform    │
                    │ Pandas / Python │
                    └────────┬────────┘
                             │
                       Parquet Files
                             │
                             ▼
                    ┌─────────────────┐
                    │      Load       │
                    │    PostgreSQL   │
                    └─────────────────┘

              Apache Airflow
       ───────────────────────────────
          Orquestra todo o fluxo
```

## 🚀 Tecnologias utilizadas

* **Python 3.12+** — desenvolvimento do pipeline
* **Pandas** — transformação e estruturação dos dados
* **Requests** — consumo da API DataJud
* **SQLAlchemy / Psycopg2** — conexão e carga no PostgreSQL
* **PostgreSQL 16** — armazenamento dos dados
* **Apache Airflow 3.1.7** — orquestração e agendamento
* **Docker / Docker Compose** — criação e isolamento do ambiente
* **Redis** — broker utilizado pelo Airflow
* **Parquet** — armazenamento intermediário entre as etapas do pipeline
* **uv** — gerenciamento do ambiente e dependências Python

## 🔄 Fluxo do ETL

O pipeline é dividido em três responsabilidades principais:

### 1. Extract

A etapa de extração realiza uma requisição à API pública do DataJud e armazena temporariamente a resposta em JSON.

```text
API DataJud
     ↓
requests.post()
     ↓
data/datajud_dados.json
```

### 2. Transform

Os dados JSON são convertidos em DataFrames e normalizados utilizando Pandas.

Durante essa etapa são realizados:

* Normalização do JSON;
* Padronização dos nomes das colunas;
* Tratamento de campos de data e hora;
* Separação das estruturas aninhadas;
* Criação dos DataFrames de processos;
* Criação dos DataFrames de assuntos;
* Criação dos DataFrames de movimentos;
* Criação dos DataFrames de movimentos tabelados.

Os dados transformados são armazenados em arquivos Parquet para serem utilizados pela etapa seguinte.

```text
JSON
 ↓
DataFrame
 ↓
Normalização
 ↓
Separação das entidades
 ↓
Parquet
```

### 3. Load

A etapa de carga lê os arquivos Parquet e persiste os dados no PostgreSQL.

As principais tabelas são:

* `processos`
* `assuntos`
* `movimentos`
* `movimentos_tabelados`

A carga é realizada utilizando Pandas, SQLAlchemy e PostgreSQL.

## ⏰ Orquestração

O Apache Airflow é responsável por controlar a execução do pipeline.

O DAG possui o seguinte fluxo:

```text
extract_data_task
        ↓
transform_data_task
        ↓
load_data_task
```

A execução está configurada para ocorrer **a cada hora**.

Além disso, o pipeline possui:

* 3 tentativas de reexecução em caso de falha;
* intervalo de 5 minutos entre tentativas;
* `catchup=False`;
* logs de acompanhamento das etapas;
* dependência explícita entre as tarefas.

## 🐳 Execução com Docker

### Pré-requisitos

Antes de executar o projeto, tenha instalado:

* Docker Desktop
* Git
* WSL2 + Ubuntu (recomendado para Windows)

### 1. Clone o repositório

```bash
git clone https://github.com/douglasazambuja/projeto_juridico.git
cd projeto_juridico
```

### 2. Configure as variáveis de ambiente

O projeto utiliza variáveis de ambiente para configuração da API e do PostgreSQL.

Crie o arquivo:

```text
config/.env
```

Com as seguintes variáveis:

```env
URL=<URL_DA_API_DATAJUD>
API_KEY=<SUA_API_KEY>

POSTGRES_DB=cnj_database
POSTGRES_USER=azamba
POSTGRES_PASSWORD=123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

> Não compartilhe credenciais reais em repositórios públicos. Utilize um arquivo `.env` local e mantenha-o fora do controle de versão.

### 3. Suba os containers

Na raiz do projeto:

```bash
docker compose up -d
```

O Docker Compose inicializa a infraestrutura necessária para o Airflow e PostgreSQL, incluindo o Redis utilizado pelo Airflow.

### 4. Verifique os containers

```bash
docker compose ps
```

Os serviços devem estar em execução.

### 5. Acesse o Airflow

Abra no navegador:

```text
http://localhost:8080
```

O Airflow disponibiliza a interface para acompanhar o DAG, tarefas, logs e histórico das execuções.

## ▶️ Executando o pipeline

Depois que os containers estiverem em execução:

1. Acesse o Airflow em `http://localhost:8080`;
2. Localize o DAG `datajud_dag`;
3. Ative o DAG;
4. Execute manualmente ou aguarde o próximo agendamento.

O fluxo será executado na seguinte ordem:

```text
Extract
   ↓
Transform
   ↓
Load
```

## 🗄️ PostgreSQL

O PostgreSQL é disponibilizado pelo Docker na porta `5433` do host.

Para conexão externa, utilize:

```text
Host: localhost
Port: 5433
Database: cnj_database
User: azamba
Password: 123
```

Dentro da rede Docker, o PostgreSQL utiliza:

```text
Host: postgres
Port: 5432
```

Isso permite acessar o banco por ferramentas como **DBeaver**.

## 🔎 Consultando os dados

Após uma execução bem-sucedida do pipeline, os dados podem ser consultados no PostgreSQL.

Exemplo:

```sql
SELECT *
FROM datajud.processos;
```

Para consultar os movimentos:

```sql
SELECT *
FROM datajud.movimentos;
```

Para relacionar processos e movimentos:

```sql
SELECT
    p.processos_numero_processo,
    m.movimentos_codigo,
    m.movimentos_nome,
    m.movimentos_data_hora
FROM datajud.processos p
JOIN datajud.movimentos m
    ON p.processos_id = m.processo_id;
```

## 📁 Estrutura do projeto

```text
projeto_juridico/
│
├── config/
│   └── .env
│
├── dags/
│   └── datajud_dag.py
│
├── data/
│   ├── datajud_dados.json
│   ├── processos.parquet
│   ├── assuntos.parquet
│   ├── movimentos.parquet
│   └── movimentos_tabelados.parquet
│
├── logs/
│
├── notebooks/
│
├── src/
│   └── pipeline_datajud/
│       ├── extract_dados.py
│       ├── transform_dados.py
│       ├── load_dados.py
│       └── main.py
│
├── docker-compose.yaml
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

## 🧩 Separação de responsabilidades

A aplicação foi estruturada para manter cada etapa com uma responsabilidade específica:

| Componente           | Responsabilidade                      |
| -------------------- | ------------------------------------- |
| `extract_dados.py`   | Extração dos dados da API             |
| `transform_dados.py` | Limpeza, normalização e estruturação  |
| `load_dados.py`      | Persistência no PostgreSQL            |
| `datajud_dag.py`     | Orquestração do pipeline              |
| PostgreSQL           | Armazenamento estruturado             |
| Docker               | Padronização e isolamento do ambiente |

Essa separação facilita a manutenção, os testes e a evolução do pipeline.

## 📊 Benefícios da solução

* Automação da ingestão dos dados;
* Execução periódica sem intervenção manual;
* Centralização dos dados em PostgreSQL;
* Estruturação dos dados jurídicos em diferentes entidades;
* Separação das responsabilidades do ETL;
* Monitoramento das execuções pelo Airflow;
* Tratamento de falhas com retries;
* Persistência intermediária em formato Parquet;
* Ambiente reproduzível através do Docker;
* Estrutura preparada para evolução do pipeline.

## 📌 Observações

Este projeto utiliza a **API pública do DataJud/CNJ** como fonte de dados.

A implementação foi desenvolvida com finalidade de estudo e demonstração de conceitos de Engenharia de Dados, incluindo:

* ETL;
* Orquestração;
* Modelagem relacional;
* Qualidade e transformação de dados;
* Persistência;
* Containerização;
* Monitoramento de pipelines.

## 👨‍💻 Autor

**Douglas Azambuja**

Projeto desenvolvido como case de Engenharia de Dados.
