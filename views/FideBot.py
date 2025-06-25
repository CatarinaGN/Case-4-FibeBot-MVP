import streamlit as st
import requests
from dotenv import load_dotenv
import os
import langwatch
from uuid import uuid4
import datetime
from supabase import create_client
import requests


# --- Configuração inicial ---
load_dotenv()
langwatch.setup(api_key=os.getenv("LANGWATCH_API_KEY"))

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
langflow_key = os.getenv("LANGFLOW_KEY")

#langflow_key = st.secrets["LANGFLOW_KEY"]
#supabase_url = st.secrets["SUPABASE_URL"]
#supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

user_email = st.session_state.user_email

# Garantir que existe current_chat_id
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

st.markdown("<h1 style='text-align: center;'>🤖 FideBot</h1>", unsafe_allow_html=True)

st.warning("""
⚠️ Este chatbot utiliza a **versão gratuita online do Langflow** hospedada no Astra DataStax, que pode apresentar lentidão ou instabilidade.

💡 Para uma performance muito superior, considere rodar a **versão local via Docker**, ou utilizar uma versão paga.

Langflow **não cobra diretamente pelo uso do Playground** via Astra, mas o que acontece é:
- A infraestrutura da **DataStax Astra é gratuita com limites** (por ex: conexões lentas, tempo de resposta maior).
- Langflow Cloud (própria) está em desenvolvimento/early access — o foco é que futuramente eles ofereçam instâncias pagas com:
  - Diminuição de Latência 
  - Modelos personalizados
  - Acesso escalável

👉 Atualmente, se quiser rodar com desempenho real, o **melhor caminho** é:

- **Rodar localmente com Docker**
- **Hospedar o Langflow (ex: render.com, AWS, etc.)**
           
""")


# --- Carregar lista de chats ---
chats_response = supabase.from_("chats").select("*").eq("user_email", user_email).eq("archived", False).order("created_at", desc=True).execute()
chat_list = chats_response.data if chats_response.data else []

chat_titles = [chat["title"] for chat in chat_list]
selected_chat = st.selectbox("Selecionar chat:", options=chat_titles + ["Novo Chat"])

# --- Criar novo chat ---
if selected_chat == "Novo Chat":
    title = st.text_input("Título do novo chat:", value=f"Chat {datetime.datetime.now().strftime('%H:%M')}")
    if st.button("Criar Chat"):
        new_chat_id = str(uuid4())
        supabase.from_("chats").insert({
            "id": new_chat_id,
            "user_email": user_email,
            "created_at": datetime.datetime.now().isoformat(),
            "title": title
        }).execute()
        st.session_state.current_chat_id = new_chat_id
        st.rerun()
else:
    selected_chat_obj = next((c for c in chat_list if c["title"] == selected_chat), None)
    if selected_chat_obj:
        st.session_state.current_chat_id = selected_chat_obj["id"]
        with st.expander("🗂️ Arquivar este chat"):
            if st.button("🗑️ Arquivar Chat"):
                chat_id_to_delete = selected_chat_obj["id"]
            
                # Apagar mensagens associadas
                supabase.from_("messages").delete().eq("chat_id", chat_id_to_delete).execute()
                
                # Apagar o próprio chat
                supabase.from_("chats").delete().eq("id", chat_id_to_delete).execute()
                
                # Resetar o estado
                st.session_state.current_chat_id = None
                st.success("✅ Chat e mensagens apagados com sucesso.")
                st.rerun()

# --- Mostrar mensagens ---
chat_id = st.session_state.current_chat_id

if chat_id:
    msgs = supabase.from_("messages").select("*").eq("chat_id", chat_id).eq("user_email", user_email).order("created_at").execute()

    chat_messages = msgs.data if msgs.data else []

    for msg in chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍", key=f"up_{msg['id']}"):
                        supabase.from_("messages").update({"feedback": "thumbs_up"}).eq("id", msg["id"]).execute()
                        st.rerun()
                with col2:
                    if st.button("👎", key=f"down_{msg['id']}"):
                        supabase.from_("messages").update({"feedback": "thumbs_down"}).eq("id", msg["id"]).execute()
                        st.rerun()

# --- Função para processar entrada ---
from langwatch import trace

#@trace(
#    name="FideBot LLM Call",
#    metadata={"source": "fidebot", "model": "gpt-4o-2024-1120"}
#)


import json
from urllib.parse import urlencode

@trace(
    name="FideBot LLM Call",
    metadata={"source": "fidebot", "model": "langflow-online-astra"}
)
def process_user_input(user_input: str, session_id: str) -> str:
    url = "https://api.langflow.astra.datastax.com/lf/84ff11d6-f983-4f56-8b88-4a6e7baca1f8/api/v1/run/4bfc1d6b-10d1-4434-b59c-c7428d33e41a?stream=false"

    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat",
        "session_id": session_id  # Important: isolate sessions
        }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {langflow_key}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()

        data = response.json()
        print("🌐 Raw response from Langflow:", data)

        # Try multiple paths depending on structure
        try:
            # Most expected structure
            bot_reply = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        except (KeyError, IndexError):
            try:
                # Alternate possible structure
                bot_reply = data["outputs"][0]["results"]["message"]["text"]
            except (KeyError, IndexError):
                # Fallback to raw JSON
                bot_reply = json.dumps(data)

    except requests.exceptions.Timeout:
        bot_reply = "⏳ O servidor demorou muito para responder. Tente novamente em instantes."
    except requests.exceptions.RequestException as e:
        bot_reply = f"❌ Erro ao comunicar com o Langflow: {str(e)}"
    except Exception as e:
        bot_reply = f"❌ Erro inesperado: {str(e)}"

    return bot_reply

# --- Entrada do utilizador ---
if user_input := st.chat_input("Digite sua mensagem..."):
    if chat_id:
        supabase.from_("messages").insert({
            "id": str(uuid4()),
            "chat_id": chat_id,
            "user_email": user_email,
            "role": "user",
            "content": user_input,
            "created_at": datetime.datetime.now().isoformat()
        }).execute()

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("🤖 Processando sua pergunta..."):
            bot_reply = process_user_input(user_input, session_id=chat_id)

        supabase.from_("messages").insert({
            "id": str(uuid4()),
            "chat_id": chat_id,
            "role": "assistant",
            "content": bot_reply,
            "created_at": datetime.datetime.now().isoformat()
        }).execute()

        with st.chat_message("assistant"):
            st.markdown(bot_reply)
    else:
        st.warning("Por favor, cria ou seleciona um chat primeiro.")
