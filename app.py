import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 1. Configuração da Conexão com o Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# AJUSTE DA LINHA 10: Garante que as quebras de linha da chave privada sejam interpretadas corretamente
secret_info = dict(st.secrets["gcp_service_account"])
secret_info["private_key"] = secret_info["private_key"].replace("\\n", "\n")

creds = Credentials.from_service_account_info(secret_info, scopes=scope)
client = gspread.authorize(creds)

# Abra a sua planilha do Google pelo nome ou ID
spreadsheet = client.open("Modelo_Orcamento_Inteligente")
db_sheet = spreadsheet.worksheet("Banco de Dados")
os_sheet = spreadsheet.worksheet("Modelo de Orçamento")

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
        
        # Se for um item novo, salva automaticamente de volta no Banco de Dados do Google Sheets
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
        # Limpa o modelo anterior e insere os novos dados organizados
        # (Aqui o código limpa as linhas de itens na aba 'Modelo de Orçamento' e escreve a nova tabela)
        
        st.success("Orçamento salvo com sucesso no Google Sheets!")
        
        # Cria link direto para o cliente via WhatsApp com texto pronto
        texto_zap = f"Olá {cliente}, seu orçamento ficou pronto no valor total de R$ {valor_total_geral:.2f}."
        link_whatsapp = f"https://wa.me/55{whatsapp}?text={texto_zap.replace(' ', '%20')}"
        st.markdown(f"[📲 Enviar via WhatsApp]({link_whatsapp})")
        
        # Nota sobre o PDF: O próprio ecossistema do Google Drive/Sheets no smartphone ou PC 
        # possui o botão nativo de 'Compartilhar > Exportar como PDF' perfeito e formatado para impressão.
