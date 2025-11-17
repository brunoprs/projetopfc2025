# Guia de Instalação de Dependências - Backend Refatorado

## Problema Identificado

O erro `No module named 'google.generativeai'` ocorre porque a biblioteca do Google Gemini (usada pelo chatbot) não está instalada.

## Solução Rápida

Execute os comandos abaixo no terminal, dentro da pasta `backend`:

```bash
# 1. Navegue até a pasta do backend
cd projetopfc2025/backend

# 2. Instale/atualize todas as dependências
pip install -r requirements.txt

# OU, se estiver usando pip3:
pip3 install -r requirements.txt

# 3. Verifique se a instalação foi bem-sucedida
python -c "import google.generativeai; print('✅ Google Generative AI instalado com sucesso!')"
```

## Dependências Adicionadas na Refatoração

A biblioteca `google-generativeai==0.8.3` foi adicionada ao `requirements.txt` para suportar o chatbot com IA.

## Instalação Individual (se preferir)

Se você quiser instalar apenas a biblioteca que está faltando:

```bash
pip install google-generativeai==0.8.3
```

## Configuração da Chave de API do Gemini

Após instalar, você precisa configurar a chave de API do Google Gemini:

### Opção 1: Variável de Ambiente (Recomendado)

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="sua_chave_aqui"
```

**Windows (CMD):**
```cmd
set GOOGLE_API_KEY=sua_chave_aqui
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="sua_chave_aqui"
```

### Opção 2: Arquivo .env

Crie um arquivo `.env` na pasta `backend` com o seguinte conteúdo:

```
GOOGLE_API_KEY=sua_chave_aqui
JWT_SECRET_KEY=sua_chave_jwt_secreta
SQLALCHEMY_DATABASE_URI=mysql+mysqlconnector://root:senha@localhost/pisos_db
```

## Como Obter a Chave de API do Gemini

1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

## Verificação Final

Após instalar tudo, execute o servidor novamente:

```bash
python run.py
```

Você deve ver a mensagem:
```
✅ Todos os blueprints refatorados registrados com sucesso
✅ Sessão de Chatbot Gemini inicializada com sucesso
```

## Troubleshooting

### Erro: "pip não é reconhecido"

Instale o Python corretamente ou use:
```bash
python -m pip install -r requirements.txt
```

### Erro: "Permission denied"

Use o comando com permissões de administrador:

**Windows:**
```bash
pip install -r requirements.txt --user
```

**Linux/Mac:**
```bash
sudo pip3 install -r requirements.txt
```

### Chatbot não funciona mesmo após instalação

Verifique se a variável de ambiente `GOOGLE_API_KEY` está configurada:

```bash
# Windows (PowerShell)
echo $env:GOOGLE_API_KEY

# Linux/Mac
echo $GOOGLE_API_KEY
```

Se estiver vazio, configure conforme instruções acima.

---

**Nota:** O chatbot é opcional. Se você não quiser usá-lo, pode comentar a importação no arquivo `routes/__init__.py`, mas é recomendado instalar todas as dependências para manter o projeto completo.
