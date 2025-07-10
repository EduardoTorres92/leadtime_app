# 📊 Dashboard Lead Time - Sistema com Login e Upload

Este é um dashboard interativo para análise de Lead Time por marca, implementado com Streamlit, sistema de autenticação e upload de arquivos CSV.

## 🔐 Sistema de Login

O dashboard possui um sistema de autenticação que protege o acesso aos dados confidenciais.

### Credenciais Disponíveis

| Usuário | Senha |
|---------|-------|
| `admin` | `admin123` |
| `leadtime` | `leadtime2024` |
| `assa` | `assa@2024` |
| `manager` | `manager@123` |

### Funcionalidades do Sistema de Login

- **Autenticação Segura**: Senhas são criptografadas usando SHA-256
- **Controle de Sessão**: Monitora tempo de sessão ativa
- **Interface Amigável**: Tela de login centralizada e intuitiva
- **Logout Seguro**: Limpa todos os dados da sessão ao sair

## 📁 Sistema de Upload de Arquivos

### Nova Funcionalidade: Upload via Interface

O dashboard agora permite fazer upload do arquivo CSV diretamente pela interface web, eliminando a necessidade de ter o arquivo na pasta do projeto.

#### Vantagens do Upload:
- ✅ **Segurança**: Não é necessário incluir dados sensíveis no repositório
- ✅ **Flexibilidade**: Suporte a diferentes arquivos de dados
- ✅ **Deploy Facilitado**: Ideal para Streamlit Cloud e outros serviços
- ✅ **Validação**: Verificação automática do formato e estrutura dos dados

#### Como Usar:
1. Faça login no sistema
2. Na tela principal, clique em "Selecione o arquivo CSV"
3. Escolha seu arquivo `leaditme_base.csv` ou similar
4. O sistema validará automaticamente o arquivo
5. Se válido, o dashboard será carregado com seus dados

### Formato do Arquivo Esperado

O arquivo CSV deve conter as seguintes colunas obrigatórias:

| Coluna | Descrição |
|--------|-----------|
| `desc_marca` | Marca do produto |
| `desc_canal_venda` | Canal de venda |
| `dat_embarque` | Data de embarque |
| `dat_emissao_nf` | Data de emissão da nota fiscal |
| `nom_cidade` | Cidade |
| `num_nota_fiscal` | Número da nota fiscal |

### Validações Automáticas

O sistema realiza as seguintes validações:

- ✅ Verificação de colunas obrigatórias
- ✅ Validação de formato de datas
- ✅ Remoção automática de duplicados
- ✅ Filtro por marcas suportadas
- ✅ Tratamento de dados inválidos

## 🚀 Como Executar

1. **Instalar Dependências**:
```bash
pip install -r requirements.txt
```

2. **Executar o Dashboard**:
```bash
streamlit run leadtime.py
```

3. **Acessar e Usar**:
   - Abra o navegador no endereço mostrado (normalmente `http://localhost:8501`)
   - Digite suas credenciais na tela de login
   - Faça upload do arquivo CSV
   - Acesse o dashboard completo

## 📋 Funcionalidades do Dashboard

### Análises Disponíveis

- **Lead Time Médio por Marca**: Comparação entre PAPAIZ, LA FONTE e SILVANA CD SP
- **Distribuição de Lead Time**: Análise estatística com boxplots
- **Análise por Canal**: Comparação entre WEBSHOP, HOME CENTER e DEMAIS CANAIS
- **Tabelas Detalhadas**: Estatísticas completas e top 10 maiores lead times

### Filtros Interativos

- **Período**: Seleção de data de início e fim
- **Marcas**: Filtro por marca específica (baseado nos dados carregados)
- **Canais**: Filtro por canal de venda

### Métricas Principais

- Total de registros processados
- Lead time médio geral
- Número de marcas analisadas
- Período de análise

### Nova Funcionalidade: Download

- **📥 Download dos Dados**: Baixe os dados filtrados em formato CSV
- **Dados Processados**: Arquivo contém apenas os registros que passaram pelos filtros
- **Formato Compatível**: CSV pronto para uso em Excel ou outras ferramentas

## 🔧 Configuração para Produção

### Alteração de Credenciais

Para uso em produção, modifique as credenciais no arquivo `leadtime.py`:

```python
def verificar_credenciais(usuario, senha):
    usuarios_validos = {
        "seu_usuario": hash_password("sua_senha_segura"),
        # Adicione mais usuários conforme necessário
    }
```

### Uso com Streamlit Secrets

Para maior segurança em produção, use o arquivo `leadtime_with_secrets.py` que suporta o sistema de secrets do Streamlit Cloud.

## 🛡️ Segurança

- **Criptografia**: Senhas são armazenadas com hash SHA-256
- **Controle de Acesso**: Apenas usuários autenticados podem acessar os dados
- **Limpeza de Sessão**: Dados sensíveis são limpos no logout
- **Validação**: Verificação de credenciais a cada acesso
- **Dados Protegidos**: CSV não fica armazenado no repositório

## 🔄 Deploy

### Streamlit Cloud (Recomendado)

1. **Preparar Repositório**:
   - Faça upload dos arquivos para o GitHub
   - **NÃO inclua** o arquivo CSV no repositório
   - Use o `.gitignore` fornecido para proteger dados sensíveis

2. **Deploy no Streamlit Cloud**:
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Conecte seu repositório GitHub
   - Configure secrets se usar `leadtime_with_secrets.py`
   - Faça o deploy

3. **Uso em Produção**:
   - Usuários fazem login normalmente
   - Upload do arquivo CSV via interface
   - Todos os dados ficam na sessão (não são persistidos)

### Outros Métodos de Deploy

- **Docker**: Use um container para maior controle
- **Servidor próprio**: Configure um servidor com Python e Streamlit
- **Heroku**: Deploy direto com buildpack Python

## 🗂️ Estrutura do Projeto

```
LEADTIME/
├── leadtime.py                 # Dashboard principal com upload
├── leadtime_with_secrets.py    # Versão para produção com secrets
├── requirements.txt            # Dependências
├── README.md                  # Esta documentação
├── .gitignore                 # Proteção de arquivos sensíveis
└── .streamlit/
    ├── config.toml            # Configurações do Streamlit
    └── secrets.toml           # Exemplo de secrets (não usar em produção)
```

## 📞 Suporte

### Problemas Comuns

1. **Arquivo não carrega**:
   - Verifique se o arquivo está em formato CSV
   - Confirme se as colunas obrigatórias estão presentes
   - Teste com um arquivo menor primeiro

2. **Erro de formato de data**:
   - Use formato DD/MM/AAAA ou AAAA-MM-DD
   - Verifique se não há células vazias em datas obrigatórias

3. **Nenhum dado encontrado**:
   - Confirme se as marcas são PAPAIZ, LA FONTE ou SILVANA CD SP
   - Verifique se há registros válidos no arquivo

### Dicas de Uso

- **Performance**: Arquivos grandes podem demorar para processar
- **Memória**: Dados ficam na sessão, logout limpa tudo
- **Filtros**: Use filtros para reduzir o volume de dados visualizados
- **Download**: Baixe dados filtrados para análises externas

## 📄 Licença

Este projeto é para uso interno da empresa. Todos os direitos reservados.

---

**Desenvolvido para análise de Lead Time | Sistema com Autenticação Segura e Upload de Arquivos** 