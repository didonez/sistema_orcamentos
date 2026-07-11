import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURAÇÃO SEGURA (Injeção direta) ---
# COLE O CONTEÚDO DO SEU JSON AQUI DENTRO DAS ASPAS TRIPLAS
JSON_CONTENT = """
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
"""

try:
    # Converte a string JSON para um dicionário real
    creds_dict = json.loads(JSON_CONTENT)
    
    # Autentica usando o dicionário em memória (ignora corrupção de arquivos do GitHub)
    creds = Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    
    # Conecta à planilha
    spreadsheet = client.open("Modelo_Orcamento_Inteligente")
    db_sheet = spreadsheet.worksheet("Banco de Dados")
    os_sheet = spreadsheet.worksheet("Modelo de Orçamento")
    
except Exception as e:
    st.error(f"Erro na conexão: {e}")
    st.stop()

# --- 2. RESTANTE DO SEU CÓDIGO ---
st.title("📄 Sistema de Orçamentos")
# ... (continue com a lógica do seu app daqui para baixo)
