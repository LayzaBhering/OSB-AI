# Agente de Inteligência Legislativa - OSB-SP

Este projeto consiste em um suporte de inteligência artificial desenvolvido para o Observatório Social do Brasil - São Paulo. O agente automatiza a fiscalização e a análise de dados, utilizando técnicas avançadas de Web Scraping e Modelos de Linguagem de Grande Escala (LLMs) para ser um suporte aos voluntários e à gestão!

# Funcionalidades Atuais

1 - **Autenticação Segura**: Integração nativa com Google OAuth 2.0 para acesso restrito a voluntários e diretores;

2 - **Análise JIT (Just-in-Time Data)**: Extração em tempo real de dados diretamente do portal de transparência da CMSP via BeautifulSoup4;

3 - **Inteligência Legislativa**: Motor de processamento baseado no modelo Gemini 2.5 Flash, configurado para interpretar a Lei 14.133/21 e processos financeiros públicos;

5 - **Interface Conversacional**: Chat interativo com gestão de estado de sessão (st.session_state) para acompanhamento de histórico de mensagens;

6 - **Ações Rápidas**: Botões otimizados para tarefas recorrentes, como resumos de prestação de contas e análise de emendas parlamentares.

# 🛠️ Stack Tecnológica

7 - **Linguagem**: Python 3.10+;

8 - **Interface**: Streamlit;

9 - **IA**: Google Generative AI (Gemini API);

10 - **Scraping**: Requests / BeautifulSoup4;

12 - **Segurança**: Google OAuth 2.0 / Python-dotenv.