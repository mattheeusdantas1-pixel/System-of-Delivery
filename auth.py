"""
auth.py - Gerenciamento de Autenticação e Controle de Acesso
Suporta: Login, Hash de Senha, JWT, e RBAC (Role-Based Access Control)
"""
import sqlite3
import bcrypt
import jwt
import os
import sys
from datetime import datetime, timedelta
from functools import wraps

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "database.db")

DB_PATH = get_db_path()
JWT_SECRET = "sopa_da_roxa_2026_secret_key"
JWT_ALGORITHM = "HS256"

# Perfis de Acesso
PERFIS = {
    'admin': ['mesas', 'delivery', 'cozinha', 'historico', 'entregas'],
    'garcom': ['mesas', 'delivery'],
    'cozinha': ['cozinha'],
    'entregador': ['delivery']
}

def init_auth_db():
    """Inicializa tabela de usuários"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome TEXT NOT NULL,
                perfil TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso TIMESTAMP
            )
        ''')

        # Verificar se já existe admin padrão
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil='admin'")
        if cursor.fetchone()[0] == 0:
            # Criar admin padrão
            criar_usuario(
                email="admin@sopadaroxa.com",
                senha="admin123",
                nome="Administrador",
                perfil="admin"
            )
            # Criar garcom padrão
            criar_usuario(
                email="garcom@sopadaroxa.com",
                senha="garcom123",
                nome="Garçom Padrão",
                perfil="garcom"
            )
            # Criar cozinha padrão
            criar_usuario(
                email="cozinha@sopadaroxa.com",
                senha="cozinha123",
                nome="Cozinha Padrão",
                perfil="cozinha"
            )
            # Criar entregador padrão
            criar_usuario(
                email="entregador@sopadaroxa.com",
                senha="entregador123",
                nome="Entregador Padrão",
                perfil="entregador"
            )

        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

def hash_senha(senha: str) -> str:
    """Hash de senha com bcrypt (10 rounds)"""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
    except:
        return False

def criar_usuario(email: str, senha: str, nome: str, perfil: str) -> bool:
    """Cria novo usuário"""
    if perfil not in PERFIS:
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, perfil)
            VALUES (?, ?, ?, ?)
        """, (email, hash_senha(senha), nome, perfil))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def fazer_login(email: str, senha: str) -> tuple:
    """
    Autentica usuário e retorna token JWT
    Retorna: (sucesso, token, usuario_info)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, senha_hash, nome, perfil, ativo
        FROM usuarios
        WHERE email = ?
    """, (email,))

    usuario = cursor.fetchone()
    conn.close()

    if not usuario:
        return False, None, None

    uid, uemail, senha_hash, nome, perfil, ativo = usuario

    if not ativo:
        return False, None, None

    if not verificar_senha(senha, senha_hash):
        return False, None, None

    # Gerar JWT
    payload = {
        'id': uid,
        'email': uemail,
        'nome': nome,
        'perfil': perfil,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Atualizar último acesso
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios SET ultimo_acesso = CURRENT_TIMESTAMP WHERE id = ?
    """, (uid,))
    conn.commit()
    conn.close()

    return True, token, {
        'id': uid,
        'email': uemail,
        'nome': nome,
        'perfil': perfil
    }

def verificar_token(token: str) -> tuple:
    """
    Verifica validade do token JWT
    Retorna: (valido, usuario_info)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True, {
            'id': payload['id'],
            'email': payload['email'],
            'nome': payload['nome'],
            'perfil': payload['perfil']
        }
    except:
        return False, None

def tem_permissao(perfil: str, modulo: str) -> bool:
    """Verifica se o perfil tem acesso ao módulo"""
    return modulo in PERFIS.get(perfil, [])

def listar_usuarios() -> list:
    """Lista todos os usuários (apenas admin)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, nome, perfil, ativo, ultimo_acesso
        FROM usuarios
        ORDER BY criado_em DESC
    """)
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

# Inicializar banco na importação
init_auth_db()
