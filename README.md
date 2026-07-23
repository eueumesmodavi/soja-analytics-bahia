# Análise da Cultura da Soja no Extremo Oeste Baiano

## Sobre o Projeto
Este projeto acadêmico tem como objetivo desenvolver um pipeline de dados ponta a ponta para analisar a correlação entre as condições climáticas, a produtividade e a rentabilidade da cultura da soja na região do Extremo Oeste Baiano. 

Através do cruzamento de dados meteorológicos, índices de produtividade e preços de mercado, a ferramenta busca fornecer suporte à decisão estratégica, ajudando a identificar janelas ideais de comercialização e a mitigar riscos associados a safras climáticas.

## Arquitetura de Dados e Tecnologias
O projeto utiliza uma arquitetura moderna de dados orientada a analytics, estruturada da seguinte forma:

* **Linguagem Principal:** Python (utilizando bibliotecas como Pandas, NumPy e SQLAlchemy para processamento e ingestão).
* **Data Warehouse:** Repositório centralizado para armazenamento dos dados processados, otimizado para consultas analíticas (OLAP).
* **Visualização e BI:** 
  * **Streamlit:** Construção de aplicações web interativas para análises rápidas via Python.
  * **Power BI:** Conexão direta com o Data Warehouse para dashboards executivos e inteligência de negócios.
* **Controle de Versão:** Git.

## Fontes de Dados
A ingestão de dados abrange três domínios principais:
* **INMET (Estação de Barreiras):** Dados meteorológicos granulares (precipitação acumulada, temperatura, umidade).
* **IBGE:** Dados históricos de área plantada, área colhida e rendimento médio (kg/ha).
* **CEPEA:** Indicador de preços da soja (referência Paranaguá), refletindo o comportamento do mercado financeiro e do agronegócio.

## Detalhamento do Pipeline (ETL) e Data Warehouse

O fluxo de dados foi desenhado para garantir a integridade, rastreabilidade e performance nas consultas.

### 1. Extração (Extract)
Coleta de dados brutos provenientes de APIs públicas, arquivos CSV e planilhas, armazenados inicialmente em uma camada de Data Lake (diretório `data/raw/`), mantendo o histórico inalterado das fontes originais.

### 2. Transformação (Transform)
Scripts em Python realizam o tratamento intensivo dos dados:
* Normalização de formatos de data e moeda.
* Tratamento de anomalias, outliers climáticos e dados faltantes (imputação ou descarte lógico).
* Harmonização da granularidade temporal (ex: agrupamento de dados climáticos diários para médias mensais ou por ciclo de safra).

### 3. Carga e Modelagem Dimensional (Load & DW)
Os dados transformados são carregados no Data Warehouse seguindo a modelagem dimensional Star Schema (Esquema Estrela), projetada para otimizar as consultas do Power BI e Streamlit:

* **Tabelas Fato (Métricas e Eventos):**
  * `Fato_Clima`: Registros diários/mensais da estação meteorológica.
  * `Fato_Mercado`: Histórico de cotações e variações do indicador CEPEA.
  * `Fato_Safra`: Volumes de produção e rendimento agrícola.

* **Tabelas Dimensão (Contexto):**
  * `Dim_Tempo`: Calendário completo com hierarquias (Ano, Semestre, Trimestre, Mês, Semana, Safra).
  * `Dim_Localidade`: Informações geográficas dos municípios do Extremo Oeste Baiano (ex: Barreiras, Luís Eduardo Magalhães).
