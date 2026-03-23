import streamlit as st
import pandas as pd
import requests
from io import StringIO

# 1. CONFIGURAÇÃO DA PÁGINA (ESTRITAMENTE NECESSÁRIA)
st.set_page_config(
    layout="wide", 
    page_title="Holding Acelerar - Portal de Gestão", 
    page_icon="🏢", 
    initial_sidebar_state="collapsed"
)

# 2. DEFINIÇÃO DE CONSTANTES E SEGURANÇA
SHEET_ID = "15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk"
MASTER_KEY = "Acelerar@2026"
LOGO_URL = "https://raw.githubusercontent.com/gerenciador-ai/Relat-rios-Comercial/main/logo_acelerar_sidebar.png"

# 3. GERENCIAMENTO DE ESTADO (SESSION STATE )
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "view" not in st.session_state:
    st.session_state.view = "portal"

# 4. MOTOR DE AUTENTICAÇÃO
@st.cache_data(ttl=600)
def fetch_authorized_users():
    try:
        endpoint = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/export?format=csv"
        res = requests.get(endpoint, timeout=10 )
        if res.status_code == 200:
            data = pd.read_csv(StringIO(res.text))
            return data.iloc[:, 0].astype(str).str.strip().str.lower().tolist()
        return []
    except Exception:
        return []

# 5. INJEÇÃO DE INTERFACE (CSS BLINDADO)
# Uso de strings curtas para evitar erros de interpretador em servidores Linux/Cloud
style = "<style>"
style += "div[data-testid='stAppViewContainer'] { background-color: #0A1E2E; }"
style += "section[data-testid='stSidebar'] { display: none !important; }"
style += "[data-testid='collapsedControl'] { display: none !important; }"
style += "header { visibility: hidden !important; }" # Esconde menu do Streamlit
style += "footer { visibility: hidden !important; }" # Esconde rodapé do Streamlit
style += ".login-card { background-color: #0B2A4E; padding: 50px; border-radius: 20px; "
style += "border: 1px solid #89CFF0; box-shadow: 0 15px 35px rgba(0,0,0,0.6); "
style += "max-width: 480px; margin: 8% auto; text-align: center; }"
style += "</style>"
st.markdown(style, unsafe_allow_html=True)

# 6. COMPONENTES DE INTERFACE
def render_login():
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.image(LOGO_URL, width=280)
        st.markdown("<h2 style='color: white; margin-bottom: 30px;'>Acesso Restrito</h2>", unsafe_allow_html=True)
        
        input_user = st.text_input("Usuário (E-mail)", placeholder="exemplo@acelerar.tech")
        input_pass = st.text_input("Senha Mestra", type="password")
        
        st.markdown("  
", unsafe_allow_html=True)
        if st.button("Entrar no Portal", use_container_width=True, type="primary"):
            valid_users = fetch_authorized_users()
            clean_user = input_user.strip().lower()
            
            if (clean_user in valid_users or clean_user == "acelerar@acelerar.tech") and input_pass == MASTER_KEY:
                st.session_state.auth = True
                st.session_state.user = clean_user
                st.rerun()
            else:
                st.error("Credenciais inválidas ou usuário não autorizado.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_portal():
    st.markdown("<h1 style='color: white; text-align: center;'>Painel de Gestão Holding</h1>", unsafe_allow_html=True)
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 📊 Módulo Comercial")
        if st.button("Acessar Dashboard Comercial", use_container_width=True):
            st.session_state.view = "comercial"
            st.rerun()
            
    with c2:
        st.success("### 💰 Módulo Financeiro")
        if st.button("Acessar DRE / Nibo", use_container_width=True):
            st.session_state.view = "financeiro"
            st.rerun()
            
    st.divider()
    if st.button("Sair"):
        st.session_state.auth = False
        st.rerun()

# 7. ORQUESTRAÇÃO DE NAVEGAÇÃO
if not st.session_state.auth:
    render_login()
else:
    if st.session_state.view == "portal":
        render_portal()
    elif st.session_state.view == "comercial":
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                exec(f.read())
        except Exception as e:
            st.error(f"Erro ao carregar módulo: {e}")
            if st.button("Voltar"): st.session_state.view = "portal"; st.rerun()
    elif st.session_state.view == "financeiro":
        st.warning("Módulo Financeiro em fase de integração.")
        if st.button("Voltar"): st.session_state.view = "portal"; st.rerun()
