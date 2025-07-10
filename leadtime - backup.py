import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import openai
import json
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Lead Time por Marca",
    page_icon="📊",
    layout="wide"
)

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
    "WEBSHOP": "#1f77b4",      # Azul
    "HOME CENTER": "#ff7f0e",   # Laranja
    "DEMAIS CANAIS": "#2ca02c"  # Verde
}

st.title('📊 Dashboard Lead Time por Marca')
st.markdown("---")

# 🤖 Configuração do Agente de IA
openai.api_key = "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"

def preparar_contexto_dados(df, stats_gerais):
    """Prepara o contexto dos dados para o agente de IA"""
    try:
        # Resumo geral dos dados
        total_registros = len(df)
        periodo = f"{df['Data'].min()} a {df['Data'].max()}"
        leadtime_geral = df['LeadTime_Dias'].mean()
        
        # Estatísticas por marca
        contexto_marcas = []
        for _, row in stats_gerais.iterrows():
            marca = row['Marca']
            contexto_marcas.append({
                "marca": marca,
                "total_registros": int(row['Total_Registros']),
                "leadtime_medio": round(float(row['LeadTime_Medio']), 2),
                "leadtime_mediano": round(float(row['LeadTime_Mediano']), 2),
                "desvio_padrao": round(float(row['Desvio_Padrao']), 2),
                "leadtime_min": round(float(row['LeadTime_Min']), 2),
                "leadtime_max": round(float(row['LeadTime_Max']), 2)
            })
        
        # Análise por canal de venda agrupado
        canais = df.groupby('Canal_Agrupado')['LeadTime_Dias'].agg(['count', 'mean']).reset_index()
        contexto_canais = []
        for _, row in canais.iterrows():
            contexto_canais.append({
                "canal": row['Canal_Agrupado'],
                "total_registros": int(row['count']),
                "leadtime_medio": round(float(row['mean']), 2)
            })
        
        # Top 5 maiores lead times
        top_leadtimes = df.nlargest(5, 'LeadTime_Dias')[
            ['Marca', 'LeadTime_Dias', 'Canal_Agrupado', 'Cidade']
        ].to_dict('records')
        
        contexto = {
            "resumo_geral": {
                "total_registros": total_registros,
                "periodo": periodo,
                "leadtime_medio_geral": round(float(leadtime_geral), 2),
                "numero_marcas": df['Marca'].nunique(),
                "marcas_disponiveis": df['Marca'].unique().tolist()
            },
            "estatisticas_por_marca": contexto_marcas,
            "analise_por_canal": contexto_canais,
            "top_leadtimes": top_leadtimes,
            "observacoes": [
                "Lead Time é calculado em dias úteis entre data de embarque e data de emissão da NF",
                "Fórmula baseada na função DIATRABALHOTOTAL do Excel",
                "Excluídos finais de semana do cálculo",
                "Dados filtrados para as 3 marcas principais: PAPAIZ, LA FONTE, SILVANA CD SP"
            ]
        }
        
        return json.dumps(contexto, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return f"Erro ao preparar contexto: {str(e)}"

def consultar_agente_ia(pergunta, contexto_dados):
    """Consulta o agente de IA com contexto dos dados"""
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        prompt_sistema = """Você é um especialista em análise de dados de Lead Time e logística. 
        Você tem acesso aos dados atuais do dashboard e deve fornecer análises precisas e insights baseados nos dados fornecidos.
        
        Instruções:
        - Sempre responda em português brasileiro
        - Base suas respostas APENAS nos dados fornecidos no contexto
        - Forneça análises precisas com números exatos
        - Sugira melhorias operacionais quando apropriado
        - Use uma linguagem técnica mas acessível
        - Inclua comparações entre marcas quando relevante
        - Destaque outliers ou padrões importantes
        """
        
        prompt_usuario = f"""
        CONTEXTO DOS DADOS ATUAIS:
        {contexto_dados}
        
        PERGUNTA DO USUÁRIO:
        {pergunta}
        
        Por favor, forneça uma análise detalhada baseada exclusivamente nos dados fornecidos acima.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ Erro ao consultar IA: {str(e)}"

def criar_interface_chat():
    """Cria a interface de chat no sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Assistente de IA")
    st.sidebar.markdown("*Faça perguntas sobre os dados*")
    
    # Inicializar histórico de chat se não existir
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Exemplos de perguntas
    with st.sidebar.expander("💡 Exemplos de Perguntas"):
        st.markdown("""
        • Qual marca tem o melhor desempenho?
        • Por que PAPAIZ tem lead time menor?
        • Há outliers nos dados?
        • Quais canais são mais eficientes?
        • Existe sazonalidade nos dados?
        • Como melhorar o lead time?
        """)
    
    # Input para nova pergunta
    pergunta = st.sidebar.text_area(
        "Sua pergunta:",
        placeholder="Ex: Qual marca tem o maior lead time e por quê?",
        height=80,
        key="pergunta_input"
    )
    
    return pergunta

@st.cache_data
def carregar_dados():
    """Carrega e processa os dados do CSV"""
    try:
        # Lê o arquivo CSV
        df = pd.read_csv('leaditme_base.csv', encoding='utf-8-sig')
        
        # Remove duplicados baseado na coluna NUM_NOTA_FISCAL
        df = df.drop_duplicates(subset=['num_nota_fiscal'], keep='first')
        
        # Renomear colunas
        df = df.rename(columns={
            'desc_marca': 'Marca',
            'desc_canal_venda': 'Canal_Venda',
            'dat_embarque': 'Data_Embarque',
            'dat_emissao_nf': 'Data_Emissao_NF',
            'nom_cidade': 'Cidade'
        })
        
        # Converter datas
        df['Data_Embarque'] = pd.to_datetime(df['Data_Embarque'])
        df['Data_Emissao_NF'] = pd.to_datetime(df['Data_Emissao_NF'])
        
        # Preencher datas de embarque vazias com data de emissão da NF
        df['Data_Embarque'] = df['Data_Embarque'].fillna(df['Data_Emissao_NF'])
        
        # Filtrar apenas as 3 marcas principais
        marcas_principais = ['PAPAIZ', 'LA FONTE', 'SILVANA CD SP']
        df = df[df['Marca'].isin(marcas_principais)]
        
        # Criar coluna de data usando data de emissão da nota fiscal
        df['Data'] = df['Data_Emissao_NF'].dt.date
        
        # Criar coluna de canal agrupado
        def agrupar_canal(canal):
            if 'WEBSHOP' in canal.upper():
                return 'WEBSHOP'
            elif 'HOME CENTER' in canal.upper():
                return 'HOME CENTER'
            else:
                return 'DEMAIS CANAIS'
        
        df['Canal_Agrupado'] = df['Canal_Venda'].apply(agrupar_canal)
        
        # Calcular lead time usando a função do Excel
        df['LeadTime_Dias'] = df.apply(calcular_leadtime_excel, axis=1)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def calcular_leadtime_excel(row):
    """Calcular lead time usando a fórmula do Excel"""
    data_emissao = row['Data_Emissao_NF']
    data_embarque = row['Data_Embarque']
    
    # Se as datas são iguais, lead time = 0
    if data_emissao.date() == data_embarque.date():
        return 0
    
    # Calcular dec: se dia da semana da emissão NF for domingo (6) ou segunda (0), dec = 0, senão dec = 1
    dia_semana_emissao = data_emissao.weekday()  # 0=segunda, 6=domingo
    if dia_semana_emissao == 6 or dia_semana_emissao == 0:  # domingo ou segunda
        dec = 0
    else:
        dec = 1
    
    # Calcular dias úteis do embarque até a emissão (como na fórmula Excel original)
    try:
        # DIATRABALHOTOTAL(L3;N3) = de embarque até emissão
        dias_uteis = np.busday_count(data_embarque.date(), data_emissao.date())
        leadtime = dias_uteis - dec
        return max(0, leadtime)  # Garantir que não seja negativo
    except:
        return 0

def calcular_estatisticas_gerais(df):
    """Calcula estatísticas gerais por marca"""
    stats = df.groupby('Marca').agg({
        'LeadTime_Dias': ['count', 'mean', 'median', 'std', 'min', 'max']
    })
    
    # Flatten column names
    stats.columns = ['Total_Registros', 'LeadTime_Medio', 'LeadTime_Mediano', 
                     'Desvio_Padrao', 'LeadTime_Min', 'LeadTime_Max']
    
    return stats.reset_index()

def calcular_estatisticas_diarias(df):
    """Calcula estatísticas diárias por marca"""
    stats_diarias = df.groupby(['Data', 'Marca']).agg({
        'LeadTime_Dias': ['count', 'mean']
    })
    
    # Flatten column names
    stats_diarias.columns = ['Total_Registros', 'LeadTime_Medio']
    
    return stats_diarias.reset_index()

def criar_grafico_geral(stats_gerais):
    """Cria gráfico de barras para lead time médio geral por marca"""
    
    fig = px.bar(
        stats_gerais,
        x='Marca',
        y='LeadTime_Medio',
        title='Lead Time Médio por Marca (Geral)',
        labels={'LeadTime_Medio': 'Lead Time Médio (dias)', 'Marca': 'Marca'},
        text='LeadTime_Medio',
        color='Marca',
        color_discrete_map=cores_marca
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(
        showlegend=False,
        height=500,
        title_font_size=20,
        xaxis_title_font_size=18,
        yaxis_title_font_size=18,
        font=dict(size=14),
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=14))
    )
    
    return fig

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
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=14)
    
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
            font=dict(size=14)
        ),
        xaxis_title='Data',
        yaxis_title='TMO Médio (dias)',
        title_font_size=18,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        font=dict(size=12),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        bargap=0.2,
        bargroupgap=0.1
    )
    
    return fig

