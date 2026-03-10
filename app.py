import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    layout="wide",
    page_title="Dashboard Comercial - Acelerar.tech",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ==================== PALETA DE CORES CORPORATIVA ACELERAR.TECH ====================
CORES = {
    "primaria_escura": "#1B3A5C",      # Azul Marinho (backgrounds, headers)
    "primaria_media": "#2E5A8C",       # Azul Médio (destaques)
    "primaria_clara": "#5BA3D0",       # Azul Claro (elementos secundários)
    "branco": "#FFFFFF",               # Branco puro
    "cinza_fundo": "#F8F9FA",          # Cinza ultra claro (background da página)
    "cinza_texto": "#212529",          # Cinza escuro (texto principal - ALTA LEGIBILIDADE)
    "cinza_subtexto": "#6C757D",       # Cinza médio (rótulos e subtextos)
    "verde": "#28A745",                # Verde Sucesso
    "vermelho": "#DC3545",             # Vermelho Churn
    "laranja": "#FD7E14"               # Laranja Destaque
}

# ==================== CSS CUSTOMIZADO (FOCO EM LEGIBILIDADE E DESIGN CLEAN) ====================
st.markdown(f"""
<style>
    /* Importação de fonte profissional */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap' );

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {CORES['cinza_texto']};
    }}

    /* Background da página */
    .stApp {{
        background-color: {CORES['cinza_fundo']};
    }}
    
    /* Sidebar Profissional */
    [data-testid="stSidebar"] {{
        background-color: {CORES['primaria_escura']};
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: {CORES['branco']} !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }}
    
    /* Ajuste de inputs na Sidebar */
    div[data-baseweb="select"] > div {{
        background-color: white !important;
        border-radius: 8px !important;
    }}

    /* Títulos Executivos */
    h1 {{
        color: {CORES['primaria_escura']} !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem !important;
    }}
    
    h2, h3 {{
        color: {CORES['primaria_escura']} !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }}
    
    /* Cartões de Métrica (Redesenhados para Legibilidade Máxima) */
    div[data-testid="metric-container"] {{
        background-color: {CORES['branco']};
        padding: 25px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: 1px solid #E9ECEF !important;
    }}
    
    div[data-testid="metric-container"] label {{
        color: {CORES['cinza_subtexto']} !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-weight: 600 !important;
    }}
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        color: {CORES['primaria_escura']} !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }}

    /* Estilo para Tabelas */
    [data-testid="stDataFrame"] {{
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #E9ECEF !important;
    }}

    /* Divisores Suaves */
    hr {{
        margin: 2rem 0 !important;
        border: 0;
        border-top: 1px solid #DEE2E6 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== IDs E GIDs DAS PLANILHAS GOOGLE SHEETS ====================
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719"

# ==================== FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO ====================
@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{{sheet_id}}/export?format=csv"
    if gid: url += f"&gid={{gid}}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {{e}}")
        return pd.DataFrame()

def parse_currency(series):
    def clean_val(val):
        if pd.isna(val) or val == "": return 0.0
        if isinstance(val, (int, float)): return float(val)
        s = str(val).replace("R$", "").strip()
        if not s: return 0.0
        if "," in s: s = s.replace(".", "").replace(",", ".")
        elif "." in s:
            parts = s.split(".")
            if len(parts[-1]) != 2: s = s.replace(".", "")
        try: return float(s)
        except: return 0.0
    return series.apply(clean_val)

def processar_dados():
    df_v = load_data(VENDAS_ID, VENDAS_GID)
    df_c = load_data(CANCELADOS_ID, CANCELADOS_GID)
    if df_v.empty: return None

    df = pd.DataFrame()
    df["vendedor"] = df_v["Vendedor"].fillna("N/A")
    df["sdr"] = df_v["SDR"].fillna("N/A")
    df["cliente"] = df_v["Cliente"].fillna("N/A")
    df["cnpj"] = df_v["CNPJ do Cliente"].astype(str).str.replace(r"\D", "", regex=True)
    df["produto"] = df_v["Qual produto?"].fillna("Sittax Simples")
    df.loc[df["produto"].astype(str).str.strip() == "", "produto"] = "Sittax Simples"

    df["mrr"] = parse_currency(df_v["Mensalidade - Simples"])
    df["adesao"] = parse_currency(df_v["Adesão - Simples"]) + parse_currency(df_v["Adesão - Recupera"])
    df["upgrade"] = parse_currency(df_v["Aumento da mensalidade"])
    
    df["data"] = pd.to_datetime(df_v["Data de Ativação"], errors="coerce", dayfirst=False)
    df.loc[df["upgrade"] > 0, "data"] = pd.to_datetime(df_v["Data alteração de CNPJ"], errors="coerce", dayfirst=False)
    
    df = df.dropna(subset=["data"])
    df["ano"] = df["data"].dt.year.astype(int)
    df["mes_num"] = df["data"].dt.month.astype(int)
    meses_pt = {{1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
                7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}}
    df["mes_nome"] = df["mes_num"].map(meses_pt)
    df["inicio_semana"] = df["data"].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

    df["status"] = "Confirmada"
    if not df_c.empty:
        canc_cnpjs = df_c["CNPJ do Cliente"].astype(str).str.replace(r"\D", "", regex=True).unique()
        df.loc[df["cnpj"].isin(canc_cnpjs), "status"] = "Cancelada"
    
    return df

# ==================== INTERFACE PRINCIPAL ====================
df = processar_dados()

if df is not None:
    # Sidebar - Filtros
    st.sidebar.markdown("### 🔍 FILTROS ESTRATÉGICOS")
    anos = sorted(df["ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano de Referência", anos)
    df_ano = df[df["ano"] == ano_sel]
    
    meses_ordem = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    meses_disp = [m for m in meses_ordem if m in df_ano["mes_nome"].unique()]
    meses_sel = st.sidebar.multiselect("Meses", meses_disp, default=meses_disp)
    
    prod_sel = st.sidebar.selectbox("Linha de Produto", ["Todos"] + sorted(df["produto"].unique().tolist()))
    vend_sel = st.sidebar.selectbox("Vendedor Responsável", ["Todos"] + sorted(df["vendedor"].unique().tolist()))

    # Aplicar filtros
    df_f = df_ano[df_ano["mes_nome"].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f["produto"] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f["vendedor"] == vend_sel]

    # Cabeçalho Principal
    st.markdown("<h1>📊 Dashboard Comercial Estratégico</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {{CORES['cinza_subtexto']}}; font-size: 1.1rem; margin-top: -10px;'>Acelerar.tech | Inteligência de Dados em Vendas</p>", unsafe_allow_html=True)

    # ==================== KPIs (DESIGN EXECUTIVO) ====================
    mrr_conq = df_f[df_f["status"] == "Confirmada"]["mrr"].sum()
    mrr_perd = df_f[df_f["status"] == "Cancelada"]["mrr"].sum()
    cl_fech = len(df_f[(df_f["status"] == "Confirmada") & (df_f["mrr"] > 0)])
    cl_canc = len(df_f[df_f["status"] == "Cancelada"])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0

    st.markdown("### 💰 Performance Financeira")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("MRR CONQUISTADO", f"R$ {{mrr_conq:,.2f}}")
    k2.metric("MRR ATIVO (NET)", f"R$ {{mrr_conq - mrr_perd:,.2f}}")
    k3.metric("MRR PERDIDO (CHURN)", f"R$ {{mrr_perd:,.2f}}", f"-{{churn_p:.1f}}%", delta_color="inverse")
    k4.metric("TICKET MÉDIO", f"R$ {{tkt_med:,.2f}}")

    st.markdown("### 📈 Volume e Conversão")
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("CLIENTES FECHADOS", cl_fech)
    k6.metric("CLIENTES CANCELADOS", cl_canc)
    k7.metric("ADESÃO TOTAL", f"R$ {{df_f['adesao'].sum():,.2f}}")
    k8.metric("TOTAL UPSELL", f"R$ {{df_f['upgrade'].sum():,.2f}}")

    st.divider()

    # ==================== GRÁFICOS (ALTA DEFINIÇÃO E CORES CORPORATIVAS) ====================
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📅 Evolução de Receita (MRR)")
        df_m = df_ano[df_ano["status"] == "Confirmada"].groupby(["mes_num", "mes_nome"]).agg({{"mrr": "sum"}}).reset_index().sort_values("mes_num")
        fig = px.area(df_m, x="mes_nome", y="mrr", text=df_m["mrr"].apply(lambda x: f"R$ {{x/1000:,.1f}}k"))
        fig.update_traces(
            line_color=CORES["primaria_media"], 
            fillcolor=f"rgba(91, 163, 208, 0.3)",
            textposition="top center",
            mode="lines+markers+text"
        )
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            margin=dict(l=0, r=0, t=30, b=0),
            height=350,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color=CORES["cinza_texto"])
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 🏆 Performance por Vendedor")
        df_v = df_f[df_f["status"] == "Confirmada"].groupby("vendedor")["mrr"].sum().reset_index().sort_values("mrr", ascending=True)
        fig = px.bar(df_v, y="vendedor", x="mrr", orientation='h', text=df_v["mrr"].apply(lambda x: f"R$ {{x:,.0f}}"))
        fig.update_traces(marker_color=CORES["primaria_escura"], textposition="outside")
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            margin=dict(l=0, r=0, t=30, b=0),
            height=350,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color=CORES["cinza_texto"])
        )
        st.plotly_chart(fig, use_container_width=True)

    col_bottom1, col_bottom2 = st.columns([2, 1])

    with col_bottom1:
        st.markdown("### 📊 Churn Mensal (Perda de MRR)")
        df_c = df_ano[df_ano["status"] == "Cancelada"].groupby(["mes_num", "mes_nome"]).agg({{"mrr": "sum"}}).reset_index().sort_values("mes_num")
        fig = px.bar(df_c, x="mes_nome", y="mrr", color_discrete_sequence=[CORES["vermelho"]])
        fig.update_layout(
            xaxis_title=None, yaxis_title=None,
            height=300,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color=CORES["cinza_texto"])
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_bottom2:
        st.markdown("### 📦 Mix de Produtos")
        fig = px.pie(df_f, names="produto", values="mrr", hole=0.5, color_discrete_sequence=[CORES["primaria_escura"], CORES["primaria_clara"], CORES["primaria_media"]])
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==================== TABELA DETALHADA ====================
    st.divider()
    st.markdown("### 📋 Detalhamento Estratégico de Vendas")
    df_table = df_f[["data", "cliente", "vendedor", "produto", "status", "mrr"]].sort_values("data", ascending=False).copy()
    df_table["data"] = df_table["data"].dt.strftime("%d/%m/%Y")
    df_table.columns = ["Data", "Cliente", "Vendedor", "Produto", "Status", "MRR (R$)"]
    
    st.dataframe(
        df_table.style.format({{"MRR (R$)": "R$ {:,.2f}"}})
        .applymap(lambda x: f"color: {{CORES['verde']}}; font-weight: bold" if x == "Confirmada" else (f"color: {{CORES['vermelho']}}" if x == "Cancelada" else ""), subset=["Status"]),
        use_container_width=True,
        hide_index=True
    )

    # Rodapé
    st.markdown(f"<p style='text-align: center; color: {{CORES['cinza_subtexto']}}; margin-top: 50px;'>© 2025 Acelerar.tech | Dashboard Comercial V3.0</p>", unsafe_allow_html=True)

else:
    st.error("❌ Erro ao conectar com as fontes de dados. Verifique o acesso às planilhas.")
