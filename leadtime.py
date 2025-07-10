import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import openai
import json
import hashlib
import io
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Lead Time por Marca",
    page_icon="📊",
    layout="wide"
)

# 🔐 Sistema de Login
def hash_password(password):
    """Hash da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_credenciais(usuario, senha):
    """Verifica se as credenciais são válidas"""
    usuarios_validos = {
        "admin": hash_password("admin123"),
        "leadtime": hash_password("leadtime2024"),
        "assa": hash_password("assa@2024"),
        "manager": hash_password("manager@123")
    }
    
    senha_hash = hash_password(senha)
    return usuario in usuarios_validos and usuarios_validos[usuario] == senha_hash

def interface_login():
    """Interface de login"""
    st.markdown("""
    <div style="max-width: 400px; margin: 0 auto; padding: 2rem; border: 1px solid #ddd; border-radius: 10px; margin-top: 5rem;">
        <h2 style="text-align: center; color: #333;">🔐 Login - Dashboard Lead Time</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Acesso Restrito")
        st.markdown("Digite suas credenciais para acessar o dashboard:")
        
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                submit_button = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
            
            if submit_button:
                if usuario and senha:
                    if verificar_credenciais(usuario, senha):
                        st.session_state.logged_in = True
                        st.session_state.username = usuario
                        st.session_state.login_time = datetime.now()
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
                else:
                    st.warning("⚠️ Por favor, preencha todos os campos!")
        
        with st.expander("ℹ️ Usuários de Teste"):
            st.markdown("""
            **Usuários disponíveis:**
            - `admin` / `admin123`
            - `leadtime` / `leadtime2024`
            - `assa` / `assa@2024`
            - `manager` / `manager@123`
            """)

