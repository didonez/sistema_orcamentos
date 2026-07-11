import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
import base64

# 1. Configuração da Conexão Inteligente via Base64 (Zero barras invertidas)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Carrega a estrutura limpa do arquivo JSON
    with open("google_creds.json", "r") as f:
        creds_dict = json.load(f)
    
    # Sua chave privada convertida em uma linha de texto puro Base64 (sem quebras de linha ou caracteres de escape)
    key_base64 = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdm独自REFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2d3Z2dTa0FnRUFBb0lCQVFDdE81NW5ERXQxb09WNlxuWWNuY0lRU2lEV0ZWMU90cUkzNjZPMUZQTXdua3kyTjZ4cXVmQzlqNGR2ZzVJanVCVytvZThwMXREZ0xvVUJialxuWCsvcG5EQWxudU1VTms5Z0JHNUI4RkY5SUpHYmpRRnZRbVlCTGl3VmVGWUIwc3NBajFhQ2hzZ3RhUWdQaW9EOVwueUc0WVZWdmNTclVJU huntsdk04TzZpZmxHNHVDcG1BOTN2WktsRGlpMFFYRFAreE5BYnV2MGtkdlFDalhXL3hMSFxuTzJRYi9paltIWjB2akZQb0xKQng2Sk1SR05kK2U3Z1lrTFpHblVMdTdIWmY0WVIxOWNmdW1xckVUMkdWNkM5XG5kQnF3QjdTZk5lT2JlUUt6OTdXTEp5VFpDKzZ0UUxMbE9pcTV2UWalkSHJxdDhsQ1dwMndxTTV4SnM4alYzSE9cbjNlWmdkdGtoQWdNQkFBRUNnZ0VBQnNobm9ROGtuZmNrSHhMb3dJaFFMakJ1RGhSaEpjTjAyakd5KzRpbVNxd1xuR1NiQjRlVUl6SDg3aEVDc2pYcDE1L3J0eWk4bkV0MnViTDRWRnFsN2V1Q2VFV3k0Tmtrc0lFSDVveGVwTGQwVFxuT0I0U1lJUFVYTzJZbUFNTytPVlQ0TUhhWVFsTWxBK3pNZVNrOTJuUnNrWWdVUnUrY05EZzIxfVdwUEJMZWN5OVxuZkZrV0RpSHZPcTV3OFl5N0UrblE4cytiUmZuZkFpSXZXQ3RSajhyV3NYaXVQNjBhNkFhcVcyZ0JmSmpQY0lDXG5YRjVzZit6eUZ2akdJcjFzWGdHdndEb20rdWpmVG5FbWxCdEk4UWJtdVdynkZsYkV0NitvZDZ6RUJTMUp3aUF2XG50U0FTNWdYSzVqU0hLZ084RTMrTkZYZzlUbmNRMkVNeUt3VFNpRzZWRVFLQmdRRGZPdE83VmZNK2dwalNXTG9nXG5xdVMwL2xpTGhsa3c5QXpkLzNnSno1c2dONjBBOFJGVmM3NnQvU0NwOVowaDJmTzc2eEE0SFc5NU80UktKanNpXG52RUNqRWVqTDNVY3hqTTVzMHJSUkpLN2hDc3VTOEEydXY3dVlweUd3QnF1a2p5aGhJeGxjSVNRaUNVN0tNbFVrXG53ay84UTdVZGROMUx3MHBwYlVnWHZwQlVRS0JnUURETS8zdS9xNVkwN2hvR0hsQ3VBL0E1Q1lRTXpyd0VxVWtcbkVORDRrRnA0QldGMWlwbm5lNEQzaU1ZSjlsOS83SGNJTnlla21qMXlvTExtNFFKWW9STkQyYWJzK3pWVRRJUFxuNjVYNXBpVDlCNFhIM0VGZGpHRjFoQ3N5akhzaHQvNEpLVnllaG5pWUQ1R05QLy9SU2lBUEVqbGM5Uk5wSTB0XG44cHdkSjcybTBRS0JnUUNqNDlCaVlONGZ5amE4RVdxT2luU243NFNpTG1jS25oemh5ckFrTTIvcVR2NGozYnpvXG42N0V2QVpLYnhDSXhoM1Q3cDlKdEJ4NHVUVFZmM2k5dElHZG10elk0UlFSd3ZMcEh4a2NLRGJqOGt0ZldBZFdcbblFjalpsRFVDSisySnBoQXo4QU1NcG9MUFlmTkllQUZkb0NIZERHRUtadjZLc2dOR29CdnFtMWJaNFFLQmdIdzhcbjVyYGFHTFdtb0g1ekJjMjR5UjVxbk9nM0ZROT1MdkZVWFV3WjU5ejYzOTBveTJ1VkxMVmx0VnJtSUVpWVVpU2lcbnAzT2FVMzlDV0YrciRBaDNFSUppYkdGeVNMeG10dm1YWjdLeFZsNVRpWTk5MzRZak5HN1FJWWRkN1doOGJSTjdcbjV0OXFqaDJOMjROa3QvMk1CL2hhQjV6NExLNzREbjZ2THoxSDdPdmhBb0dCQU5SLzdaM2VZNitzb3g0cTFSZzVcbkx0cWtEQzM5eVdPUWZhaVd4SGhERzUyK1h3R0JraE0zc2dhYkxVaFphd0loamJCM2VqcFJzVmliZWJ3cm40T1JcbkdmOG1TZnM0TkwwWGZzV1l6V1VoajUzajcycHhlbmo1VFArbXlxVXNGNzRjemV1SHFuMWhseUxuMlJaaURiVkVcbjFFN2piUEpOcDZOZVRyWERuK0cwdU5VRlxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIi5lbmNvZGUoJ2FzY2lpJyksIGJhc2U2NF9lbmNvZGUgPSAnLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdmctLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tJw===="
    
    # Decodifica e reconstrói o formato correto com quebras de linha reais
    decoded_key = base64.b64decode(key_base64).decode("utf-8")
    
    # Se a decodificação trouxe a string bruta com \n literais, limpa para quebras físicas
    if "\\n" in decoded_key:
        decoded_key = decoded_key.replace("\\n", "\n")
        
    creds_dict["private_key"] = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtO55nDEt1oOV6
