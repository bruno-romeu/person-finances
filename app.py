import streamlit as st
import pandas as pd
import os


st.set_page_config(
    page_title="Meu Dashboard de Finanças",
    layout="wide"  
)
ARQUIVO_PLANILHA = 'data/gastos.xlsx'

# --- Função para Carregar os Dados ---
# O decorator @st.cache_data "guarda" o resultado da função
@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Carrega a planilha Excel. Retorna um DataFrame vazio se o arquivo não existir.
    """
    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame(columns=['Data', 'Tipo', 'Valor', 'Categoria'])
    
    try:
        df = pd.read_excel(caminho_arquivo, engine='openpyxl')
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame(columns=['Data', 'Tipo', 'Valor', 'Categoria'])


st.title("Meu Dashboard de Finanças Pessoais 📈")

df = carregar_dados(ARQUIVO_PLANILHA)

if df.empty:
    st.warning("Nenhum dado encontrado. Envie sua primeira despesa pelo WhatsApp!")
else:
    st.subheader("Resumo Financeiro")
    
    receitas_df = df[df['Tipo'] == 'receita']
    gastos_df = df[df['Tipo'] == 'gasto']

    total_receitas = receitas_df['Valor'].sum()
    total_gastos = gastos_df['Valor'].sum()
    saldo = total_receitas - total_gastos

    col1, col2, col3 = st.columns(3)
    col1.metric(label="✅ Receitas Totais", value=f"R$ {total_receitas:,.2f}")
    col2.metric(label="❌ Gastos Totais", value=f"R$ {total_gastos:,.2f}")
    
    if saldo >= 0:
        col3.metric(label="💰 Saldo Atual", value=f"R$ {saldo:,.2f}")
    else:
        col3.metric(label="💰 Saldo Atual", value=f"R$ {saldo:,.2f}", delta="Cuidado!", delta_color='inverse')

    st.markdown("---")

    st.subheader("Análise de Gastos")

    gastos_por_categoria = gastos_df.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
    
    if not gastos_por_categoria.empty:
        st.bar_chart(gastos_por_categoria)
    else:
        st.info("Nenhum gasto registrado para exibir no gráfico.")
        
    st.subheader("Todos os Lançamentos")
    # st.dataframe(df) usa a tela inteira
    # st.write(df) é mais simples
    st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)