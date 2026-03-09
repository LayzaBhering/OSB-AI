import streamlit as st
from google import genai
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="OSB-SP AI Assistant", page_icon="⚖️", layout="wide")

if not st.user.get("is_logged_in", False): #st.user.is_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("") 
        st.write("") 
        st.markdown(
            """
            <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border: 1px solid #d1d5db; text-align: center;">
                <h1 style="color: #1f2937; margin-bottom: 10px;">🤖 Agente IA OSB-SP</h1>
                <p style="color: #4b5563; font-size: 1.1em;">Assistente de Inteligência Legislativa</p>
                <hr style="margin: 20px 0; border: 0; border-top: 1px solid #ccc;">
                <p style="color: #6b7280; margin-bottom: 25px;">Para acessar o agente de OSB IA, identifique-se com sua conta Google.</p>
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

else:
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
            Você é o agente de de Inteligência Legislativa do Observatório Social do Brasil - SP (https://www.osb-saopaulo.org.br/).
            Sua missão é atuar como uma autoridade técnica em transparência pública.
            Ao responder, foque em:
            1. LEGISLATIVO: Explicar proposições, leis e processos da Câmara de SP.
            2. FINANCEIRO: Detalhar despesas de mandato, emendas e contratações.
            3. LINGUAGEM: Linguagem simples e acessível ao cidadão.
            4. RIGOR: Basear-se na legislação vigente (Lei 14.133/21).
            CONTEXTO ATUAL DOS DADOS DA CÂMARA: {contexto_adicional}
            Se o usuário perguntar algo fora desse escopo, traga a conversa de volta para a transparência de SP.

            Quando o/a usuário(a) te fizer uma solicitação, responda falando o nome do mesmo. Você encontrará essa informação em: {st.user.name}

            Outro ponto, retorne as solicitações com links úteis: como artigos ou textos / vídeos que falem diretante da requisição do(a) usuário(a)!
            """
            response = client.models.generate_content(
                model="gemini-2.0-flash", #gemini-2.5-flash
                contents=contexto_sistema + prompt
            )
            return response.text
        except Exception as e:
            return f"Erro na IA: {e}"
        
    st.title("🤖 Agente IA OSB-SP")

    with st.sidebar:
        st.write(f"👤 **Olá, {st.user.name}!**")
        if st.button("Sair"):
            st.logout()
            st.rerun()
        
        st.divider()
        st.title("Ações Rápidas")
        if st.button("Transparência"):
            with st.spinner("Analisando portal da transparência..."):
                url = "https://www.saopaulo.sp.leg.br/transparencia/"
                dados = extrair_dados_camara(url)
                pergunta = "Explique como funcionam as etapas do portal de Transparência em SP hoje."
                resposta = responder_usuario(pergunta, contexto_adicional=dados)              
                if "messages" not in st.session_state: st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": "Ação Rápida: Resumo de Prestação de Contas"})
                st.session_state.messages.append({"role": "assistant", "content": resposta})
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Como posso ajudar hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                resposta = responder_usuario(prompt)
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})