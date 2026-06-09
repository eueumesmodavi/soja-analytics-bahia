import pandas as pd
import requests


url_sidra = "https://apisidra.ibge.gov.br/values/t/5457/n8/2901,2902,2903,2904,2905,2906,2907/v/allxp/p/last%2025/c782/0,40124"

print("Iniciando a extração corrigida do IBGE SIDRA...")

response = requests.get(url_sidra)

if response.status_code == 200:
    dados_json = response.json()

    # 1. Cria o DataFrame com a estrutura bruta do JSON
    df_bruto = pd.DataFrame(dados_json)

    # 2. Transforma a primeira linha no cabeçalho real das colunas
    df_bruto.columns = df_bruto.iloc[0]

    # 3. Remove a primeira linha para ficar apenas com os dados
    df_soja_ibge = df_bruto[1:].copy()

    # 4. Converte a coluna 'Valor' para numérico (trata os nulos "-" automaticamente)
    df_soja_ibge['Valor'] = pd.to_numeric(df_soja_ibge['Valor'], errors='coerce')

    print("Extração e correção concluídas com sucesso!\n")

    # Mostra as colunas principais
    colunas_foco = ['Mesorregião Geográfica', 'Ano', 'Variável', 'Valor']
    print(df_soja_ibge[colunas_foco].head(10))

else:
    print(f"Erro ao acessar a API: {response.status_code}")

print("Iniciando a transformação dos dados (Pivot)...")

# 1. Fazemos o pivot table para transformar as linhas da coluna 'Variável' em colunas reais
# Usamos 'mean' (média) ou 'max' para consolidar as linhas repetidas do mesmo ano/região
df_soja_pivot = df_soja_ibge.pivot_table(
    index=['Mesorregião Geográfica', 'Ano'],
    columns='Variável',
    values='Valor',
    aggfunc='max'
).reset_index()

# 2. Removemos o nome do índice das colunas para deixar o DataFrame limpo
df_soja_pivot.columns.name = None

print("Transformação concluída! Abaixo está a nova estrutura da sua Base IBGE:")
print(df_soja_pivot.head())

# 3. Opcional: Salvar este primeiro resultado em CSV
df_soja_pivot.to_csv("ibge_soja_transformado.csv", index=False, encoding="utf-8-sig")
print("\nArquivo 'ibge_soja_transformado.csv' salvo com sucesso!")

# Filtra para ver os dados apenas do Extremo Oeste Baiano
df_oeste = df_soja_pivot[df_soja_pivot['Mesorregião Geográfica'].str.contains('Extremo Oeste')]
print(df_oeste.head())

#Fonte 2
caminho_arquivo = "csv/soja_indicador.csv"

try:
    print("Iniciando a leitura do arquivo CSV plano...")

    # Leitua do CSV
    df_cepea_bruto = pd.read_csv(caminho_arquivo, skiprows=3, sep=None, engine='python', encoding='utf-8')
    print("Arquivo MENSAL do CEPEA carregado com sucesso via CSV!")

    # Renomeia as colunas baseadas na estrutura real ('Data', 'À vista R$', 'À vista US$')
    df_cepea_bruto.columns = ['Periodo', 'Preco_Real', 'Preco_Dolar'] + list(df_cepea_bruto.columns[3:])

    # Tratamento dos Preços (Remove pontos de milhar e troca a vírgula por ponto decimal)
    df_cepea_bruto['Preco_Real'] = df_cepea_bruto['Preco_Real'].astype(str)\
                                    .str.replace('.', '', regex=False)\
                                    .str.replace(',', '.', regex=False)

    # Converte o preço para float numérico real
    df_cepea_bruto['Preco_Real'] = pd.to_numeric(df_cepea_bruto['Preco_Real'], errors='coerce')

    # Extração do Ano
    df_cepea_bruto['Ano'] = df_cepea_bruto['Periodo'].astype(str).str.extract(r'(\d{4})')

    # Remove eventuais linhas vazias no fim do arquivo e converte o Ano para int
    df_cepea_bruto = df_cepea_bruto.dropna(subset=['Ano'])
    df_cepea_bruto['Ano'] = df_cepea_bruto['Ano'].astype(int)

    # Clustering: Calcula a média anual dos preços para bater com o formato do IBGE
    df_cepea_anual = df_cepea_bruto.groupby('Ano')['Preco_Real'].mean().reset_index()
    df_cepea_anual['Preco_Real'] = df_cepea_anual['Preco_Real'].round(2)

    # Filtra o intervalo correto do projeto
    df_cepea_anual = df_cepea_anual[(df_cepea_anual['Ano'] >= 2000) & (df_cepea_anual['Ano'] <= 2024)]

    # Transforma o 'Ano' em string para o merge final do pipeline
    df_cepea_anual['Ano'] = df_cepea_anual['Ano'].astype(str)

    print("\nTransformação concluída! Base de preços do CEPEA pronta:")
    print(df_cepea_anual.head(10))

    # Salva o resultado em CSV
    df_cepea_anual.to_csv("csv/cepea_soja_anual.csv", index=False, encoding="utf-8-sig")
    print("\nArquivo 'cepea_soja_anual.csv' gerado com sucesso!")

