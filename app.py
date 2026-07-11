import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- 1. CONEXÃO DIRETA (O MODO MAIS ESTÁVEL) ---
try:
    # Este comando lê o arquivo service-account.json automaticamente da pasta raiz
    client = gspread.service_account(filename="service-account.json")
    
    # Abre a planilha
    spreadsheet = client.open("Modelo_Orcamento_Inteligente")
    db_sheet = spreadsheet.worksheet("Banco de Dados")
    os_sheet = spreadsheet.worksheet("Modelo de Orçamento")
    
except Exception as e:
    st.error(f"Erro na conexão: {e}")
    st.info("💡 Dica: Verifique se o e-mail que está dentro do 'service-account.json' tem permissão de Editor na sua planilha.")
    st.stop()

# --- 2. INTERFACE E LÓGICA ---
st.title("📄 Sistema de Orçamentos")

# Carrega dados
df_db = pd.DataFrame(db_sheet.get_all_records())
lista_itens = df_db["Nome do Item / Serviço"].tolist() if not df_db.empty else []

cliente = st.text_input("Nome do Cliente:")
whatsapp = st.text_input("WhatsApp do Cliente:")

if "itens" not in st.session_state: st.session_state.itens = []

item_sel = st.selectbox("Selecione o item:", ["-- Novo Item --"] + lista_itens)

if item_sel == "-- Novo Item --":
    nome_item = st.text_input("Nome do item:")
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
    df_orc = pd.DataFrame(st.session_state.itens)
    st.table(df_orc)
    if st.button("💾 Finalizar"):
        for i in st.session_state.itens:
            os_sheet.append_row([datetime.now().strftime("%d/%m/%Y"), cliente, whatsapp, i["Desc"], i["Qtd"], i["Preco"], i["Total"]])
        st.success("Salvo!")
        st.session_state.itens = []
        st.rerun()
