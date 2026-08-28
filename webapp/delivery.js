'use strict';

const API = window.location.origin;
let cardapio = { sopas: [], tapiocas: [] };
let pedidoAtualDelivery = null;
let cupomTextoDelivery = '';
let cupomAtualMes = '';
let cupomAtualNome = '';

async function iniciarAppDelivery() {
    await carregarCardapioDelivery();
    renderizarProdutosDelivery('sopas', 'lista-sopas-delivery');
    renderizarProdutosDelivery('tapiocas', 'lista-tapiocas-delivery');
    configurarAbas();
    carregarPedidosDelivery();
    setInterval(carregarPedidosDelivery, 15000);
}

async function carregarCardapioDelivery() {
    try {
        const r = await fetch(`${API}/api/cardapio`);
        cardapio = await r.json();
    } catch (e) { console.error('Erro cardápio', e); }
}

function configurarAbas() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });
}

function renderizarProdutosDelivery(categoria, containerId) {
    const produtos = categoria === 'sopas' ? cardapio.sopas : cardapio.tapiocas;
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    produtos.forEach(prod => {
        const tipo = categoria === 'sopas' ? 'sopa' : 'tapioca';
        const div = document.createElement('div');
        div.className = 'produto-card';
        div.innerHTML = `
            <div class="prod-info"><span class="prod-nome">${prod.nome}</span><span class="prod-preco">R$ ${prod.preco.toFixed(2)}</span></div>
            <div class="prod-controles">
                <div class="qtd-controle">
                    <button class="btn-qtd menos">−</button>
                    <span class="qtd-num">0</span>
                    <button class="btn-qtd mais">+</button>
                </div>
            </div>
        `;
        const qtdSpan = div.querySelector('.qtd-num');
        div.querySelector('.btn-qtd.mais').addEventListener('click', async () => {
            const tipo_entrega = document.querySelector('input[name="tipo-entrega"]:checked').value;
            await adicionarItemDelivery(prod.nome, prod.preco, tipo, tipo_entrega);
            qtdSpan.textContent = parseInt(qtdSpan.textContent) + 1;
        });
        div.querySelector('.btn-qtd.menos').addEventListener('click', async () => {
            const atual = parseInt(qtdSpan.textContent);
            if (atual <= 0) return;
            const tipo_entrega = document.querySelector('input[name="tipo-entrega"]:checked').value;
            await removerItemDelivery(prod.nome, tipo, tipo_entrega);
            qtdSpan.textContent = Math.max(0, atual - 1);
        });
        container.appendChild(div);
    });
}

async function adicionarItemDelivery(nome, preco, tipo, tipo_entrega) {
    if (!pedidoAtualDelivery) {
        criarPedidoDelivery();
    }
    if (!pedidoAtualDelivery) return;

    const item = {
        nome, preco, tipo, tipo_entrega,
        quantidade: 1
    };

    if (!pedidoAtualDelivery.itens) pedidoAtualDelivery.itens = [];
    const existente = pedidoAtualDelivery.itens.find(i => i.nome === nome && i.tipo === tipo && i.tipo_entrega === tipo_entrega);
    if (existente) {
        existente.quantidade += 1;
    } else {
        pedidoAtualDelivery.itens.push(item);
    }

    atualizarPedidoDelivery();
}

async function removerItemDelivery(nome, tipo, tipo_entrega) {
    if (!pedidoAtualDelivery) return;
    const existente = pedidoAtualDelivery.itens.find(i => i.nome === nome && i.tipo === tipo && i.tipo_entrega === tipo_entrega);
    if (existente) {
        existente.quantidade -= 1;
        if (existente.quantidade <= 0) {
            pedidoAtualDelivery.itens = pedidoAtualDelivery.itens.filter(i => i !== existente);
        }
    }
    atualizarPedidoDelivery();
}