except Exception as e:
    print(f"Erro ao processar o arquivo CSV: {e}")

#Fonte 3
caminho_arquivo = "csv/clima_barreiras.csv"

try:
    print("Iniciando o tratamento calibrado da Fonte 3 (INMET)...")

    # skiprows=10 pula perfeitamente as 10 linhas de metadados do INMET
    df_inmet_bruto = pd.read_csv(caminho_arquivo, skiprows=10, sep=';', encoding='utf-8')
    print("Arquivo mensal do INMET carregado com sucesso!")

    # Renomeia as colunas baseado na estrutura real do seu arquivo
    df_inmet_bruto.columns = ['Periodo', 'Chuva_mm'] + list(df_inmet_bruto.columns[2:])

    # Extração do Ano: Como a data do arquivo vem no padrão "YYYY-MM-DD", isolamos os 4 primeiros dígitos
    df_inmet_bruto['Ano'] = df_inmet_bruto['Periodo'].astype(str).str.extract(r'(\d{4})')

    # Remove linhas vazias e garante que a chuva seja tratada como número flutuante
    df_inmet_bruto = df_inmet_bruto.dropna(subset=['Ano'])
    df_inmet_bruto['Chuva_mm'] = pd.to_numeric(df_inmet_bruto['Chuva_mm'], errors='coerce')

    # Transformação (Agrupamento): Soma a chuva dos 12 meses de cada ano em Barreiras-BA
    df_inmet_anual = df_inmet_bruto.groupby('Ano')['Chuva_mm'].sum().reset_index()
    df_inmet_anual['Chuva_mm'] = df_inmet_anual['Chuva_mm'].round(1)

    # Filtra o recorte temporal de 2000 a 2024 para alinhar com o IBGE
    df_inmet_anual['Ano'] = df_inmet_anual['Ano'].astype(int)
    df_inmet_anual = df_inmet_anual[(df_inmet_anual['Ano'] >= 2000) & (df_inmet_anual['Ano'] <= 2024)]

    # Converte o Ano para string/objeto para o cruzamento final (Merge)
    df_inmet_anual['Ano'] = df_inmet_anual['Ano'].astype(str)

    print("\nTransformação concluída com sucesso! Chuva acumulada anual:")
    print(df_inmet_anual.head(10))

    # Salva o arquivo final isolado da terceira fonte
    df_inmet_anual.to_csv("csv\inmet_clima_anual.csv", index=False, encoding="utf-8-sig")
    print("\nArquivo 'inmet_clima_anual.csv' gerado e pronto na barra lateral!")

except Exception as e:
    print(f"Erro ao processar o arquivo do INMET: {e}")
    print("Dica: Verifique se o nome do arquivo upado bate exatamente com a variável 'caminho_arquivo'.")

# Nós lemos os outputs das células anteriores para fazer o Join final:
arq_ibge  = "csv/ibge_soja_transformado.csv"
arq_cepea = "csv/cepea_soja_anual.csv"
arq_inmet = "csv/inmet_clima_anual.csv"

try:
    print("Iniciando a unificação final do Pipeline de Big Data...")

    # 1. Carrega as três bases limpas
    df_ibge = pd.read_csv(arq_ibge)
    df_cepea = pd.read_csv(arq_cepea)
    df_inmet = pd.read_csv(arq_inmet)

    # 2. Padroniza a coluna 'Ano' como string em todas as tabelas para evitar erros de tipo no Join
    df_ibge['Ano'] = df_ibge['Ano'].astype(str)
    df_cepea['Ano'] = df_cepea['Ano'].astype(str)
    df_inmet['Ano'] = df_inmet['Ano'].astype(str)

    # 3. Filtra o IBGE para focar no Extremo Oeste Baiano
    # Como o nosso dado climático é de Barreiras, o cruzamento perfeito e cientificamente correto ocorre nessa região produtora
    df_ibge_oeste = df_ibge[df_ibge['Mesorregião Geográfica'].str.contains('Extremo Oeste')].copy()

    # 4. Faz os Merges (Joins) sequenciais usando o 'Ano' como chave de ligação
    # Primeiro: Produção (IBGE) + Preço (CEPEA)
    df_merge_1 = pd.merge(df_ibge_oeste, df_cepea, on='Ano', how='inner')

    # Segundo: Resultado anterior + Clima (INMET)
    df_final = pd.merge(df_merge_1, df_inmet, on='Ano', how='inner')

    print("\n Pipeline Integrada com Sucesso!")
    print("Abaixo está uma prévia do Data Warehouse regional integrado:")

    # Seleciona as colunas estratégicas para exibição limpa no print
    colunas_exibicao = ['Mesorregião Geográfica', 'Ano', 'Rendimento médio da produção', 'Preco_Real', 'Chuva_mm']
    print(df_final[colunas_exibicao].head(10))

    # 5. CARGA FINAL: Salva o arquivo mestre definitivo
    df_final.to_csv("csv/base_analitica_soja_bahia.csv", index=False, encoding="utf-8-sig")
    print("\nArquivo mestre 'base_analitica_soja_bahia.csv' gerado com sucesso!")

