import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE AUTENTICAÇÃO RESILIENTE (GOOGLE SHEETS) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Coleta o dicionário das credenciais salvas no painel de Secrets do Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Intercepta e limpa qualquer variação de barras invertidas na chave privada
    raw_key = creds_dict["private_key"]
    raw_key = raw_key.replace("\\\\n", "\n").replace("\\n", "\n")
    creds_dict["private_key"] = raw_key.strip()
    
    # Inicializa a conexão nativa com o ecossistema Google
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha do Google pelos nomes exatos das abas
    nome_planilha = "Modelo_Orcamento_Inteligente"
    spreadsheet = client.open(nome_planilha)
    db_sheet = spreadsheet.worksheet("Banco de Dados")
    os_sheet = spreadsheet.worksheet("Modelo de Orçamento")
    
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"❌ Erro: A planilha '{nome_planilha}' não foi encontrada no Google Drive.")
    st.info("💡 **Como resolver:** Certifique-se de que compartilhou a planilha com o e-mail da Conta de Serviço como Editor.")
    st.stop()
except Exception as e:
    st.error("❌ Erro Crítico de Autenticação.")
    st.code(str(e))
    st.stop()


# --- 2. INTERFACE DO APLICATIVO STREAMLIT ---
st.title("📄 Sistema de Orçamentos & OS")
st.subheader("Integração Inteligente PC & Smartphone")

# Carregar dados existentes do Banco de Dados do Sheets para o Auto-completar
df_db = pd.DataFrame(db_sheet.get_all_records())
if not df_db.empty and "Nome do Item / Serviço" in df_db.columns:
    lista_itens_existentes = df_db["Nome do Item / Serviço"].tolist()
else:
    lista_itens_existentes = []

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

# Campo de seleção/auto-completar dinâmico
item_selecionado = st.selectbox(
    "Selecione ou digite um Equipamento/Serviço (Auto-completar):",
    options=["-- Novo Item --"] + lista_itens_existentes
)

if item_selecionado == "-- Novo Item --":
    nome_item = st.text_input("Digite o nome do novo equipamento ou serviço:")
    preco_sugerido = st.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=10.0)
else:
    nome_item = item_selecionado
    # Busca o preço cadastrado na planilha automaticamente
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
        
        # Se for um item novo, envia automaticamente para a aba Banco de Dados
        if item_selecionado == "-- Novo Item --" and nome_item not in lista_itens_existentes:
            db_sheet.append_row([nome_item, preco_sugerido])
            st.success(f"'{nome_item}' foi aprendido e salvo no seu Banco de Dados para as próximas vezes!")
        st.rerun()


# --- 3. EXIBIÇÃO DOS ITENS E SOMA TOTAL ---
if st.session_state.itens_orcamento:
    df_atual = pd.DataFrame(st.session_state.itens_orcamento)
    st.table(df_atual)
    
    valor_total_geral = df_atual["Total"].sum()
    st.markdown(f"## 💰 Valor Total Geral: **R$ {valor_total_geral:.2f}**")
    
    # --- 4. FINALIZAÇÃO E EXPORTAÇÃO CONTRA O SHEETS & WHATSAPP ---
    st.markdown("---")
    if st.button("💾 Finalizar e Enviar para o Google Sheets"):
        # Salva as informações principais do orçamento na planilha
        for item in st.session_state.itens_orcamento:
            os_sheet.append_row([
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                cliente,
                whatsapp,
                item["Descrição"],
                item["Qtd"],
                item["Valor Unit."],
                item["Total"],
                valor_total_geral
            ])
            
        st.success("Orçamento salvo com sucesso no Google Sheets!")
        
        # Gera o link direto de envio do texto estruturado para o WhatsApp
        texto_zap = f"Olá {cliente}, seu orçamento ficou pronto no valor total de R$ {valor_total_geral:.2f}."
        link_whatsapp = f"https://wa.me/55{whatsapp}?text={texto_zap.replace(' ', '%20')}"
        st.markdown(f"[📲 Enviar via WhatsApp]({link_whatsapp})")
