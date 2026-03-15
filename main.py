import streamlit as st
from google import genai
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

st.set_page_config(
    page_title="OSB-SP AI",
    page_icon="⚖️",
    layout="wide"
)

if "modo_atual" not in st.session_state:
    st.session_state.modo_atual = "chat"

if not st.user.is_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown(
            """
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 15px; border: 1px solid #006437; text-align: center;">
                <h1 style="color: #006437; margin-bottom: 10px;">🤖 Agente IA OSB-SP</h1>
                <p style="color: #4b5563; font-size: 1.1em;">Assistente de Inteligência Legislativa</p>
                <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;">
                <p style="color: #6b7280; margin-bottom: 25px;">Identifique-se com sua conta Google para utilizar o agente de IA.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            if st.button("Entrar com Google", use_container_width=True, type="primary"):
                st.login("google")
        st.info("🔒 Acesso restrito aos voluntários do Observatório Social.")
    st.stop()

api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def extrair_dados_camara(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.decompose()
        texto_limpo = soup.get_text(separator=' ')
        return " ".join(texto_limpo.split())[:6000]
    except Exception as e:
        return f"Erro ao acessar dados: {e}"

def responder_usuario(prompt, contexto_adicional=""):
    try:
        contexto_sistema = f"""
        Você é o agente de Inteligência Legislativa do Observatório Social do Brasil - SP (https://www.osb-saopaulo.org.br/).

        Sua missão é atuar como uma autoridade técnica em transparência pública.

        Ao responder, foque em:

        1. LEGISLATIVO: Explicar proposições, leis e processos da Câmara de SP.
        2. FINANCEIRO: Detalhar despesas de mandato, emendas e contratações.
        3. LINGUAGEM: Linguagem simples e acessível ao cidadão.
        4. RIGOR: Basear-se na legislação vigente (Lei 14.133/21).

        CONTEXTO ATUAL DOS DADOS DA CÂMARA:
        {contexto_adicional}

        Se o usuário perguntar algo fora desse escopo, traga a conversa de volta para a transparência de SP.

        Quando responder, utilize o nome do usuário:
        {st.user.name}

        Sempre que possível inclua links úteis com fontes confiáveis.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=contexto_sistema + prompt
        )
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

with st.sidebar:
    st.markdown(f"<h2 style='color: #006437;'>👤 Olá, {st.user.name}!</h2>", unsafe_allow_html=True)
    
    if st.button("Sair", use_container_width=True):
        st.logout()
        st.rerun()

    st.divider()
    st.title("Menu do Agente")
  
    if st.button("📊 Planilhas", use_container_width=True):
        st.session_state.modo_atual = "planilha"
        st.rerun()

    st.divider()
    st.title("Ações Rápidas")
    if st.button("Analisar Portal Transparência"):
        with st.spinner("Lendo portal..."):
            url = "https://www.saopaulo.sp.leg.br/transparencia/"
            dados = extrair_dados_camara(url)
            resposta = responder_usuario("Explique as etapas do portal de Transparência.", contexto_adicional=dados)
            if "messages" not in st.session_state: st.session_state.messages = []
            st.session_state.messages.append({"role": "assistant", "content": resposta})

if st.session_state.modo_atual == "planilha":
    st.title("📊 Dados - Planilhas")
    st.write("Faça o upload dos dados para uma análise técnica do Agente IA.")
    
    arquivo_upload = st.file_uploader("Subir planilha (CSV ou XLSX)", type=["csv", "xlsx"])
    
    if arquivo_upload:
        try:
            if arquivo_upload.name.endswith('.csv'):
                df = pd.read_csv(arquivo_upload)
            else:
                df = pd.read_excel(arquivo_upload)
            
            st.subheader("Visualização dos Dados (até 10.000)")
            st.dataframe(df.head(10000))
            
            if st.button("Analisar", type="primary"):
                resumo = df.head(30).to_string(index=False)
                with st.spinner("O Agente está auditando as linhas..."):
                    analise = responder_usuario(f"Resumo: {resumo}")
                    st.markdown("### ⚖️ Resultado da Auditoria")
                    st.info(analise)
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

else:
    st.title("🤖 Agente IA OSB-SP")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Como posso te ajudar hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando requisição..."):
                resposta = responder_usuario(prompt)
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})