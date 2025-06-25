import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime

# --- Carrega .env ---
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# --- Simula login se não existir ---
if "user_email" not in st.session_state:
    st.session_state.user_email = "teste@exemplo.com"  # Substitui por login real

user_email = st.session_state.user_email

# --- Título ---
st.title("📨 Sugestões")

# --- Selecionar assunto ---
subject = st.selectbox(
    "Seleciona o assunto:",
    ["", "Erros Fidebot", "Ideias", "Outros"]
)

# --- Escrever sugestão ---
suggestion = st.text_area("Escreve a tua sugestão:")

# --- Botão Submeter ---
if st.button("Submeter"):
    if not subject:
        st.error("Por favor seleciona o assunto.")
    elif not suggestion.strip():
        st.error("Por favor escreve a tua sugestão.")
    else:
        # Criar e guardar no Supabase
        sug_data = {
            "id": str(uuid4()),
            "user_email": user_email,
            "assunto": subject,
            "sugestao": suggestion.strip(),
            "data": datetime.now().isoformat()
        }

        supabase.from_("suggestions").insert(sug_data).execute()

        st.success("✅ Obrigado pela tua sugestão!")
        st.markdown("---")
        st.write("### Resumo:")
        st.write(f"- **Email:** {user_email}")
        st.write(f"- **Assunto:** {subject}")
        st.write(f"- **Sugestão:** {suggestion}")

