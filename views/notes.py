import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from uuid import uuid4

# Then your other imports or logic...
import streamlit.components.v1 as components

# --- Carregar variáveis de ambiente ---
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# --- Simulação de login do utilizador ---
# No teu projeto real, st.session_state.user_email já deve vir de autenticação
if "user_email" not in st.session_state:
    st.session_state.user_email = "teste@exemplo.com"  # Substituir com login real

user_email = st.session_state.user_email

# --- Tabs ---
tab1, tab2 = st.tabs(['🗒️ Caderno', '📌 Notas Guardadas'])


with tab1:
    st.header("📝 Caderno de Notas")


    title = st.text_input("Título da nota")
    category = st.selectbox("Assunto / Categoria", ["Cliente", "Produto", "Ideia", "Outro"])
    note_input = st.text_area("Escreve a tua nota:")

    if st.button("Guardar nota"):
        if title.strip() and note_input.strip():
            nota = {
                "id": str(uuid4()),
                "user_email": user_email,
                "titulo": title.strip(),
                "categoria": category,
                "conteudo": note_input.strip(),
                "data": datetime.now().isoformat()
            }
            supabase.from_("notes").insert(nota).execute()
            st.success("✅ Nota guardada com sucesso!")
            st.rerun()
        else:
            st.warning("⚠️ Título e conteúdo são obrigatórios para guardar.")

with tab2:
    st.header("📌 Notas Guardadas")

    # --- Obter notas do utilizador ---
    response = supabase.from_("notes").select("*").eq("user_email", user_email).order("data", desc=True).execute()
    notas_data = response.data if response.data else []

    if notas_data:
        df_notes = pd.DataFrame(notas_data)

        with st.expander("🔍 Filtrar notas"):
            categoria_filtro = st.multiselect("Filtrar por categoria", df_notes['categoria'].unique())
            data_min = st.date_input("A partir de:", value=None, key="data_min")
            data_max = st.date_input("Até:", value=None, key="data_max")

        df_filtrado = df_notes.copy()
        if categoria_filtro:
            df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categoria_filtro)]
        if data_min:
            df_filtrado = df_filtrado[df_filtrado['data'] >= str(data_min)]
        if data_max:
            df_filtrado = df_filtrado[df_filtrado['data'] <= str(data_max)]

        cols = st.columns(1)
        for idx, (_, row) in enumerate(df_filtrado.iterrows()):
            with cols[0].container(border=True):
                st.markdown(f"""
                <style>
                .note-box {{
                    padding: 10px;
                    border-radius: 8px;
                    background-color: #f0f2f6;
                }}
                </style>
                <div class="note-box">
                    <h3 style="color: #2e86de;">🗂️ {row['titulo']}</h3>
                    <p><b>📅 Data:</b> {row['data']}</p>
                    <p><b>🏷️ Categoria:</b> {row['categoria']}</p>
                    <p>{row['conteudo']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"Apagar nota {idx + 1}", key=f"del_{row['id']}"):
                    supabase.from_("notes").delete().eq("id", row["id"]).execute()
                    st.success("🗑️ Nota apagada.")
                    st.rerun()

        st.download_button(
            label="⬇️ Fazer download das notas (CSV)",
            data=df_filtrado.to_csv(index=False).encode('utf-8'),
            file_name="notas_fidebot.csv",
            mime="text/csv"
        )
    else:
        st.info("Ainda não guardaste nenhuma nota.")


components.html("""
    <script src="https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js"></script>
    <langflow-chat
        window_title="Fidebot"
        flow_id="c98ac3ec-d8e7-40c1-a8c4-775661f756a5"
        host_url="http://localhost:7860">
    </langflow-chat>
""", height=800)
