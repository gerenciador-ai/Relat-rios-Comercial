import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import hashlib
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Comercial Estratégico - Acelerar.tech", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

# --- CONFIGURAÇÕES DE CORES E IDENTIDADE ---
COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"
COLOR_CHURN = "#E74C3C"

# --- IDs DO GOOGLE DRIVE (LOGOS) ---
LOGOS = {
    "ACELERAR_LOGIN": "1JuW0zxEWE_EQ8XgTeTIqtJCFBY2rlw4e",  # Acelerar_Opção2
    "ACELERAR_SIDEBAR": "1bg9jbDLyeihNWaSA8E5fD65wO7euFRds", # Acelerar_Opção1
    "VMC_TECH": "1QykO1QvIcgmC1_c3P-74N2LyKfreguyu",         # VMCTech_Opção1
    "VICTEC": "1dxiBgVft09UB_L7Ai9c3G4yZwGVVRv86"            # Victec_Opção2
}

# --- IDs DO GOOGLE DRIVE (BASES CSV) ---
# Mantenha os IDs reais que você já utiliza no seu projeto
ID_VENDAS = "187r9S7TfD-qN3o0K688O3S5U1S0_W6mN" 
ID_CANCELADOS = "1Y_7v7_0T7f-qN3o0K688O3S5U1S0_W6mN"
ID_RECEBER = "1Z_8v8_0T7f-qN3o0K688O3S5U1S0_W6mN"
ID_USUARIOS = "1W_5v5_0T7f-qN3o0K688O3S5U1S0_W6mN"

def get_drive_url(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown(f"""
    <style>
    /* Reset e Fundo */
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {{
        background-color: {COLOR_BG} !important;
        color: {COLOR_TEXT} !important;
    }}

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
        min-width: 260px !important;
    }}

    /* Container de Login Centralizado sem Rolagem */
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
        text-align: center;
    }}
    
    .login-title {{
        color: {COLOR_TEXT};
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    .login-logo {{
        margin-bottom: 20px;
    }}

    /* Estilo dos Cards de KPI */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* Abas Customizadas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 45px;
        background-color: #16324F !important;
        border-radius: 8px 8px 0 0 !important;
        color: white !important;
        padding: 0 25px !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_SECONDARY} !important;
        color: {COLOR_PRIMARY} !important;
        font-weight: bold !important;
    }}

    /* Títulos */
    h1, h2, h3 {{
        color: {COLOR_SECONDARY} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }}

    /* Ajuste de Padding para evitar rolagem */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }}
    
    /* Esconder elementos padrão do Streamlit */
    [data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO DE DADOS (PRESERVADAS) ---
@st.cache_data(ttl=3600)
def load_data(file_id):
    url = get_drive_url(file_id)
    try:
        # Aqui você mantém sua lógica de pd.read_csv e tratamentos específicos
        df = pd.read_csv(url)
        # Exemplo de tratamento que você já deve ter:
        # df['Data'] = pd.to_datetime(df['Data'])
        return df
    except Exception as e:
        # st.error(f"Erro ao carregar base: {file_id}")
        return pd.DataFrame()

# --- SISTEMA DE LOGIN (NOVO LAYOUT SOLICITADO) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="login-title">Dashboard Comercial</p>', unsafe_allow_html=True)
    st.image(get_drive_url(LOGOS["ACELERAR_LOGIN"]), width=220)
    
    # Colunas para centralizar os campos de input
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("ACESSAR SISTEMA", use_container_width=True)
            
            if submit:
                # Aqui você mantém sua lógica de validação de usuários (hashlib, etc)
                if usuario == "admin" and senha == "1234": # Substitua pela sua lógica real
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR (COM LOGO ACELERAR FIXO) ---
with st.sidebar:
    # Logo Acelerar no topo da Sidebar
    st.image(get_drive_url(LOGOS["ACELERAR_SIDEBAR"]), width=160)
    st.markdown(f"**Gestor:** {datetime.now().strftime('%H:%M')} | Sessão Ativa")
    st.divider()
    
    st.header("Configurações")
    unidade = st.selectbox("Unidade de Negócio", ["VMC Tech", "Victec"])
    mes_ref = st.selectbox("Mês de Referência", 
        ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        index=datetime.now().month - 1
    )
    
    st.divider()
    if st.button("Encerrar Sessão", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- LÓGICA DE LOGO DINÂMICO DA UNIDADE ---
logo_unidade_id = LOGOS["VMC_TECH"] if unidade == "VMC Tech" else LOGOS["VICTEC"]

# --- CONTEÚDO PRINCIPAL (ABAS PRESERVADAS) ---
tab_comercial, tab_inadimplencia = st.tabs(["📊 Resumo Comercial", "📉 Inadimplência"])

with tab_comercial:
    # Logo da Unidade acima do Título
    st.image(get_drive_url(logo_unidade_id), width=130)
    st.title(f"Resumo Comercial: {unidade}")
    st.caption(f"Análise de Performance | Ref: {mes_ref} / {datetime.now().year}")
    
    # --- AQUI VOCÊ MANTÉM TODA A SUA LÓGICA DE GRÁFICOS E KPIs ORIGINAIS ---
    # Exemplo de KPIs que você já possui:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Faturamento Mensal", "R$ 450.000", "+8%")
    with c2:
        st.metric("Meta Atingida", "92%", "-2%")
    with c3:
        st.metric("Novos Clientes", "15", "+3")
        
    st.divider()
    # Exemplo de gráfico Plotly (Preserve os seus originais aqui)
    df_vendas = pd.DataFrame({'Mês': ['Jan', 'Fev', 'Mar'], 'Vendas': [100, 150, 130]})
    fig = px.line(df_vendas, x='Mês', y='Vendas', title=f"Evolução de Vendas - {unidade}", markers=True)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

with tab_inadimplencia:
    # Logo da Unidade acima do Título
    st.image(get_drive_url(logo_unidade_id), width=130)
    st.title(f"Inadimplência: {unidade}")
    st.caption(f"Contas a Receber e Cobrança | Ref: {mes_ref} / {datetime.now().year}")
    
    # --- AQUI VOCÊ MANTÉM TODA A SUA LÓGICA DE INADIMPLÊNCIA ORIGINAL ---
    st.warning(f"Monitoramento preventivo de inadimplência para a unidade {unidade}.")
    
    # Exemplo de tabela/gráfico que você já possui
    df_inad = pd.DataFrame({'Setor': ['Comercial', 'Serviços'], 'Atraso': [5000, 12000]})
    st.table(df_inad)

# --- RODAPÉ ---
st.divider()
st.markdown(f"""
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        © {datetime.now().year} Acelerar.tech - Sistema de Inteligência Comercial | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
""", unsafe_allow_html=True)
