# 🚀 Guia de Deploy - Streamlit Cloud

Este guia mostra como fazer o deploy do Dashboard Lead Time no Streamlit Cloud.

## 📋 Pré-requisitos

- Conta no GitHub
- Conta no [Streamlit Cloud](https://share.streamlit.io)
- Arquivos do projeto (sem o CSV de dados)

## 🔄 Passos para Deploy

### 1. Preparar o Repositório GitHub

```bash
# 1. Criar repositório no GitHub (pelo site)
# 2. Clonar localmente
git clone https://github.com/seu-usuario/leadtime-dashboard.git
cd leadtime-dashboard

# 3. Copiar arquivos do projeto (EXCETO o CSV)
cp leadtime.py leadtime_with_secrets.py requirements.txt README.md ./
cp -r .streamlit ./

# 4. Verificar .gitignore
cat .gitignore  # Deve incluir *.csv

# 5. Commit inicial
git add .
git commit -m "Initial commit: Dashboard Lead Time com sistema de login e upload"
git push origin main
```

### 2. Deploy no Streamlit Cloud

1. **Acessar**: https://share.streamlit.io
2. **Conectar GitHub**: Autorizar acesso ao repositório
3. **Nova App**:
   - Repository: `seu-usuario/leadtime-dashboard`
   - Branch: `main`
   - Main file path: `leadtime.py`
   - App URL: `leadtime-dashboard` (ou personalizado)

### 3. Configurar Secrets (Opcional)

Se usar `leadtime_with_secrets.py`:

1. **Settings** → **Secrets**
2. **Adicionar**:
```toml
[auth]
admin_user = "admin"
admin_password = "sua_senha_segura"
leadtime_user = "leadtime"
leadtime_password = "outra_senha_segura"
```

### 4. Testar o Deploy

1. **Aguardar**: Deploy leva ~2-5 minutos
2. **Acessar**: URL fornecida pelo Streamlit Cloud
3. **Testar Login**: Use credenciais configuradas
4. **Upload CSV**: Teste com arquivo de exemplo
5. **Verificar Funcionalidades**: Gráficos, filtros, download

## ✅ Checklist de Deploy

- [ ] Repositório no GitHub criado
- [ ] Arquivos copiados (sem CSV)
- [ ] .gitignore configurado
- [ ] Deploy realizado no Streamlit Cloud
- [ ] Login funcionando
- [ ] Upload de arquivo funcionando
- [ ] Gráficos sendo gerados
- [ ] Filtros funcionando
- [ ] Download de dados funcionando

## 🔧 Configurações Avançadas

### Custom Domain

No Streamlit Cloud:
1. **Settings** → **General**
2. **Custom domain**: Seu domínio personalizado

### Analytics

No Streamlit Cloud:
1. **Analytics**: Visualizar métricas de uso
2. **Logs**: Debug em caso de problemas

### Environment Variables

Se necessário:
```toml
[env]
AMBIENTE = "producao"
DEBUG = "false"
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Erro de dependências**:
   ```bash
   # Verificar requirements.txt
   cat requirements.txt
   ```

2. **Arquivo não encontrado**:
   - Verificar se todos os arquivos foram commitados
   - Confirmar estrutura de pastas

3. **Erro de memória**:
   - Arquivo CSV muito grande (limite Streamlit Cloud)
   - Otimizar processamento de dados

4. **Login não funciona**:
   - Verificar credenciais hardcoded
   - Confirmar secrets se usando versão com secrets

### Logs e Debug

1. **Streamlit Cloud Logs**:
   - Settings → Logs
   - Ver erros em tempo real

2. **Debug Local**:
   ```bash
   streamlit run leadtime.py --logger.level debug
   ```

## 📊 Monitoramento

### Métricas Importantes

- **Tempo de carregamento**: < 30 segundos
- **Uso de memória**: < 1GB
- **Usuários simultâneos**: Depende do plano
- **Uptime**: 99%+ esperado

### Alertas

Configure alertas para:
- App offline
- Erros frequentes
- Uso excessivo de recursos

## 🔄 Atualizações

Para atualizar o dashboard:

```bash
# 1. Fazer mudanças localmente
# 2. Testar localmente
streamlit run leadtime.py

# 3. Commit e push
git add .
git commit -m "Atualização: [descrição]"
git push origin main

# 4. Streamlit Cloud atualiza automaticamente
```

## 📱 Uso em Produção

### Instruções para Usuários

1. **Acessar**: URL do dashboard
2. **Login**: Usar credenciais fornecidas
3. **Upload**: Selecionar arquivo CSV (leaditme_base.csv)
4. **Aguardar**: Processamento dos dados
5. **Explorar**: Usar filtros e gráficos
6. **Download**: Baixar dados filtrados se necessário
7. **Logout**: Sempre fazer logout ao terminar

### Boas Práticas

- **Dados Sensíveis**: Nunca compartilhar credenciais
- **Arquivos**: Usar apenas dados autorizados
- **Performance**: Evitar arquivos muito grandes
- **Segurança**: Fazer logout ao terminar sessão

## 📞 Suporte

Em caso de problemas:

1. **Verificar**: README.md para troubleshooting
2. **Logs**: Verificar logs no Streamlit Cloud
3. **Local**: Testar localmente primeiro
4. **GitHub**: Verificar issues conhecidas

---

**Dashboard Lead Time | Deploy Guide v1.0** 