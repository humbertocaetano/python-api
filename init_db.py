import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    """Inicializa o banco de dados criando as tabelas e inserindo dados iniciais"""
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL CHECK(perfil IN ('funcionario', 'cliente')),
            telefone TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de livros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            isbn TEXT UNIQUE,
            ano_publicacao INTEGER,
            categoria TEXT,
            quantidade_total INTEGER NOT NULL DEFAULT 1,
            quantidade_disponivel INTEGER NOT NULL DEFAULT 1,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            livro_id INTEGER NOT NULL,
            data_reserva TIMESTAMP NOT NULL,
            data_devolucao TIMESTAMP,
            status TEXT NOT NULL CHECK(status IN ('ativa', 'devolvida')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (livro_id) REFERENCES livros (id)
        )
    ''')
    
    # Insere usuários de exemplo
    senha_funcionario = generate_password_hash('admin123')
    senha_cliente = generate_password_hash('cliente123')
    
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (nome, email, senha, perfil, telefone)
        VALUES 
        ('Admin Biblioteca', 'admin@biblioteca.com', ?, 'funcionario', '81987654321'),
        ('Maria Silva', 'maria@email.com', ?, 'cliente', '81912345678'),
        ('João Santos', 'joao@email.com', ?, 'cliente', '81998765432')
    ''', (senha_funcionario, senha_cliente, senha_cliente))
    
    # Insere livros de exemplo
    cursor.execute('''
        INSERT OR IGNORE INTO livros (titulo, autor, isbn, ano_publicacao, categoria, quantidade_total, quantidade_disponivel)
        VALUES 
        ('Clean Code', 'Robert C. Martin', '978-0132350884', 2008, 'Tecnologia', 5, 5),
        ('Python Fluente', 'Luciano Ramalho', '978-8575226568', 2015, 'Tecnologia', 3, 3),
        ('Design Patterns', 'Gang of Four', '978-0201633610', 1994, 'Tecnologia', 4, 4),
        ('1984', 'George Orwell', '978-0451524935', 1949, 'Ficção', 6, 6),
        ('Dom Casmurro', 'Machado de Assis', '978-8535908770', 1899, 'Literatura Brasileira', 4, 4),
        ('O Senhor dos Anéis', 'J.R.R. Tolkien', '978-8533613379', 1954, 'Fantasia', 7, 7),
        ('Sapiens', 'Yuval Noah Harari', '978-0062316097', 2011, 'História', 5, 5),
        ('Código Limpo em Python', 'Mariano Anaya', '978-8575228999', 2020, 'Tecnologia', 2, 2)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Banco de dados inicializado com sucesso!")
    print("\n📋 Usuários criados:")
    print("  Funcionário:")
    print("    Email: admin@biblioteca.com")
    print("    Senha: admin123")
    print("\n  Clientes:")
    print("    Email: maria@email.com | Senha: cliente123")
    print("    Email: joao@email.com  | Senha: cliente123")
    print("\n📚 8 livros de exemplo foram cadastrados")

if __name__ == '__main__':
    init_db()