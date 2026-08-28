'use strict';

// Usa o próprio endereço de onde a página foi carregada
// Se acessou http://192.168.15.9:5000, API = http://192.168.15.9:5000
// Funciona no navegador do celular, tablet, qualquer dispositivo
const API = window.location.origin;

// ========== ESTADO GLOBAL ==========
let cardapio = { sopas: [], tapiocas: [] };
let mesaAtual = null;
let pedidoId = null;
let totalAtual = 0;
let cupomTextoAtual = '';

// ========== INICIALIZAR ==========
async function iniciarApp() {
    await carregarCardapio();
    await carregarMesas();
    setInterval(carregarMesas, 20000);
}

// ========== NAVEGAÇÃO ==========
function mostrarTela(id) {
    document.querySelectorAll('.tela').forEach(t => t.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// ========== ABAS ==========
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// ========== CARDÁPIO ==========
async function carregarCardapio() {
    try {
        const r = await fetch(`${API}/api/cardapio`, {
            headers: AUTH.obterHeaders()
        });
        cardapio = await r.json();
    } catch (e) { console.error('Erro cardápio', e); }
}

// ========== MESAS ==========
async function carregarMesas() {
    try {
        const r = await fetch(`${API}/api/mesas`, {
            headers: AUTH.obterHeaders()
        });
        const mesas = await r.json();
        const grid = document.getElementById('mesas-grid');
        grid.innerHTML = '';
        mesas.forEach(m => {
            const card = document.createElement('div');
            const livre = m.status === 'livre';
            const ps = m.pedido_status;
            let statusLabel = livre ? '🟢 LIVRE' : '🔴 OCUPADA';
            let pedidoLabel = '';
            if (!livre) {
                if (ps === 'preparando') pedidoLabel = '<div class="pedido-badge preparando">🍳 Preparando</div>';
                else if (ps === 'pronto') pedidoLabel = '<div class="pedido-badge pronto">✅ Pronto!</div>';
                else pedidoLabel = '<div class="pedido-badge aguardando">⏳ Aguardando</div>';
            }
            card.className = `mesa-card ${livre ? 'livre' : 'ocupada'}`;
            card.innerHTML = `<div class="mesa-num">Mesa ${m.numero}</div>
                <div class="mesa-status-label">${statusLabel}</div>${pedidoLabel}`;
            card.onclick = () => abrirMesa(m);
            grid.appendChild(card);
        });
        document.getElementById('info-conexao').textContent = `✅ ${mesas.length} mesas`;
        document.getElementById('info-conexao').className = 'badge badge-ok';
    } catch (e) {
        document.getElementById('info-conexao').textContent = '❌ Offline';
        document.getElementById('info-conexao').className = 'badge badge-erro';
    }
}

// ========== ABRIR MESA ==========
async function abrirMesa(mesa) {
    mesaAtual = mesa;
    document.getElementById('titulo-mesa').textContent = `Mesa ${mesa.numero}`;
    const r = await fetch(`${API}/api/mesa/${mesa.id}/pedido`, { method: 'POST' });
    const d = await r.json();
    pedidoId = d.pedido_id;
    await carregarPedido();
    renderizarProdutos('sopas', 'lista-sopas');
    renderizarProdutos('tapiocas', 'lista-tapiocas');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('[data-tab="tab-sopas"]').classList.add('active');
    document.getElementById('tab-sopas').classList.add('active');
    mostrarTela('tela-pedido');
}

async function voltarParaMesas() {
    mesaAtual = null;
    pedidoId = null;
    mostrarTela('tela-mesas');
    await carregarMesas();
}

// ========== PEDIDO ==========
async function carregarPedido() {
    if (!pedidoId) return;
    const [rItens, rTotal, rObs, rStatus] = await Promise.all([
        fetch(`${API}/api/pedido/${pedidoId}/itens`),
        fetch(`${API}/api/pedido/${pedidoId}/total`),
        fetch(`${API}/api/pedido/${pedidoId}/observacao`),
        fetch(`${API}/api/pedido/${pedidoId}/status`)
    ]);
    const itens = await rItens.json();
    const { total } = await rTotal.json();
    const { observacao } = await rObs.json();
    const { status } = await rStatus.json();
    totalAtual = total;
    document.getElementById('total-valor').textContent = total.toFixed(2);
    document.getElementById('obs-texto').value = observacao || '';
    const badge = document.getElementById('badge-status');
    const labels = { ativo: '⏳ Aguardando', preparando: '🍳 Preparando', pronto: '✅ Pronto' };
    badge.textContent = labels[status] || status || '';
    badge.className = `badge badge-${status || 'ativo'}`;
    const lista = document.getElementById('itens-pedido');
    lista.innerHTML = '';
    if (itens.length === 0) {
        lista.innerHTML = '<p class="vazio">Nenhum item ainda.</p>';
        return;
    }
    itens.forEach(item => {
        const div = document.createElement('div');
        div.className = `item-linha ${item.entregue ? 'entregue' : ''}`;
        const tagViagem = item.para_viagem ? ' <span class="tag-viagem">🧳 Viagem</span>' : '';
        const tagNovo = !item.enviado ? ' <span class="tag-novo">🆕</span>' : '';
        div.innerHTML = `
            <div class="item-info">
                <label><input type="checkbox" ${item.entregue ? 'checked' : ''} onchange="marcarEntregue(${item.id}, this.checked)"></label>
                <span class="item-nome">${item.nome}${tagViagem}${tagNovo}</span>
                <span class="item-qtd">${item.quantidade}x — R$${(item.preco * item.quantidade).toFixed(2)}</span>
            </div>
            <button class="btn-remover" onclick="removerItem(${item.id})" ${item.entregue ? 'disabled' : ''}>🗑</button>
        `;
        lista.appendChild(div);
    });
}

// ========== PRODUTOS ==========
function renderizarProdutos(categoria, containerId) {
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
                <label class="viagem-label"><input type="checkbox" class="chk-viagem"> Viagem</label>
                <div class="qtd-controle">
                    <button class="btn-qtd menos">−</button>
                    <span class="qtd-num">0</span>
                    <button class="btn-qtd mais">+</button>
                </div>
            </div>
        `;
        const qtdSpan = div.querySelector('.qtd-num');
        const chkViagem = div.querySelector('.chk-viagem');
        div.querySelector('.btn-qtd.mais').addEventListener('click', async () => {
            const pv = chkViagem.checked ? 1 : 0;
            await fetch(`${API}/api/pedido/${pedidoId}/item`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome: prod.nome, preco: prod.preco, quantidade: 1, tipo, para_viagem: pv })
            });
            qtdSpan.textContent = parseInt(qtdSpan.textContent) + 1;
            await carregarPedido();
        });
        div.querySelector('.btn-qtd.menos').addEventListener('click', async () => {
            const atual = parseInt(qtdSpan.textContent);
            if (atual <= 0) return;
            await fetch(`${API}/api/pedido/${pedidoId}/item`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome: prod.nome, preco: prod.preco, quantidade: -1, tipo, para_viagem: 0 })
            });
            qtdSpan.textContent = Math.max(0, atual - 1);
            await carregarPedido();
        });
        container.appendChild(div);
    });
}

// ========== BEBIDA ==========
async function adicionarBebida() {
    const nome = document.getElementById('bebida-nome').value.trim();
    const preco = parseFloat(document.getElementById('bebida-preco').value);
    if (!nome || isNaN(preco) || preco <= 0) { alert('Preencha nome e preço.'); return; }
    await fetch(`${API}/api/pedido/${pedidoId}/item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, preco, quantidade: 1, tipo: 'bebida_personalizada', para_viagem: 0 })
    });
    document.getElementById('bebida-nome').value = '';
    document.getElementById('bebida-preco').value = '';
    await carregarPedido();
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('[data-tab="tab-pedido"]').classList.add('active');
    document.getElementById('tab-pedido').classList.add('active');
}

