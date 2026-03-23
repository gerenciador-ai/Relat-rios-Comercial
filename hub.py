import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import requests
from io import StringIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="Hub Holding Acelerar - Portal Estratégico", 
    page_icon="🏢", 
    initial_sidebar_state="collapsed"
)

# --- 2. INICIALIZAÇÃO DOS ESTADOS DE SESSÃO (MOVIDO PARA O TOPO) ---
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = False
if 'email_usuario' not in st.session_state: st.session_state.email_usuario = None
if 'modulo' not in st.session_state: st.session_state.modulo = 'hub'

# --- 3. CORES E ESTILOS ---
COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"

# --- 4. LÓGICA DE CSS CONDICIONAL (AGORA SEGURO) ---
if st.session_state.modulo == 'hub':
    st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{
            display: none !important;
        }}
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        .stApp {{
            background-color: {COLOR_BG};
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. CONFIGURAÇÕES DE ACESSO (LITERAL DO COMERCIAL.PY) ---
USUARIOS_SHEET_ID = '15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk'
SENHA_MESTRA = 'Acelerar@2026'

# --- 6. FUNÇÃO DE CARREGAMENTO DE USUÁRIOS ---
@st.cache_data(ttl=600)
def carregar_usuarios_autorizados():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{{USUARIOS_SHEET_ID}}/export?format=csv"
        response = requests.get(url )
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df.iloc[:, 0].astype(str).str.strip().str.lower().tolist()
        return []
    except:
        return []

# --- 7. TELA DE LOGIN ---
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background-color: #0B2A4E; padding: 40px; border-radius: 15px; border: 1px solid #89CFF0; text-align: center;'>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/gerenciador-ai/Relat-rios-Comercial/main/logo_acelerar_sidebar.png", width=250 )
        st.markdown(f"<h2 style='color: {COLOR_TEXT}; margin-top: 20px;'>Portal da Holding</h2>", unsafe_allow_html=True)
        
        email = st.text_input("E-mail corporativo", placeholder="seuemail@acelerar.tech")
        senha = st.text_input("Senha mestra", type="password", placeholder="Digite a senha")
        
        st.markdown("  
", unsafe_allow_html=True)
        if st.button("Acessar Portal", use_container_width=True):
            usuarios_permitidos = carregar_usuarios_autorizados()
            email_input = email.strip().lower()
            
            if (email_input in usuarios_permitidos or email_input == 'acelerar@acelerar.tech') and senha == SENHA_MESTRA:
                st.session_state.usuario_logado = True
                st.session_state.email_usuario = email_input
                st.rerun()
            else:
                st.error("❌ Acesso negado.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 8. PORTAL DE SELEÇÃO DE MÓDULOS ---
def portal_hub():
    nome_exibicao = st.session_state.email_usuario.split('@')[0].upper() if st.session_state.email_usuario else "USUÁRIO"
    st.markdown(f"<h1 style='color: {COLOR_TEXT}; text-align: center;'>🚀 Bem-vindo, {nome_exibicao}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color: {COLOR_SECONDARY}; text-align: center;'>Escolha o módulo da Holding Acelerar para iniciar:</h4>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📊 Módulo Comercial")
        if st.button("Acessar Comercial", use_container_width=True, type="primary"):
            st.session_state.modulo = 'comercial'
            st.rerun()
            
    with col2:
        st.success("### 💰 Módulo Financeiro")
        if st.button("Acessar Financeiro", use_container_width=True, type="primary"):
            st.session_state.modulo = 'financeiro'
            st.rerun()
    
    st.divider()
    if st.button("🚪 Sair do Portal"):
        st.session_state.usuario_logado = False
        st.rerun()

# --- 9. NAVEGAÇÃO PRINCIPAL ---
if not st.session_state.usuario_logado:
    tela_login()
else:
    if st.session_state.modulo == 'hub':
        portal_hub()
    elif st.session_state.modulo == 'comercial':
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                exec(f.read())
        except Exception as e:
            st.error(f"Erro ao carregar o módulo Comercial: {e}")
            if st.button("Voltar ao Hub"):
                st.session_state.modulo = 'hub'
                st.rerun()
    elif st.session_state.modulo == 'financeiro':
        st.info("### 💰 Módulo Financeiro em Desenvolvimento")
        if st.button("Voltar ao Hub"):
            st.session_state.modulo = 'hub'
            st.rerun()
