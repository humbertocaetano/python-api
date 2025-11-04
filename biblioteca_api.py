from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime
import jwt
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-super-segura'

# =====================================================
# FUNÇÕES AUXILIARES E DECORATORS
# =====================================================

def get_db_connection():
    """Estabelece conexão com o banco de dados SQLite"""
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    """Decorator para proteger rotas que precisam de autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'mensagem': 'Token não fornecido'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data
        except:
            return jsonify({'mensagem': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def funcionario_required(f):
    """Decorator para rotas que só funcionários podem acessar"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user['perfil'] != 'funcionario':
            return jsonify({'mensagem': 'Acesso negado. Apenas funcionários podem acessar'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

# =====================================================
# ROTAS DE AUTENTICAÇÃO
# =====================================================

@app.route('/api/login', methods=['POST'])
def login():
    """
    Rota de login - retorna token JWT
    Exemplo de requisição:
    {
        "email": "admin@biblioteca.com",
        "senha": "admin123"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'mensagem': 'Email e senha são obrigatórios'}), 400
    
    conn = get_db_connection()
    usuario = conn.execute(
        'SELECT * FROM usuarios WHERE email = ?',
        (data['email'],)
    ).fetchone()
    conn.close()
    
    if not usuario or not check_password_hash(usuario['senha'], data['senha']):
        return jsonify({'mensagem': 'Credenciais inválidas'}), 401
    
    token = jwt.encode({
        'id': usuario['id'],
        'email': usuario['email'],
        'perfil': usuario['perfil'],
        'nome': usuario['nome']
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'mensagem': 'Login realizado com sucesso',
        'token': token,
        'usuario': {
            'id': usuario['id'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'perfil': usuario['perfil']
        }
    }), 200

# =====================================================
# ROTAS DE USUÁRIOS
# =====================================================

@app.route('/api/usuarios', methods=['POST'])
@funcionario_required
def cadastrar_usuario(current_user):
    """
    Cadastra um novo usuário (apenas funcionários)
    Exemplo de requisição:
    {
        "nome": "João Silva",
        "email": "joao@email.com",
        "senha": "senha123",
        "perfil": "cliente",
        "telefone": "81999999999"
    }
    """
    data = request.get_json()
    
    # Validações
    if not data or not all(k in data for k in ('nome', 'email', 'senha', 'perfil')):
        return jsonify({'mensagem': 'Dados incompletos'}), 400
    
    if data['perfil'] not in ['funcionario', 'cliente']:
        return jsonify({'mensagem': 'Perfil inválido. Use "funcionario" ou "cliente"'}), 400
    
    conn = get_db_connection()
    
    # Verifica se o email já existe
    usuario_existe = conn.execute(
        'SELECT id FROM usuarios WHERE email = ?',
        (data['email'],)
    ).fetchone()
    
    if usuario_existe:
        conn.close()
        return jsonify({'mensagem': 'Email já cadastrado'}), 409
    
    # Insere novo usuário
    senha_hash = generate_password_hash(data['senha'])
    cursor = conn.execute(
        'INSERT INTO usuarios (nome, email, senha, perfil, telefone) VALUES (?, ?, ?, ?, ?)',
        (data['nome'], data['email'], senha_hash, data['perfil'], data.get('telefone', ''))
    )
    conn.commit()
    usuario_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'mensagem': 'Usuário cadastrado com sucesso',
        'usuario': {
            'id': usuario_id,
            'nome': data['nome'],
            'email': data['email'],
            'perfil': data['perfil']
        }
    }), 201

@app.route('/api/usuarios', methods=['GET'])
@funcionario_required
def listar_usuarios(current_user):
    """Lista todos os usuários (apenas funcionários)"""
    conn = get_db_connection()
    usuarios = conn.execute('SELECT id, nome, email, perfil, telefone, data_cadastro FROM usuarios').fetchall()
    conn.close()
    
    usuarios_lista = []
    for usuario in usuarios:
        usuarios_lista.append({
            'id': usuario['id'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'perfil': usuario['perfil'],
            'telefone': usuario['telefone'],
            'data_cadastro': usuario['data_cadastro']
        })
    
    return jsonify({'usuarios': usuarios_lista}), 200

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
@token_required
def obter_usuario(current_user, usuario_id):
    """Obtém dados de um usuário específico"""
    # Clientes só podem ver seus próprios dados
    if current_user['perfil'] == 'cliente' and current_user['id'] != usuario_id:
        return jsonify({'mensagem': 'Acesso negado'}), 403
    
    conn = get_db_connection()
    usuario = conn.execute(
        'SELECT id, nome, email, perfil, telefone, data_cadastro FROM usuarios WHERE id = ?',
        (usuario_id,)
    ).fetchone()
    conn.close()
    
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    
    return jsonify({
        'id': usuario['id'],
        'nome': usuario['nome'],
        'email': usuario['email'],
        'perfil': usuario['perfil'],
        'telefone': usuario['telefone'],
        'data_cadastro': usuario['data_cadastro']
    }), 200

# =====================================================
# ROTAS DE LIVROS
# =====================================================

@app.route('/api/livros', methods=['POST'])
@funcionario_required
def cadastrar_livro(current_user):
    """
    Cadastra um novo livro (apenas funcionários)
    Exemplo de requisição:
    {
        "titulo": "Clean Code",
        "autor": "Robert C. Martin",
        "isbn": "978-0132350884",
        "ano_publicacao": 2008,
        "categoria": "Tecnologia",
        "quantidade_total": 5
    }
    """
    data = request.get_json()
    
    # Validações
    if not data or not all(k in data for k in ('titulo', 'autor', 'quantidade_total')):
        return jsonify({'mensagem': 'Dados incompletos (titulo, autor e quantidade_total são obrigatórios)'}), 400
    
    conn = get_db_connection()
    
    # Verifica se o ISBN já existe (se fornecido)
    if data.get('isbn'):
        livro_existe = conn.execute(
            'SELECT id FROM livros WHERE isbn = ?',
            (data['isbn'],)
        ).fetchone()
        
        if livro_existe:
            conn.close()
            return jsonify({'mensagem': 'ISBN já cadastrado'}), 409
    
    # Insere novo livro
    cursor = conn.execute(
        '''INSERT INTO livros 
           (titulo, autor, isbn, ano_publicacao, categoria, quantidade_total, quantidade_disponivel) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            data['titulo'],
            data['autor'],
            data.get('isbn', ''),
            data.get('ano_publicacao', None),
            data.get('categoria', ''),
            data['quantidade_total'],
            data['quantidade_total']
        )
    )
    conn.commit()
    livro_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'mensagem': 'Livro cadastrado com sucesso',
        'livro': {
            'id': livro_id,
            'titulo': data['titulo'],
            'autor': data['autor'],
            'isbn': data.get('isbn', ''),
            'quantidade_total': data['quantidade_total']
        }
    }), 201

@app.route('/api/livros', methods=['GET'])
def listar_livros():
    """
    Lista todos os livros (rota pública)
    Parâmetros de query opcionais:
    - titulo: filtrar por título
    - autor: filtrar por autor
    - categoria: filtrar por categoria
    - disponivel: filtrar apenas livros disponíveis (true/false)
    """
    titulo = request.args.get('titulo', '')
    autor = request.args.get('autor', '')
    categoria = request.args.get('categoria', '')
    disponivel = request.args.get('disponivel', '')
    
    conn = get_db_connection()
    
    query = 'SELECT * FROM livros WHERE 1=1'
    params = []
    
    if titulo:
        query += ' AND titulo LIKE ?'
        params.append(f'%{titulo}%')
    
    if autor:
        query += ' AND autor LIKE ?'
        params.append(f'%{autor}%')
    
    if categoria:
        query += ' AND categoria LIKE ?'
        params.append(f'%{categoria}%')
    
    if disponivel.lower() == 'true':
        query += ' AND quantidade_disponivel > 0'
    
    livros = conn.execute(query, params).fetchall()
    conn.close()
    
    livros_lista = []
    for livro in livros:
        livros_lista.append({
            'id': livro['id'],
            'titulo': livro['titulo'],
            'autor': livro['autor'],
            'isbn': livro['isbn'],
            'ano_publicacao': livro['ano_publicacao'],
            'categoria': livro['categoria'],
            'quantidade_total': livro['quantidade_total'],
            'quantidade_disponivel': livro['quantidade_disponivel']
        })
    
    return jsonify({'livros': livros_lista}), 200

@app.route('/api/livros/<int:livro_id>', methods=['GET'])
def obter_livro(livro_id):
    """Obtém dados de um livro específico (rota pública)"""
    conn = get_db_connection()
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (livro_id,)).fetchone()
    conn.close()
    
    if not livro:
        return jsonify({'mensagem': 'Livro não encontrado'}), 404
    
    return jsonify({
        'id': livro['id'],
        'titulo': livro['titulo'],
        'autor': livro['autor'],
        'isbn': livro['isbn'],
        'ano_publicacao': livro['ano_publicacao'],
        'categoria': livro['categoria'],
        'quantidade_total': livro['quantidade_total'],
        'quantidade_disponivel': livro['quantidade_disponivel']
    }), 200

@app.route('/api/livros/<int:livro_id>', methods=['PUT'])
@funcionario_required
def atualizar_livro(current_user, livro_id):
    """Atualiza dados de um livro (apenas funcionários)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'mensagem': 'Dados não fornecidos'}), 400
    
    conn = get_db_connection()
    
    # Verifica se o livro existe
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (livro_id,)).fetchone()
    if not livro:
        conn.close()
        return jsonify({'mensagem': 'Livro não encontrado'}), 404
    
    # Atualiza apenas os campos fornecidos
    campos_atualizaveis = ['titulo', 'autor', 'isbn', 'ano_publicacao', 'categoria', 'quantidade_total']
    updates = []
    params = []
    
    for campo in campos_atualizaveis:
        if campo in data:
            updates.append(f'{campo} = ?')
            params.append(data[campo])
    
    # Atualiza quantidade_disponivel se quantidade_total foi alterada
    if 'quantidade_total' in data:
        diferenca = data['quantidade_total'] - livro['quantidade_total']
        nova_disponivel = livro['quantidade_disponivel'] + diferenca
        updates.append('quantidade_disponivel = ?')
        params.append(max(0, nova_disponivel))
    
    if updates:
        params.append(livro_id)
        query = f"UPDATE livros SET {', '.join(updates)} WHERE id = ?"
        conn.execute(query, params)
        conn.commit()
    
    conn.close()
    
    return jsonify({'mensagem': 'Livro atualizado com sucesso'}), 200

