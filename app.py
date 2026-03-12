import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuração da página - Estilo Sênior Premium
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

def get_drive_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}"

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown(f"""
    <style>
    /* Fundo Principal */
    .main {{ background-color: {COLOR_BG}; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
    }}
    
    /* Centralização e Ajuste do Login */
    .login-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 0;
        margin-top: -50px;
    }}
    
    .login-title {{
        color: {COLOR_TEXT};
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    
    .login-logo {{
        width: 180px;
        margin-bottom: 20px;
    }}

    /* KPIs */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    }}

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #16324F;
        border-radius: 5px 5px 0 0;
        color: white;
        padding: 8px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_SECONDARY} !important;
        color: {COLOR_PRIMARY} !important;
        font-weight: bold;
    }}
    
    /* Remover barra de rolagem desnecessária no login */
    .block-container {{
        padding-top: 3rem !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS COM CACHE ---
@st.cache_data
def carregar_dados_vendas():
    # Exemplo de como você deve apontar para seus CSVs reais do Drive
    # Substitua pela sua URL real de exportação do Google Drive
    # url = "https://drive.google.com/uc?id=SEU_ID_DO_CSV_DE_VENDAS"
    # return pd.read_csv(url)
    return pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        'Faturamento': [380000, 410000, 395000, 425000, 440000, 450000]
    })

# --- SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # Estrutura da Página de Login solicitada
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<p class="login-title">Dashboard Comercial</p>', unsafe_allow_html=True)
    st.image(get_drive_url(LOGOS["ACELERAR_LOGIN"]), width=200)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Acessar Dashboard", use_container_width=True):
            if usuario == "admin" and senha == "1234": # Altere para sua senha real
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD APÓS LOGIN ---
with st.sidebar:
    # Logo Acelerar Fixo na Sidebar
    st.image(get_drive_url(LOGOS["ACELERAR_SIDEBAR"]), width=150)
    st.markdown(f"**Usuário:** {datetime.now().strftime('%H:%M')} | Online")
    
    st.divider()
    st.header("Filtros")
    
    empresa_selecionada = st.selectbox(
        "Selecione a Empresa",
        ["VMC Tech", "Victec"]
    )
    
    mes_referencia = st.selectbox(
        "Mês",
        ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        index=datetime.now().month - 1
    )
    
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- CABEÇALHO DINÂMICO ---
# Define qual logo mostrar com base na empresa
logo_id = LOGOS["VMC_TECH"] if empresa_selecionada == "VMC Tech" else LOGOS["VICTEC"]

# Abas Principais
tab_comercial, tab_inadimplencia = st.tabs(["📈 Resumo Comercial", "📉 Inadimplência"])

with tab_comercial:
    # Logo da Empresa Selecionada acima do título
    st.image(get_drive_url(logo_id), width=120)
    st.title(f"Resumo Comercial: {empresa_selecionada}")
    st.caption(f"Referência: {mes_referencia} / {datetime.now().year}")
    
    # KPIs (Exemplo)
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento", "R$ 450.000", "+12%")
    c2.metric("Meta Atingida", "92%", "Meta: 500k")
    c3.metric("Novos Contratos", "24", "+3")
    
    st.divider()
    df_vendas = carregar_dados_vendas()
    fig = px.area(df_vendas, x='Mês', y='Faturamento', title="Evolução de Vendas", color_discrete_sequence=[COLOR_SECONDARY])
    st.plotly_chart(fig, use_container_width=True)

with tab_inadimplencia:
    # Logo da Empresa Selecionada acima do título
    st.image(get_drive_url(logo_id), width=120)
    st.title(f"Gestão de Inadimplência: {empresa_selecionada}")
    
    st.warning(f"Atenção: Monitoramento de contas a receber para {empresa_selecionada}")
    
    # Exemplo de gráfico de inadimplência
    df_inad = pd.DataFrame({'Status': ['Em Dia', 'Atrasado', 'Crítico'], 'Valor': [80, 15, 5]})
    fig_inad = px.pie(df_inad, values='Valor', names='Status', color_discrete_sequence=['#27AE60', '#F1C40F', '#E74C3C'])
    st.plotly_chart(fig_inad, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Holding Acelerar.tech")
