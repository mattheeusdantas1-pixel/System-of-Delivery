'use strict';
const API = window.location.origin;
let cupomAtual = null;

async function carregarMeses() {
  const r = await fetch(`${API}/api/cupons/meses`);
  const meses = await r.json();
  const lista = document.getElementById('meses-lista');
  lista.innerHTML = '';
  if (meses.length === 0) { lista.innerHTML = '<p style="color:#999">Nenhum cupom.</p>'; return; }
  meses.forEach(mes => {
    const btn = document.createElement('button');
    btn.className = 'mes-btn';
    btn.textContent = mes;
    btn.onclick = () => { document.querySelectorAll('.mes-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); carregarCupons(mes); };
    lista.appendChild(btn);
  });
  // Abre o mês mais recente automaticamente
  lista.firstChild.click();
}

async function carregarCupons(mes) {
  const r = await fetch(`${API}/api/cupons/${mes}`);
  const cupons = await r.json();
  const lista = document.getElementById('cupons-lista');
  lista.innerHTML = '';
  document.getElementById('cupom-box').style.display = 'none';
  if (cupons.length === 0) { lista.innerHTML = '<p style="color:#999">Nenhum cupom neste mês.</p>'; return; }
  cupons.forEach(nome => {
    const btn = document.createElement('button');
    btn.className = 'cupom-btn';
    btn.textContent = nome;
    btn.onclick = () => { document.querySelectorAll('.cupom-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); verCupom(mes, nome); };
    lista.appendChild(btn);
  });
}

let cupomMesAtual = '';
let cupomNomeAtual = '';

async function verCupom(mes, nome) {
  const r = await fetch(`${API}/api/cupons/${mes}/${nome}`);
  const texto = await r.text();
  cupomAtual = texto;
  cupomMesAtual = mes;
  cupomNomeAtual = nome;
  document.getElementById('cupom-conteudo').textContent = texto;
  document.getElementById('cupom-box').style.display = 'block';
}

function reimprimirCupom() {
  if (!cupomAtual) return;
  const w = window.open('', '_blank');
  w.document.write(`<pre style="font-family:monospace;font-size:0.85em">${cupomAtual}</pre>`);
  w.print();
}

function whatsappCupom() {
  if (!cupomAtual) return;
  window.open(`https://wa.me/?text=${encodeURIComponent(cupomAtual)}`);
}

async function excluirCupom() {
  if (!cupomAtual || !cupomNomeAtual || !cupomMesAtual) return;
  if (!confirm('Tem certeza que deseja excluir este cupom?')) return;

  try {
    const r = await fetch(`${API}/api/cupons/${cupomMesAtual}/${cupomNomeAtual}`, {
      method: 'DELETE'
    });
    const d = await r.json();
    if (d.status === 'ok') {
      alert('Cupom excluído com sucesso');
      document.getElementById('cupom-box').style.display = 'none';
      cupomAtual = null;
      cupomMesAtual = '';
      cupomNomeAtual = '';
      const mesAtivo = document.querySelector('.mes-btn.active');
      if (mesAtivo) {
        carregarCupons(mesAtivo.textContent);
      }
    } else {
      alert('Erro ao excluir cupom');
    }
  } catch (e) {
    alert('Erro: ' + e);
  }
}

function abrirCalculadoraEntregas() {
  const data = document.getElementById('data-calculo').value;
  if (!data) {
    alert('Selecione uma data');
    return;
  }
  carregarCalculadoraEntregas(data);
}

async function carregarCalculadoraEntregas(data) {
  try {
    const r = await fetch(`${API}/api/calculo-entregas?data=${data}`);
    const d = await r.json();

    let html = `<strong style="color:#6C5CE7">Cálculo de Entregas - ${data}</strong><br><br>`;
    html += `<strong>Resumo do Dia</strong><br>`;
    html += `Total de Entregas: ${d.total_entregas}<br>`;
    html += `Faturamento Total: R$ ${d.faturamento_total.toFixed(2)}<br>`;
    html += `Total de Taxas: R$ ${d.total_taxas.toFixed(2)}<br><br>`;

    html += `<strong>Detalhes por Entregador (Simulado)</strong><br>`;
    html += `Neste momento, você pode atualizar manualmente o sistema<br>`;
    html += `com os dados de entregas de cada entregador.<br><br>`;

    html += `<strong>Entregadores</strong><br>`;
    d.entregas.forEach((e, idx) => {
      html += `${idx + 1}. ${e.cliente} - R$ ${e.valor.toFixed(2)}<br>`;
    });

    document.getElementById('calculo-conteudo').innerHTML = html;
    document.getElementById('modal-calculadora').style.display = 'flex';
  } catch (e) {
    alert('Erro ao carregar cálculo: ' + e);
  }
}

function fecharCalculadora() {
  document.getElementById('modal-calculadora').style.display = 'none';
}

// Define data de hoje como padrão
const hoje = new Date().toISOString().split('T')[0];
document.getElementById('data-calculo').value = hoje;

carregarMeses();