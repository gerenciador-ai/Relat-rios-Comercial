import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard de Vendas e Cancelamentos")

# IDs das planilhas Google Sheets
VENDAS_ID = "1df7wNT1XQaiVK38vNdjbQudXkeH-lHTZWoYQ9gikZ0M"
CANCELADOS_ID = "1GDU6qVJ9Gf9C9lwHx2KwOiTltyeUPWhD_y3ODUczuTw"

@st.cache_data(ttl=600) # Atualiza o cache a cada 10 minutos
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url )
        # Normalizar nomes de colunas: remover espaços e colocar em minúsculo
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha {sheet_id}: {e}")
        return pd.DataFrame()

def processar_dados():
    df_vendas = load_data(VENDAS_ID)
    df_cancelados = load_data(CANCELADOS_ID)
    
    if df_vendas.empty:
        return None

    # Mapeamento de colunas esperadas (ajustado para o que está nas suas planilhas)
    # Suas colunas reais: 'vendedor', 'cliente', 'cnpj do cliente', 'plano', 'valor', 'data de ativação'
    
    # Normalizar CNPJ para comparação
    col_cnpj = 'cnpj do cliente'
    if col_cnpj in df_vendas.columns:
        df_vendas['cnpj_norm'] = df_vendas[col_cnpj].astype(str).str.replace(r'\D', '', regex=True)
    if col_cnpj in df_cancelados.columns:
        df_cancelados['cnpj_norm'] = df_cancelados[col_cnpj].astype(str).str.replace(r'\D', '', regex=True)
    
    # Criar coluna de Status
    df_vendas['status'] = 'Confirmada'
    if not df_cancelados.empty and 'cnpj_norm' in df_cancelados.columns:
        cancelados_cnpjs = df_cancelados['cnpj_norm'].unique()
        df_vendas.loc[df_vendas['cnpj_norm'].isin(cancelados_cnpjs), 'status'] = 'Cancelada'
    
    # Converter datas
    col_data = 'data de ativação'
    if col_data in df_vendas.columns:
        df_vendas[col_data] = pd.to_datetime(df_vendas[col_data], errors='coerce', dayfirst=True)
    
    return df_vendas

# Início do Dashboard
df = processar_dados()

if df is not None:
    st.title("📊 Dashboard de Vendas e Cancelamentos")
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Data
    col_data = 'data de ativação'
    data_min = df[col_data].min()
    data_max = df[col_data].max()
    
    if pd.notnull(data_min) and pd.notnull(data_max):
        periodo = st.sidebar.date_input("Período", [data_min, data_max])
    
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
        fig_status = px.bar(df_f['status'].value_counts().reset_index(), x='status', y='count', title="Status das Vendas", color='status')
        st.plotly_chart(fig_status, use_container_width=True)

    # Tabela
    st.subheader("📋 Detalhamento")
    st.dataframe(df_f[['vendedor', 'cliente', 'plano', 'valor', 'data de ativação', 'status']], use_container_width=True)

else:
    st.error("Não foi possível carregar os dados. Verifique se as planilhas estão públicas.")
