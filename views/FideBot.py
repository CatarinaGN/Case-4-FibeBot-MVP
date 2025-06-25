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
import sseclient
#@trace(
#    name="FideBot LLM Call",
#    metadata={"source": "fidebot", "model": "gpt-4o-2024-1120"}
#)


import json
from urllib.parse import urlencode

@trace(
    name="FideBot LLM Call",
    metadata={"source": "fidebot", "model": "langflow-docker-local"}
)
def process_user_input(user_input: str) -> str:
    url = "http://localhost:7860/api/v1/run/c98ac3ec-d8e7-40c1-a8c4-775661f756a5"  # Docker Langflow endpoint!!! chamge this (the online version was much slower)

    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        start_time = datetime.datetime.now()
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        output = response.json()
        end_time = datetime.datetime.now()

        bot_reply = output["outputs"][0]["outputs"][0]["results"]["message"]["text"]

        # --- Token & Cost Estimation (GPT-4o 2024) ---
        prompt_tokens = len(user_input.split())
        completion_tokens = len(bot_reply.split())
        total_tokens = prompt_tokens + completion_tokens

        # Pricing (per 1M tokens) for GPT-4o (Batch API):
        input_price_per_token = 1.09852 / 1_000_000
        output_price_per_token = 4.3941 / 1_000_000

        estimated_cost = (prompt_tokens * input_price_per_token) + (completion_tokens * output_price_per_token)

        print(f"📊 Prompt Tokens: {prompt_tokens}")
        print(f"📊 Completion Tokens: {completion_tokens}")
        print(f"💰 Estimated Cost: €{estimated_cost:.6f}")

    except Exception as e:
        bot_reply = f"❌ Erro: {e}"

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

        bot_reply = process_user_input(user_input)

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
