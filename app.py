import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 1. Configuração da Autenticação via Secrets
# O Streamlit lê o TOML que você configurou no painel de Secrets
creds = Credentials.from_service_account_info(
    st.secrets,
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)

# 2. Acesso à planilha pelo ID (Use o ID: 1zFziJ1eXlaTAS8cFavalmCBWwEkdaPHD)
spreadsheet = client.open_by_key("1zFziJ1eXlaTAS8cFavalmCBWwEkdaPHD")
db_sheet = spreadsheet.worksheet("Banco de Dados")
os_sheet = spreadsheet.worksheet("Modelo de Orçamento")

# 3. Interface do App
st.title("📄 Sistema de Orçamentos")

# Carregar dados
df_db = pd.DataFrame(db_sheet.get_all_records())
lista_itens = df_db["Nome do Item / Serviço"].tolist()

cliente = st.text_input("Nome do Cliente:")
whatsapp = st.text_input("WhatsApp do Cliente:")

if "itens" not in st.session_state: st.session_state.itens = []

item_sel = st.selectbox("Selecione o item:", ["-- Novo Item --"] + lista_itens)

if item_sel == "-- Novo Item --":
    nome_item = st.text_input("Nome do novo item:")
    preco = st.number_input("Preço:", value=0.0)
else:
    nome_item = item_sel
    preco = float(df_db[df_db["Nome do Item / Serviço"] == item_sel]["Preço Padrão (R$)"].values[0])

qtd = st.number_input("Qtd:", value=1)

if st.button("➕ Adicionar"):
    st.session_state.itens.append({"Desc": nome_item, "Qtd": qtd, "Preco": preco, "Total": qtd*preco})
    if item_sel == "-- Novo Item --": 
        db_sheet.append_row([nome_item, preco])
    st.rerun()

if st.session_state.itens:
    st.table(pd.DataFrame(st.session_state.itens))
    if st.button("💾 Finalizar"):
        for i in st.session_state.itens:
            os_sheet.append_row([datetime.now().strftime("%d/%m/%Y"), cliente, whatsapp, i["Desc"], i["Qtd"], i["Preco"], i["Total"]])
        st.success("Orçamento salvo com sucesso!")
        st.session_state.itens = []
        st.rerun()