async function removerItem(itemId) {
    await fetch(`${API}/api/pedido/${pedidoId}/item/${itemId}`, { method: 'DELETE' });
    await carregarPedido();
}

async function salvarObs() {
    const obs = document.getElementById('obs-texto').value;
    await fetch(`${API}/api/pedido/${pedidoId}/observacao`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ observacao: obs })
    });
}

async function enviarCozinha() {
    await salvarObs();
    const r = await fetch(`${API}/api/pedido/${pedidoId}/enviar`, { method: 'POST' });
    const d = await r.json();
    if (d.novos === 0) alert('Nenhum item novo para enviar.');
    await carregarPedido();
}

// ========== FECHAR CONTA ==========
function abrirFecharConta() {
    document.getElementById('modal-mesa-info').textContent = `Mesa ${mesaAtual.numero} — Total: R$ ${totalAtual.toFixed(2)}`;
    document.querySelectorAll('input[name="pagamento"]').forEach(r => {
        r.onchange = () => {
            document.getElementById('grupo-dinheiro').style.display = (r.value === 'dinheiro' && r.checked) ? 'block' : 'none';
            atualizarTotalModal();
        };
    });
    document.getElementById('grupo-dinheiro').style.display = 'none';
    document.getElementById('chk-dividir').checked = false;
    document.getElementById('grupo-dividir').style.display = 'none';
    document.getElementById('chk-embalagem').checked = false;
    document.getElementById('grupo-embalagem').style.display = 'none';
    document.getElementById('valor-recebido').value = '';
    document.getElementById('info-troco').textContent = '';
    document.getElementById('info-divisao').textContent = '';
    atualizarTotalModal();
    document.getElementById('modal-fechar').style.display = 'flex';
}