@app.route('/api/livros/<int:livro_id>', methods=['DELETE'])
@funcionario_required
def deletar_livro(current_user, livro_id):
    """Deleta um livro (apenas funcionários)"""
    conn = get_db_connection()
    
    # Verifica se existem reservas ativas para este livro
    reservas_ativas = conn.execute(
        'SELECT COUNT(*) as total FROM reservas WHERE livro_id = ? AND status = "ativa"',
        (livro_id,)
    ).fetchone()
    
    if reservas_ativas['total'] > 0:
        conn.close()
        return jsonify({'mensagem': 'Não é possível deletar livro com reservas ativas'}), 400
    
    cursor = conn.execute('DELETE FROM livros WHERE id = ?', (livro_id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'mensagem': 'Livro não encontrado'}), 404
    
    conn.close()
    return jsonify({'mensagem': 'Livro deletado com sucesso'}), 200

# =====================================================
# ROTAS DE RESERVAS
# =====================================================

@app.route('/api/reservas', methods=['POST'])
@token_required
def criar_reserva(current_user):
    """
    Cria uma nova reserva
    Exemplo de requisição:
    {
        "livro_id": 1
    }
    """
    data = request.get_json()
    
    if not data or 'livro_id' not in data:
        return jsonify({'mensagem': 'livro_id é obrigatório'}), 400
    
    livro_id = data['livro_id']
    usuario_id = current_user['id']
    
    conn = get_db_connection()
    
    # Verifica se o livro existe e está disponível
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (livro_id,)).fetchone()
    
    if not livro:
        conn.close()
        return jsonify({'mensagem': 'Livro não encontrado'}), 404
    
    if livro['quantidade_disponivel'] <= 0:
        conn.close()
        return jsonify({'mensagem': 'Livro indisponível no momento'}), 400
    
    # Verifica se o usuário já tem reserva ativa deste livro
    reserva_existente = conn.execute(
        'SELECT id FROM reservas WHERE usuario_id = ? AND livro_id = ? AND status = "ativa"',
        (usuario_id, livro_id)
    ).fetchone()
    
    if reserva_existente:
        conn.close()
        return jsonify({'mensagem': 'Você já possui uma reserva ativa deste livro'}), 400
    
    # Cria a reserva
    data_reserva = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.execute(
        'INSERT INTO reservas (usuario_id, livro_id, data_reserva, status) VALUES (?, ?, ?, ?)',
        (usuario_id, livro_id, data_reserva, 'ativa')
    )
    reserva_id = cursor.lastrowid
    
    # Atualiza quantidade disponível do livro
    conn.execute(
        'UPDATE livros SET quantidade_disponivel = quantidade_disponivel - 1 WHERE id = ?',
        (livro_id,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'mensagem': 'Reserva criada com sucesso',
        'reserva': {
            'id': reserva_id,
            'livro_id': livro_id,
            'data_reserva': data_reserva,
            'status': 'ativa'
        }
    }), 201