def criar_grafico_geral_com_total(stats_gerais, df_filtrado):
    """Cria gráfico de barras para lead time médio por marca + Total geral"""
    
    # Calcular o total geral
    total_geral = df_filtrado['LeadTime_Dias'].mean()
    
    # Criar uma cópia dos dados e adicionar o total
    stats_com_total = stats_gerais.copy()
    
    # Adicionar linha do total
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
    
    fig = px.bar(
        stats_com_total,
        x='Marca',
        y='LeadTime_Medio',
        title='TMO Expedição Médio por Marca',
        labels={'LeadTime_Medio': 'Lead Time (dias)', 'Marca': 'Marca'},
        text='LeadTime_Medio',
        color='Marca',
        color_discrete_map=cores_marca
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=16)
    fig.update_layout(
        showlegend=False,
        height=500,
        title_font_size=20,
        xaxis_title_font_size=18,
        yaxis_title_font_size=18,
        font=dict(size=14),
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=14))
    )
    
    return fig

def criar_grafico_estatisticas_gerais(stats_gerais):
    """Cria gráfico de linha com métricas estatísticas por marca"""
    
    # Preparar dados para o gráfico de linha
    dados_linha = []
    
    for _, row in stats_gerais.iterrows():
        marca = row['Marca']
        dados_linha.extend([
            {'Marca': marca, 'Métrica': 'Média', 'Valor': row['LeadTime_Medio']},
            {'Marca': marca, 'Métrica': 'Mediana', 'Valor': row['LeadTime_Mediano']},
            {'Marca': marca, 'Métrica': 'Desvio Padrão', 'Valor': row['Desvio_Padrao']},
            {'Marca': marca, 'Métrica': 'Mínimo', 'Valor': row['LeadTime_Min']},
            {'Marca': marca, 'Métrica': 'Máximo', 'Valor': row['LeadTime_Max']}
        ])
    
    df_stats = pd.DataFrame(dados_linha)
    
    fig = px.line(
        df_stats,
        x='Métrica',
        y='Valor',
        color='Marca',
        title='Perfil Estatístico de Lead Time por Marca',
        labels={'Valor': 'Lead Time (dias)', 'Métrica': 'Métricas Estatísticas'},
        color_discrete_map=cores_marca,
        markers=True,
        line_shape='linear'
    )
    
    # Formatação
    fig.update_traces(
        mode='lines+markers+text',
        textposition='top center',
        texttemplate='%{y:.2f}',
        textfont_size=11,
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        font=dict(size=12),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        hovermode='x unified'
    )
    
    return fig

