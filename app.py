import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 1. Configuração de Autenticação Segura via Streamlit Secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Coleta o dicionário das credenciais salvas no painel do Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Substitui a string textual do TOML por quebras de linha reais que o leitor de PEM exige
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # Inicializa a conexão com o ecossistema Google
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha do Google pelo nome exato
    nome_planilha = "Modelo_Orcamento_Inteligente"
    spreadsheet = client.open(nome_planilha)
    db_sheet = spreadsheet.worksheet("Banco de Dados")
    os_sheet = spreadsheet.worksheet("Modelo de Orçamento")
    
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"❌ Erro: Planilha '{nome_planilha}' não foi encontrada.")
    st.stop()
except Exception as e:
    st.error("❌ Erro Crítico ao conectar com o Google Sheets.")
    st.code(str(e))
    st.stop()

# --- Resto da Interface do Aplicativo (Tabelas e Inputs) ---
# ... mantém o restante do código igual ...
