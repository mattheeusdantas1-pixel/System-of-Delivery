'use strict';

/**
 * auth-client.js - Gerenciamento de Autenticação no Frontend
 * Verifica token, armazena usuário e intercepta requisições
 */

const AUTH = {
  token: localStorage.getItem('token'),
  usuario: JSON.parse(localStorage.getItem('usuario') || 'null'),

  temToken() {
    return !!this.token;
  },

  obterHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  },

  async verificar() {
    if (!this.token) {
      window.location.href = '/login.html';
      return false;
    }

    try {
      const response = await fetch(`${window.location.origin}/api/verificar-token`, {
        method: 'POST',
        headers: this.obterHeaders()
      });

      if (!response.ok) {
        // Token inválido
        this.logout();
        return false;
      }

      const data = await response.json();
      this.usuario = data.usuario;
      localStorage.setItem('usuario', JSON.stringify(this.usuario));
      return true;

    } catch (error) {
      console.error('Erro ao verificar token:', error);
      this.logout();
      return false;
    }
  },

  temAcesso(modulo) {
    const ACESSOS = {
      'admin': ['mesas', 'delivery', 'cozinha', 'historico', 'entregas'],
      'garcom': ['mesas', 'delivery'],
      'cozinha': ['cozinha'],
      'entregador': ['delivery']
    };

    if (!this.usuario) return false;
    const permissoes = ACESSOS[this.usuario.perfil] || [];
    return permissoes.includes(modulo);
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    window.location.href = '/login.html';
  },

  exibirUsuario() {
    if (!this.usuario) return '';
    return `👤 ${this.usuario.nome} (${this.usuario.perfil.toUpperCase()})`;
  }
};

// Verificar autenticação ao carregar página
document.addEventListener('DOMContentLoaded', async () => {
  const paginasPublicas = ['/login.html', '/login'];

  // Se está em página pública, não verifica
  if (paginasPublicas.includes(window.location.pathname)) {
    return;
  }

  // Verificar token em páginas privadas
  const autenticado = await AUTH.verificar();
  if (!autenticado && !paginasPublicas.includes(window.location.pathname)) {
    window.location.href = '/login.html';
  }
});
