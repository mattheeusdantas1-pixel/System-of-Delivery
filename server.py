"""
server.py — Servidor único da Sopa da Roxa
Serve a API REST e os arquivos estáticos da webapp.
Roda em thread daemon junto com o app desktop (tkinter).
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import sys
import glob

# Importa o gerenciador de mesas (mesmo usado pelo desktop)
import gerenciador_mesas as gm
from cardapio import cardapio, tapioca
from auth import fazer_login, verificar_token, tem_permissao, listar_usuarios, criar_usuario

# ── Caminhos ──────────────────────────────────────────────────────
def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_PATH = get_app_path()
WEBAPP_FOLDER = os.path.join(APP_PATH, 'webapp')
CUPOMS_FOLDER = os.path.join(APP_PATH, 'cupoms')

# ── Flask ─────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)
CORS(app)

# ══════════════════════════════════════════════════════════════════
# SERVE ARQUIVOS ESTÁTICOS DA WEBAPP
# ══════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    return send_from_directory(WEBAPP_FOLDER, 'index.html')

@app.route('/cozinha')
def cozinha_page():
    return send_from_directory(WEBAPP_FOLDER, 'cozinha.html')

@app.route('/historico')
def historico_page():
    return send_from_directory(WEBAPP_FOLDER, 'historico.html')

@app.route('/delivery')
def delivery_page():
    return send_from_directory(WEBAPP_FOLDER, 'delivery.html')

@app.route('/<path:filename>')
def static_files(filename):
    full = os.path.join(WEBAPP_FOLDER, filename)
    if os.path.exists(full):
        return send_from_directory(WEBAPP_FOLDER, filename)
    return jsonify({"erro": "Arquivo não encontrado"}), 404

# ══════════════════════════════════════════════════════════════════
# API — AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email', '').strip()
    senha = data.get('senha', '')

    if not email or not senha:
        return jsonify({"status": "erro", "msg": "E-mail e senha obrigatórios"}), 400

    sucesso, token, usuario = fazer_login(email, senha)

    if not sucesso:
        return jsonify({"status": "erro", "msg": "E-mail ou senha inválidos"}), 401

    return jsonify({
        "status": "ok",
        "token": token,
        "usuario": usuario
    })

@app.route('/api/verificar-token', methods=['POST'])
def api_verificar_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({"status": "erro", "msg": "Token não fornecido"}), 401

    valido, usuario = verificar_token(token)

    if not valido:
        return jsonify({"status": "erro", "msg": "Token inválido ou expirado"}), 401

    return jsonify({
        "status": "ok",
        "usuario": usuario
    })

@app.route('/api/usuarios', methods=['GET'])
def api_listar_usuarios():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    valido, usuario = verificar_token(token)

    if not valido or usuario['perfil'] != 'admin':
        return jsonify({"status": "erro", "msg": "Acesso negado"}), 403

    usuarios = listar_usuarios()
    return jsonify([{
        "id": u[0],
        "email": u[1],
        "nome": u[2],
        "perfil": u[3],
        "ativo": bool(u[4]),
        "ultimo_acesso": u[5]
    } for u in usuarios])

@app.route('/api/usuarios', methods=['POST'])
def api_criar_usuario():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    valido, usuario = verificar_token(token)

    if not valido or usuario['perfil'] != 'admin':
        return jsonify({"status": "erro", "msg": "Acesso negado"}), 403

    data = request.json
    sucesso = criar_usuario(
        data.get('email'),
        data.get('senha'),
        data.get('nome'),
        data.get('perfil')
    )

    if not sucesso:
        return jsonify({"status": "erro", "msg": "Falha ao criar usuário"}), 400

    return jsonify({"status": "ok", "msg": "Usuário criado com sucesso"})

# ══════════════════════════════════════════════════════════════════
# API — CARDÁPIO
# ══════════════════════════════════════════════════════════════════
@app.route('/api/cardapio')
def api_cardapio():
    return jsonify({"sopas": cardapio, "tapiocas": tapioca})

# ══════════════════════════════════════════════════════════════════
# API — MESAS
# ══════════════════════════════════════════════════════════════════
@app.route('/api/mesas')
def api_mesas():
    mesas = gm.get_mesas()
    resultado = []
    for m in mesas:
        mid, num, status = m
        pedido_status = gm.obter_pedido_status(mid)
        resultado.append({
            "id": mid,
            "numero": num,
            "status": status,
            "pedido_status": pedido_status  # ativo / preparando / pronto / None
        })
    return jsonify(resultado)

@app.route('/api/mesa/<int:mesa_id>/pedido', methods=['POST'])
def api_criar_pedido(mesa_id):
    pedido_id = gm.criar_pedido(mesa_id)
    return jsonify({"pedido_id": pedido_id})

# ══════════════════════════════════════════════════════════════════
# API — PEDIDO
# ══════════════════════════════════════════════════════════════════
@app.route('/api/pedido/<int:pedido_id>/itens')
def api_itens_pedido(pedido_id):
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome_item, preco_unitario, quantidade, tipo,
               para_viagem, enviado_para_cozinha, entregue
        FROM itens_pedido WHERE pedido_id=? ORDER BY id
    """, (pedido_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([{
        "id": r[0], "nome": r[1], "preco": r[2], "quantidade": r[3],
        "tipo": r[4], "para_viagem": bool(r[5]),
        "enviado": bool(r[6]), "entregue": bool(r[7])
    } for r in rows])

@app.route('/api/pedido/<int:pedido_id>/total')
def api_total_pedido(pedido_id):
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT total FROM pedidos WHERE id=?", (pedido_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify({"total": row[0] if row else 0})

@app.route('/api/pedido/<int:pedido_id>/status')
def api_status_pedido(pedido_id):
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT status FROM pedidos WHERE id=?", (pedido_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify({"status": row[0] if row else None})

@app.route('/api/pedido/<int:pedido_id>/item', methods=['POST'])
def api_adicionar_item(pedido_id):
    data = request.json

    total = gm.adicionar_item(
        pedido_id,
        data['nome'],
        data['preco'],
        data['quantidade'],
        data['tipo'],
        data.get('para_viagem', 0)
    )

    # Se estava pronto, volta para preparando
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT status FROM pedidos WHERE id=?", (pedido_id,))
    status = cur.fetchone()

    if status and status[0] == "pronto":
        cur.execute("UPDATE pedidos SET status='preparando' WHERE id=?", (pedido_id,))

    conn.commit()
    conn.close()

    return jsonify({"total": total})

@app.route('/api/pedido/<int:pedido_id>/item/<int:item_id>', methods=['DELETE'])
def api_remover_item(pedido_id, item_id):
    gm.remover_item(item_id)
    # Recalcula total
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT SUM(preco_unitario*quantidade) FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    total = cur.fetchone()[0] or 0
    cur.execute("UPDATE pedidos SET total=? WHERE id=?", (total, pedido_id))
    conn.commit()
    conn.close()
    return jsonify({"total": total})

@app.route('/api/pedido/<int:pedido_id>/enviar', methods=['POST'])
def api_enviar_cozinha(pedido_id):
    """Marca itens não enviados como enviados e muda status para preparando."""
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    # Verifica se há itens não enviados
    cur.execute("SELECT COUNT(*) FROM itens_pedido WHERE pedido_id=? AND enviado_para_cozinha=0 AND entregue=0", (pedido_id,))
    novos = cur.fetchone()[0]
    if novos > 0:
        cur.execute("UPDATE itens_pedido SET enviado_para_cozinha=1 WHERE pedido_id=? AND entregue=0", (pedido_id,))
        cur.execute("UPDATE pedidos SET status='preparando' WHERE id=?", (pedido_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "novos": novos})

@app.route('/api/pedido/<int:pedido_id>/status', methods=['POST'])
def api_atualizar_status(pedido_id):
    data = request.json
    gm.atualizar_status_pedido(pedido_id, data['status'])
    return jsonify({"status": "ok"})

@app.route('/api/pedido/<int:pedido_id>/observacao', methods=['GET', 'POST'])
def api_observacao(pedido_id):
    if request.method == 'GET':
        return jsonify({"observacao": gm.obter_observacao(pedido_id)})
    gm.salvar_observacao(pedido_id, request.json.get('observacao', ''))
    return jsonify({"status": "ok"})

@app.route('/api/item/<int:item_id>/entregue', methods=['POST'])
def api_marcar_entregue(item_id):
    data = request.json
    gm.marcar_item_entregue(item_id, data.get('entregue', 1))
    return jsonify({"status": "ok"})

@app.route('/api/pedido/<int:pedido_id>/fechar', methods=['POST'])
def api_fechar_pedido(pedido_id):
    data = request.json
    resultado = gm.fechar_pedido(
        pedido_id,
        data['forma_pagamento'],
        data.get('valor_recebido'),
        data.get('taxa_embalagem', 0)
    )
    if not resultado:
        return jsonify({"status": "erro"}), 400

    # Salva cupom em arquivo
    from datetime import datetime
    agora = datetime.now()
    pasta = os.path.join(CUPOMS_FOLDER, agora.strftime("%Y-%m"))
    os.makedirs(pasta, exist_ok=True)
    arquivo = os.path.join(pasta, agora.strftime("cupom_mesa_%Y%m%d_%H%M%S.txt"))
    cupom_texto = _gerar_cupom_texto(resultado)
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(cupom_texto)

    return jsonify({
        "status": "ok",
        "mesa": resultado["mesa"],
        "total": resultado["total"],
        "cupom": cupom_texto,
        "forma_pagamento": resultado["forma_pagamento"],
        "valor_recebido": resultado["valor_recebido"],
        "taxa_embalagem": resultado["taxa_embalagem"],
        "itens": [{"nome": i[0], "preco": i[1], "quantidade": i[2], "para_viagem": bool(i[3])}
                  for i in resultado["itens"]]
    })

def _gerar_cupom_texto(p):
    from datetime import datetime
    L = []
    L.append("=" * 42)
    L.append("         🍲 SOPA DA ROXA 🍲")
    L.append("=" * 42)
    L.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    L.append(f"Mesa: {p['mesa']}")
    L.append("-" * 42)
    L.append(f"{'ITEM':<25} {'QTD':>3} {'UNIT':>6} {'TOTAL':>7}")
    L.append("-" * 42)
    for item in p["itens"]:
        nome, preco, qtd, viagem = item[0], item[1], item[2], item[3]
        sub = preco * qtd
        tag = " (V)" if viagem else ""
        L.append(f"{(nome+tag)[:24]:<24} {qtd:>3}  R${preco:>5.2f} R${sub:>6.2f}")
    if p.get("taxa_embalagem", 0) > 0:
        L.append(f"{'Embalagem':<24}       R${p['taxa_embalagem']:>6.2f}")
    L.append("-" * 42)
    L.append(f"TOTAL: R$ {p['total']:.2f}")
    L.append(f"Pagamento: {p['forma_pagamento'].upper()}")
    if p.get("valor_recebido"):
        troco = p["valor_recebido"] - p["total"]
        L.append(f"Recebido: R$ {p['valor_recebido']:.2f}  Troco: R$ {troco:.2f}")
    L.append("=" * 42)
    L.append("   Obrigado pela preferência!")
    L.append("   Sopa da Roxa — (81) 99623-5992")
    L.append("   Instagram: @sopadaroxa_82")
    L.append("=" * 42)
    return "\n".join(L)

# ══════════════════════════════════════════════════════════════════
# API — COZINHA (CORRIGIDO: filtra itens entregues)
# ══════════════════════════════════════════════════════════════════
@app.route('/api/pedidos/ativos')
def api_pedidos_ativos():
    pedidos = gm.listar_pedidos_ativos()
    resultado = []
    for pid, mesa_num, data_hora, status, total in pedidos:
        conn = sqlite3.connect(gm.DB_PATH)
        cur = conn.cursor()
        # 🔥 CORREÇÃO: filtra itens não entregues E já enviados para cozinha
        cur.execute("""
            SELECT id, nome_item, quantidade, para_viagem, enviado_para_cozinha, entregue
            FROM itens_pedido
            WHERE pedido_id=? AND entregue = 0 AND enviado_para_cozinha = 1
            ORDER BY id
        """, (pid,))
        itens = cur.fetchall()
        obs = gm.obter_observacao(pid)
        conn.close()
        tem_novos = any(not i[4] for i in itens)  # na verdade já são enviados, mas mantido
        resultado.append({
            "id": pid,
            "mesa": mesa_num,
            "data_hora": data_hora[:16],
            "status": status,
            "total": total,
            "tem_novos": tem_novos,
            "observacao": obs,
            "itens": [{
                "id": i[0], "nome": i[1], "quantidade": i[2],
                "para_viagem": bool(i[3]),
                "novo": not bool(i[4]),  # enviado_para_cozinha (0 = novo)
                "entregue": bool(i[5])
            } for i in itens]
        })
    return jsonify(resultado)

# ══════════════════════════════════════════════════════════════════
# API — HISTÓRICO
# ══════════════════════════════════════════════════════════════════
@app.route('/api/cupons/meses')
def api_meses():
    if not os.path.exists(CUPOMS_FOLDER):
        return jsonify([])
    meses = sorted([
        d for d in os.listdir(CUPOMS_FOLDER)
        if os.path.isdir(os.path.join(CUPOMS_FOLDER, d)) and len(d) == 7 and d[4] == '-'
    ], reverse=True)
    return jsonify(meses)

@app.route('/api/cupons/<mes>')
def api_cupons_mes(mes):
    pasta = os.path.join(CUPOMS_FOLDER, mes)
    if not os.path.exists(pasta):
        return jsonify([])
    arquivos = sorted(glob.glob(os.path.join(pasta, "cupom_*.txt")), reverse=True)
    return jsonify([os.path.basename(a) for a in arquivos])

@app.route('/api/cupons/<mes>/<nome>')
def api_cupom_arquivo(mes, nome):
    caminho = os.path.join(CUPOMS_FOLDER, mes, nome)
    if not os.path.exists(caminho):
        return "Não encontrado", 404
    with open(caminho, encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/plain; charset=utf-8"}

@app.route('/api/cupons/<mes>/<nome>', methods=['DELETE'])
def api_deletar_cupom(mes, nome):
    caminho = os.path.join(CUPOMS_FOLDER, mes, nome)
    if not os.path.exists(caminho):
        return jsonify({"status": "erro", "msg": "Arquivo não encontrado"}), 404
    try:
        os.remove(caminho)
        return jsonify({"status": "ok", "msg": "Cupom deletado"})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

# ══════════════════════════════════════════════════════════════════
# API — DELIVERY
# ══════════════════════════════════════════════════════════════════
@app.route('/api/pedido-delivery', methods=['POST'])
def api_criar_delivery():
    from datetime import datetime
    data = request.json
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()

    # Inicializa tabela de delivery se necessário
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pedidos_delivery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT,
            cliente_telefone TEXT,
            cliente_endereco TEXT,
            tipo_entrega TEXT DEFAULT 'normal',
            observacoes TEXT,
            status TEXT DEFAULT 'pendente',
            total REAL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS itens_delivery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            nome_item TEXT,
            quantidade INTEGER,
            preco_unitario REAL,
            tipo TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos_delivery(id)
        )
    ''')

    subtotal = sum(i['preco'] * i['quantidade'] for i in data['itens'])
    taxa = 5.0 if data['tipo_entrega'] == 'normal' else 0.0
    total = subtotal + taxa

    cur.execute("""
        INSERT INTO pedidos_delivery
        (cliente_nome, cliente_telefone, cliente_endereco, tipo_entrega, observacoes, total, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pendente')
    """, (data['cliente_nome'], data['cliente_telefone'], data['cliente_endereco'],
          data['tipo_entrega'], data['observacoes'], total))

    pedido_id = cur.lastrowid

    for item in data['itens']:
        cur.execute("""
            INSERT INTO itens_delivery
            (pedido_id, nome_item, quantidade, preco_unitario, tipo)
            VALUES (?, ?, ?, ?, ?)
        """, (pedido_id, item['nome'], item['quantidade'], item['preco'], item['tipo']))

    conn.commit()
    conn.close()

    cupom = _gerar_cupom_delivery(pedido_id, data, total)

    return jsonify({
        "status": "ok",
        "pedido_id": pedido_id,
        "total": total,
        "cupom": cupom
    })

@app.route('/api/pedidos-delivery/ativos')
def api_pedidos_delivery_ativos():
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, cliente_nome, cliente_telefone, cliente_endereco, tipo_entrega, status, total
        FROM pedidos_delivery
        WHERE status IN ('pendente', 'preparando', 'pronto', 'em_entrega')
        ORDER BY data_hora DESC
    """)
    pedidos_raw = cur.fetchall()
    resultado = []

    for p in pedidos_raw:
        pid, nome, tel, end, tipo, status, total = p
        cur.execute("SELECT nome_item, quantidade FROM itens_delivery WHERE pedido_id=?", (pid,))
        itens = [{"nome": i[0], "quantidade": i[1]} for i in cur.fetchall()]
        resultado.append({
            "id": pid,
            "cliente_nome": nome,
            "cliente_telefone": tel,
            "cliente_endereco": end,
            "tipo_entrega": tipo,
            "status": status,
            "total": total,
            "itens": itens
        })

    conn.close()
    return jsonify(resultado)

@app.route('/api/pedido-delivery/<int:pedido_id>/status', methods=['POST'])
def api_atualizar_delivery_status(pedido_id):
    data = request.json
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE pedidos_delivery SET status=? WHERE id=?", (data['status'], pedido_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

# ══════════════════════════════════════════════════════════════════
# API — CÁLCULO DE ENTREGAS
# ══════════════════════════════════════════════════════════════════
@app.route('/api/calculo-entregas')
def api_calculo_entregas():
    data_str = request.args.get('data', '')
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, cliente_nome, total
        FROM pedidos_delivery
        WHERE DATE(data_hora) = ? AND status = 'entregue'
    """, (data_str,))

    entregas = cur.fetchall()
    conn.close()

    total_entregas = len(entregas)
    faturamento_total = sum(e[2] for e in entregas)
    total_taxas = sum(5.0 for e in entregas)  # apenas entregas normais têm taxa

    return jsonify({
        "data": data_str,
        "total_entregas": total_entregas,
        "faturamento_total": faturamento_total,
        "total_taxas": total_taxas,
        "entregas": [
            {"cliente": e[1], "valor": e[2]}
            for e in entregas
        ]
    })

def _gerar_cupom_delivery(pedido_id, data, total):
    conn = sqlite3.connect(gm.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT nome_item, quantidade, preco_unitario FROM itens_delivery WHERE pedido_id=?", (pedido_id,))
    itens = cur.fetchall()
    conn.close()

    from datetime import datetime
    L = []
    L.append("=" * 42)
    L.append("      🍲 SOPA DA ROXA - DELIVERY 🍲")
    L.append("=" * 42)
    L.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    L.append(f"Pedido #{pedido_id}")
    L.append("-" * 42)
    L.append(f"Cliente: {data['cliente_nome']}")
    L.append(f"Telefone: {data['cliente_telefone']}")
    L.append(f"Endereço: {data['cliente_endereco']}")
    L.append(f"Tipo: {data['tipo_entrega'].upper()}")
    L.append("-" * 42)
    L.append(f"{'ITEM':<25} {'QTD':>3} {'UN':>6} {'TOTAL':>7}")
    L.append("-" * 42)
    for item in itens:
        nome, qtd, preco = item[0], item[1], item[2]
        sub = preco * qtd
        L.append(f"{nome[:24]:<24} {qtd:>3}  R${preco:>5.2f} R${sub:>6.2f}")

    taxa = 5.0 if data['tipo_entrega'] == 'normal' else 0.0
    if taxa > 0:
        L.append(f"{'Taxa de Entrega':<24}       R${taxa:>6.2f}")

    L.append("-" * 42)
    L.append(f"TOTAL: R$ {total:.2f}")
    L.append("=" * 42)
    if data['observacoes']:
        L.append(f"Observações: {data['observacoes']}")
    L.append("   Obrigado pela preferência!")
    L.append("   Sopa da Roxa — (81) 99623-5992")
    L.append("   Instagram: @sopadaroxa_82")
    L.append("=" * 42)
    return "\n".join(L)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)