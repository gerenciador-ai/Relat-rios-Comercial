import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página - Estilo Sênior Limpo
st.set_page_config(layout="wide", page_title="Dashboard Comercial Estratégico", page_icon="📊")

# IDs e GIDs das planilhas Google Sheets (agora referenciando VMC Tech)
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M" # Vendas Realizadas_VMC Tech
VENDAS_GID = "1202307787"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw" # Cancelados_VMC Tech
CANCELADOS_GID = "606807719"

# Paleta de cores corporativa Acelerar.tech
CORES = {
    "primaria_escura": "#0B2A4E",      # Azul Marinho
    "primaria_clara": "#89CFF0",       # Azul Claro
    "branco": "#FFFFFF",               # Branco
    "cinza_claro": "#F5F5F5",          # Cinza muito claro (backgrounds)
    "cinza_subtexto": "#6C757D",      # Cinza para subtextos
    "verde_sucesso": "#28A745",        # Verde para sucesso
    "vermelho_perda": "#DC3545",       # Vermelho para perda
    "laranja_alerta": "#FFC107"        # Laranja para alerta
}

# CSS customizado para Streamlit
st.markdown(f"""
<style>
    /* Geral */
    .reportview-container {{ background-color: {CORES["cinza_claro"]}; }}
    .sidebar .sidebar-content {{ background-color: {CORES["primaria_escura"]}; color: {CORES["branco"]}; }}
    .stButton>button {{ background-color: {CORES["primaria_clara"]}; color: {CORES["primaria_escura"]}; border-radius: 5px; border: none; padding: 10px 20px; font-weight: bold; }}
    .stButton>button:hover {{ background-color: {CORES["primaria_escura"]}; color: {CORES["branco"]}; }}
    h1, h2, h3, h4, h5, h6 {{ color: {CORES["primaria_escura"]}; font-family: 'Inter', sans-serif; }}
    p, .stMarkdown {{ color: {CORES["primaria_escura"]}; font-family: 'Inter', sans-serif; }}

    /* Métricas */
    div[data-testid="stMetric"] {{ 
        background-color: {CORES["branco"]};
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid {CORES["primaria_clara"]};
    }}
    div[data-testid="stMetric"] label {{ color: {CORES["primaria_escura"]}; font-size: 1.1em; font-weight: bold; }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: {CORES["primaria_escura"]}; font-size: 2.2em; font-weight: bold; }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{ font-size: 1.2em; font-weight: bold; }}

    /* Churn específico */
    div[data-testid="stMetric"]:nth-child(3) div[data-testid="stMetricValue"] {{ color: {CORES["vermelho_perda"]}; }}
    div[data-testid="stMetric"]:nth-child(3) div[data-testid="stMetricDelta"] {{ color: {CORES["vermelho_perda"]}; }}

    /* Sidebar */
    .css-1d391kg {{ background-color: {CORES["primaria_escura"]}; }}
    .css-1lcbmhc {{ color: {CORES["branco"]}; }}
    .css-pkz32j {{ color: {CORES["branco"]}; }}
    .css-1a3y7a4 {{ color: {CORES["branco"]}; }}
    .css-1v3fvcr {{ color: {CORES["branco"]}; }}
    .css-1l02zno {{ color: {CORES["branco"]}; }}
    .css-1cpxqw2 {{ color: {CORES["branco"]}; }}
    .css-1kyxreq {{ color: {CORES["branco"]}; }}
    .css-1cpxqw2:hover {{ color: {CORES["primaria_clara"]}; }}
    .css-1cpxqw2:focus {{ color: {CORES["primaria_clara"]}; }}
    .css-1cpxqw2:active {{ color: {CORES["primaria_clara"]}; }}

    /* Tabela */
    .dataframe {{ font-family: 'Inter', sans-serif; font-size: 0.9em; }}

</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid: url += f"&gid={gid}"
    try:
        df = pd.read_csv(url )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
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
    df["downgrade"] = parse_currency(df_v["Redução da mensalidade"])

    # Padronização para Formato Americano (Mês/Dia/Ano)
    df["data_h"] = pd.to_datetime(df_v["Data de Ativação"], errors="coerce", dayfirst=False)
    df["data_x"] = pd.to_datetime(df_v["Data alteração de CNPJ"], errors="coerce", dayfirst=False)
    
    df["data"] = df["data_h"]
    df.loc[df["upgrade"] > 0, "data"] = df["data_x"]
    
    df = df.dropna(subset=["data"])
    df["ano"] = df["data"].dt.year.astype(int)
    df["mes_num"] = df["data"].dt.month.astype(int)
    meses_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
                7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
    df["mes_nome"] = df["mes_num"].map(meses_pt)
    df["inicio_semana"] = df["data"].apply(lambda x: x - pd.Timedelta(days=x.weekday()))

    df["status"] = "Confirmada"
    if not df_c.empty:
        canc_cnpjs = df_c["CNPJ do Cliente"].astype(str).str.replace(r"\D", "", regex=True).unique()
        df.loc[df["cnpj"].isin(canc_cnpjs), "status"] = "Cancelada"
    
    return df

# --- UI ---
df = processar_dados()
if df is not None:
    st.title("📊 Dashboard Comercial Estratégico")
    
    st.sidebar.header("🔍 Filtros")
    anos = sorted(df["ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", anos)
    df_ano = df[df["ano"] == ano_sel]
    
    meses_ordem = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    meses_disp = [m for m in meses_ordem if m in df_ano["mes_nome"].unique()]
    meses_sel = st.sidebar.multiselect("Meses", meses_disp, default=meses_disp)
    
    prod_sel = st.sidebar.selectbox("Produto", ["Todos"] + sorted(df["produto"].unique().tolist()))
    vend_sel = st.sidebar.selectbox("Vendedor", ["Todos"] + sorted(df["vendedor"].unique().tolist()))
    sdr_sel = st.sidebar.selectbox("SDR", ["Todos"] + sorted(df["sdr"].unique().tolist()))

    df_f = df_ano[df_ano["mes_nome"].isin(meses_sel)].copy()
    if prod_sel != "Todos": df_f = df_f[df_f["produto"] == prod_sel]
    if vend_sel != "Todos": df_f = df_f[df_f["vendedor"] == vend_sel]
    if sdr_sel != "Todos": df_f = df_f[df_f["sdr"] == sdr_sel]

    # KPIs
    mrr_conq = df_f[df_f["status"] == "Confirmada"]["mrr"].sum()
    mrr_perd = df_f[df_f["status"] == "Cancelada"]["mrr"].sum()
    upsell_v = df_f["upgrade"].sum()
    upsell_q = len(df_f[df_f["upgrade"] > 0])
    cl_fech = len(df_f[(df_f["status"] == "Confirmada") & (df_f["mrr"] > 0)])
    cl_canc = len(df_f[df_f["status"] == "Cancelada"])
    tkt_med = mrr_conq / cl_fech if cl_fech > 0 else 0
    base_ativa = len(df[df["status"] == "Confirmada"]) - len(df[df["status"] == "Cancelada"])
    churn_p = (mrr_perd / mrr_conq * 100) if mrr_conq > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("MRR Conquistado", f"R$ {mrr_conq:,.2f}")
    c2.metric("MRR Ativo (Net)", f"R$ {mrr_conq - mrr_perd:,.2f}")
    c3.metric("MRR Perdido (Churn)", f"R$ {mrr_perd:,.2f}", delta=f"- {churn_p:.1f}%", delta_color="inverse")
    
    c4, c5, c6 = st.columns(3)
    c4.metric("Total de Upsell", f"R$ {upsell_v:,.2f}", delta=f"{upsell_q} eventos")
    c5.metric("Ticket Médio", f"R$ {tkt_med:,.2f}")
    c6.metric("Adesão Total", f"R$ {df_f["adesao"].sum():,.2f}")
    
    c7, c8, c9 = st.columns(3)
    c7.metric("Clientes fechado (no periodo)", cl_fech)
    c8.metric("Clientes Cancelados (no periodo)", cl_canc)
    c9.metric("Total Clientes Ativos (Base)", base_ativa)

    st.divider()
    
    st.subheader("📈 Evolução Mensal")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        df_m = df_ano[df_ano["status"] == "Confirmada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        fig = px.bar(df_m, x="mes_nome", y="mrr", text="cliente", title="MRR Conquistado", color_discrete_sequence=[CORES["primaria_clara"]])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_u = df_ano[df_ano["upgrade"] > 0].groupby(["mes_num","mes_nome"]).agg({"upgrade":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        fig = px.bar(df_u, x="mes_nome", y="upgrade", text="cliente", title="Evolução de Upsell", color_discrete_sequence=[CORES["primaria_escura"]])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        df_c = df_ano[df_ano["status"] == "Cancelada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
        df_c = df_c[df_c["mrr"] > 0]
        fig = px.bar(df_c, x="mes_nome", y="mrr", text="cliente", title="Churn Mensal", color_discrete_sequence=[CORES["vermelho_perda"]])
        fig.update_traces(texttemplate="%{text}", textposition="inside")
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    st.subheader("🎯 Performance vs. Metas")
    col4, col5 = st.columns(2)
    
    df_meta = df_f[df_f["status"] == "Confirmada"].groupby(["mes_num","mes_nome"]).agg({"mrr":"sum", "cliente":"count"}).reset_index().sort_values("mes_num")
    df_meta["mrr_a"] = df_meta["mrr"].cumsum()
    df_meta["cont_a"] = df_meta["cliente"].cumsum()
    df_meta["meta_m"] = [8000 * (i+1) for i in range(len(df_meta))]
    df_meta["meta_c"] = [17 * (i+1) for i in range(len(df_meta))]

    with col4:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["mrr_a"], name="Real", marker_color=CORES["primaria_clara"]))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_m"], name="Meta (8k/mês)", line=dict(color=CORES["primaria_escura"], width=4)))
        fig.update_layout(title="MRR Acumulado vs. Meta", xaxis_title=None, yaxis_title=None, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_meta["mes_nome"], y=df_meta["cont_a"], name="Real", marker_color=CORES["primaria_clara"]))
        fig.add_trace(go.Scatter(x=df_meta["mes_nome"], y=df_meta["meta_c"], name="Meta (17/mês)", line=dict(color=CORES["primaria_escura"], width=4)))
        fig.update_layout(title="Contratos Acumulados vs. Meta", xaxis_title=None, yaxis_title=None, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    col6, col7 = st.columns(2)
    with col6:
        df_s = df_f[df_f["status"] == "Confirmada"].groupby("inicio_semana")["mrr"].sum().reset_index().sort_values("inicio_semana")
        df_s["data_s"] = df_s["inicio_semana"].dt.strftime("%d/%m/%Y")
        fig = go.Figure(go.Scatter(x=df_s["data_s"], y=df_s["mrr"], mode="lines+markers+text", text=df_s["mrr"].apply(lambda x: f"{x:,.0f}"), textposition="top center", line=dict(color=CORES["primaria_escura"], width=4)))
        fig.update_layout(title="MRR SEMANA", xaxis_title=None, yaxis_title=None, showlegend=False, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)
    
    with col7:
        fig = px.pie(df_f, names="produto", values="mrr", title="Receita por Produto", hole=0.4, color_discrete_sequence=[CORES["primaria_escura"], CORES["primaria_clara"], CORES["cinza_subtexto"], CORES["laranja_alerta"]])
        fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("🏆 Ranking de Vendedores")
    col8, col9 = st.columns(2)

    with col8:
        df_vendedores_contratos = df_f[df_f["status"] == "Confirmada"].groupby("vendedor")["cliente"].count().reset_index().sort_values("cliente", ascending=False)
        fig = px.pie(df_vendedores_contratos, names="vendedor", values="cliente", title="Top Vendedores (Contratos)", hole=0.4, color_discrete_sequence=[CORES["primaria_escura"], CORES["primaria_clara"], CORES["cinza_subtexto"], CORES["laranja_alerta"]])
        fig.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}  
%{value}")
        fig.update_layout(showlegend=False, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)

    with col9:
        df_vendedores_mrr = df_f[df_f["status"] == "Confirmada"].groupby("vendedor")["mrr"].sum().reset_index().sort_values("mrr", ascending=False)
        fig = px.pie(df_vendedores_mrr, names="vendedor", values="mrr", title="Top Vendedores (MRR)", hole=0.4, color_discrete_sequence=[CORES["primaria_escura"], CORES["primaria_clara"], CORES["cinza_subtexto"], CORES["laranja_alerta"]])
        fig.update_traces(textinfo="label+value", textposition="inside", texttemplate="%{label}  
R$ %{value:,.2f}")
        fig.update_layout(showlegend=False, plot_bgcolor=CORES["branco"], paper_bgcolor=CORES["branco"], font_color=CORES["primaria_escura"])
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("📋 Detalhamento")
    st.dataframe(
        df_f[["data", "cliente", "vendedor", "produto", "status", "mrr", "upgrade", "adesao"]].sort_values("data", ascending=False)
        .style.applymap(lambda x: f"color: {CORES["vermelho_perda"]}; font-weight: bold;" if x == "Cancelada" else (f"color: {CORES["verde_sucesso"]}; font-weight: bold;" if x == "Confirmada" else ""), subset=["status"])
        .format({"mrr": "R$ {:,.2f}", "upgrade": "R$ {:,.2f}", "adesao": "R$ {:,.2f}"}),
        use_container_width=True,
        hide_index=True
    )

    # Rodapé
    st.markdown(f"<p style=\'text-align: center; color: {CORES["cinza_subtexto"]}; margin-top: 50px;\'>© 2025 Acelerar.tech | Dashboard Comercial V4.0</p>", unsafe_allow_html=True)

else:
    st.error("❌ Erro ao conectar com as fontes de dados. Verifique o acesso às planilhas.")
