# logica.py

def calcular_total(vars_sopas, cardapio, vars_tapioca, tapioca, bebida_valor, entrega_valor):
    total = 0.0

    # Soma das sopas
    for i, item in enumerate(cardapio):
        total += vars_sopas[i].get() * item["preco"]

    # Soma das tapiocas
    for i, item in enumerate(tapioca):
        total += vars_tapioca[i].get() * item["preco"]

    # Bebida avulsa
    if bebida_valor:
        total += bebida_valor

    # Taxa de entrega
    if entrega_valor:
        total += entrega_valor

    return total