@app.route('/api/reservas', methods=['GET'])
@token_required
def listar_reservas(current_user):
    """
    Lista reservas
    - Clientes veem apenas suas próprias reservas
    - Funcionários veem todas as reservas
    """
    conn = get_db_connection()
    
    if current_user['perfil'] == 'funcionario':
        # Funcionários veem todas as reservas
        reservas = conn.execute('''
            SELECT r.*, u.nome as usuario_nome, u.email as usuario_email,
                   l.titulo as livro_titulo, l.autor as livro_autor
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN livros l ON r.livro_id = l.id
            ORDER BY r.data_reserva DESC
        ''').fetchall()
    else:
        # Clientes veem apenas suas reservas
        reservas = conn.execute('''
            SELECT r.*, l.titulo as livro_titulo, l.autor as livro_autor
            FROM reservas r
            JOIN livros l ON r.livro_id = l.id
            WHERE r.usuario_id = ?
            ORDER BY r.data_reserva DESC
        ''', (current_user['id'],)).fetchall()
    
    conn.close()
    
    reservas_lista = []
    for reserva in reservas:
        item = {
            'id': reserva['id'],
            'livro_id': reserva['livro_id'],
            'livro_titulo': reserva['livro_titulo'],
            'livro_autor': reserva['livro_autor'],
            'data_reserva': reserva['data_reserva'],
            'data_devolucao': reserva['data_devolucao'],
            'status': reserva['status']
        }
        
        # Adiciona informações do usuário apenas para funcionários
        if current_user['perfil'] == 'funcionario':
            item['usuario_id'] = reserva['usuario_id']
            item['usuario_nome'] = reserva['usuario_nome']
            item['usuario_email'] = reserva['usuario_email']
        
        reservas_lista.append(item)
    
    return jsonify({'reservas': reservas_lista}), 200

