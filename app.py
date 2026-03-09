import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard de Vendas e Cancelamentos")

# IDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
VENDAS_GID = "1202307787" # GID da aba 'Base de Dados'
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"
CANCELADOS_GID = "606807719" # GID da aba 'Cancelados'

@st.cache_data(ttl=600)
def load_data(sheet_id, gid=None):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid is not None:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        # Limpar espaços extras nos nomes das colunas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha {sheet_id} (GID: {gid}): {e}")
        return pd.DataFrame()

def encontrar_coluna(df, termo):
    """Encontra uma coluna que contenha o termo pesquisado (ignora maiúsculas/minúsculas)"""
    for col in df.columns:
        if termo.lower() in col.lower():
            return col
    return None

def parse_currency(series):
    """Converte uma série de strings de moeda brasileira para float"""
    # Remove 'R$', pontos de milhar e substitui vírgula decimal por ponto
    return pd.to_numeric(
        series.astype(str)
        .str.replace(r'[R$]', '', regex=True)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)

def processar_dados():
    df_vendas = load_data(VENDAS_ID, gid=VENDAS_GID)
    df_cancelados = load_data(CANCELADOS_ID, gid=CANCELADOS_GID)
    
    if df_vendas.empty:
        return None

    # Identificar colunas dinamicamente
    col_vendedor = encontrar_coluna(df_vendas, 'vendedor')
    col_cliente = encontrar_coluna(df_vendas, 'cliente')
    col_cnpj = encontrar_coluna(df_vendas, 'cnpj')
    col_plano = encontrar_coluna(df_vendas, 'plano')
    col_data = encontrar_coluna(df_vendas, 'data')

    # Novas colunas de métricas
    col_mrr_simples = encontrar_coluna(df_vendas, 'Mensalidade - Simples')
    col_adesao_simples = encontrar_coluna(df_vendas, 'Adesão - Simples')
    col_adesao_recupera = encontrar_coluna(df_vendas, 'Adesão - Recupera')
    col_aumento_mensalidade = encontrar_coluna(df_vendas, 'Aumento da mensalidade')
    col_reducao_mensalidade = encontrar_coluna(df_vendas, 'Redução da mensalidade')

    # Criar um novo DataFrame padronizado para o dashboard
    df_clean = pd.DataFrame()
    df_clean['vendedor'] = df_vendas[col_vendedor] if col_vendedor else "N/A"
    df_clean['cliente'] = df_vendas[col_cliente] if col_cliente else "N/A"
    df_clean['plano'] = df_vendas[col_plano] if col_plano else "N/A"
    df_clean['data'] = pd.to_datetime(df_vendas[col_data], errors='coerce', dayfirst=True) if col_data else None

    # Processar as novas colunas de métricas
    df_clean['mrr_simples'] = parse_currency(df_vendas[col_mrr_simples]) if col_mrr_simples else 0.0
    df_clean['adesao_simples'] = parse_currency(df_vendas[col_adesao_simples]) if col_adesao_simples else 0.0
    df_clean['adesao_recupera'] = parse_currency(df_vendas[col_adesao_recupera]) if col_adesao_recupera else 0.0
    df_clean['aumento_mensalidade'] = parse_currency(df_vendas[col_aumento_mensalidade]) if col_aumento_mensalidade else 0.0
    df_clean['reducao_mensalidade'] = parse_currency(df_vendas[col_reducao_mensalidade]) if col_reducao_mensalidade else 0.0

    # Calcular o valor total para gráficos e KPIs que usam 'valor'
    df_clean['valor_total_venda'] = df_clean['mrr_simples'] + df_clean['adesao_simples'] + df_clean['adesao_recupera']

    # Normalizar CNPJ para cruzamento com cancelados
    if col_cnpj:
        df_vendas['cnpj_norm'] = df_vendas[col_cnpj].astype(str).str.replace(r'\D', '', regex=True)
        
        # Processar cancelados
        df_clean['status'] = 'Confirmada'
        if not df_cancelados.empty:
            col_cnpj_canc = encontrar_coluna(df_cancelados, 'cnpj')
            if col_cnpj_canc:
                df_cancelados['cnpj_norm'] = df_cancelados[col_cnpj_canc].astype(str).str.replace(r'\D', '', regex=True)
                cancelados_cnpjs = df_cancelados['cnpj_norm'].unique()
                df_clean.loc[df_vendas['cnpj_norm'].isin(cancelados_cnpjs), 'status'] = 'Cancelada'
    else:
        df_clean['status'] = 'Confirmada'
    
    return df_clean

# Início do Dashboard
df = processar_dados()

if df is not None:
    st.title("📊 Dashboard de Vendas e Cancelamentos")
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Vendedor
    vendedores = ["Todos"] + sorted(df['vendedor'].unique().tolist())
    vendedor_sel = st.sidebar.selectbox("Vendedor", vendedores)
    
    # Aplicar Filtros
    df_f = df.copy()
    if vendedor_sel != "Todos":
        df_f = df_f[df_f['vendedor'] == vendedor_sel]
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    vendas_totais = len(df_f)
    cancelados = len(df_f[df_f['status'] == 'Cancelada'])
    
    # Novos KPIs baseados nas métricas definidas
    mrr_total = df_f['mrr_simples'].sum()
    adesao_total = df_f['adesao_simples'].sum() + df_f['adesao_recupera'].sum()
    saldo_up_downgrade = df_f['aumento_mensalidade'].sum() - df_f['reducao_mensalidade'].sum()
    
    c1.metric("Total de Vendas", vendas_totais)
    c2.metric("Cancelamentos", cancelados)
    c3.metric("MRR Total (R$)", f"R$ {mrr_total:,.2f}")
    c4.metric("Adesão Total (R$)", f"R$ {adesao_total:,.2f}")

    st.markdown(f"**Saldo Upgrade/Downgrade (R$):** R$ {saldo_up_downgrade:,.2f}")
    
    st.divider()
    
    # Gráficos
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        fig_plano = px.pie(df_f, names='plano', values='valor_total_venda', title="Vendas por Plano")
        st.plotly_chart(fig_plano, use_container_width=True)
        
    with col_dir:
        # Gráfico de Status
        status_counts = df_f['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'quantidade']
        fig_status = px.bar(status_counts, x='status', y='quantidade', title="Status das Vendas", color='status')
        st.plotly_chart(fig_status, use_container_width=True)

    # Tabela
    st.subheader("📋 Detalhamento")
    st.dataframe(df_f, use_container_width=True)

else:
    st.error("Não foi possível carregar os dados. Verifique se as planilhas estão públicas e os GIDs corretos.")