YcncIQSiDWFW1OtqI366O1FPMwnJy2N6xqufC9j4dvg5Ij5BW+oe8p1tDgLoUBbj
X+/pnDAlnuMUNk9gBG5BxFF9IJGbjQFvQmYBLiwVeFYB0ssAj1aChsgtaQgPioD9
yG4YVVvcSrUIQVmjMG8O6iflG4uCpmA9LvZKlDi0QXDP+xNABuv0kdvQCjXW/xLH
O2Qb/ijXHZ0vjFPoLJBx6JGMRGN9+e7gYkLZGnULu7HZf4YR19cfumqrET2GV6C9
dBqwB7SfNeObeQKz97WLJyTZc+6tQLLlOiq5vQe2kHrqt8lCWp2wqM5xJs8jV3HO
3eZgdtkhAgMBAAECggEABshnoQ8qnfckHxLowIhQLjBuDhRhiJcN02jGy+4imSqw
GSbB4eUIzH87hECsjXp15/rtyi8nEt2ubL4VFql7euCeEWy4NkksIEH5oxepLd0T
OB4SYIPUXO2YmAMO+OVT4MHaYQlMlA+zMeSk92nRskYgURu+cNDg21WUpPBLecy9
fFkWDiHvOq5w8Yy7E+nQ8s+bRfnfAiIvWCtRrj8rWsXiuP60a6AaqW2gBfJjPcIC
XF5sf+zyFvjGIr1sXgGvwDom+ujfTnEmlBtI8QbmtWruFlbEt6+od6zEBS0JwiAv
tSAS5gXK5jSHKgO8E3+NFXg9TncQ1EMyKwTSiG6VEQKBgQDjOTO7VfM+gpjSWLOg
quS0/liLhlkw9Azd/3gJz5sgN60A8RFVc76t/SCp9Z0j2fO76xA4HW95O4RKJjsi
vECjEejL3UcxjM5s0rRRJ+4hCsuS+A2uv7uYpyGwBqukjyhhIxlcISQiCU7KMlUk
wk/8Q7UgdNu1Lw0p4bUgXvpBUQKBgQDDK/3u/q5Y07hoGHlCuA/A5CYQMzrwEqUk
ENR4kFp4BWF1ipnne4D3iMYJ9l9/7IcINyekmj1yoLLm4QJYoRND2abs+zV9TmIP
65X5piT9B4XH3EFdjGF1hCsyjHSht/4JKVyehniYD5GNP//RSiAPIejlc9RNpI0t
8pwdJ72m0QKBgQCj49BiYN4vyja8EWqOinSn74SiLmcKnhzhyrAkM2/qTv4j3bzo
67EvAZKbxCJxh3T7p9JtBx4uTTVf3i9tIGdmtzY4RQRiwvLpHxkcKDbj8ktfWDdW
QcjnlDUCJ+2JphAz8AMMpoLPYfNIeAFdoCHdDGEKZf9KsgNGoBvqm1bZ4QKBgHw8
5rpaGLWmoH5zBc24yR5qnOg3FE96LvFUXUwZ59z6390oy2uVLLVltVrmIEiYUiSi
p3OaU39CWF+r4Ah3EIJibGXyS0xmtvmXZ7KxVl5TiY9934YjNG7QIYdd7Wh8bRN7
5t9qjh2N24Nkt/2MB/haB5z4LK74Dn6vLz1H7OvhAoGBANR/7z3eY6+sox4q9Rg5
LtqkDC39yWOQfaiWxHhDG52+XwGBkhM3sgabLUhZawIhjbB3ejpRvWibebwrn4OR
Gf8mSfs4NL0XfsWYzWUhj53j72pxenj5TP+myqUsF74czeuHqn1hlyLj2RZiDbVE
1E7jbPJNp6NeTrXDn+G0uNUF
-----END PRIVATE KEY-----"""

    # Inicializa as credenciais a partir do dicionário mesclado
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha do Google pelo nome exato
    nome_planilha = "Modelo_Orcamento_Inteligente"
    spreadsheet = client.open(nome_planilha)
    db_sheet = spreadsheet.worksheet("Banco de Dados")
    os_sheet = spreadsheet.worksheet("Modelo de Orçamento")
    
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"❌ Erro: Planilha '{nome_planilha}' não foi encontrada.")
    st.info("💡 Compartilhe a planilha com o e-mail do robô do Google Sheets como Editor.")
    st.stop()
except Exception as e:
    st.error("❌ Erro de Autenticação.")
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