@app.route('/api/reservas/<int:reserva_id>/devolver', methods=['PUT'])
@token_required
def devolver_livro(current_user, reserva_id):
    """Marca uma reserva como devolvida"""
    conn = get_db_connection()
    
    # Busca a reserva
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()
    
    if not reserva:
        conn.close()
        return jsonify({'mensagem': 'Reserva não encontrada'}), 404
    
    # Verifica permissões: cliente só pode devolver suas próprias reservas
    if current_user['perfil'] == 'cliente' and reserva['usuario_id'] != current_user['id']:
        conn.close()
        return jsonify({'mensagem': 'Acesso negado'}), 403
    
    if reserva['status'] == 'devolvida':
        conn.close()
        return jsonify({'mensagem': 'Livro já foi devolvido'}), 400
    
    # Atualiza a reserva
    data_devolucao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        'UPDATE reservas SET status = ?, data_devolucao = ? WHERE id = ?',
        ('devolvida', data_devolucao, reserva_id)
    )
    
    # Atualiza quantidade disponível do livro
    conn.execute(
        'UPDATE livros SET quantidade_disponivel = quantidade_disponivel + 1 WHERE id = ?',
        (reserva['livro_id'],)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'mensagem': 'Livro devolvido com sucesso',
        'data_devolucao': data_devolucao
    }), 200

@app.route('/api/reservas/<int:reserva_id>', methods=['DELETE'])
@funcionario_required
def cancelar_reserva(current_user, reserva_id):
    """Cancela/deleta uma reserva (apenas funcionários)"""
    conn = get_db_connection()
    
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()
    
    if not reserva:
        conn.close()
        return jsonify({'mensagem': 'Reserva não encontrada'}), 404
    
    # Se a reserva está ativa, devolve o livro ao estoque
    if reserva['status'] == 'ativa':
        conn.execute(
            'UPDATE livros SET quantidade_disponivel = quantidade_disponivel + 1 WHERE id = ?',
            (reserva['livro_id'],)
        )
    
    conn.execute('DELETE FROM reservas WHERE id = ?', (reserva_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'mensagem': 'Reserva cancelada com sucesso'}), 200

# =====================================================
# ROTA DE STATUS DA API
# =====================================================

@app.route('/api/status', methods=['GET'])
def status():
    """Verifica se a API está funcionando"""
    return jsonify({
        'status': 'online',
        'mensagem': 'API de Biblioteca funcionando',
        'versao': '1.0'
    }), 200

# =====================================================
# INICIALIZAÇÃO
# =====================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)