def criar_grafico_radar_estatisticas(stats_gerais):
    """Cria gráfico radar com métricas estatísticas por marca"""
    
    # Normalizar os dados para o radar (escala 0-1)
    metricas = ['LeadTime_Medio', 'LeadTime_Mediano', 'Desvio_Padrao', 'LeadTime_Min', 'LeadTime_Max']
    
    fig = go.Figure()
    
    for _, row in stats_gerais.iterrows():
        marca = row['Marca']
        valores = [row[metrica] for metrica in metricas]
        
        fig.add_trace(go.Scatterpolar(
            r=valores,
            theta=['Média', 'Mediana', 'Desvio Padrão', 'Mínimo', 'Máximo'],
            fill='toself',
            name=marca,
            line=dict(color=cores_marca.get(marca, '#000000'), width=2),
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(stats_gerais[metricas].max()) * 1.1],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=True,
        title="Radar de Métricas Estatísticas por Marca",
        title_font_size=18,
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        height=500
    )
    
    return fig

def criar_heatmap_marcas_dias(df):
    """Cria heatmap mostrando lead time por marca e dia da semana"""
    # Adicionar dia da semana
    df_copy = df.copy()
    df_copy['Dia_Semana'] = df_copy['Data_Emissao_NF'].dt.day_name()
    
    # Mapear para português
    dias_pt = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    df_copy['Dia_Semana'] = df_copy['Dia_Semana'].map(dias_pt)
    
    # Calcular lead time médio por marca e dia da semana
    heatmap_data = df_copy.groupby(['Marca', 'Dia_Semana'])['LeadTime_Dias'].mean().unstack()
    
    # Reordenar colunas para ordem correta dos dias
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    heatmap_data = heatmap_data.reindex(columns=[dia for dia in ordem_dias if dia in heatmap_data.columns])
    
    fig = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale='RdYlGn_r',
        title='Lead Time Médio por Marca e Dia da Semana',
        labels={'color': 'Lead Time (dias)', 'x': 'Dia da Semana', 'y': 'Marca'},
        text_auto='.2f'
    )
    
    fig.update_layout(height=400)
    
    return fig