function fecharModal() { document.getElementById('modal-fechar').style.display = 'none'; }

function toggleDividir() {
    const show = document.getElementById('chk-dividir').checked;
    document.getElementById('grupo-dividir').style.display = show ? 'block' : 'none';
    if (show) calcularDivisao();
}

function toggleEmbalagem() {
    const show = document.getElementById('chk-embalagem').checked;
    document.getElementById('grupo-embalagem').style.display = show ? 'block' : 'none';
    atualizarTotalModal();
}

function totalComEmbalagem() {
    let t = totalAtual;
    if (document.getElementById('chk-embalagem').checked) {
        t += (parseInt(document.getElementById('qtd-embalagem').value) || 0) * 2;
    }
    return t;
}

function atualizarTotalModal() {
    const t = totalComEmbalagem();
    document.getElementById('total-modal').textContent = `Total: R$ ${t.toFixed(2)}`;
    calcularTroco();
    calcularDivisao();
}

function calcularTroco() {
    const t = totalComEmbalagem();
    const rec = parseFloat(document.getElementById('valor-recebido').value);
    const el = document.getElementById('info-troco');
    if (!isNaN(rec)) {
        const troco = rec - t;
        el.textContent = troco >= 0 ? `Troco: R$ ${troco.toFixed(2)}` : '⚠️ Valor insuficiente';
        el.style.color = troco >= 0 ? '#00B894' : '#E17055';
    } else el.textContent = '';
}

function calcularDivisao() {
    if (!document.getElementById('chk-dividir').checked) return;
    const t = totalComEmbalagem();
    const p = parseInt(document.getElementById('num-pessoas').value) || 1;
    document.getElementById('info-divisao').textContent = `R$ ${(t / p).toFixed(2)} por pessoa`;
}

async function confirmarFechamento() {
    const forma = document.querySelector('input[name="pagamento"]:checked').value;
    let valorRec = null;
    const t = totalComEmbalagem();
    if (forma === 'dinheiro') {
        valorRec = parseFloat(document.getElementById('valor-recebido').value);
        if (isNaN(valorRec) || valorRec < t) { alert('Valor insuficiente ou inválido.'); return; }
    }
    const taxa = document.getElementById('chk-embalagem').checked
        ? (parseInt(document.getElementById('qtd-embalagem').value) || 0) * 2 : 0;
    const r = await fetch(`${API}/api/pedido/${pedidoId}/fechar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ forma_pagamento: forma, valor_recebido: valorRec, taxa_embalagem: taxa })
    });
    const d = await r.json();
    if (d.status !== 'ok') { alert('Erro ao fechar conta.'); return; }
    fecharModal();
    cupomTextoAtual = d.cupom;
    document.getElementById('cupom-texto').textContent = d.cupom;
    document.getElementById('modal-cupom').style.display = 'flex';
}

function enviarWhatsapp() {
    if (!cupomTextoAtual) return;
    window.open(`https://wa.me/?text=${encodeURIComponent(cupomTextoAtual)}`);
}

async function marcarEntregue(itemId, entregue) {
    await fetch(`${API}/api/item/${itemId}/entregue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entregue: entregue ? 1 : 0 })
    });
    await carregarPedido();
}

// Inicia
iniciarApp();