function adicionarBebidaDelivery() {
    const nome = document.getElementById('bebida-nome-delivery').value.trim();
    const preco = parseFloat(document.getElementById('bebida-preco-delivery').value);
    if (!nome || isNaN(preco) || preco <= 0) { alert('Preencha nome e preço.'); return; }

    if (!pedidoAtualDelivery) {
        criarPedidoDelivery();
    }
    if (!pedidoAtualDelivery) return;

    const tipo_entrega = document.querySelector('input[name="tipo-entrega"]:checked').value;
    const existente = pedidoAtualDelivery.itens.find(i => i.nome === nome && i.tipo === 'bebida' && i.tipo_entrega === tipo_entrega);
    if (existente) {
        existente.quantidade += 1;
    } else {
        pedidoAtualDelivery.itens.push({
            nome, preco, tipo: 'bebida', tipo_entrega,
            quantidade: 1
        });
    }

    document.getElementById('bebida-nome-delivery').value = '';
    document.getElementById('bebida-preco-delivery').value = '';
    atualizarPedidoDelivery();
}

function criarPedidoDelivery() {
    pedidoAtualDelivery = {
        cliente_nome: '',
        cliente_telefone: '',
        cliente_endereco: '',
        tipo_entrega: 'normal',
        itens: [],
        observacoes: ''
    };
}

function atualizarPedidoDelivery() {
    if (!pedidoAtualDelivery) return;

    const lista = document.getElementById('itens-delivery');
    lista.innerHTML = '';

    let subtotal = 0;
    pedidoAtualDelivery.itens.forEach((item, idx) => {
        const sub = item.preco * item.quantidade;
        subtotal += sub;
        const div = document.createElement('div');
        div.className = 'item-linha';
        div.innerHTML = `
            <div class="item-info">
                <span class="item-nome">${item.nome}</span>
                <span class="item-qtd">${item.quantidade}x — R$${(item.preco * item.quantidade).toFixed(2)}</span>
            </div>
            <button class="btn-remover" onclick="removerItemDeliveryItem(${idx})">🗑</button>
        `;
        lista.appendChild(div);
    });

    const taxa = pedidoAtualDelivery.tipo_entrega === 'normal' ? 5.00 : 0;
    const total = subtotal + taxa;

    document.getElementById('subtotal-delivery').textContent = subtotal.toFixed(2);
    document.getElementById('taxa-delivery').textContent = taxa.toFixed(2);
    document.getElementById('total-delivery').textContent = total.toFixed(2);
}

function removerItemDeliveryItem(idx) {
    if (!pedidoAtualDelivery) return;
    pedidoAtualDelivery.itens.splice(idx, 1);
    atualizarPedidoDelivery();
}

async function confirmarDelivery() {
    const nome = document.getElementById('cliente-nome').value.trim();
    const telefone = document.getElementById('cliente-telefone').value.trim();
    const endereco = document.getElementById('cliente-endereco').value.trim();

    if (!nome || !telefone || !endereco) {
        alert('Preencha todos os campos de cliente.');
        return;
    }

    if (!pedidoAtualDelivery || pedidoAtualDelivery.itens.length === 0) {
        alert('Adicione itens ao pedido.');
        return;
    }

    const tipo_entrega = document.querySelector('input[name="tipo-entrega"]:checked').value;
    pedidoAtualDelivery.cliente_nome = nome;
    pedidoAtualDelivery.cliente_telefone = telefone;
    pedidoAtualDelivery.cliente_endereco = endereco;
    pedidoAtualDelivery.tipo_entrega = tipo_entrega;
    pedidoAtualDelivery.observacoes = document.getElementById('obs-delivery').value.trim();

    try {
        const r = await fetch(`${API}/api/pedido-delivery`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pedidoAtualDelivery)
        });
        const d = await r.json();
        if (d.status === 'ok') {
            cupomTextoDelivery = d.cupom;
            document.getElementById('cupom-delivery-texto').textContent = d.cupom;
            document.getElementById('modal-cupom-delivery').style.display = 'flex';

            // Limpa formulário
            document.getElementById('cliente-nome').value = '';
            document.getElementById('cliente-telefone').value = '';
            document.getElementById('cliente-endereco').value = '';
            document.getElementById('obs-delivery').value = '';
            pedidoAtualDelivery = null;
            atualizarPedidoDelivery();

            await carregarPedidosDelivery();
        } else {
            alert('Erro ao confirmar pedido.');
        }
    } catch (e) {
        alert('Erro: ' + e);
    }
}