def criar_boxplot_melhorado(df_filtrado):
    """Cria boxplot melhorado com média destacada"""
    
    fig = px.box(
        df_filtrado,
        x='Marca',
        y='LeadTime_Dias',
        title='Distribuição Completa do Lead Time por Marca (Boxplot)',
        labels={'LeadTime_Dias': 'Lead Time (dias)', 'Marca': 'Marca'},
        color='Marca',
        color_discrete_map=cores_marca
    )
    
    # Adicionar pontos da média
    medias = df_filtrado.groupby('Marca')['LeadTime_Dias'].mean()
    
    for i, marca in enumerate(medias.index):
        fig.add_trace(
            go.Scatter(
                x=[marca],
                y=[medias[marca]],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=12,
                    color='red',
                    line=dict(width=2, color='darkred')
                ),
                name=f'Média {marca}',
                showlegend=True if i == 0 else False,
                legendgroup='média'
            )
        )
    
    # Adicionar anotação explicativa
    fig.add_annotation(
        text="♦ = Média",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        xanchor="left", yanchor="top",
        showarrow=False,
        font=dict(size=12, color="red"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="red",
        borderwidth=1
    )
    
    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        font=dict(size=12),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=True
    )
    
    return fig

def criar_grafico_barras_erro(stats_gerais):
    """Cria gráfico de barras com barras de erro (desvio padrão)"""
    
    fig = go.Figure()
    
    for _, row in stats_gerais.iterrows():
        marca = row['Marca']
        media = row['LeadTime_Medio']
        desvio = row['Desvio_Padrao']
        
        fig.add_trace(go.Bar(
            x=[marca],
            y=[media],
            error_y=dict(
                type='data',
                array=[desvio],
                visible=True,
                thickness=3,
                width=8
            ),
            name=marca,
            marker_color=cores_marca.get(marca, '#333333'),
            text=[f'{media:.2f}'],
            textposition='outside',
            textfont=dict(size=14)
        ))
    
    fig.update_layout(
        title='Lead Time Médio ± Desvio Padrão por Marca',
        xaxis_title='Marca',
        yaxis_title='Lead Time (dias)',
        title_font_size=18,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        font=dict(size=12),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=12)),
        height=500,
        showlegend=False
    )
    
    return fig

