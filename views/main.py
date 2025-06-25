import streamlit as st

# Set page title
st.title("Home Page")

# Add spacing before the logo
#st.markdown("<br><br>", unsafe_allow_html=True)

# Center the main logo
#st.image("assets/logo.png", use_container_width=True)

# More spacing between logo and section
#st.markdown("<br><br>", unsafe_allow_html=True)

# Section title
st.markdown("### Bem-vindo ao **FideBot**!")

st.markdown("""
O **FideBot** é um assistente virtual inteligente criado para apoiar os vendedores da **Fidelidade** na sua atividade diária.
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/fidebot.png", width=350)  # adjust width as needed

# Bot description
st.markdown("""
Com ele, vais poder:

- **Colocar perguntas genéricas** sobre os produtos da Fidelidade — por exemplo:  
> “Qual foi o produto mais rentável no último ano?”  
O FideBot responde de forma clara, objetiva e acessível, mesmo em temas financeiros complexos.

- **Descrever casos de clientes** — por exemplo:  
> “Tenho um cliente de 45 anos, com perfil moderado, que quer investir para a reforma.”  
O FideBot analisa a situação e recomenda os produtos mais adequados, explicando de forma simples e direta.
            
⚠️ Se fizeres uma descrição de cliente, lembra-te que o FideBot só consegue recomendar produtos quando tiver:
- A idade do cliente  
- O perfil de risco (baixo, moderado ou elevado)  
- O objetivo (ex: reforma, filhos, crescer capital)  
- O horizonte temporal (anos até à reforma ou até o cliente precisar do dinheiro)

Se faltar algum destes dados, o FideBot vai pedir esses dados antes de dar uma recomendação.

---

### O que consegues fazer aqui?

- **Conversar com o FideBot** para obter respostas rápidas e bem explicadas.
- **Registar sugestões ou anotações** sobre cada cliente que atendes.

Esta ferramenta combina modelos de inteligência artificial com o conhecimento da Fidelidade — sempre com foco em facilitar o teu trabalho e melhorar o aconselhamento ao cliente.

> Usa-a como um aliado no balcão — simples, claro e sempre do teu lado.
""", unsafe_allow_html=True)


