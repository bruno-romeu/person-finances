import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
import json
from dotenv import load_dotenv

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

load_dotenv()

creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
client = gspread.authorize(creds)

try:
    spreadsheet = client.open_by_key(os.getenv("SHEET_ID"))
    worksheet = spreadsheet.sheet1
    print("Conectado ao Google Sheets com sucesso!")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"ERRO: Planilha '{os.getenv('SHEET_ID')}' não encontrada. Você a compartilhou com o e-mail de serviço?")
    exit()


st.set_page_config(
    page_title="Meu Dashboard de Finanças",
    layout="wide"  
)

@st.cache_data(ttl=60)
def carregar_dados():
    """
    Carrega a planilha Excel. Retorna um DataFrame vazio se o arquivo não existir.
    """
    try:
        dados = worksheet.get_all_records()
        
        if not dados:
            return pd.DataFrame(columns=['DATA', 'TIPO', 'VALOR', 'CATEGORIA'])
            
        df = pd.DataFrame(dados)
        
        df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
        df['VALOR'] = df['VALOR'].fillna(0)
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados do Google Sheets: {e}")
        return pd.DataFrame(columns=['DATA', 'TIPO', 'VALOR', 'CATEGORIA'])


st.title("Meu Dashboard de Finanças Pessoais 📈")

df = carregar_dados()

if df.empty:
    st.warning("Nenhum dado encontrado. Envie sua primeira despesa pelo WhatsApp!")
else:
    st.subheader("Resumo Financeiro")
    
    receitas_df = df[df['TIPO'] == 'receita']
    gastos_df = df[df['TIPO'] == 'gasto']

    total_receitas = receitas_df['VALOR'].sum()
    total_gastos = gastos_df['VALOR'].sum()
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

    gastos_por_categoria = gastos_df.groupby('CATEGORIA')['VALOR'].sum().sort_values(ascending=False)
    
    if not gastos_por_categoria.empty:
        st.bar_chart(gastos_por_categoria)
    else:
        st.info("Nenhum gasto registrado para exibir no gráfico.")
        
    st.subheader("Todos os Lançamentos")
    # st.dataframe(df) usa a tela inteira
    # st.write(df) é mais simples
    st.dataframe(df.sort_values(by='DATA', ascending=False), use_container_width=True)