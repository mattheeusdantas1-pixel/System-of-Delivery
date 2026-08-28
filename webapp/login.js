'use strict';

const API = window.location.origin;

async function fazerLogin(event) {
  event.preventDefault();

  const email = document.getElementById('email').value.trim();
  const senha = document.getElementById('senha').value;
  const errorDiv = document.getElementById('errorMessage');
  const loadingDiv = document.getElementById('loading');
  const loginForm = document.getElementById('loginForm');

  // Limpar erro anterior
  errorDiv.style.display = 'none';
  errorDiv.textContent = '';

  // Mostrar loading
  loadingDiv.style.display = 'block';
  loginForm.style.display = 'none';

  try {
    const response = await fetch(`${API}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, senha })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.msg || 'Erro ao fazer login');
    }

    // Salvar token e usuário no localStorage
    localStorage.setItem('token', data.token);
    localStorage.setItem('usuario', JSON.stringify(data.usuario));

    // Redirecionar para página inicial
    window.location.href = '/';

  } catch (error) {
    loadingDiv.style.display = 'none';
    loginForm.style.display = 'block';
    errorDiv.textContent = '❌ ' + error.message;
    errorDiv.style.display = 'block';
    document.getElementById('senha').value = '';
    document.getElementById('email').focus();
  }
}

// Verificar se já está logado
function verificarAutenticacao() {
  const token = localStorage.getItem('token');
  if (token) {
    // Se já tem token, redireciona para home
    window.location.href = '/';
  }
}

// Executar ao carregar
document.addEventListener('DOMContentLoaded', verificarAutenticacao);
