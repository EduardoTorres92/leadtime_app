# 🚀 Instruções para Deploy no Streamlit Cloud

## Problemas Corrigidos

### 1. ✅ Configuração do Streamlit
- **Problema**: `global.dataFrameSerialization IS NO LONGER SUPPORTED`
- **Solução**: Removida a configuração `dataFrameSerialization = "legacy"` do arquivo `.streamlit/config.toml`

### 2. ✅ Compatibilidade de Versões
- **Problema**: Pandas 2.1.3 incompatível com Python 3.13.5
- **Solução**: 
  - Criado arquivo `runtime.txt` especificando Python 3.11
  - Atualizado `requirements.txt` com versões compatíveis

### 3. ✅ Segurança da API Key
- **Problema**: Chave OpenAI hardcoded no código
- **Solução**: Configuração segura usando `st.secrets`

### 4. ✅ Espaçamento dos Gráficos
- **Problema**: Barras muito espaçadas no Streamlit Cloud
- **Solução**: Ajustado `bargap=0.3` e `boxgap=0.3` nos gráficos Plotly

## Arquivos Modificados

### 📁 `.streamlit/config.toml`
```toml
[global]
# Configuração geral do Streamlit
# (Removida configuração depreciada)

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### 📁 `requirements.txt`
```txt
streamlit>=1.28.0,<2.0.0
pandas>=2.2.0,<3.0.0
plotly>=5.17.0,<6.0.0
numpy>=1.24.0,<2.0.0
openai>=1.13.3,<2.0.0
```

### 📁 `runtime.txt`
```txt
python-3.11
```

## Passos para Deploy

### 1. 🔑 Configurar Secrets no Streamlit Cloud
No painel do Streamlit Cloud, vá em **Settings > Secrets** e adicione:

```toml
[auth]
admin_user = "admin"
admin_password = "admin123"
leadtime_user = "leadtime"
leadtime_password = "leadtime2024"
assa_user = "assa"
assa_password = "assa@2024"
manager_user = "manager"
manager_password = "manager@123"

[openai]
api_key = "sua-chave-openai-aqui"
```

### 2. 🚀 Fazer Deploy
1. Commit e push das alterações para o GitHub
2. No Streamlit Cloud, clique em **"Reboot App"** ou **"Deploy"**
3. Aguarde o processamento das dependências

### 3. 📊 Upload do Arquivo CSV
- A aplicação agora requer upload manual do arquivo CSV
- Faça upload do arquivo `leaditme_base.csv` na interface

## Verificações Pós-Deploy

### ✅ Testes a Realizar
- [ ] Login funciona com as credenciais configuradas
- [ ] Upload de arquivo CSV funciona
- [ ] Gráficos são exibidos corretamente
- [ ] Filtros funcionam adequadamente
- [ ] Download de dados funciona

### 🔧 Troubleshooting

#### Problema: Erro de dependências
- **Solução**: Verificar se todas as versões no `requirements.txt` são compatíveis
- **Alternativa**: Usar `pip freeze > requirements.txt` em ambiente local

#### Problema: Arquivo CSV não encontrado
- **Solução**: Fazer upload manual do arquivo na interface da aplicação

#### Problema: Chave OpenAI não funciona
- **Solução**: Verificar se a chave foi configurada corretamente nos Secrets

## Versões Testadas

- **Python**: 3.11
- **Streamlit**: 1.28.0+
- **Pandas**: 2.2.0+
- **Plotly**: 5.17.0+
- **NumPy**: 1.24.0+
- **OpenAI**: 1.13.3+

## Suporte

Se houver problemas adicionais:
1. Verificar logs do Streamlit Cloud
2. Testar localmente com as mesmas versões
3. Verificar se todos os arquivos necessários foram commitados
4. Confirmar configuração dos Secrets

---
*Última atualização: Versão de Deploy com correções de compatibilidade* 