# 🍲 Sistema de Pedidos - Sopa da Roxa

Um sistema completo de gerenciamento de pedidos para restaurante, desenvolvido com **Flask** (backend) e **HTML/CSS/JavaScript** (frontend), com suporte para mesas, delivery, cozinha e histórico de vendas.

## 🎯 Características

### 📋 Funcionalidades Principais
- **Gestão de Mesas**: Controle de 12 mesas com status (livre, ocupada, reservada)
- **Sistema de Pedidos Presenciais**: Adicionar itens, observações e gerar cupom
- **Sistema de Delivery**: 3 tipos de entrega (Normal R$5, Uber Flash, 99 Flash)
- **Painel da Cozinha**: Visualizar pedidos com status em tempo real
- **Histórico de Vendas**: Registrar todos os pedidos finalizados
- **Calculadora de Entregas**: Cálculo automático de entregas por data
- **Exclusão de Pedidos**: Remover pedidos do histórico quando necessário
- **Impressão Térmica**: Suporte para impressora térmica 58mm

### 🎨 Identidade Visual
- Tema roxo predominante (#7c3aed) - Identidade "Sopa da Roxa"
- Interface responsiva para desktop, tablet e mobile
- Design limpo e intuitivo

### 🔧 Tecnologias

**Backend:**
- Python 3.x
- Flask
- SQLite3
- CORS habilitado

**Frontend:**
- HTML5
- CSS3 (com variáveis CSS)
- JavaScript vanilla
- PWA (Progressive Web App)

## 📦 Estrutura do Projeto

```
SistemaPedidos/
├── webapp/                    # Frontend (HTML, CSS, JS)
│   ├── index.html            # Página principal (Mesas)
│   ├── delivery.html         # Página de Delivery
│   ├── cozinha.html          # Painel da Cozinha
│   ├── historico.html        # Histórico de Vendas
│   ├── style.css             # Estilos principais
│   ├── style-delivery.css    # Estilos do Delivery
│   ├── style-cozinha.css     # Estilos da Cozinha
│   ├── style-historico.css   # Estilos do Histórico
│   ├── script.js             # Lógica das Mesas
│   ├── delivery.js           # Lógica do Delivery
│   ├── cozinha.js            # Lógica da Cozinha
│   └── historico.js          # Lógica do Histórico
├── server.py                 # Servidor Flask principal
├── app.py                    # Interface Tkinter + Servidor
├── gerenciador_mesas.py      # Gerenciador de dados
├── cardapio.py               # Cardápio de produtos
├── database.db               # Banco de dados SQLite
└── README.md                 # Este arquivo
```

## 🚀 Como Usar

### Requisitos
- Python 3.8+
- Flask
- Flask-CORS

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/mattheeusdantas1-pixel/System-of-Delivery.git
cd System-of-Delivery

# 2. Instalar dependências
pip install flask flask-cors

# 3. Executar a aplicação
python app.py
```

### Acessar

- **Local**: `http://localhost:5000`
- **Rede**: `http://<seu-ip>:5000`

## 📱 Módulos

### 1. Mesas (index.html)
- Visualizar todas as mesas em grid
- Clicar em mesa para abrir formulário de pedido
- Adicionar itens, bebidas customizadas e observações
- Enviar para cozinha ou fechar conta
- Pagamento: PIX, Cartão, Dinheiro (com cálculo de troco)

### 2. Delivery (delivery.html) - **NOVO**
- Cadastrar pedido com dados do cliente
- Selecionar tipo de entrega
- Adicionar itens do cardápio
- Controlar status (Pendente → Preparando → Pronto → Em Entrega → Entregue)
- Gerar cupom para impressora térmica

### 3. Cozinha (cozinha.html)
- Visualizar pedidos confirmados
- Alterar status: Preparando → Pronto
- Destacar pedidos por cor
- Visualizar observações importantes

### 4. Histórico (historico.html)
- Filtrar cupons por mês
- Visualizar detalhes de cada venda
- **Calculadora de Entregas** - Cálculo automático por data
- **Excluir cupons** - Remover registros quando necessário
- Reimprir cupom ou enviar por WhatsApp

## 🔌 API Endpoints

### Cardápio
- `GET /api/cardapio` - Retorna sopas e tapiocas

### Mesas
- `GET /api/mesas` - Lista todas as mesas
- `POST /api/mesa/<id>/pedido` - Criar pedido para mesa

### Pedidos
- `GET /api/pedido/<id>/itens` - Itens do pedido
- `GET /api/pedido/<id>/total` - Total do pedido
- `POST /api/pedido/<id>/item` - Adicionar item
- `DELETE /api/pedido/<id>/item/<item_id>` - Remover item
- `POST /api/pedido/<id>/fechar` - Fechar conta

### Delivery - **NOVO**
- `POST /api/pedido-delivery` - Criar pedido delivery
- `GET /api/pedidos-delivery/ativos` - Listar pedidos ativos
- `POST /api/pedido-delivery/<id>/status` - Atualizar status

### Entregas - **NOVO**
- `GET /api/calculo-entregas?data=YYYY-MM-DD` - Cálculo do dia

### Cupons
- `GET /api/cupons/meses` - Listar meses
- `GET /api/cupons/<mes>` - Cupons do mês
- `DELETE /api/cupons/<mes>/<nome>` - Deletar cupom

## 📊 Requisitos do Sistema

### Requisitos Funcionais (43)
✅ Todos implementados, incluindo:
- Gerenciamento de mesas
- Pedidos presenciais e delivery
- Sistema de pagamento
- Histórico de vendas
- Cálculo de entregas
- Exclusão de pedidos

### Requisitos Não Funcionais (15)
✅ Todos implementados, incluindo:
- Desempenho em tempo real (<1s)
- Segurança com JWT
- Responsividade
- Identidade visual roxo
- Impressão térmica 58mm

## 🎓 Projeto Acadêmico

Este é um projeto de **Trabalho de Conclusão de Curso (TCC)** em **Análise e Desenvolvimento de Sistemas** (ADS.53) pela UNICAP, Recife - PE.

**Autor**: Mattheeus Dantas

## 📝 Licença

Projeto pessoal e acadêmico.

## 🔗 Links

- [GitHub Repository](https://github.com/mattheeusdantas1-pixel/System-of-Delivery)
- [Portfólio do Desenvolvedor](https://github.com/mattheeusdantas1-pixel)

---

**Desenvolvido com ❤️ para otimizar processos do restaurante Sopa da Roxa**
