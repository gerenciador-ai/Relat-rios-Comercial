import streamlit as st
import pandas as pd
import requests
from io import StringIO

# 1. CONFIGURACOES DE PAGINA
st.set_page_config(layout="wide", page_title="Holding Acelerar", page_icon="🏢", initial_sidebar_state="collapsed")

# 2. CONSTANTES
ID_S = "15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk"
KEY_M = "Acelerar@2026"
URL_L = "https://raw.githubusercontent.com/gerenciador-ai/Relat-rios-Comercial/main/logo_acelerar_sidebar.png"

# 3. ESTADOS
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "portal"

# 4. USUARIOS
@st.cache_data(ttl=600 )
def get_users():
    try:
        u = "https://docs.google.com/spreadsheets/d/" + ID_S + "/export?format=csv"
        r = requests.get(u, timeout=10 )
        if r.status_code == 200:
            d = pd.read_csv(StringIO(r.text))
            return d.iloc[:, 0].astype(str).str.strip().str.lower().tolist()
        return []
    except:
        return []

# 5. CSS BLINDADO (SEM STRINGS LONGAS)
st.write("<style>div[data-testid='stAppViewContainer'] { background-color: #0A1E2E; }</style>", unsafe_allow_html=True)
st.write("<style>section[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
st.write("<style>[data-testid='collapsedControl'] { display: none !important; }</style>", unsafe_allow_html=True)
st.write("<style>header { visibility: hidden !important; } footer { visibility: hidden !important; }</style>", unsafe_allow_html=True)
st.write("<style>.card { background-color: #0B2A4E; padding: 50px; border-radius: 20px; border: 1px solid #89CFF0; text-align: center; }</style>", unsafe_allow_html=True)

# 6. LOGIN
def show_login():
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.write("<div class='card'>", unsafe_allow_html=True)
        st.image(URL_L, width=250)
        st.write("<h2 style='color: white;'>Acesso Restrito</h2>", unsafe_allow_html=True)
        u_in = st.text_input("Usuario", placeholder="e-mail")
        p_in = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True, type="primary"):
            v_u = get_users()
            c_u = u_in.strip().lower()
            if (c_u in v_u or c_u == "acelerar@acelerar.tech") and p_in == KEY_M:
                st.session_state.auth = True
                st.session_state.user = c_u
                st.rerun()
            else:
                st.error("Erro de credenciais.")
        st.write("</div>", unsafe_allow_html=True)

# 7. PORTAL
def show_portal():
    st.write("<h1 style='color: white; text-align: center;'>Holding Acelerar</h1>", unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.info("### Comercial")
        if st.button("Abrir Comercial", use_container_width=True):
            st.session_state.view = "comercial"
            st.rerun()
    with c2:
        st.success("### Financeiro")
        if st.button("Abrir Financeiro", use_container_width=True):
            st.session_state.view = "financeiro"
            st.rerun()
    st.divider()
    if st.button("Sair"):
        st.session_state.auth = False
        st.rerun()

# 8. NAVEGACAO
if not st.session_state.auth:
    show_login()
else:
    if st.session_state.view == "portal":
        show_portal()
    elif st.session_state.view == "comercial":
        try:
            with open("comercial/comercial.py", encoding="utf-8") as f:
                exec(f.read())
        except Exception as e:
            st.error("Erro: " + str(e))
    elif st.session_state.view == "financeiro":
        st.warning("Modulo em integracao.")
        if st.button("Voltar"): st.session_state.view = "portal"; st.rerun()
