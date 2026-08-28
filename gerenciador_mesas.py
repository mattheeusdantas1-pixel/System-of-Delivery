import sqlite3
import os
import sys
from datetime import datetime

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "database.db")

DB_PATH = get_db_path()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN observacao TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY,
            numero INTEGER UNIQUE,
            status TEXT DEFAULT 'livre',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'ativo',
            total REAL DEFAULT 0,
            taxa_embalagem REAL DEFAULT 0,
            observacao TEXT DEFAULT '',
            FOREIGN KEY (mesa_id) REFERENCES mesas(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            nome_item TEXT,
            preco_unitario REAL,
            quantidade INTEGER,
            tipo TEXT,
            para_viagem INTEGER DEFAULT 0,
            enviado_para_cozinha INTEGER DEFAULT 0,
            entregue INTEGER DEFAULT 0,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_mesas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero, status FROM mesas ORDER BY numero")
    mesas = cursor.fetchall()
    conn.close()
    return mesas

def adicionar_mesa(numero):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mesas (numero, status) VALUES (?, 'livre')", (numero,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remover_mesa(numero):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM mesas WHERE numero=?", (numero,))
    result = cursor.fetchone()
    if result and result[0] == 'livre':
        cursor.execute("DELETE FROM mesas WHERE numero=?", (numero,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_pedido_aberto(mesa_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, status FROM pedidos WHERE mesa_id=? AND status != 'finalizado' ORDER BY id DESC LIMIT 1", (mesa_id,))
    pedido = cursor.fetchone()
    if not pedido:
        conn.close()
        return None
    pedido_id = pedido[0]
    cursor.execute("SELECT id, nome_item, preco_unitario, quantidade, tipo, para_viagem, enviado_para_cozinha, entregue FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    itens = cursor.fetchall()
    cursor.execute("SELECT total, taxa_embalagem FROM pedidos WHERE id=?", (pedido_id,))
    total, taxa = cursor.fetchone()
    conn.close()
    return {"id": pedido_id, "itens": itens, "total": total, "taxa_embalagem": taxa, "status": pedido[1]}

def criar_pedido(mesa_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Verifica se já existe pedido ativo
    cursor.execute("SELECT id FROM pedidos WHERE mesa_id=? AND status != 'finalizado'", (mesa_id,))
    pedido = cursor.fetchone()
    if pedido:
        conn.close()
        return pedido[0]
    # Insere pedido vazio, mas NÃO ocupa a mesa ainda
    cursor.execute("INSERT INTO pedidos (mesa_id, status, taxa_embalagem, observacao) VALUES (?, 'ativo', 0, '')", (mesa_id,))
    pedido_id = cursor.lastrowid
    # NÃO atualiza mesa para ocupada aqui
    conn.commit()
    conn.close()
    return pedido_id

def adicionar_item(pedido_id, nome_item, preco_unitario, quantidade, tipo, para_viagem=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se é o primeiro item do pedido (nenhum outro item existe)
    cursor.execute("SELECT COUNT(*) FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        # Ocupa a mesa correspondente
        cursor.execute("SELECT mesa_id FROM pedidos WHERE id=?", (pedido_id,))
        mesa_id = cursor.fetchone()[0]
        cursor.execute("UPDATE mesas SET status='ocupada' WHERE id=?", (mesa_id,))
    
    # Procura por um item do mesmo nome, tipo e para_viagem que NÃO esteja entregue
    cursor.execute("""
        SELECT id, quantidade FROM itens_pedido 
        WHERE pedido_id=? AND nome_item=? AND tipo=? AND para_viagem=? AND entregue=0
    """, (pedido_id, nome_item, tipo, para_viagem))
    item = cursor.fetchone()
    if item:
        nova_qtd = item[1] + quantidade
        if nova_qtd <= 0:
            cursor.execute("DELETE FROM itens_pedido WHERE id=?", (item[0],))
        else:
            cursor.execute("""
                UPDATE itens_pedido 
                SET quantidade=?, enviado_para_cozinha=0 
                WHERE id=?
            """, (nova_qtd, item[0]))
    else:
        if quantidade > 0:
            cursor.execute("""
                INSERT INTO itens_pedido 
                (pedido_id, nome_item, preco_unitario, quantidade, tipo, para_viagem, enviado_para_cozinha, entregue) 
                VALUES (?,?,?,?,?,?,0,0)
            """, (pedido_id, nome_item, preco_unitario, quantidade, tipo, para_viagem))
    # Recalcula total
    cursor.execute("SELECT SUM(preco_unitario * quantidade) FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    total = cursor.fetchone()[0] or 0
    cursor.execute("UPDATE pedidos SET total=? WHERE id=?", (total, pedido_id))
    conn.commit()
    conn.close()
    return total

def remover_item(item_id):
    """Remove um item do pedido pelo seu ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT pedido_id FROM itens_pedido WHERE id=?", (item_id,))
    result = cursor.fetchone()
    if result:
        pedido_id = result[0]
        cursor.execute("DELETE FROM itens_pedido WHERE id=?", (item_id,))
        cursor.execute("SELECT SUM(preco_unitario * quantidade) FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
        total = cursor.fetchone()[0] or 0
        cursor.execute("UPDATE pedidos SET total=? WHERE id=?", (total, pedido_id))
        # Se não restar nenhum item, desocupa a mesa
        cursor.execute("SELECT COUNT(*) FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT mesa_id FROM pedidos WHERE id=?", (pedido_id,))
            mesa_id = cursor.fetchone()[0]
            cursor.execute("UPDATE mesas SET status='livre' WHERE id=?", (mesa_id,))
    conn.commit()
    conn.close()

def atualizar_status_pedido(pedido_id, novo_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET status=? WHERE id=?", (novo_status, pedido_id))
    if novo_status == 'finalizado':
        cursor.execute("SELECT mesa_id FROM pedidos WHERE id=?", (pedido_id,))
        mesa_id = cursor.fetchone()[0]
        cursor.execute("UPDATE mesas SET status='livre' WHERE id=?", (mesa_id,))
    conn.commit()
    conn.close()

def listar_pedidos_ativos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, m.numero, p.data_hora, p.status, p.total
        FROM pedidos p
        JOIN mesas m ON p.mesa_id = m.id
        WHERE p.status IN ('ativo', 'preparando', 'pronto')
        ORDER BY p.data_hora
    ''')
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

def fechar_pedido(pedido_id, forma_pagamento, valor_recebido=None, taxa_embalagem=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, m.numero, p.total, p.data_hora
        FROM pedidos p
        JOIN mesas m ON p.mesa_id = m.id
        WHERE p.id=?
    ''', (pedido_id,))
    pedido = cursor.fetchone()
    if not pedido:
        conn.close()
        return None
    cursor.execute("SELECT nome_item, preco_unitario, quantidade, para_viagem FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    itens = cursor.fetchall()
    total_final = pedido[2] + taxa_embalagem
    cursor.execute("UPDATE pedidos SET total=?, taxa_embalagem=?, status='finalizado' WHERE id=?", (total_final, taxa_embalagem, pedido_id))
    cursor.execute("UPDATE mesas SET status='livre' WHERE id=?", (pedido[1],))
    conn.commit()
    conn.close()
    return {
        "mesa": pedido[1],
        "total": total_final,
        "data_hora": pedido[3],
        "itens": itens,
        "forma_pagamento": forma_pagamento,
        "valor_recebido": valor_recebido,
        "taxa_embalagem": taxa_embalagem
    }

def obter_itens_com_status(pedido_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_item, preco_unitario, quantidade, tipo, para_viagem, enviado_para_cozinha, entregue FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    itens = cursor.fetchall()
    conn.close()
    return itens

def marcar_item_entregue(item_id, entregue=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE itens_pedido SET entregue=? WHERE id=?", (entregue, item_id))
    conn.commit()
    conn.close()

def obter_pedido_status(mesa_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status FROM pedidos
        WHERE mesa_id=? AND status != 'finalizado'
        ORDER BY id DESC LIMIT 1
    """, (mesa_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def marcar_itens_como_enviados(pedido_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE itens_pedido SET enviado_para_cozinha=1 WHERE pedido_id=? AND entregue=0", (pedido_id,))
    conn.commit()
    conn.close()

def existe_item_nao_enviado(pedido_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM itens_pedido WHERE pedido_id=? AND entregue=0", (pedido_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def salvar_observacao(pedido_id, observacao):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET observacao=? WHERE id=?", (observacao, pedido_id))
    conn.commit()
    conn.close()

def obter_observacao(pedido_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT observacao FROM pedidos WHERE id=?", (pedido_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

init_db()
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM mesas")
if cursor.fetchone()[0] == 0:
    for i in range(1, 13):
        cursor.execute("INSERT INTO mesas (numero, status) VALUES (?, 'livre')", (i,))
    conn.commit()
conn.close()