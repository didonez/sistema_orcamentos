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
    
    # Trata as quebras de linha da chave privada de forma limpa na memória
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
    st.info("💡 Lembre-se de compartilhar a planilha com o e-mail da Conta de Serviço como Editor.")
    st.stop()
except Exception as e:
    st.error("❌ Erro Crítico ao conectar com o Google Sheets.")
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

# 3. Exibição dos Itens Adicionados
if st.session_state.itens_orcamento:
    df_atual = pd.DataFrame(st.session_state.itens_orcamento)
    st.table(df_atual)
    
    valor_total_geral = df_atual["Total"].sum()
    st.markdown(f"## 💰 Valor Total Geral: **R$ {valor_total_geral:.2f}**")
    
    st.markdown("---")
    if st.button("💾 Finalizar e Enviar para o Google Sheets"):
        st.success("Orçamento salvo com sucesso no Google Sheets!")
        
        texto_zap = f"Olá {cliente}, seu orçamento ficou pronto no valor total de R$ {valor_total_geral:.2f}."
        link_whatsapp = f"https://wa.me/55{whatsapp}?text={texto_zap.replace(' ', '%20')}"
        st.markdown(f"[📲 Enviar via WhatsApp]({link_whatsapp})")
