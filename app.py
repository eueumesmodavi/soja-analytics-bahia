import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Análise Estratégica - Soja Bahia")


@st.cache_data
def ld_csv():
    d_a = pd.read_csv('csv/base_analitica_soja_bahia.csv')
    d_m = pd.read_csv('csv/base_sazonal_mensal_soja.csv')
    return d_a, d_m


def plt_g(df, x, y_b, y_l, tit, nome_b, nome_l):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(name=nome_b, x=df[x], y=df[y_b], marker_color='#E97132'), secondary_y=False)
    fig.add_trace(go.Scatter(name=nome_l, x=df[x], y=df[y_l], mode='lines', line=dict(color='#111E6C', width=3)),
                  secondary_y=True)

    fig.update_layout(title_text=tit, plot_bgcolor='rgba(0,0,0,0)',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    fig.update_yaxes(showgrid=False)

    return fig


d_a, d_m = ld_csv()
min_ano = int(d_a['Ano'].min())
max_ano = int(d_a['Ano'].max())

st.title("🌱 Análise Integrada da Cadeia Produtiva da Soja")
st.markdown(
    "Estudo do impacto das variáveis climáticas (INMET) e mercadológicas (CEPEA) no rendimento agrícola do Extremo Oeste Baiano (IBGE).")

t1, t2 = st.tabs([
    "📊 Dashboard & Estatísticas",
    "🔍 Gráficos de Exploração (EDA)"
])

with t1:
    # Alternador do método de entrada para seleção do período
    modo_filtro = st.radio(
        "Opção de Seleção do Período:",
        ["Barra Interativa (Slider)", "Digitar os Anos Manualmente"],
        horizontal=True
    )

    if modo_filtro == "Barra Interativa (Slider)":
        a_mn, a_mx = st.slider("Selecione o Intervalo de Anos", min_ano, max_ano, (min_ano, max_ano))
    else:
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            a_mn = st.number_input("Ano Inicial", min_value=min_ano, max_value=max_ano, value=min_ano, step=1)
        with col_in2:
            a_mx = st.number_input("Ano Final", min_value=min_ano, max_value=max_ano, value=max_ano, step=1)

        if a_mn > a_mx:
            st.error("Atenção: O Ano Inicial não pode ser maior que o Ano Final.")
            a_mn, a_mx = min_ano, max_ano

    d_af = d_a[(d_a['Ano'] >= a_mn) & (d_a['Ano'] <= a_mx)]
    d_mf = d_m[(d_m['Ano'] >= a_mn) & (d_m['Ano'] <= a_mx)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Média Chuva (mm)", f"{d_af['Chuva_mm'].mean():.2f}")
    c2.metric("Média Rendimento (kg/ha)", f"{d_af['Rendimento médio da produção'].mean():.2f}")
    c3.metric("Preço Médio (R$)", f"{d_af['Preco_Real'].mean():.2f}")

    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        f_h = plt_g(d_af, 'Ano', 'Chuva_mm', 'Preco_Real', "Evolução Histórica", "Chuva Acumulada (mm)",
                    "Preço da Saca (R$)")
        st.plotly_chart(f_h, use_container_width=True)
        st.markdown(
            "**Explicação:** O gráfico acima ilustra a trajetória anual do preço da soja confrontado com o volume acumulado de chuvas.")

    with g2:
        d_sm = d_mf.groupby('Mes')[['Preco_Real', 'Chuva_mm']].mean().reset_index()
        f_s = plt_g(d_sm, 'Mes', 'Chuva_mm', 'Preco_Real', "Sazonalidade Mensal", "Chuva Acumulada (mm)",
                    "Preço da Saca (R$)")
        st.plotly_chart(f_s, use_container_width=True)
        st.markdown("**Explicação:** Esta visão mensal consolida o perfil sazonal de precipitação e preços.")

    st.divider()

    st.header("📈 Detalhamento Estatístico do Período Selecionado")
    st.markdown("Estes dados numéricos fornecem suporte científico imediato para as análises visuais exibidas acima.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Resumo Estatístico Descritivo")
        cols_num = d_af.select_dtypes(include='number').columns
        st.dataframe(d_af[cols_num].describe().T)

    with col_t2:
        st.subheader("Matriz de Correlação Linear (Pearson)")
        cols_corr = [c for c in ['Chuva_mm', 'Rendimento médio da produção', 'Preco_Real'] if c in d_af.columns]
        if cols_corr:
            st.dataframe(d_af[cols_corr].corr().round(3))

with t2:
    st.header("Análise Exploratória de Dados (EDA)")
    st.markdown(
        "Visualizações estáticas geradas durante a etapa de limpeza e tratamento estrutural dos dados (Seaborn/Matplotlib).")

    img_col1, img_col2 = st.columns(2)
    with img_col1:
        st.subheader("Distribuição e Outliers")
        st.image("csv/eda_boxplots_outliers.png", use_container_width=True)
        st.markdown(
            "**Interpretação:** Identificação de valores atípicos (outliers) na série histórica de preços e chuvas.")

        st.subheader("Correlação: Chuva vs Rendimento")
        st.image("csv/eda_dispersao_chuva_rendimento.png", use_container_width=True)

    with img_col2:
        st.subheader("Frequência dos Dados")
        st.image("csv/eda_histogramas.png", use_container_width=True)
        st.markdown("**Interpretação:** Curvas de distribuição mostrando a concentração dos registros de precipitação.")

        st.subheader("Sazonalidade Histórica")
        st.image("csv/eda_sazonalidade_mensal.png", use_container_width=True)