def criar_violin_plot(df_filtrado):
    """Cria violin plot para análise avançada da distribuição"""
    
    fig = px.violin(
        df_filtrado,
        x='Marca',
        y='LeadTime_Dias',
        title='Análise Avançada da Distribuição (Violin Plot)',
        labels={'LeadTime_Dias': 'Lead Time (dias)', 'Marca': 'Marca'},
        color='Marca',
        color_discrete_map=cores_marca,
        box=True,  # Inclui boxplot dentro do violin
        points='outliers'  # Mostra apenas outliers
    )
    
    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        font=dict(size=12),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=False
    )
    
    return fig

def criar_serie_temporal_estatisticas(df_filtrado):
    """Cria gráfico de linha temporal com estatísticas móveis"""
    
    # Calcular estatísticas por data e marca
    stats_temporais = df_filtrado.groupby(['Data', 'Marca'])['LeadTime_Dias'].agg([
        'mean', 'median', 'std', 'count'
    ]).reset_index()
    
    # Calcular médias móveis de 3 dias
    for marca in stats_temporais['Marca'].unique():
        mask = stats_temporais['Marca'] == marca
        stats_temporais.loc[mask, 'media_movel'] = (
            stats_temporais.loc[mask, 'mean'].rolling(window=3, min_periods=1).mean()
        )
    
    fig = px.line(
        stats_temporais,
        x='Data',
        y='mean',
        color='Marca',
        title='Evolução Temporal do Lead Time Médio por Marca',
        labels={'mean': 'Lead Time Médio (dias)', 'Data': 'Data'},
        color_discrete_map=cores_marca,
        markers=True
    )
    
    # Adicionar linha de média móvel
    for marca in stats_temporais['Marca'].unique():
        dados_marca = stats_temporais[stats_temporais['Marca'] == marca]
        fig.add_trace(
            go.Scatter(
                x=dados_marca['Data'],
                y=dados_marca['media_movel'],
                mode='lines',
                name=f'{marca} (Média Móvel 3d)',
                line=dict(
                    color=cores_marca.get(marca, '#333333'),
                    dash='dash',
                    width=2
                ),
                opacity=0.7
            )
        )
    
    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        font=dict(size=12),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(size=10)
        ),
        hovermode='x unified'
    )
    
    return fig

