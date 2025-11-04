# 📚 API de Gestão de Biblioteca

API RESTful desenvolvida em Python/Flask para gerenciar uma biblioteca com sistema de autenticação, cadastro de usuários, livros e reservas.

## 🚀 Configuração e Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Inicializar o Banco de Dados

```bash
python init_db.py
```

Este comando cria o banco SQLite e insere dados de exemplo.

### 3. Executar a API

```bash
python biblioteca_api.py
```

A API estará disponível em: `http://localhost:5000`

---

## 👥 Usuários de Teste

### Funcionário
- **Email:** admin@biblioteca.com
- **Senha:** admin123

### Clientes
- **Email:** maria@email.com | **Senha:** cliente123
- **Email:** joao@email.com | **Senha:** cliente123

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação. Após o login, você receberá um token que deve ser incluído no header `Authorization` de todas as requisições protegidas.

**Formato do header:**
```
Authorization: Bearer SEU_TOKEN_AQUI
```

---

## 📋 Endpoints da API

### 🏥 Status da API

#### `GET /api/status`
Verifica se a API está funcionando.

**Resposta:**
```json
{
  "status": "online",
  "mensagem": "API de Biblioteca funcionando",
  "versao": "1.0"
}
```

---

### 🔑 Autenticação

#### `POST /api/login`
Realiza login e retorna token JWT.

**Body (JSON):**
```json
{
  "email": "admin@biblioteca.com",
  "senha": "admin123"
}
```

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Login realizado com sucesso",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nome": "Admin Biblioteca",
    "email": "admin@biblioteca.com",
    "perfil": "funcionario"
  }
}
```

**Possíveis Erros:**
- `400`: Dados incompletos
- `401`: Credenciais inválidas

---

### 👤 Usuários

#### `POST /api/usuarios`
Cadastra um novo usuário. **[Requer autenticação - Funcionário]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Body (JSON):**
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senha123",
  "perfil": "cliente",
  "telefone": "81999999999"
}
```

**Campos:**
- `nome` (obrigatório): Nome completo
- `email` (obrigatório): Email único
- `senha` (obrigatório): Senha do usuário
- `perfil` (obrigatório): "funcionario" ou "cliente"
- `telefone` (opcional): Telefone de contato

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Usuário cadastrado com sucesso",
  "usuario": {
    "id": 4,
    "nome": "João Silva",
    "email": "joao@email.com",
    "perfil": "cliente"
  }
}
```

**Possíveis Erros:**
- `400`: Dados incompletos ou perfil inválido
- `401`: Não autenticado
- `403`: Não é funcionário
- `409`: Email já cadastrado

---

#### `GET /api/usuarios`
Lista todos os usuários. **[Requer autenticação - Funcionário]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Resposta de Sucesso (200):**
```json
{
  "usuarios": [
    {
      "id": 1,
      "nome": "Admin Biblioteca",
      "email": "admin@biblioteca.com",
      "perfil": "funcionario",
      "telefone": "81987654321",
      "data_cadastro": "2025-11-04 10:30:00"
    }
  ]
}
```

---

#### `GET /api/usuarios/{usuario_id}`
Obtém dados de um usuário específico. **[Requer autenticação]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Regras:**
- Funcionários podem ver qualquer usuário
- Clientes podem ver apenas seus próprios dados

**Resposta de Sucesso (200):**
```json
{
  "id": 2,
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "perfil": "cliente",
  "telefone": "81912345678",
  "data_cadastro": "2025-11-04 10:30:00"
}
```

**Possíveis Erros:**
- `401`: Não autenticado
- `403`: Acesso negado
- `404`: Usuário não encontrado

---

### 📚 Livros

#### `POST /api/livros`
Cadastra um novo livro. **[Requer autenticação - Funcionário]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Body (JSON):**
```json
{
  "titulo": "Clean Code",
  "autor": "Robert C. Martin",
  "isbn": "978-0132350884",
  "ano_publicacao": 2008,
  "categoria": "Tecnologia",
  "quantidade_total": 5
}
```

**Campos:**
- `titulo` (obrigatório): Título do livro
- `autor` (obrigatório): Nome do autor
- `quantidade_total` (obrigatório): Quantidade total de exemplares
- `isbn` (opcional): Código ISBN único
- `ano_publicacao` (opcional): Ano de publicação
- `categoria` (opcional): Categoria do livro

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Livro cadastrado com sucesso",
  "livro": {
    "id": 9,
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "isbn": "978-0132350884",
    "quantidade_total": 5
  }
}
```

**Possíveis Erros:**
- `400`: Dados incompletos
- `401`: Não autenticado
- `403`: Não é funcionário
- `409`: ISBN já cadastrado

---

#### `GET /api/livros`
Lista todos os livros. **[Rota pública - não requer autenticação]**

**Parâmetros de Query (opcionais):**
- `titulo`: Filtrar por título (busca parcial)
- `autor`: Filtrar por autor (busca parcial)
- `categoria`: Filtrar por categoria (busca parcial)
- `disponivel`: Filtrar apenas livros disponíveis (true/false)

**Exemplos de uso:**
```
GET /api/livros
GET /api/livros?titulo=Python
GET /api/livros?autor=Martin&disponivel=true
GET /api/livros?categoria=Tecnologia
```

