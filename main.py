import uvicorn
import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import os
import httpx
import requests
import json

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]



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


app = FastAPI()

def parse_mensagem(texto: str):
    """
    Recebe uma string como "gasto 400 comida" e a divide.
    Retorna (Tipo, Valor, Categoria)
    """
    try:
        partes = texto.lower().split()
        
        if len(partes) < 3:
            print("Erro de parsing: mensagem muito curta.")
            return None
        
        tipo = partes[0]
        valor_str = partes[1].replace(',', '.') 
        categoria = " ".join(partes[2:])

        if tipo not in ['gasto', 'receita']:
            print(f"Erro de parsing: tipo '{tipo}' inválido.")
            return None
            
        valor = float(valor_str)
        
        print(f"Parsing OK: {tipo}, {valor}, {categoria}")
        return tipo, valor, categoria

    except Exception as e:
        print(f"Erro fatal no parsing: {e}")
        return None
    
def salvar_na_planilha(tipo: str, valor: float, categoria: str):
    """
    Carrega a planilha, adiciona a nova linha e salva.
    """
    print(f"Iniciando salvamento: {tipo}, {valor}, {categoria}")
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        nova_linha = [data_atual, tipo, valor, categoria]
        worksheet.append_row(nova_linha)
        
        print("Salvo no Google Sheets com sucesso!")
    
    except Exception as e:
        print(f"Erro ao salvar no Google Sheets: {e}")


@app.post("/webhook")
async def receber_webhook(request: Request):

    try:
        dados = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")
    

    try:
        remote_jid = dados['data']['key']['remoteJid']
        key = dados['data']['key']
        texto_mensagem = dados['data']['message']['conversation']

    except (KeyError, TypeError):
        print("Evento ignorado (não é uma mensagem de conversa padrão).")
        return {"status": "evento ignorado (estrutura de JSON não esperada)"}
    
    if remote_jid != os.getenv("group"):
        print(f"Mensagem ignorada (veio de {remote_jid}, não do grupo alvo).")
        return {"status": "mensagem ignorada (não é do grupo alvo)"}
    
    print(f'mensagem recebida: {texto_mensagem}')

    dados_parseados = parse_mensagem(texto_mensagem)
    
    if dados_parseados is None:
        print("Mensagem ignorada (não é um comando de finanças).")
        return {"status": "mensagem ignorada"}

    tipo, valor, categoria = dados_parseados
    try:
        salvar_na_planilha(tipo, valor, categoria)

        await enviar_reacao(key, "👍")

    except Exception as e:
        print(f"Erro ao salvar: {e}")
        await enviar_reacao(key, "❌")

    return {"status": "processado"}

async def enviar_reacao(key: dict, reaction: str):
    """
    Envia uma reação para uma mensagem específica usando a Evolution API.
    """
    print(f"Enviando reação '{reaction}' para {key}")

    url_endpoint = f"{os.getenv("EVOLUTION_API_URL")}/message/sendReaction/manu"

    payload = {
    "key": {
        "remoteJid": key['remoteJid'],
        "fromMe": True,
        "id": key['id']
    },
    "reaction": reaction
}

    headers = {
        "apikey": os.getenv("EVOLUTION_API_KEY"),
        "Content-Type": "application/json"
    }

    

    print(f"Payload enviado: {payload}")
    print("KEY RECEBIDA:", key)

    response = requests.post(url_endpoint, json=payload, headers=headers, timeout=30.0)

    print(response.json())


    ''' try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url_endpoint, json=payload, headers=headers, timeout=30.0)
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Resposta da API: {response.text}")

        if response.status_code in [200, 201]:
            print("Reação enviada com sucesso.")
        else:
            print(f"Erro ao enviar reação: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Exceção ao enviar reação: {e}")

'''
# --- Ponto de entrada para rodar o servidor ---
if __name__ == "__main__":
    print("Iniciando servidor FastAPI local em http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)