# MAIN APP
def main():
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
    
    # Filtro de data
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
    
    # Filtro de marca (apenas as 3 marcas principais)
    marcas_disponiveis = ['PAPAIZ', 'LA FONTE', 'SILVANA CD SP']
    marcas_selecionadas = st.sidebar.multiselect(
        "Selecionar Marcas",
        options=marcas_disponiveis,
        default=marcas_disponiveis
    )
    
    # Filtro de canal agrupado (opcional)
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
    
    # Mostrar dados filtrados
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dados Filtrados")
    st.sidebar.metric("Registros", len(df_filtrado))
    st.sidebar.metric("Lead Time Médio", f"{df_filtrado['LeadTime_Dias'].mean():.2f} dias")
    
    # Interface do Agente de IA
    pergunta_usuario = criar_interface_chat()
    
    # Calcular estatísticas
    stats_gerais = calcular_estatisticas_gerais(df_filtrado)
    stats_diarias = calcular_estatisticas_diarias(df_filtrado)
    
    # Processar pergunta do usuário para IA
    if pergunta_usuario and pergunta_usuario.strip():
        if st.sidebar.button("🚀 Consultar IA", type="primary"):
            with st.spinner("Analisando dados..."):
                # Preparar contexto dos dados
                contexto_dados = preparar_contexto_dados(df_filtrado, stats_gerais)
                
                # Consultar IA
                resposta_ia = consultar_agente_ia(pergunta_usuario, contexto_dados)
                
                # Adicionar ao histórico
                st.session_state.chat_history.append({
                    "pergunta": pergunta_usuario,
                    "resposta": resposta_ia,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
    
    # Exibir histórico de chat
    if st.session_state.chat_history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💬 Histórico de Conversas")
        
        # Botão para limpar histórico
        if st.sidebar.button("🗑️ Limpar Histórico"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Exibir conversas (mais recente primeiro)
        for i, conversa in enumerate(reversed(st.session_state.chat_history)):
            with st.sidebar.expander(f"💬 {conversa['timestamp']} - Pergunta {len(st.session_state.chat_history)-i}"):
                st.markdown(f"**Pergunta:** {conversa['pergunta']}")
                st.markdown("---")
                st.markdown(f"**Resposta:** {conversa['resposta']}")
    
    # Seção principal para exibir resposta da IA
    if st.session_state.chat_history:
        ultima_conversa = st.session_state.chat_history[-1]
        st.header("🤖 Análise do Assistente de IA")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Pergunta:** {ultima_conversa['pergunta']}")
        with col2:
            st.markdown(f"*{ultima_conversa['timestamp']}*")
        
        st.markdown("**Resposta:**")
        st.info(ultima_conversa['resposta'])
        st.markdown("---")
    
    # Exibir gráficos
    st.header("📈 Análises de Lead Time")
    
    # Primeira linha de gráficos
    

    st.subheader("Lead Time Médio Geral por Marca")
    if not stats_gerais.empty:
        fig_geral = criar_grafico_geral_com_total(stats_gerais, df_filtrado)
        st.plotly_chart(fig_geral, use_container_width=True)
    else:
        st.warning("Não há dados suficientes para este gráfico.")


    
    # Gráfico temporal
    st.subheader("TMO Expedição Diário por Marca - Barras Agrupadas")
    if not stats_diarias.empty:
        fig_temporal = criar_grafico_linha_temporal(stats_diarias)
        st.plotly_chart(fig_temporal, use_container_width=True)
    else:
        st.warning("Não há dados suficientes para este gráfico.")
    
    # Nova seção: Análises Estatísticas Avançadas
    st.header("📊 Análises Estatísticas Avançadas")
    
    st.subheader("Distribuição do Lead Time por Marca")
    fig_boxplot = criar_boxplot_melhorado(df_filtrado)
    st.plotly_chart(fig_boxplot, use_container_width=True)


    # Seletor de tipo de análise avançada
    tipo_analise = st.selectbox(
        "Escolha o tipo de análise estatística:",
        [
            "Barras com Desvio Padrão", 
            "Violin Plot (Distribuição Avançada)",
            "Série Temporal com Médias Móveis"
        ],
        key="tipo_analise_avancada"
    )
    
    if tipo_analise == "Barras com Desvio Padrão":
        fig_avancada = criar_grafico_barras_erro(stats_gerais)
        st.plotly_chart(fig_avancada, use_container_width=True)
        
        st.info("""
        📈 **Interpretação**: As barras mostram a média e as "bigodes" indicam o desvio padrão.
        - Barras mais altas = maior lead time médio
        - Bigodes maiores = maior variabilidade nos dados
        """)
        
    elif tipo_analise == "Violin Plot (Distribuição Avançada)":
        fig_avancada = criar_violin_plot(df_filtrado)
        st.plotly_chart(fig_avancada, use_container_width=True)
        
        st.info("""
        🎻 **Interpretação**: O formato "violino" mostra a densidade da distribuição.
        - Largura maior = mais dados nessa faixa de valores
        - Inclui boxplot interno e outliers
        - Ideal para identificar padrões de distribuição únicos
        """)
        
    else:  # Série Temporal
        fig_avancada = criar_serie_temporal_estatisticas(df_filtrado)
        st.plotly_chart(fig_avancada, use_container_width=True)
        
        st.info("""
        📈 **Interpretação**: Evolução do lead time ao longo do tempo.
        - Linhas sólidas = valores diários reais
        - Linhas tracejadas = médias móveis de 3 dias (suavizadas)
        - Útil para identificar tendências e sazonalidades
        """)

    # Heatmap
    st.subheader("Lead Time por Marca e Dia da Semana")
    try:
        fig_heatmap = criar_heatmap_marcas_dias(df_filtrado)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    except Exception as e:
        st.warning("Não há dados suficientes para criar o heatmap.")
    
    
    # Análise por canal de venda agrupado
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
        fig_canal.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=14)
        fig_canal.update_layout(
            height=400, 
            xaxis_tickangle=-45,
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            font=dict(size=12),
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12)),
            showlegend=False
        )
        st.plotly_chart(fig_canal, use_container_width=True)
    
    # Dados detalhados (últimos registros)
    with st.expander("📊 Ver Dados Detalhados (Últimos 100 registros)"):
        if len(df_filtrado) > 0:
            colunas_importantes = ['Marca', 'Data_Emissao_NF', 'Data_Embarque', 'LeadTime_Dias', 
                                  'Canal_Agrupado', 'Cidade']
            dados_detalhados = df_filtrado[colunas_importantes].tail(100).copy()
            # Formatar datas para melhor visualização
            dados_detalhados['Data_Emissao_NF'] = dados_detalhados['Data_Emissao_NF'].dt.strftime('%d/%m/%Y')
            dados_detalhados['Data_Embarque'] = dados_detalhados['Data_Embarque'].dt.strftime('%d/%m/%Y')
            st.dataframe(dados_detalhados, use_container_width=True)
        else:
            st.warning("Não há dados para exibir.")
            