except Exception as e:
    print(f"Erro ao unificar as bases de dados: {e}")

#Extração de dados das 2 fontes para obter análise mensal
try:
    print("Criando a base mensal de sazonalidade (CEPEA + INMET)...")

    # 1. Carrega os arquivos brutos que você enviou para o Colab
    df_cepea_bruto = pd.read_csv("csv/soja_indicador.csv", skiprows=3, sep=None, engine='python', encoding='utf-8')
    df_inmet_bruto = pd.read_csv("csv/clima_barreiras.csv", skiprows=10, sep=';', encoding='utf-8')

    # 2. Trata o CEPEA Mensal (Ex: "03/2006" -> Extrai Mês e Ano)
    df_cepea_bruto.columns = ['Periodo', 'Preco_Real', 'Preco_Dolar'] + list(df_cepea_bruto.columns[3:])
    df_cepea_bruto['Preco_Real'] = df_cepea_bruto['Preco_Real'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df_cepea_bruto['Preco_Real'] = pd.to_numeric(df_cepea_bruto['Preco_Real'], errors='coerce')

    # Extrai Mês e Ano do formato "MM/YYYY" do CEPEA
    df_cepea_bruto['Mes'] = df_cepea_bruto['Periodo'].astype(str).str.extract(r'^(\d{2})')
    df_cepea_bruto['Ano'] = df_cepea_bruto['Periodo'].astype(str).str.extract(r'(\d{4})$')

    # 3. Trata o INMET Mensal (Ex: "2006-03-31" -> Extrai Mês e Ano)
    df_inmet_bruto.columns = ['Periodo_Inmet', 'Chuva_mm'] + list(df_inmet_bruto.columns[2:])
    df_inmet_bruto['Chuva_mm'] = pd.to_numeric(df_inmet_bruto['Chuva_mm'], errors='coerce')

    # Extrai Ano e Mês do formato "YYYY-MM-DD" do INMET
    df_inmet_bruto['Ano'] = df_inmet_bruto['Periodo_Inmet'].astype(str).str.extract(r'^(\d{4})')
    df_inmet_bruto['Mes'] = df_inmet_bruto['Periodo_Inmet'].astype(str).str.extract(r'-(\d{2})-')

    # 4. Cria uma chave única de junção mensal (Ex: "2006-03") em ambas as tabelas
    df_cepea_bruto['Chave_Mensal'] = df_cepea_bruto['Ano'] + "-" + df_cepea_bruto['Mes']
    df_inmet_bruto['Chave_Mensal'] = df_inmet_bruto['Ano'] + "-" + df_inmet_bruto['Mes']

    # 5. Faz o Merge Mensal das duas fontes
    df_mensal_final = pd.merge(
        df_cepea_bruto[['Chave_Mensal', 'Ano', 'Mes', 'Preco_Real']],
        df_inmet_bruto[['Chave_Mensal', 'Chuva_mm']],
        on='Chave_Mensal',
        how='inner'
    )

    # Filtra o período do projeto e organiza
    df_mensal_final['Ano'] = df_mensal_final['Ano'].astype(int)
    df_mensal_final = df_mensal_final[(df_mensal_final['Ano'] >= 2006) & (df_mensal_final['Ano'] <= 2024)]
    df_mensal_final = df_mensal_final.sort_values('Chave_Mensal').dropna()

    print("\n Base Mensal Gerada com Sucesso!")
    print(df_mensal_final[['Ano', 'Mes', 'Preco_Real', 'Chuva_mm']].head(12))

    # Salva o segundo arquivo para o Power BI
    df_mensal_final.to_csv("csv/base_sazonal_mensal_soja.csv", index=False, encoding="utf-8-sig")
    print("\nArquivo 'base_sazonal_mensal_soja.csv' salvo")

except Exception as e:
    print(f"Erro ao gerar base mensal: {e}")