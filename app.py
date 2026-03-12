import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import hashlib
import os

# Configuração da página - Estilo Sênior Premium (Alterado para expanded)
st.set_page_config(layout="wide", page_title="Dashboard Comercial Estratégico - Acelerar.tech", page_icon="📊", initial_sidebar_state="expanded")

COLOR_PRIMARY = "#0B2A4E"
COLOR_SECONDARY = "#89CFF0"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#0A1E2E"
COLOR_CHURN = "#E74C3C"

# Estilização CSS Customizada - VERSÃO EXECUTIVA PREMIUM
st.markdown(f"""
    <style>
    .main {{ background-color: {COLOR_BG}; }}
    
    /* Estilo Base dos Cards */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_PRIMARY} !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        color: {COLOR_TEXT} !important;
        min-width: 180px !important;
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        color: {COLOR_TEXT} !important;
    }}
    
    div[data-testid="stMetricLabel"] > div {{
        color: {COLOR_TEXT} !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
    }}
    
    /* Destaque para o Card de Churn (Coluna 3) */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {{
        border: 2px solid {COLOR_CHURN} !important;
    }}
    
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] > div,
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {{
        color: {COLOR_CHURN} !important;
    }}
    
    /* Estilo do Delta no Churn */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] > div {{
        background-color: rgba(231, 76, 60, 0.2) !important;
        color: {COLOR_CHURN} !important;
        padding: 2px 8px !important;
        border-radius: 15px !important;
    }}
    
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricDelta"] svg {{
        fill: {COLOR_CHURN} !important;
        stroke: {COLOR_CHURN} !important;
    }}
    
    /* Estilo da Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_PRIMARY} !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: {COLOR_TEXT} !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {{
        background-color: #F8F9FA !important;
        color: {COLOR_PRIMARY} !important;
        border-radius: 5px !important;
    }}
    
    [data-testid="stSidebar"] .stExpander {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }}
    
    /* Títulos e Gráficos */
    h1, h2, h3 {{
        color: {COLOR_SECONDARY} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }}
    
    /* White Label - Ocultar menus padrão do Streamlit */
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    footer {{ display: none !important; }}
    .stApp > header {{ display: none !important; }}
    [data-testid="stDecoration"] {{ display: none !important; }}
    a[href*="github"], a[href*="deploy"], a[href*="settings"] {{ display: none !important; }}
    
    /* Login Styles */
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background-color: #0F2438 !important;
    }}
    .login-card {{
        background-color: rgba(10, 30, 46, 0.95) !important;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        width: 100%;
        max-width: 400px;
        border: 2px solid {COLOR_SECONDARY};
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# Estados de Sessão
if 'page' not in st.session_state: st.session_state.page = 'comercial'
if 'empresa' not in st.session_state: st.session_state.empresa = 'VMC Tech'
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = False
if 'email_usuario' not in st.session_state: st.session_state.email_usuario = None

# Configurações de Empresas e Usuários
EMPRESAS = {
    'VMC Tech': {
        'vendas_id': '1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M',
        'vendas_gid': '1202307787',
        'cancelados_id': '1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw',
        'cancelados_gid': '606807719',
        'contas_receber_id': '1Nqmn2c9p0QFu8LFIqFQ0EBxA8klHFUsVjAW15la-Fjg'
    },
    'Victec': {
        'vendas_id': '1o0RJI58HW-NLX97Jab4YpKiM4b8_kIw2o11EL8iMgCo',
        'vendas_gid': '0',
        'cancelados_id': '1-eXWcie9mPwtWOiQDDiPlwrDmexvXeeQ4FAIDPEQ9c4',
        'cancelados_gid': '0',
        'contas_receber_id': '1Y28LP_ZPqWKMjXqf88ahzaDET_DneOYhxuNOmyinxus'
    }
}
USUARIOS_SHEET_ID = '15FsHefIdRzwUGm6FcpQQF-qiOtPwYHd-v70MwErOAMk'
SENHA_MESTRA = 'Acelerar@2026'

# Funções de Carregamento de Dados
@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    if gid and gid != '0':
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def load_usuarios():
    url = f"https://docs.google.com/spreadsheets/d/{USUARIOS_SHEET_ID}/export?format=csv"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def parse_currency(series):
    def clean_val(val):
        if pd.isna(val) or val == "": return 0.0
        if isinstance(val, (int, float)): return float(val)
        s = str(val).replace('R$', '').strip()
        if not s: return 0.0
        if ',' in s: s = s.replace('.', '').replace(',', '.')
        elif '.' in s:
            parts = s.split('.')
            if len(parts[-1]) != 2: s = s.replace('.', '')
        try: return float(s)
        except: return 0.0
    return series.apply(clean_val)

def render_login():
    img_base64 = ""
    try:
        if os.path.exists('Acelerar-Identidade-Visual.png'):
            with open('Acelerar-Identidade-Visual.png', 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode()
    except: pass
    
    st.markdown(f"""
        <div class="login-container">
            <div class="login-card">
                {"<img src='data:image/png;base64," + img_base64 + "' style='width: 150px; margin-bottom: 20px;'>" if img_base64 else ""}
                <h1 style="color: {COLOR_SECONDARY}; font-size: 1.8rem; margin-bottom: 10px;">Dashboard Comercial</h1>
                <p style="color: {COLOR_TEXT}; opacity: 0.8; margin-bottom: 30px;">Acelerar.tech - Holding</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            email = st.text_input("📧 E-mail", placeholder="seu.email@empresa.com")
            senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                if not email or not senha: st.error("❌ Preencha todos os campos.")
                elif senha != SENHA_MESTRA: st.error("❌ Senha incorreta.")
                else:
                    df_u = load_usuarios()
                    if not df_u.empty and email.lower() in df_u['Email'].str.lower().values:
                        st.session_state.usuario_logado = True
                        st.session_state.email_usuario = email
                        st.rerun()
                    else: st.error("❌ E-mail não autorizado.")

def processar_dados(empresa):
    config = EMPRESAS[empresa]
    df_v = load_data(config['vendas_id'], config['vendas_gid'])
    df_c = load_data(config['cancelados_id'], config['cancelados_gid'])
    df_cr = load_data(config['contas_receber_id'])
    if df_v.empty: return None, None
    df = pd.DataFrame()
    df['vendedor'] = df_v['Vendedor'].fillna("N/A")
    df['sdr'] = df_v['SDR'].fillna("N/A")
    df['cliente'] = df_v['Cliente'].fillna("N/A")
    df['cnpj'] = df_v['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True)
    df['produto'] = df_v['Qual produto?'].fillna("Sittax Simples")
    df['mrr'] = parse_currency(df_v['Mensalidade - Simples'])
    df['adesao'] = parse_currency(df_v['Adesão - Simples']) + parse_currency(df_v['Adesão - Recupera'])
    df['upgrade'] = parse_currency(df_v['Aumento da mensalidade'])
    df['data'] = pd.to_datetime(df_v['Data de Ativação'], errors='coerce')
    df = df.dropna(subset=['data'])
    df['ano'] = df['data'].dt.year.astype(int)
    df['mes_num'] = df['data'].dt.month.astype(int)
    meses_pt = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
    df['mes_nome'] = df['mes_num'].map(meses_pt)
    df['status'] = 'Confirmada'
    if not df_c.empty:
        canc_cnpjs = df_c['CNPJ do Cliente'].astype(str).str.replace(r'\D', '', regex=True).unique()
        df.loc[df['cnpj'].isin(canc_cnpjs), 'status'] = 'Cancelada'
    return df, df_cr

def render_page_comercial(df):
    st.sidebar.markdown("<h3 style='color: white; text-align: center;'>🏢 Seletor de Empresa</h3>", unsafe_allow_html=True)
    empresa_sel = st.sidebar.selectbox("Selecione a Empresa", list(EMPRESAS.keys()), index=list(EMPRESAS.keys()).index(st.session_state.empresa))
    if empresa_sel != st.session_state.empresa:
        st.session_state.empresa = empresa_sel
        st.cache_data.clear(); st.rerun()
    
    st.sidebar.markdown("<h3 style='color: white; text-align: center;'>🔍 Filtros Estratégicos</h3>", unsafe_allow_html=True)
    anos = sorted(df['ano'].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("📅 Ano de Referência", anos)
    df_ano = df[df['ano'] == ano_sel]
    
    with st.sidebar.expander("📅 Selecionar Período (Meses)"):
        meses_ordem = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
        meses_disp = [m for m in meses_ordem if m in df_ano['mes_nome'].unique()]
        meses_sel = st.multiselect("Meses", meses_disp, default=meses_disp)
    
    st.sidebar.divider()
    prod_sel = st.sidebar.selectbox("📦 Produto", ["Todos"] + sorted(df['produto'].unique().tolist()))
    vend_sel = st.sidebar.selectbox("👤 Vendedor", ["Todos"] + sorted(df['vendedor'].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("🎧 SDR", ["Todos"] + sorted(df['sdr'].unique().tolist()))
    
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario_logado = False; st.rerun()

    df_f = df_ano[df_ano['mes_nome'].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f['produto'] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f['vendedor'] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f['sdr'] == sdr_sel]

    mrr_conq = df_f[df_f['status'] == 'Confirmada']['mrr'].sum()
    mrr_perd = df_f[df_f['status'] == 'Cancelada']['mrr'].sum()
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0
    
    col_nav_left, col_nav_right = st.columns([0.8, 0.2])
    with col_nav_right:
        if st.button("📋 Inadimplência", use_container_width=True):
            st.session_state.page = 'inadimplencia'; st.rerun()

    st.title(f"📊 Resumo Comercial - {st.session_state.empresa}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MRR Conquistado", f"R$ {int(mrr_conq):,}".replace(",", "."))
    c2.metric("MRR Ativo (Net)", f"R$ {int(mrr_conq - mrr_perd):,}".replace(",", "."))
    c3.metric("MRR Perdido (Churn)", f"R$ {int(mrr_perd):,}".replace(",", "."), delta=f"{-churn_p:.1f}%", delta_color="inverse")
    c4.metric("Clientes fechado", len(df_f[df_f['status'] == 'Confirmada']))

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        df_m = df_ano[df_ano['status'] == 'Confirmada'].groupby(['mes_num','mes_nome'])['mrr'].sum().reset_index().sort_values('mes_num')
        st.plotly_chart(px.bar(df_m, x='mes_nome', y='mrr', title="MRR por Mês", color_discrete_sequence=[COLOR_PRIMARY]), use_container_width=True)
    with col2:
        df_rank = df_f[df_f['status'] == 'Confirmada'].groupby('vendedor')['mrr'].sum().reset_index().sort_values('mrr', ascending=False)
        st.plotly_chart(px.bar(df_rank.head(10), x='mrr', y='vendedor', orientation='h', title="Top Vendedores", color_discrete_sequence=[COLOR_SECONDARY]), use_container_width=True)
    
    st.divider()
    st.subheader("📋 Detalhamento")
    st.dataframe(df_f[['data', 'cliente', 'vendedor', 'sdr', 'produto', 'status', 'mrr']].sort_values('data', ascending=False), use_container_width=True)

def render_page_inadimplencia(df_cr):
    col_nav_left, col_nav_right = st.columns([0.8, 0.2])
    with col_nav_right:
        if st.button("📊 Comercial", use_container_width=True):
            st.session_state.page = 'comercial'; st.rerun()
    st.title(f"📋 Inadimplência - {st.session_state.empresa}")
    if df_cr.empty: st.warning("Sem dados."); return
    df_cr['valor_n'] = parse_currency(df_cr.iloc[:, -1])
    total = df_cr['valor_n'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total em Aberto", f"R$ {int(total):,}".replace(",", "."))
    c2.metric("Clientes", df_cr.iloc[:, 1].nunique())
    c3.metric("Repasse (30%)", f"R$ {int(total*0.3):,}".replace(",", "."))
    st.divider()
    st.dataframe(df_cr.head(50), use_container_width=True)

if not st.session_state.usuario_logado:
    render_login()
else:
    st.sidebar.markdown(f"<h4 style='color: white;'>👤 Usuário: {st.session_state.email_usuario}</h4>", unsafe_allow_html=True)
    df_p, df_cr = processar_dados(st.session_state.empresa)
    if df_p is not None:
        if st.session_state.page == 'comercial': render_page_comercial(df_p)
        else: render_page_inadimplencia(df_cr)
    else: st.error("Erro ao carregar os dados.")