# Tabelas de dados
    st.header("📋 Tabelas de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estatísticas Gerais por Marca")
        if not stats_gerais.empty:
            # Formatação da tabela - mantendo valores exatos
            stats_display = stats_gerais.copy()
            stats_display['LeadTime_Medio'] = stats_display['LeadTime_Medio'].map('{:.2f}'.format)
            stats_display['LeadTime_Mediano'] = stats_display['LeadTime_Mediano'].map('{:.2f}'.format)
            stats_display['Desvio_Padrao'] = stats_display['Desvio_Padrao'].map('{:.2f}'.format)
            stats_display['LeadTime_Min'] = stats_display['LeadTime_Min'].map('{:.2f}'.format)
            stats_display['LeadTime_Max'] = stats_display['LeadTime_Max'].map('{:.2f}'.format)
            st.dataframe(stats_display, use_container_width=True)
        else:
            st.warning("Não há dados para exibir.")
    
    with col2:
        st.subheader("Top 10 Maiores Lead Times")
        if len(df_filtrado) > 0:
            top_leadtimes = df_filtrado.nlargest(10, 'LeadTime_Dias')[
                ['Marca', 'Data_Emissao_NF', 'Data_Embarque', 'LeadTime_Dias', 'Canal_Agrupado', 'Cidade']
            ]
            st.dataframe(top_leadtimes, use_container_width=True)
        else:
            st.warning("Não há dados para exibir.")
    

if __name__ == "__main__":
    main()
