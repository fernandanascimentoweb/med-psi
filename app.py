import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory


template = """ Você é um Psicólogo brasileiro que conversa de forma descontraida, usando gírias, expressões informais e um jeito amigavel e brincalhão, mas ainda com empatia e profissionalismo. Fale como se estivesse num papo de bar, mas sempre respeitando o paciente. 
Ajuda a entender os comportamentos e as funções mentais do ser humano.Ele aplica métodos científicos para compreender a psiquê humana e atuar no tratamento e prevenção de doenças mentais e melhorar sua qualidade de vida. A prática da empatia é fundamental.

Use gírias leves como "poxa", "cara", "mandar ver", "de boa",
"tipo assim", "bora", "beleza", para deixar a conversa mais
natural e próxima.

Primeiro, pergunte:
- Qual é seu nome?
- O que te trouxe aqui hoje, tipo, qual o rolê que você quer resolver?

Histórico da conversa:
{history}

Entrada do usuário:
{input}"""


prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    MessagesPlaceholder(variable_name="history"), #placeholder para historico estruturado
    ("human", "{input}")
])

# modelo de linguagem que vai utilizar
llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")

chain = prompt | llm

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)


# -------------------- STREAMLIT APP --------------------
st.set_page_config(page_title="Psicólogo Virtual", page_icon="🧠")

# Título simples sem imagem e sem colunas
st.markdown("<h1 style='margin:0; padding:10px 0;'>🧠 Psicólogo Virtual</h1>", unsafe_allow_html=True)

# Inicializa a sessão
if "session_id" not in st.session_state:
    st.session_state.session_id = "user123"  # poderia ser algo dinâmico
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico no frontend
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
if prompt_user := st.chat_input("Digite sua mensagem..."):
    # Mostra a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt_user})
    with st.chat_message("user"):
        st.markdown(prompt_user)

    # Gera resposta
    resposta = chain_with_history.invoke(
        {"input": prompt_user},
        config={"configurable": {"session_id": st.session_state.session_id}}
    )

    # Mostra resposta do psicólogo
    st.session_state.messages.append({"role": "assistant", "content": resposta.content})
    with st.chat_message("assistant"):
        st.markdown(resposta.content)
