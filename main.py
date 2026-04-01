import streamlit as st
from google import genai
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
import time

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

#Função criada para a interação com o site. Uso tanto no botão de sair, quando no else, pra ser default
def chat_input_agenteIA():
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

    #Menu lateral do sidebar, onde há botões de navegação
    st.title("Menu do Agente")
  
    if st.button("📊 Planilhas", use_container_width=True):
        st.session_state.modo_atual = "planilha"
        st.rerun()
    
    if st.button("Chat", use_container_width=True):
        st.session_state.modo_atual = "Chat"
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

def responder_planilha(prompt, contexto_adicional=""):
    try:
        contexto_sistema = f"""
        Você é o agente de Inteligência Legislativa do Observatório Social do Brasil - SP (https://www.osb-saopaulo.org.br/).

        Sua missão é atuar como um analista de aruivos e  autoridade técnica em transparência pública, respectivamente.

        Ao responder, nesse caso, foque em:
        1. FOCO DESSA ETAPA: Detalhar sobre o arquivo que foi realizado upload, a reposta deve ser baseada na pergunta do usuário(a) {st.user.name}.
        3. LINGUAGEM: Linguagem simples e acessível ao cidadão.
        4. RIGOR: Basear-se na legislação vigente (Lei 14.133/21).

        CONTEXTO ATUAL DOS DADOS DA CÂMARA:
        {contexto_adicional}

        Se o usuário perguntar algo fora desse escopo, traga a conversa de volta para a transparência de SP.

        Quando responder, utilize o nome do usuário:
        {st.user.name}

        Sempre que possível inclua links úteis com fontes confiáveis e crie uma tabela resumo da solicitação de {st.user.name}.
        """
        response = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=contexto_sistema + prompt
        )
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"
    
def processar_planilha_por_lotes(df, prompt_usuario):
    tamanho_lote = 500  # Quantidade de linhas por vez para não estourar a cota
    analises_parciais = []
    progresso_bar = st.progress(0)
    status_texto = st.empty()
    # Calcula quantos lotes existem
    linhas_totais = len(df)
    total_lotes = (linhas_totais // tamanho_lote) + (1 if linhas_totais % tamanho_lote > 0 else 0)
    for i, inicio in enumerate(range(0, linhas_totais, tamanho_lote)):
        fim = inicio + tamanho_lote
        df_lote = df.iloc[inicio:fim]
        contexto_lote = df_lote.to_string(index=False)
        status_texto.text(f"Analisando lote {i+1} de {total_lotes}...")

        resposta = responder_planilha(
            f"Analise este lote de dados ({i+1}/{total_lotes}) e extraia pontos críticos: {prompt_usuario}", 
            contexto_adicional=contexto_lote
        )
        analises_parciais.append(f"--- ANÁLISE LOTE {i+1} ---\n{resposta}")
        progresso_bar.progress((i + 1) / total_lotes)
        if i < total_lotes - 1:
            time.sleep(5) 

    status_texto.text("Consolidando relatório final...")

    contexto_final = "\n\n".join(analises_parciais)
    
    # !!!!!!! Limita o contexto final para não estourar o prompt de saída
    relatorio_final = responder_planilha(
        "Gere um relatório de auditoria final consolidado e estruturado unindo as análises de todos os lotes anteriores.", 
        contexto_adicional=contexto_final[:15000] 
    )
    status_texto.empty()
    progresso_bar.empty()
    return relatorio_final


if st.session_state.modo_atual.lower() == "planilha":
    st.title("📊 Dados - Planilhas")
    st.write("Faça o upload dos dados para uma análise técnica do Agente IA.")
    
    arquivo_upload = st.file_uploader("Subir planilha (CSV ou XLSX)", type=["csv", "xlsx"])
    
    if arquivo_upload:
        try:
            if arquivo_upload.name.endswith('.csv'):
                df = pd.read_csv(arquivo_upload)
            else:
                df = pd.read_excel(arquivo_upload)
            
            st.subheader("Visualização dos Dados")
            st.dataframe(df) 
            resumo_dados = df.to_csv(index=False)
            #Serve para contar as linhas da tabela e suas colunas
            col_metrica1, col_metrica2 = st.columns(2)
            with col_metrica1:
                st.metric("Total de Linhas", len(df))
            with col_metrica2:
                st.metric("Total de Colunas", df.shape[1])

            if "messages_planilha" not in st.session_state:
                st.session_state.messages_planilha = []

            for message in st.session_state.messages_planilha:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt_planilha := st.chat_input("Pergunte algo sobre este arquivo!", key="chat_p"):
                st.session_state.messages_planilha.append({"role": "user", "content": prompt_planilha})
                with st.chat_message("user"):
                    st.markdown(prompt_planilha)
                with st.chat_message("assistant"):
                    with st.spinner("Analisando arquivo..."):
                        resposta = responder_planilha(prompt_planilha, contexto_adicional=resumo_dados)
                        st.markdown(resposta)
                        st.session_state.messages_planilha.append({"role": "assistant", "content": resposta})

            st.divider()

            if st.button("Gerar Auditoria", type="primary"):
                analise = processar_planilha_por_lotes(
                    df, 
                    "Realize uma auditoria técnica completa e detalhada sobre estes dados, buscando inconsistências, gastos atípicos e conformidade com a transparência pública."
                )
                st.markdown("### ⚖️ Resultado da Auditoria Final")
                st.info(analise)
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")
else:
    st.title("🤖 Agente IA OSB-SP")
    chat_input_agenteIA()