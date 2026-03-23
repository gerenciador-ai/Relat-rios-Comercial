import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import requests
from io import StringIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Holding Acelerar", 
    page_icon="🏢", 
    initial_sidebar_state="collapsed"
)

# --- 2. INICIALIZAÇÃO DOS ESTADOS DE SESSÃO ---
# Definimos como True para integrar com o login do Portal Vercel
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = True
if 'modulo' not in st.session_state: st.session_state.modulo = 'comercial'

# --- 3. CORES E ESTILOS ---
COLOR_BG = "#0A1E2E"

# --- 4. CSS DE LIMPEZA E LIBERAÇÃO DE IFRAME ---
st.markdown(f"""
    <style>
        /* Remove elementos do Streamlit para parecer nativo no portal */
        [data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        [data-testid="collapsedControl"], [data-testid="stSidebar"] {{ display: none !important; }}
        .main .block-container {{ padding-top: 0rem !important; }}
        .stApp {{ background-color: {COLOR_BG}; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. CARREGAMENTO DO MÓDULO COMERCIAL ---
try:
    # O comando exec() carrega o comercial.py diretamente
    with open("comercial/comercial.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"Erro ao carregar o módulo Comercial: {e}")
