import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard de Vendas e Cancelamentos")

# IDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"

@st.cache_data(ttl=600)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url )
        # Limpar espaços extras nos nomes das colunas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha {sheet_id}: {e}")
        return pd.DataFrame()

def encontrar_coluna(df, termo):
    """Encontra uma coluna que contenha o termo pesquisado (ignora maiúsculas/minúsculas)"""
    for col in df.columns:
        if termo.lower() in col.lower():
            return col
    return None

def processar_dados():
    df_vendas = load_data(VENDAS_ID)
    df_cancelados = load_data(CANCELADOS_ID)
    
    if df_vendas.empty:
        return None

    # Identificar colunas dinamicamente
    col_vendedor = encontrar_coluna(df_vendas, 'vendedor')
    col_cliente = encontrar_coluna(df_vendas, 'cliente')
    col_cnpj = encontrar_coluna(df_vendas, 'cnpj')
    col_plano = encontrar_coluna(df_vendas, 'plano')
    col_valor = encontrar_coluna(df_vendas, 'valor')
    col_data = encontrar_coluna(df_vendas, 'data')

    # Criar um novo DataFrame padronizado para o dashboard
    df_clean = pd.DataFrame()
    df_clean['vendedor'] = df_vendas[col_vendedor] if col_vendedor else "N/A"
    df_clean['cliente'] = df_vendas[col_cliente] if col_cliente else "N/A"
    df_clean['plano'] = df_vendas[col_plano] if col_plano else "N/A"
    df_clean['valor'] = pd.to_numeric(df_vendas[col_valor].replace(r'[R\$\.\s]', '', regex=True).replace(',', '.', regex=True), errors='coerce').fillna(0) if col_valor else 0
    df_clean['data'] = pd.to_datetime(df_vendas[col_data], errors='coerce', dayfirst=True) if col_data else None
    
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
    valor_total = df_f['valor'].sum()
    
    c1.metric("Total de Vendas", vendas_totais)
    c2.metric("Cancelamentos", cancelados)
    c3.metric("Valor Total (R$)", f"R$ {valor_total:,.2f}")
    c4.metric("Taxa de Cancelamento", f"{(cancelados/vendas_totais*100 if vendas_totais > 0 else 0):.1f}%")
    
    st.divider()
    
    # Gráficos
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        fig_plano = px.pie(df_f, names='plano', values='valor', title="Vendas por Plano")
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
    st.error("Não foi possível carregar os dados. Verifique se as planilhas estão públicas.")