def logout():
    """Função para fazer logout"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.login_time = None
    if 'uploaded_data' in st.session_state:
        del st.session_state.uploaded_data
    st.rerun()

def header_com_logout():
    """Cabeçalho com informações do usuário e botão de logout"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title('📊 Dashboard Lead Time por Marca')
        if st.session_state.get('username'):
            tempo_logado = datetime.now() - st.session_state.login_time
            horas = int(tempo_logado.total_seconds() // 3600)
            minutos = int((tempo_logado.total_seconds() % 3600) // 60)
            st.markdown(f"*Usuário: **{st.session_state.username}** | Sessão: {horas}h {minutos}min*")
    
    with col2:
        st.markdown("")
        st.markdown("")
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()

def verificar_sessao():
    """Verifica se o usuário está logado"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        interface_login()
        return False
    
    return True

def interface_upload():
    """Interface para upload do arquivo CSV"""
    st.markdown("### 📁 Upload do Arquivo de Dados")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Selecione o arquivo CSV com os dados de Lead Time",
            type=['csv'],
            help="Faça upload do arquivo 'leaditme_base.csv' ou similar com os dados de lead time."
        )
        
        if uploaded_file is not None:
            # Salvar o arquivo na sessão
            st.session_state.uploaded_file = uploaded_file
            st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
            
            # Mostrar informações do arquivo
            file_details = {
                "Nome": uploaded_file.name,
                "Tamanho": f"{uploaded_file.size / 1024:.1f} KB",
                "Tipo": uploaded_file.type
            }
            
            with st.expander("ℹ️ Detalhes do Arquivo"):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")
    
    with col2:
        st.markdown("#### 📋 Formato Esperado")
        st.markdown("""
        **Colunas necessárias:**
        - `desc_marca`
        - `desc_canal_venda`
        - `dat_embarque`
        - `dat_emissao_nf`
        - `nom_cidade`
        - `num_nota_fiscal`
        """)
        
        st.markdown("#### 📊 Marcas Suportadas")
        st.markdown("""
        - PAPAIZ
        - LA FONTE
        - SILVANA CD SP
        """)
    
    return uploaded_file

def carregar_dados(uploaded_file=None):
    """Carrega e processa os dados do CSV"""
    try:
        # Tentar carregar de arquivo carregado primeiro
        if uploaded_file is not None:
            # Reset do ponteiro do arquivo
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            data_source = f"arquivo carregado '{uploaded_file.name}'"
        else:
            # Fallback para arquivo local (desenvolvimento)
            try:
                df = pd.read_csv('leaditme_base.csv', encoding='utf-8-sig')
                data_source = "arquivo local 'leaditme_base.csv'"
            except FileNotFoundError:
                return pd.DataFrame(), "Nenhum arquivo encontrado. Faça upload do arquivo CSV."
        
        # Verificar se o DataFrame não está vazio
        if df.empty:
            return pd.DataFrame(), "O arquivo carregado está vazio."
        
        # Verificar colunas necessárias
        colunas_necessarias = ['desc_marca', 'desc_canal_venda', 'dat_embarque', 'dat_emissao_nf', 'nom_cidade', 'num_nota_fiscal']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            return pd.DataFrame(), f"Colunas faltantes no arquivo: {', '.join(colunas_faltantes)}"
        
        # Remove duplicados baseado na coluna NUM_NOTA_FISCAL
        df_original_size = len(df)
        df = df.drop_duplicates(subset=['num_nota_fiscal'], keep='first')
        duplicados_removidos = df_original_size - len(df)
        
        # Renomear colunas
        df = df.rename(columns={
            'desc_marca': 'Marca',
            'desc_canal_venda': 'Canal_Venda',
            'dat_embarque': 'Data_Embarque',
            'dat_emissao_nf': 'Data_Emissao_NF',
            'nom_cidade': 'Cidade'
        })
        
        # Converter datas
        df['Data_Embarque'] = pd.to_datetime(df['Data_Embarque'], errors='coerce')
        df['Data_Emissao_NF'] = pd.to_datetime(df['Data_Emissao_NF'], errors='coerce')
        
        # Verificar se há datas inválidas
        datas_invalidas = df['Data_Emissao_NF'].isna().sum()
        if datas_invalidas > 0:
            st.warning(f"⚠️ {datas_invalidas} registros com datas inválidas foram encontrados.")
        
        # Remover registros com datas inválidas
        df = df.dropna(subset=['Data_Emissao_NF'])
        
        # Preencher datas de embarque vazias com data de emissão da NF
        df['Data_Embarque'] = df['Data_Embarque'].fillna(df['Data_Emissao_NF'])
        
        # Filtrar apenas as 3 marcas principais
        marcas_principais = ['PAPAIZ', 'LA FONTE', 'SILVANA CD SP']
        df_antes_filtro = len(df)
        df = df[df['Marca'].isin(marcas_principais)]
        registros_filtrados = df_antes_filtro - len(df)
        
        if df.empty:
            return pd.DataFrame(), "Nenhum registro encontrado para as marcas suportadas (PAPAIZ, LA FONTE, SILVANA CD SP)."
        
        # Criar coluna de data usando data de emissão da nota fiscal
        df['Data'] = df['Data_Emissao_NF'].dt.date
        
        # Criar coluna de canal agrupado
        def agrupar_canal(canal):
            if pd.isna(canal):
                return 'DEMAIS CANAIS'
            if 'WEBSHOP' in str(canal).upper():
                return 'WEBSHOP'
            elif 'HOME CENTER' in str(canal).upper():
                return 'HOME CENTER'
            else:
                return 'DEMAIS CANAIS'
        
        df['Canal_Agrupado'] = df['Canal_Venda'].apply(agrupar_canal)
        
        def calcular_leadtime_excel(row):
            data_emissao = row['Data_Emissao_NF']
            data_embarque = row['Data_Embarque']
            
            if pd.isna(data_emissao) or pd.isna(data_embarque):
                return 0
            
            if data_emissao.date() == data_embarque.date():
                return 0
            
            dia_semana_emissao = data_emissao.weekday()
            dec = 0 if dia_semana_emissao == 6 or dia_semana_emissao == 0 else 1
            
            try:
                dias_uteis = np.busday_count(data_embarque.date(), data_emissao.date())
                leadtime = dias_uteis - dec
                return max(0, leadtime)
            except:
                return 0
        
        df['LeadTime_Dias'] = df.apply(calcular_leadtime_excel, axis=1)
        
        # Mensagem de sucesso com estatísticas
        mensagem_sucesso = f"""
        ✅ Dados processados com sucesso de {data_source}!
        - **Registros processados:** {len(df):,}
        - **Duplicados removidos:** {duplicados_removidos:,}
        - **Registros filtrados:** {registros_filtrados:,}
        - **Marcas encontradas:** {', '.join(df['Marca'].unique())}
        """
        
        return df, mensagem_sucesso
        
    except Exception as e:
        return pd.DataFrame(), f"❌ Erro ao processar arquivo: {str(e)}"

# 🔵 Cores por marca padronizadas
cores_marca = {
    "PAPAIZ": "blue",
    "LA FONTE": "darkred",
    "SILVANA CD SP": "orange",
    "YALE": "yellow",
    "VAULT": "gray",
    "Total": "darkgreen",
}

# 🟡 Cores por canal de venda
cores_canal = {
    "WEBSHOP": "#1f77b4",
    "HOME CENTER": "#ff7f0e",
    "DEMAIS CANAIS": "#2ca02c"
}

# 🤖 Configuração do Agente de IA
openai.api_key = "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"

# MAIN APP
def main():
    if not verificar_sessao():
        return

    header_com_logout()
    st.markdown("---")
    
    # Interface de upload
    uploaded_file = interface_upload()
    
    # Só continua se houver arquivo carregado ou arquivo local disponível
    if uploaded_file is None and 'uploaded_file' not in st.session_state:
        st.info("👆 Por favor, faça upload do arquivo CSV para continuar.")
        st.stop()
    
    # Usar arquivo da sessão se disponível
    file_to_use = st.session_state.get('uploaded_file', uploaded_file)
    
    # Carregar dados
    with st.spinner('🔄 Processando dados...'):
        df, mensagem = carregar_dados(file_to_use)
    
    if df.empty:
        st.error(mensagem)
        st.stop()
    
    # Mostrar mensagem de sucesso
    st.success(mensagem)
    
    # Informações básicas dos dados
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Registros", f"{len(df):,}")
    with col2:
        st.metric("Lead Time Médio Geral", f"{df['LeadTime_Dias'].mean():.2f} dias")
    with col3:
        st.metric("Número de Marcas", df['Marca'].nunique())
    with col4:
        st.metric("Período", f"{df['Data'].min()} a {df['Data'].max()}")
    
    st.markdown("---")
    
    # Filtros na sidebar
    st.sidebar.header("🔧 Filtros")
    
    data_min = df['Data'].min()
    data_max = df['Data'].max()
    
    data_inicio = st.sidebar.date_input(
        "Data Início",
        value=data_min,
        min_value=data_min,
        max_value=data_max
    )
    
    data_fim = st.sidebar.date_input(
        "Data Fim", 
        value=data_max,
        min_value=data_min,
        max_value=data_max
    )
    
    marcas_disponiveis = sorted(df['Marca'].unique())
    marcas_selecionadas = st.sidebar.multiselect(
        "Selecionar Marcas",
        options=marcas_disponiveis,
        default=marcas_disponiveis
    )
    
    canais_disponiveis = sorted(df['Canal_Agrupado'].unique())
    canais_selecionados = st.sidebar.multiselect(
        "Selecionar Canais de Venda",
        options=canais_disponiveis,
        default=canais_disponiveis
    )
    
    # Aplicar filtros
    df_filtrado = df[
        (df['Data'] >= data_inicio) &
        (df['Data'] <= data_fim) &
        (df['Marca'].isin(marcas_selecionadas)) &
        (df['Canal_Agrupado'].isin(canais_selecionados))
    ]
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados.")
        st.stop()
    
    # Mostrar dados filtrados na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dados Filtrados")
    st.sidebar.metric("Registros", f"{len(df_filtrado):,}")
    st.sidebar.metric("Lead Time Médio", f"{df_filtrado['LeadTime_Dias'].mean():.2f} dias")
    
    # Exibir gráficos
    st.header("📈 Análises de Lead Time")
    
    # Calcular estatísticas
    stats_gerais = df_filtrado.groupby('Marca').agg({
        'LeadTime_Dias': ['count', 'mean', 'median', 'std', 'min', 'max']
    })
    stats_gerais.columns = ['Total_Registros', 'LeadTime_Medio', 'LeadTime_Mediano', 
                           'Desvio_Padrao', 'LeadTime_Min', 'LeadTime_Max']
    stats_gerais = stats_gerais.reset_index()
    
    # Calcular estatísticas diárias
    stats_diarias = df_filtrado.groupby(['Data', 'Marca']).agg({
        'LeadTime_Dias': ['count', 'mean']
    })
    stats_diarias.columns = ['Total_Registros', 'LeadTime_Medio']
    stats_diarias = stats_diarias.reset_index()
    
    # Gráfico principal
    st.subheader("Lead Time Médio por Marca")
    if not stats_gerais.empty:
        # Calcular total geral
        total_geral = df_filtrado['LeadTime_Dias'].mean()
        stats_com_total = stats_gerais.copy()
        linha_total = pd.DataFrame({
            'Marca': ['Total'],
            'Total_Registros': [len(df_filtrado)],
            'LeadTime_Medio': [total_geral],
            'LeadTime_Mediano': [df_filtrado['LeadTime_Dias'].median()],
            'Desvio_Padrao': [df_filtrado['LeadTime_Dias'].std()],
            'LeadTime_Min': [df_filtrado['LeadTime_Dias'].min()],
            'LeadTime_Max': [df_filtrado['LeadTime_Dias'].max()]
        })
        stats_com_total = pd.concat([stats_com_total, linha_total], ignore_index=True)
        
        fig_geral = px.bar(
            stats_com_total,
            x='Marca',
            y='LeadTime_Medio',
            title='Lead Time Médio por Marca',
            labels={'LeadTime_Medio': 'Lead Time (dias)', 'Marca': 'Marca'},
            text='LeadTime_Medio',
            color='Marca',
            color_discrete_map=cores_marca
        )
        fig_geral.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_geral.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_geral, use_container_width=True)
    
    # Gráfico temporal
    st.subheader("TMO Expedição Diário por Marca - Barras Agrupadas")
    if not stats_diarias.empty:
        # Função para criar gráfico temporal
        def criar_grafico_linha_temporal(stats_diarias):
            """Cria gráfico de barras agrupadas temporal por marca"""
            
            # Converter Data para datetime se não for
            if not pd.api.types.is_datetime64_any_dtype(stats_diarias['Data']):
                stats_diarias = stats_diarias.copy()
                stats_diarias['Data'] = pd.to_datetime(stats_diarias['Data'])
            
            # Converter Data para string para melhor visualização
            stats_diarias = stats_diarias.copy()
            stats_diarias['Data_Str'] = stats_diarias['Data'].dt.strftime('%d/%m')
            
            fig = px.bar(
                stats_diarias,
                x='Data_Str',
                y='LeadTime_Medio',
                color='Marca',
                color_discrete_map=cores_marca,
                title='Tempo Médio de Operação (TMO) - Expedição por Dia e Marca',
                labels={
                    'Data_Str': 'Data',
                    'LeadTime_Medio': 'TMO Médio (dias)',
                    'Marca': 'Marca'
                },
                barmode='group',
                text='LeadTime_Medio'
            )
            
            # Formatar valores no texto das barras
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=12)
            
            # Ajustar layout
            fig.update_layout(
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12)
                ),
                xaxis_title='Data',
                yaxis_title='TMO Médio (dias)',
                title_font_size=16,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                font=dict(size=11),
                xaxis=dict(tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=10)),
                bargap=0.2,
                bargroupgap=0.1
            )
            
            return fig
        
        fig_temporal = criar_grafico_linha_temporal(stats_diarias)
        st.plotly_chart(fig_temporal, use_container_width=True)
    else:
        st.warning("Não há dados suficientes para este gráfico.")
    
    # Gráfico boxplot
    st.subheader("Distribuição do Lead Time por Marca")
    fig_boxplot = px.box(
        df_filtrado,
        x='Marca',
        y='LeadTime_Dias',
        title='Distribuição do Lead Time por Marca',
        labels={'LeadTime_Dias': 'Lead Time (dias)', 'Marca': 'Marca'},
        color='Marca',
        color_discrete_map=cores_marca
    )
    fig_boxplot.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig_boxplot, use_container_width=True)
    
    # Análise por canal
    if len(canais_selecionados) > 1:
        st.subheader("Lead Time Médio por Canal de Venda")
        canal_stats = df_filtrado.groupby('Canal_Agrupado')['LeadTime_Dias'].agg(['count', 'mean'])
        canal_stats.columns = ['Total_Registros', 'LeadTime_Medio']
        canal_stats = canal_stats.reset_index().sort_values('LeadTime_Medio', ascending=False)
        
        fig_canal = px.bar(
            canal_stats,
            x='Canal_Agrupado',
            y='LeadTime_Medio',
            title='Lead Time Médio por Canal de Venda',
            labels={'LeadTime_Medio': 'Lead Time Médio (dias)', 'Canal_Agrupado': 'Canal de Venda'},
            text='LeadTime_Medio',
            color='Canal_Agrupado',
            color_discrete_map=cores_canal
        )
        fig_canal.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_canal.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_canal, use_container_width=True)
    
    # Tabelas de dados
    st.header("📋 Tabelas de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estatísticas por Marca")
        if not stats_gerais.empty:
            stats_display = stats_gerais.copy()
            stats_display['LeadTime_Medio'] = stats_display['LeadTime_Medio'].map('{:.2f}'.format)
            stats_display['LeadTime_Mediano'] = stats_display['LeadTime_Mediano'].map('{:.2f}'.format)
            stats_display['Desvio_Padrao'] = stats_display['Desvio_Padrao'].map('{:.2f}'.format)
            stats_display['LeadTime_Min'] = stats_display['LeadTime_Min'].map('{:.2f}'.format)
            stats_display['LeadTime_Max'] = stats_display['LeadTime_Max'].map('{:.2f}'.format)
            st.dataframe(stats_display, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Maiores Lead Times")
        if len(df_filtrado) > 0:
            top_leadtimes = df_filtrado.nlargest(10, 'LeadTime_Dias')[
                ['Marca', 'Data_Emissao_NF', 'Data_Embarque', 'LeadTime_Dias', 'Canal_Agrupado', 'Cidade']
            ]
            st.dataframe(top_leadtimes, use_container_width=True)
    
    # Opção para baixar dados filtrados
    if len(df_filtrado) > 0:
        st.markdown("---")
        st.subheader("📥 Download dos Dados")
        
        # Preparar dados para download
        df_download = df_filtrado.copy()
        df_download['Data_Emissao_NF'] = df_download['Data_Emissao_NF'].dt.strftime('%d/%m/%Y')
        df_download['Data_Embarque'] = df_download['Data_Embarque'].dt.strftime('%d/%m/%Y')
        df_download['Data'] = df_download['Data'].astype(str)
        
        csv_buffer = io.StringIO()
        df_download.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📊 Baixar dados filtrados (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"leadtime_filtrado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Baixa os dados atualmente filtrados em formato CSV"
        )

if __name__ == "__main__":
    main() 