function fecharModalDelivery() {
    document.getElementById('modal-cupom-delivery').style.display = 'none';
}

function imprimirDelivery() {
    if (!cupomTextoDelivery) return;
    const w = window.open('', '_blank');
    w.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
        body { margin:0; padding:0; font-family:monospace; }
        pre { margin:0; padding:0; font-size:0.75em; line-height:1.1; width:58mm; white-space:pre-wrap; word-wrap:break-word; }
        @media print { body { margin:0; padding:0; } }
    </style></head><body><pre>${cupomTextoDelivery}</pre></body></html>`);
    setTimeout(() => { w.print(); }, 500);
}

async function carregarPedidosDelivery() {
    try {
        const r = await fetch(`${API}/api/pedidos-delivery/ativos`);
        const pedidos = await r.json();
        const lista = document.getElementById('lista-pedidos-delivery');
        lista.innerHTML = '';

        if (pedidos.length === 0) {
            lista.innerHTML = '<p style="color:#999;text-align:center">Nenhum pedido ativo</p>';
            return;
        }

        pedidos.forEach(p => {
            const card = document.createElement('div');
            card.className = `pedido-delivery-card status-${p.status}`;
            const itensHtml = p.itens.map(i => `${i.quantidade}x ${i.nome}`).join('<br>');
            const iconEntrega = p.tipo_entrega === 'normal' ? '🚴' : (p.tipo_entrega === 'uber_flash' ? '🚗' : '🚗');

            card.innerHTML = `
                <div class="delivery-header">
                    <div>
                        <strong>${p.cliente_nome}</strong>
                        <div style="font-size:0.8rem;color:#636E72">${iconEntrega} ${p.tipo_entrega}</div>
                    </div>
                    <div class="status-badge">${p.status}</div>
                </div>
                <div class="delivery-info">
                    <div>📱 ${p.cliente_telefone}</div>
                    <div>📍 ${p.cliente_endereco}</div>
                </div>
                <div class="delivery-itens">${itensHtml}</div>
                <div class="delivery-total">Total: R$ ${p.total.toFixed(2)}</div>
                <div class="delivery-controls">
                    <select onchange="atualizarStatusDelivery(${p.id}, this.value)" class="input-field">
                        <option value="pendente" ${p.status === 'pendente' ? 'selected' : ''}>⏳ Pendente</option>
                        <option value="preparando" ${p.status === 'preparando' ? 'selected' : ''}>🍳 Preparando</option>
                        <option value="pronto" ${p.status === 'pronto' ? 'selected' : ''}>✅ Pronto</option>
                        <option value="em_entrega" ${p.status === 'em_entrega' ? 'selected' : ''}>🚴 Em Entrega</option>
                        <option value="entregue" ${p.status === 'entregue' ? 'selected' : ''}>🎉 Entregue</option>
                    </select>
                </div>
            `;
            lista.appendChild(card);
        });
    } catch (e) {
        console.error('Erro ao carregar pedidos delivery', e);
    }
}

async function atualizarStatusDelivery(pedidoId, novoStatus) {
    try {
        const r = await fetch(`${API}/api/pedido-delivery/${pedidoId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: novoStatus })
        });
        const d = await r.json();
        if (d.status === 'ok') {
            await carregarPedidosDelivery();
        }
    } catch (e) {
        alert('Erro ao atualizar status: ' + e);
    }
}

iniciarAppDelivery();
