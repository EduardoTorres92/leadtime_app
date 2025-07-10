import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import hashlib
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Lead Time por Marca",
    page_icon="📊",
    layout="wide"
)

# 🔐 Sistema de Login com Streamlit Secrets
def hash_password(password):
    """Hash da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_credenciais(usuario, senha):
    """Verifica se as credenciais são válidas usando Streamlit secrets"""
    try:
        # Tenta usar secrets do Streamlit Cloud
        if hasattr(st, 'secrets') and 'auth' in st.secrets:
            usuarios_validos = {
                st.secrets["auth"]["admin_user"]: st.secrets["auth"]["admin_password"],
                st.secrets["auth"]["leadtime_user"]: st.secrets["auth"]["leadtime_password"],
                st.secrets["auth"]["assa_user"]: st.secrets["auth"]["assa_password"],
                st.secrets["auth"]["manager_user"]: st.secrets["auth"]["manager_password"]
            }
        else:
            # Fallback para credenciais hardcoded (desenvolvimento)
            usuarios_validos = {
                "admin": "admin123",
                "leadtime": "leadtime2025",
                "assaabloy": "assa@2025",
                "manager": "manager@123"
            }
        
        return usuario in usuarios_validos and usuarios_validos[usuario] == senha
    
    except Exception as e:
        st.error(f"Erro ao verificar credenciais: {str(e)}")
        return False

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
        
        # Só mostra usuários de teste se não estiver usando secrets
        if not (hasattr(st, 'secrets') and 'auth' in st.secrets):
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

@st.cache_data
def carregar_dados():
    """Carrega e processa os dados do CSV"""
    try:
        df = pd.read_csv('leaditme_base.csv', encoding='utf-8-sig')
        df = df.drop_duplicates(subset=['num_nota_fiscal'], keep='first')
        
        df = df.rename(columns={
            'desc_marca': 'Marca',
            'desc_canal_venda': 'Canal_Venda',
            'dat_embarque': 'Data_Embarque',
            'dat_emissao_nf': 'Data_Emissao_NF',
            'nom_cidade': 'Cidade'
        })
        
        df['Data_Embarque'] = pd.to_datetime(df['Data_Embarque'])
        df['Data_Emissao_NF'] = pd.to_datetime(df['Data_Emissao_NF'])
        df['Data_Embarque'] = df['Data_Embarque'].fillna(df['Data_Emissao_NF'])
        
        marcas_principais = ['PAPAIZ', 'LA FONTE', 'SILVANA CD SP']
        df = df[df['Marca'].isin(marcas_principais)]
        
        df['Data'] = df['Data_Emissao_NF'].dt.date
        
        def agrupar_canal(canal):
            if 'WEBSHOP' in canal.upper():
                return 'WEBSHOP'
            elif 'HOME CENTER' in canal.upper():
                return 'HOME CENTER'
            else:
                return 'DEMAIS CANAIS'
        
        df['Canal_Agrupado'] = df['Canal_Venda'].apply(agrupar_canal)
        
        def calcular_leadtime_excel(row):
            data_emissao = row['Data_Emissao_NF']
            data_embarque = row['Data_Embarque']
            
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
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# MAIN APP
def main():
    if not verificar_sessao():
        return

    header_com_logout()
    st.markdown("---")
    
    # Carregar dados
    with st.spinner('Carregando dados...'):
        df = carregar_dados()
    
    if df.empty:
        st.error("❌ Não foi possível carregar os dados ou não há dados válidos.")
        st.stop()
    
    # Informações básicas dos dados
    st.success(f"✅ Dados carregados com sucesso!")
    
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
    
    marcas_disponiveis = ['PAPAIZ', 'LA FONTE', 'SILVANA CD SP']
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
    
    # Exibir gráficos
    st.header("📈 Análises de Lead Time")
    
    # Calcular estatísticas
    stats_gerais = df_filtrado.groupby('Marca').agg({
        'LeadTime_Dias': ['count', 'mean', 'median', 'std', 'min', 'max']
    })
    stats_gerais.columns = ['Total_Registros', 'LeadTime_Medio', 'LeadTime_Mediano', 
                           'Desvio_Padrao', 'LeadTime_Min', 'LeadTime_Max']
    stats_gerais = stats_gerais.reset_index()
    
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
    
    # Rodapé informativo
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        <p>🔐 Sistema com autenticação segura | 📊 Dashboard Lead Time por Marca</p>
        <p>Versão com suporte a Streamlit Secrets para produção segura</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 