from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import gerenciador_mesas as gm
import sqlite3
from cardapio import cardapio, tapioca
import os
import glob

app = Flask(__name__)
CORS(app)

# ========== SERVE O WEBAPP ==========
@app.route('/')
def index():
    return send_from_directory('webapp', 'index.html')

@app.route('/cozinha')
def cozinha():
    return send_from_directory('webapp', 'cozinha.html')

@app.route('/historico')
def historico():
    return send_from_directory('webapp', 'historico.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('webapp', path)):
        return send_from_directory('webapp', path)
    return "Arquivo não encontrado", 404

# ========== ENDPOINTS DA API ==========
@app.route('/api/cardapio', methods=['GET'])
def get_cardapio():
    return jsonify({"sopas": cardapio, "tapiocas": tapioca})

@app.route('/api/mesas', methods=['GET'])
def get_mesas():
    mesas = gm.get_mesas()
    return jsonify([{"id": m[0], "numero": m[1], "status": m[2]} for m in mesas])

@app.route('/api/mesa/<int:mesa_id>/pedido', methods=['POST'])
def criar_pedido(mesa_id):
    pedido_id = gm.criar_pedido(mesa_id)
    return jsonify({"pedido_id": pedido_id})

@app.route('/api/pedido/<int:pedido_id>/item', methods=['POST'])
def adicionar_item(pedido_id):
    data = request.json
    nome = data['nome']
    preco = data['preco']
    quantidade = data['quantidade']
    tipo = data['tipo']
    para_viagem = data.get('para_viagem', 0)
    total = gm.adicionar_item(pedido_id, nome, preco, quantidade, tipo, para_viagem)
    return jsonify({"total": total})

@app.route('/api/pedido/<int:pedido_id>/item/<int:item_id>', methods=['DELETE'])
def remover_item(pedido_id, item_id):
    gm.remover_item(item_id)
    return jsonify({"status": "ok"})

@app.route('/api/pedido/<int:pedido_id>/itens', methods=['GET'])
def get_itens_pedido(pedido_id):
    conn = sqlite3.connect(gm.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_item, preco_unitario, quantidade, tipo, para_viagem, entregue FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    itens = cursor.fetchall()
    conn.close()
    return jsonify([{
        "id": item[0],
        "nome": item[1],
        "preco": item[2],
        "quantidade": item[3],
        "tipo": item[4],
        "para_viagem": bool(item[5]),
        "entregue": bool(item[6])
    } for item in itens])

@app.route('/api/pedido/<int:pedido_id>/total', methods=['GET'])
def get_total_pedido(pedido_id):
    conn = sqlite3.connect(gm.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT total FROM pedidos WHERE id=?", (pedido_id,))
    row = cursor.fetchone()
    total = row[0] if row else 0
    conn.close()
    return jsonify({"total": total})

@app.route('/api/pedido/<int:pedido_id>/observacao', methods=['GET', 'POST'])
def observacao_pedido(pedido_id):
    if request.method == 'GET':
        obs = gm.obter_observacao(pedido_id)
        return jsonify({"observacao": obs})
    else:
        data = request.json
        obs = data.get('observacao', '')
        gm.salvar_observacao(pedido_id, obs)
        return jsonify({"status": "ok"})

@app.route('/api/pedido/<int:pedido_id>/enviar', methods=['POST'])
def enviar_para_cozinha(pedido_id):
    conn = sqlite3.connect(gm.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE itens_pedido SET enviado_para_cozinha=1 WHERE pedido_id=? AND entregue=0", (pedido_id,))
    cursor.execute("SELECT status FROM pedidos WHERE id=?", (pedido_id,))
    status = cursor.fetchone()[0]
    if status == "pronto":
        cursor.execute("UPDATE pedidos SET status='preparando' WHERE id=?", (pedido_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route('/api/pedido/<int:pedido_id>/fechar', methods=['POST'])
def fechar_pedido(pedido_id):
    data = request.json
    forma_pagamento = data['forma_pagamento']
    valor_recebido = data.get('valor_recebido')
    taxa_embalagem = data.get('taxa_embalagem', 0)
    pedido_fechado = gm.fechar_pedido(pedido_id, forma_pagamento, valor_recebido, taxa_embalagem)
    if pedido_fechado:
        return jsonify({
            "status": "ok",
            "mesa": pedido_fechado["mesa"],
            "total": pedido_fechado["total"],
            "itens": pedido_fechado["itens"],
            "forma_pagamento": pedido_fechado["forma_pagamento"],
            "valor_recebido": pedido_fechado["valor_recebido"],
            "taxa_embalagem": pedido_fechado["taxa_embalagem"]
        })
    else:
        return jsonify({"status": "erro", "mensagem": "Falha ao fechar pedido"}), 400

@app.route('/api/item/<int:item_id>/entregue', methods=['POST'])
def marcar_item_entregue(item_id):
    data = request.json
    entregue = data.get('entregue', 0)
    gm.marcar_item_entregue(item_id, entregue)
    return jsonify({"status": "ok"})

# Endpoints para a cozinha
@app.route('/api/pedidos/ativos', methods=['GET'])
def get_pedidos_ativos():
    pedidos = gm.listar_pedidos_ativos()
    return jsonify([{
        "id": p[0],
        "mesa_numero": p[1],
        "data_hora": p[2],
        "status": p[3],
        "total": p[4]
    } for p in pedidos])

@app.route('/api/pedido/<int:pedido_id>/detalhes', methods=['GET'])
def get_pedido_detalhes(pedido_id):
    itens = gm.obter_itens_com_status(pedido_id)
    observacao = gm.obter_observacao(pedido_id)
    return jsonify({
        "itens": [{
            "id": i[0],
            "nome": i[1],
            "quantidade": i[3],
            "para_viagem": bool(i[5]),
            "entregue": bool(i[7])
        } for i in itens],
        "observacao": observacao
    })

@app.route('/api/pedido/<int:pedido_id>/status', methods=['POST'])
def atualizar_status_pedido(pedido_id):
    data = request.json
    novo_status = data['status']
    gm.atualizar_status_pedido(pedido_id, novo_status)
    return jsonify({"status": "ok"})

# Endpoints para o histórico
@app.route('/api/cupons/meses', methods=['GET'])
def get_meses_cupons():
    pasta = "cupoms"
    if not os.path.exists(pasta):
        return jsonify([])
    meses = set()
    for item in os.listdir(pasta):
        caminho = os.path.join(pasta, item)
        if os.path.isdir(caminho) and len(item) == 7 and item[4] == '-':
            meses.add(item)
    return jsonify(sorted(meses, reverse=True))

@app.route('/api/cupons/<mes>', methods=['GET'])
def get_cupons_do_mes(mes):
    pasta = os.path.join("cupoms", mes)
    if not os.path.exists(pasta):
        return jsonify([])
    arquivos = glob.glob(os.path.join(pasta, "cupom_*.txt"))
    arquivos.sort(reverse=True)
    return jsonify([os.path.basename(arq) for arq in arquivos])

@app.route('/api/cupons/<mes>/<nome_arquivo>', methods=['GET'])
def get_cupom(mes, nome_arquivo):
    caminho = os.path.join("cupoms", mes, nome_arquivo)
    if not os.path.exists(caminho):
        return "Arquivo não encontrado", 404
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
    return conteudo

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)