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
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = True # Sempre True pois o login é na Vercel
if 'modulo' not in st.session_state: st.session_state.modulo = 'comercial' # Abre direto no Comercial

# --- 3. CORES E ESTILOS ---
COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"

# --- 4. CSS DE LIMPEZA (REMOVE CABEÇALHO E RODAPÉ DO STREAMLIT) ---
st.markdown(f"""
    <style>
        [data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        [data-testid="collapsedControl"], [data-testid="stSidebar"] {{ display: none !important; }}
        .main .block-container {{ padding-top: 0rem !important; }}
        .stApp {{ background-color: {COLOR_BG}; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO DIRETA (INTEGRAÇÃO COM PORTAL VERCEL) ---
try:
    with open("comercial/comercial.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"Erro ao carregar o módulo Comercial: {e}")
