import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import os


ARQUIVO_PLANILHA = 'data/gastos.xlsx'
COLUNAS = ['Data', 'Tipo', 'Valor', 'Categoria']

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
    data_atual = datetime.now()
    
    nova_linha_df = pd.DataFrame(
        [[data_atual, tipo, valor, categoria]],  
        columns=COLUNAS                         
    )

    if not os.path.exists(ARQUIVO_PLANILHA):
        print("Arquivo não existe. Criando novo...")
        nova_linha_df.to_excel(ARQUIVO_PLANILHA, index=False, engine='openpyxl')
    else:
        print("Arquivo existe. Carregando e concatenando...")
        try:
            df_antigo = pd.read_excel(ARQUIVO_PLANILHA, engine='openpyxl')
            
            df_novo = pd.concat([df_antigo, nova_linha_df], ignore_index=True)
            
            df_novo.to_excel(ARQUIVO_PLANILHA, index=False, engine='openpyxl')
        except Exception as e:
            print(f"Erro ao ler ou salvar o Excel: {e}")
            # Em um caso real, poderíamos salvar em um ".backup"
            return
            
    print("Salvo com sucesso!")


@app.post("/webhook")
async def receber_webhook(request: Request):

    try:
        dados = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")
    

    try:
        texto_mensagem = dados['data']['message']['conversation']
        print(f"Mensagem recebida: {texto_mensagem}")

    except KeyError:
        print(f"Estrutura do JSON inesperada. JSON recebido: {dados}")
        raise HTTPException(status_code=422, detail="JSON com formato inesperado.")

    dados_parseados = parse_mensagem(texto_mensagem)
    
    if dados_parseados is None:
        print("Mensagem ignorada (não é um comando de finanças).")
        return {"status": "mensagem ignorada"}

    tipo, valor, categoria = dados_parseados
    salvar_na_planilha(tipo, valor, categoria)

    return {"status": "processado com sucesso"}

# --- Ponto de entrada para rodar o servidor ---
if __name__ == "__main__":
    print("Iniciando servidor FastAPI local em http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)