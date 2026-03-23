if not st.session_state.usuario_logado or st.session_state.modulo == 'hub':
    st.markdown(f"""
    <style>
        /* 1. Remove o padding padrão do Streamlit e puxa o conteúdo para o topo absoluto */
        .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -5rem !important; /* Puxa o logo e os botões para cima */
        }}

        /* 2. Esconde a decoração superior (elipse/linha) */
        [data-testid="stDecoration"] {{
            display: none !important;
        }}

        /* 3. Esconde os controles de interface (setinha, menu, sidebar) */
        [data-testid="collapsedControl"], 
        [data-testid="stSidebar"], 
        [data-testid="stHeader"], 
        footer {{
            display: none !important;
        }}

        /* 4. Cor de fundo do portal */
        .stApp {{
            background-color: {COLOR_BG};
        }}
    </style>
    """, unsafe_allow_html=True)
