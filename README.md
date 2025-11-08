# 🏠 PiFloor - Sistema Completo Integrado

Sistema completo de gerenciamento de pisos com frontend em React e backend em Flask, totalmente integrado e pronto para uso.

---

## 🚀 Início Rápido (3 Passos)

### 1️⃣ Extrair o Projeto

Extraia o arquivo `pifloor.zip` para qualquer pasta do seu computador (recomendado: Área de Trabalho).

### 2️⃣ Instalar Dependências

**Clique duas vezes em:** `INSTALAR.bat`

Este script irá:
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências do backend
- ✅ Instalar todas as dependências do frontend
- ✅ Configurar o projeto automaticamente

**Tempo estimado:** 3-5 minutos

### 3️⃣ Iniciar o Projeto

**Clique duas vezes em:** `INICIAR.bat`

Este script irá:
- ✅ Iniciar o servidor backend (Flask)
- ✅ Iniciar o servidor frontend (React)
- ✅ Abrir automaticamente no navegador

**Pronto! O sistema está rodando!** 🎉

---

## 📋 Pré-requisitos

Antes de executar o `INSTALAR.bat`, certifique-se de ter instalado:

### Obrigatórios:
- ✅ **Python 3.8+** - [Download aqui](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download aqui](https://nodejs.org/)
- ✅ **MySQL Server** - Rodando com o banco `pisos_db` criado

### Verificação Rápida:
Abra o CMD e execute:
```cmd
python --version
node --version
```

Se ambos retornarem versões, você está pronto!

---

## 🌐 URLs de Acesso

Após executar `INICIAR.bat`:

- **Frontend (Interface):** http://localhost:5173
- **Backend (API):** http://localhost:5000

---

## 📁 Estrutura do Projeto

```
pifloor_completo/
├── backend/              # Servidor Flask (API)
│   ├── app/             # Código da aplicação
│   ├── migrations/      # Migrações do banco
│   ├── requirements.txt # Dependências Python
│   └── run.py          # Arquivo principal
│
├── frontend/            # Aplicação React
│   ├── src/            # Código fonte
│   │   ├── pages/      # Páginas da aplicação
│   │   ├── components/ # Componentes reutilizáveis
│   │   └── services/   # Serviços de API
│   ├── package.json    # Dependências Node
│   └── .env           # Configuração da API
│
├── INSTALAR.bat        # Script de instalação
├── INICIAR.bat         # Script para iniciar
└── README.md           # Este arquivo
```

---

## ⚙️ Configuração do Banco de Dados

O backend está configurado para conectar ao MySQL com:

```
Host: localhost
Usuário: root
Senha: root
Banco: pisos_db
```

**Para alterar**, edite o arquivo:
```
backend/app/__init__.py
```

Linha 19:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/pisos_db'
```

---

## 🔑 Funcionalidades Integradas

### Para Usuários:
- ✅ Cadastro e login com autenticação JWT
- ✅ Navegação de produtos
- ✅ Sistema de favoritos
- ✅ Visualização de dicas e FAQs
- ✅ Perfil de usuário

### Para Administradores:
- ✅ Gerenciamento de produtos (CRUD)
- ✅ Criação de dicas
- ✅ Criação de FAQs
- ✅ Gerenciamento de usuários

---

## 🧪 Testando o Sistema

### Teste Rápido:

1. **Acesse:** http://localhost:5173
2. **Clique em "Cadastrar"**
3. **Crie uma conta**
4. **Faça login**
5. **Navegue pelos produtos**
6. **Adicione favoritos**

### Teste da API:

Execute o script de teste:
```cmd
cd backend
python test_api.py
```

---

## 🛠️ Comandos Manuais (Avançado)

Se preferir iniciar manualmente:

### Backend:
```cmd
cd backend
venv\Scripts\activate
python run.py
```

### Frontend (em outro terminal):
```cmd
cd frontend
pnpm dev
```

---

## 🐛 Solução de Problemas

### ❌ Erro: "Python não encontrado"
**Solução:** Instale o Python e marque a opção "Add to PATH" durante a instalação.

### ❌ Erro: "Node.js não encontrado"
**Solução:** Instale o Node.js e reinicie o terminal.

### ❌ Erro: "MySQL connection failed"
**Solução:** 
1. Verifique se o MySQL está rodando
2. Confirme que o banco `pisos_db` existe
3. Verifique usuário/senha no arquivo `backend/app/__init__.py`

### ❌ Frontend não conecta com backend
**Solução:**
1. Verifique se o backend está rodando (http://localhost:5000)
2. Verifique o arquivo `frontend/.env`
3. Limpe o cache do navegador (Ctrl+Shift+Delete)

### ❌ Erro de CORS
**Solução:** O CORS já está configurado. Se persistir, verifique se o arquivo `backend/app/__init__.py` tem a linha `CORS(app)`.

---

## 📚 Documentação Adicional

- **Endpoints da API:** Veja `backend/app/routes.py`
- **Componentes React:** Veja `frontend/src/components/`
- **Serviços de API:** Veja `frontend/src/services/api.js`

---

## 🔄 Atualizações e Manutenção

### Atualizar Dependências do Backend:
```cmd
cd backend
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Atualizar Dependências do Frontend:
```cmd
cd frontend
pnpm update
```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique a seção "Solução de Problemas" acima
2. Consulte os logs nos terminais do backend e frontend
3. Verifique se todos os pré-requisitos estão instalados

---

## 📝 Notas Importantes

- ⚠️ **Não feche** as janelas do backend e frontend enquanto estiver usando o sistema
- ⚠️ O **MySQL deve estar rodando** antes de iniciar o backend
- ⚠️ O **banco `pisos_db`** deve existir e estar configurado
- ⚠️ Para **produção**, altere a `JWT_SECRET_KEY` no arquivo `.env` do backend

---

## ✨ Tecnologias Utilizadas

### Backend:
- Flask 3.0.3
- SQLAlchemy (ORM)
- JWT Extended (Autenticação)
- Flask-CORS
- MySQL Connector

### Frontend:
- React 19
- Vite (Build tool)
- React Router (Navegação)
- Tailwind CSS (Estilização)
- Shadcn/ui (Componentes)

---
---

## 🎯 Próximos Passos Sugeridos

Após testar o sistema, considere:

1. ✅ Adicionar mais produtos ao banco de dados
2. ✅ Customizar o tema e cores
3. ✅ Adicionar upload de imagens para produtos
4. ✅ Implementar sistema de avaliações
5. ✅ Criar painel administrativo completo

---

**Aproveite o PiFloor! 🏠✨**

