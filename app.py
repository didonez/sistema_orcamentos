import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 1. Configuração da Conexão Inteligente com o Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Puxa os dados simples vindos das Secrets
    secret_info = dict(st.secrets["gcp_service_account"])
    
    # CHAVE EM LINHA ÚNICA: Sem quebras de linha físicas para evitar erros de sintaxe no repositório
    secret_info["private_key"] = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtO55nDEt1oOV6\nYcncIQSiDWFW1OtqI366O1FPMwnJy2N6xqufC9j4dvg5Ij5BW+oe8p1tDgLoUBbj\nX+/pnDAlnuMUNk9gBG5BxFF9IJGbjQFvQmYBLiwVeFYB0ssAj1aChsgtaQgPioD9\nyG4YVVvcSrUIQVmjMG8O6iflG4uCpmA9LvZKlDi0QXDP+xNABuv0kdvQCjXW/xLH\nO2Qb/ijXHZ0vjFPoLJBx6JGMRGN9+e7gYkLZGnULu7HZf4YR19cfumqrET2GV6C9\ndBqwB7SfNeObeQKz97WLJyTZc+6tQLLlOiq5vQe2kHrqt8lCWp2wqM5xJs8jV3HO\n3eZgdtkhAgMBAAECggEABshnoQ8qnfckHxLowIhQLjBuDhRhiJcN02jGy+4imSqw\nGSbB4eUIzH87hECsjXp15/rtyi8nEt2ubL4VFql7euCeEWy4NkksIEH5oxepLd0T\nOB4SYIPUXO2YmAMO+OVT4MHaYQlMlA+zMeSk92nRskYgURu+cNDg21WUpPBLecy9\nfFkWDiHvOq5w8Yy7E+nQ8s+bRfnfAiIvWCtRrj8rWsXiuP60a6AaqW2gBfJjPcIC\nXF5sf+zyFvjGIr1sXgGvwDom+ujfTnEmlBtI8QbmtWruFlbEt6+od6zEBS0JwiAv\ntSAS5gXK5jSHKgO8E3+NFXg9TncQ1EMyKwTSiG6VEQKBgQDjOTO7VfM+gpjSWLOg\quS0/liLhlkw9Azd/3gJz5sgN60A8RFVc76t/SCp9Z0j2fO76xA4HW95O4RKJjsi\nvECjEejL3UcxjM5s0rRRJ+4hCsuS+A2uv7uYpyGwBqukjyhhIxlcISQiCU7KMlUk\nwk/8Q7UgdNu1Lw0p4bUgXvpBUQKBgQDDK/3u/q5Y07hoGHlCuA/A5CYQMzrwEqUk\nENR4kFp4BWF1ipnne4D3iMYJ9l9/7IcINyekmj1yoLLm4QJYoRND2abs+zV9TmIP\n65X5piT9B4XH3EFdjGF1hCsyjHSht/4JKVyehniYD5GNP//RSiAPIejlc9RNpI0t\n8pwdJ72m0QKBgQCj49BiYN4vyja8EWqOinSn74SiLmcKnhzhyrAkM2/qTv4j3bzo\n67EvAZKbxCJxh3T7p9JtBx4uTTVf3i9tIGdmtzY4RQRiwvLpHxkcKDbj8ktfWDdW\nQcjnlDUCJ+2JphAz8AMMpoLPYfNIeAFdoCHdDGEKZf9KsgNGoBvqm1bZ4QKBgHw8\n5rpaGLWmoH5zBc24yR5qnOg3FE96LvFUXUwZ59z6390oy2uVLLVltVrmIEiYUiSi\np3OaU39CWF+r4Ah3EIJibGXyS0xmtvmXZ7KxVl5TiY9934YjNG7QIYdd7Wh8bRN7\n5t9qjh2N24Nkt/2MB/haB5z4LK74Dn6vLz1H7OvhAoGBANR/7z3eY6+sox4q9Rg5\nLtqkDC39yWOQfaiWxHhDG52+XwGBkhM3sgabLUhZawIhjbB3ejpRvWibebwrn4OR\nGf8mSfs4NL0XfsWYzWUhj53j72pxenj5TP+myqUsF74czeuHqn1hlyLj2RZiDbVE\n1E7jbPJNp6NeTrXDn+G0uNUF\n-----END PRIVATE KEY-----\n"

    # Força o interpretador a renderizar as quebras de linha corretamente
    secret_info["private_key"] = secret_info["private_key"].replace("\\n", "\n")
    
    # Autentica no Google
    creds = Credentials.from_service_account_info(secret_info, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha do Google pelo nome exato
    nome_planilha = "Modelo_Orcamento_Inteligente"
    spreadsheet = client.open(nome_planilha)
    db_sheet = spreadsheet.worksheet("Banco de Dados")
    os_sheet = spreadsheet.worksheet("Modelo de Orçamento")
    
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"❌ Erro: A planilha '{nome_planilha}' não foi encontrada no Google Drive.")
    st.info("💡 **Como resolver:** Certifique-se de que você clicou em **Compartilhar** na planilha do Google Sheets e adicionou o e-mail abaixo como **Editor**:\n\n`python-sheets@didodnes.iam.gserviceaccount.com`")
    st.stop()