**Resposta de Sucesso (200):**
```json
{
  "livros": [
    {
      "id": 1,
      "titulo": "Clean Code",
      "autor": "Robert C. Martin",
      "isbn": "978-0132350884",
      "ano_publicacao": 2008,
      "categoria": "Tecnologia",
      "quantidade_total": 5,
      "quantidade_disponivel": 3
    }
  ]
}
```

---

#### `GET /api/livros/{livro_id}`
Obtém dados de um livro específico. **[Rota pública]**

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "titulo": "Clean Code",
  "autor": "Robert C. Martin",
  "isbn": "978-0132350884",
  "ano_publicacao": 2008,
  "categoria": "Tecnologia",
  "quantidade_total": 5,
  "quantidade_disponivel": 3
}
```

**Possíveis Erros:**
- `404`: Livro não encontrado

---

#### `PUT /api/livros/{livro_id}`
Atualiza dados de um livro. **[Requer autenticação - Funcionário]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Body (JSON) - Enviar apenas os campos a serem atualizados:**
```json
{
  "quantidade_total": 10,
  "categoria": "Programação"
}
```

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Livro atualizado com sucesso"
}
```

**Possíveis Erros:**
- `400`: Dados não fornecidos
- `401`: Não autenticado
- `403`: Não é funcionário
- `404`: Livro não encontrado

---

#### `DELETE /api/livros/{livro_id}`
Deleta um livro. **[Requer autenticação - Funcionário]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Livro deletado com sucesso"
}
```

**Possíveis Erros:**
- `400`: Livro possui reservas ativas
- `401`: Não autenticado
- `403`: Não é funcionário
- `404`: Livro não encontrado

---

### 📖 Reservas

#### `POST /api/reservas`
Cria uma nova reserva de livro. **[Requer autenticação]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Body (JSON):**
```json
{
  "livro_id": 1
}
```

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Reserva criada com sucesso",
  "reserva": {
    "id": 1,
    "livro_id": 1,
    "data_reserva": "2025-11-04 14:30:00",
    "status": "ativa"
  }
}
```

**Possíveis Erros:**
- `400`: Livro indisponível ou usuário já possui reserva ativa deste livro
- `401`: Não autenticado
- `404`: Livro não encontrado

---

#### `GET /api/reservas`
Lista reservas. **[Requer autenticação]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Regras:**
- Clientes veem apenas suas próprias reservas
- Funcionários veem todas as reservas

**Resposta de Sucesso (200) - Cliente:**
```json
{
  "reservas": [
    {
      "id": 1,
      "livro_id": 1,
      "livro_titulo": "Clean Code",
      "livro_autor": "Robert C. Martin",
      "data_reserva": "2025-11-04 14:30:00",
      "data_devolucao": null,
      "status": "ativa"
    }
  ]
}
```

**Resposta de Sucesso (200) - Funcionário:**
```json
{
  "reservas": [
    {
      "id": 1,
      "livro_id": 1,
      "livro_titulo": "Clean Code",
      "livro_autor": "Robert C. Martin",
      "usuario_id": 2,
      "usuario_nome": "Maria Silva",
      "usuario_email": "maria@email.com",
      "data_reserva": "2025-11-04 14:30:00",
      "data_devolucao": null,
      "status": "ativa"
    }
  ]
}
```

---

#### `PUT /api/reservas/{reserva_id}/devolver`
Marca uma reserva como devolvida. **[Requer autenticação]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Regras:**
- Clientes podem devolver apenas suas próprias reservas
- Funcionários podem devolver qualquer reserva

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Livro devolvido com sucesso",
  "data_devolucao": "2025-11-05 10:15:00"
}
```

**Possíveis Erros:**
- `400`: Livro já foi devolvido
- `401`: Não autenticado
- `403`: Acesso negado
- `404`: Reserva não encontrada

---

#### `DELETE /api/reservas/{reserva_id}`
Cancela/deleta uma reserva. **[Requer autenticação - Funcionário]**

**Headers:**
```
Authorization: Bearer TOKEN
```

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Reserva cancelada com sucesso"
}
```

**Possíveis Erros:**
- `401`: Não autenticado
- `403`: Não é funcionário
- `404`: Reserva não encontrada

---

## 🔒 Níveis de Permissão

### Funcionário
Pode realizar todas as operações:
- ✅ Cadastrar usuários
- ✅ Listar todos os usuários
- ✅ Cadastrar livros
- ✅ Atualizar livros
- ✅ Deletar livros
- ✅ Ver todas as reservas
- ✅ Cancelar reservas
- ✅ Devolver livros

### Cliente
Pode realizar operações limitadas:
- ✅ Ver próprio perfil
- ✅ Consultar acervo de livros
- ✅ Criar reservas
- ✅ Ver próprias reservas
- ✅ Devolver próprios livros
- ❌ Não pode cadastrar usuários ou livros
- ❌ Não pode ver dados de outros usuários

### Rotas Públicas
Não requerem autenticação:
- ✅ GET /api/status
- ✅ POST /api/login
- ✅ GET /api/livros
- ✅ GET /api/livros/{id}
