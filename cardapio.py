import json
import os
import sys

def get_data_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def carregar_cardapio():
    caminho_externo = get_data_path("cardapio.json")
    if os.path.exists(caminho_externo):
        with open(caminho_externo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados["sopas"], dados["tapiocas"]
    caminho_embutido = get_resource_path("cardapio.json")
    if os.path.exists(caminho_embutido):
        with open(caminho_embutido, "r", encoding="utf-8") as f:
            dados = json.load(f)
        with open(caminho_externo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return dados["sopas"], dados["tapiocas"]
    # Cria padrão
    dados_padrao = {
        "sopas": [
            {"nome": "Carne", "preco": 10.0},
            {"nome": "Canja", "preco": 10.0},
            {"nome": "Costela", "preco": 17.0},
            {"nome": "4 Queijos", "preco": 18.0},
            {"nome": "Charque", "preco": 22.0},
            {"nome": "Queijo do Reino", "preco": 27.0},
            {"nome": "Africana", "preco": 18.0},
            {"nome": "Costela ao Queijo", "preco": 20.0},
            {"nome": "Camarão", "preco": 27.0},
            {"nome": "Cebola", "preco": 18.0},
            {"nome": "Batata com costela", "preco": 20.0},
            {"nome": "Batata com calabresa", "preco": 20.0}
        ],
        "tapiocas": [
            {"nome": "Coco", "preco": 10.0},
            {"nome": "Coco com Leite condensado", "preco": 15.0},
            {"nome": "Queijo coalho", "preco": 12.0},
            {"nome": "Queijo coalho com Coco", "preco": 15.0},
            {"nome": "Queijo coalho com Coco e Leite condensado", "preco": 17.0},
            {"nome": "Franco com Queijo Coalho", "preco": 17.0},
            {"nome": "Pizza", "preco": 17.0},
            {"nome": "Charque com Queijo Coalho", "preco": 22.0},
            {"nome": "Camarão", "preco": 25.0},
            {"nome": "Queijo do Reino", "preco": 25.0}
        ]
    }
    with open(caminho_externo, "w", encoding="utf-8") as f:
        json.dump(dados_padrao, f, indent=4, ensure_ascii=False)
    return dados_padrao["sopas"], dados_padrao["tapiocas"]

# Carrega os dados ao importar o módulo
cardapio, tapioca = carregar_cardapio()