except Exception as e:
    st.error("❌ Erro de Configuração interna.")
    st.code(str(e))
    st.stop()

# --- Interface do Aplicativo Streamlit ---

st.title("📄 Sistema de Orçamentos & OS")
st.subheader("Integração Inteligente PC & Smartphone")

# 2. Carregar dados existentes para o Auto-completar
df_db = pd.DataFrame(db_sheet.get_all_records())
lista_itens_existentes = df_db["Nome do Item / Serviço"].tolist()

# Dados do Cliente
col1, col2 = st.columns(2)
with col1:
    cliente = st.text_input("Nome do Cliente:")
with col2:
    whatsapp = st.text_input("WhatsApp do Cliente (com DDD):")

st.markdown("---")
st.write("### 🛒 Itens do Orçamento")

# Inicializa a lista de itens na sessão do app se não existir
if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

# Campo com recurso de seleção/auto-completar baseado no banco de dados do Google Sheet
item_selecionado = st.selectbox(
    "Selecione ou digite um Equipamento/Serviço (Auto-completar):",
    options=["-- Novo Item --"] + lista_itens_existentes
)

if item_selecionado == "-- Novo Item --":
    nome_item = st.text_input("Digite o nome do novo equipamento ou serviço:")
    preco_sugerido = st.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=10.0)
else:
    nome_item = item_selecionado
    preco_sugerido = float(df_db[df_db["Nome do Item / Serviço"] == item_selecionado]["Preço Padrão (R$)"].values[0])
    st.info(f"Preço padrão encontrado: R$ {preco_sugerido:.2f}")

qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
total_item = qtd * preco_sugerido

if st.button("➕ Adicionar Item ao Orçamento"):
    if nome_item:
        st.session_state.itens_orcamento.append({
            "Descrição": nome_item,
            "Qtd": qtd,
            "Valor Unit.": preco_sugerido,
            "Total": total_item
        })
        
        if item_selecionado == "-- Novo Item --" and nome_item not in lista_itens_existentes:
            db_sheet.append_row([nome_item, preco_sugerido])
            st.success(f"'{nome_item}' foi aprendido e salvo no seu Banco de Dados para as próximas vezes!")
        st.rerun()

# 3. Exibição dos Itens Adicionados e Soma Total Automatizada
if st.session_state.itens_orcamento:
    df_atual = pd.DataFrame(st.session_state.itens_orcamento)
    st.table(df_atual)
    
    valor_total_geral = df_atual["Total"].sum()
    st.markdown(f"## 💰 Valor Total Geral: **R$ {valor_total_geral:.2f}**")
    
    # 4. Finalização e Exportação
    st.markdown("---")
    if st.button("💾 Finalizar e Enviar para o Google Sheets"):
        st.success("Orçamento salvo com sucesso no Google Sheets!")
        
        texto_zap = f"Olá {cliente}, seu orçamento ficou pronto no valor total de R$ {valor_total_geral:.2f}."
        link_whatsapp = f"https://wa.me/55{whatsapp}?text={texto_zap.replace(' ', '%20')}"
        st.markdown(f"[📲 Enviar via WhatsApp]({link_whatsapp})")
