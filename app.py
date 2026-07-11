import streamlit as st

# Verifica se o campo existe e mostra na tela de forma limpa
try:
    chave_bruta = st.secrets["gcp_service_account"]["private_key"]
    
    # Remove as barras e limpa o texto na tela para você copiar
    chave_limpa = chave_bruta.replace("\\n", "\n").replace("\\\\n", "\n")
    
    st.write("### 📋 COPIE TODO O CONTEÚDO DO QUADRO ABAIXO:")
    st.text_area(label="Sua Chave PEM Limpa", value=chave_limpa, height=400)

except Exception as e:
    st.error("Certifique-se de que o painel de Secrets possui o campo 'private_key'.")
