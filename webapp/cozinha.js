'use strict';
const API = window.location.origin;
let pedidoExpandido = null;

async function carregarPedidos() {
  const r = await fetch(`${API}/api/pedidos/ativos`);
  const pedidos = await r.json();

  const novos = document.getElementById('col-novos');
  const preparando = document.getElementById('col-preparando');

  novos.innerHTML = '';
  preparando.innerHTML = '';

  pedidos.forEach(p => {

    const div = document.createElement('div');
    div.className = 'comanda';

    const itens = p.itens.map(i => {
      return `<li>${i.quantidade}x ${i.nome}</li>`;
    }).join('');

    div.innerHTML = `
      <h3>Mesa ${p.mesa}</h3>
      <ul>${itens}</ul>
      <button onclick="marcarStatus(${p.id}, 'preparando')">🍳 Preparando</button>
      <button onclick="marcarStatus(${p.id}, 'pronto')">✅ Pronto</button>
    `;

    if (p.status === 'ativo') {
      novos.appendChild(div);
    } else if (p.status === 'preparando') {
      preparando.appendChild(div);
    }
  });
}

function toggleCard(pedidoId, headerEl) {
  const body = document.getElementById(`body-${pedidoId}`);
  if (!body) return;
  const aberto = body.style.display !== 'none';
  // Fecha todos
  document.querySelectorAll('.card-body').forEach(b => b.style.display = 'none');
  document.querySelectorAll('.pedido-cozinha-card').forEach(c => c.classList.remove('expandido'));
  if (aberto) {
    pedidoExpandido = null;
  } else {
    body.style.display = 'block';
    headerEl.closest('.pedido-cozinha-card').classList.add('expandido');
    pedidoExpandido = pedidoId;
  }
}

async function marcarStatus(pedidoId, novoStatus) {
  await fetch(`${API}/api/pedido/${pedidoId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: novoStatus })
  });
  await carregarPedidos();
}

// Carrega e auto-atualiza a cada 10s
carregarPedidos();
setInterval(carregarPedidos, 10000);