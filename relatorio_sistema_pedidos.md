# SistemaPedidos Technical Report

## 1. Visão Geral do Sistema e Propósito

SistemaPedidos é um sistema de gerenciamento de pedidos desenvolvido para o restaurante "Sopa da Roxa", especializado em sopas e tapiocas. O sistema integra:

- Aplicação desktop para gerenciamento direto de pedidos
- Interface web para garçons realizarem pedidos
- Sistema de display para cozinha acompanhar preparação
- Histórico de pedidos anteriores
- API centralizada usando Flask
- Banco de dados SQLite para persistência de dados
- Integração com impressora Bluetooth para impressão de recibos

O objetivo principal é otimizar o processo de gestão de pedidos do restaurante, desde o pedido do cliente até a preparação na cozinha e processamento de pagamentos.

## 2. Componentes Principais e Suas Funções

### Componentes Centrais:

1. **Aplicação Desktop (`app.py`, `interface.py`)**
   - Interface primária para equipe do restaurante
   - Gerenciamento direto de pedidos e processamento de pagamentos
   - Monitoramento do status das mesas
   - Gestão de pedidos para viagem

2. **Aplicação Web (`webapp/`)**
   - Interface baseada em navegador para garçons
   - Visualização em grade das mesas com indicadores de status
   - Criação e modificação de pedidos em tempo real
   - Sistema de display para cozinheiros
   - Visualizador histórico de pedidos

3. **Servidor API (`server.py`, `api.py`)**
   - API RESTful servindo clientes desktop e web
   - Hub central de comunicação entre frontend e backend
   - Serviço de arquivos estáticos para aplicação web

4. **Gerenciador de Banco de Dados (`gerenciador_mesas.py`)**
   - Camada de interação com banco de dados SQLite
   - Funções de gerenciamento de mesas, pedidos e itens
   - Implementação da lógica de negócios

5. **Sistema de Cardápio (`cardapio.py`, `cardapio.json`)**
   - Carregamento e gerenciamento dinâmico do cardápio
   - Suporte para sopas, tapiocas e bebidas
   - Arquivo de configuração externo para fácil atualização do cardápio

6. **Utilitários de Impressão (`utils_impressao.py`)**
   - Integração com impressora Bluetooth
   - Fallback para geração de recibos em arquivo
   - Suporte à impressão cross-platform

## 3. Stack Tecnológica

- **Backend**: Python 3.x com framework Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Banco de Dados**: SQLite
- **Interface Desktop**: Tkinter
- **Mobile/Web**: Design responsivo com capacidades PWA
- **Networking**: API HTTP/REST com suporte CORS
- **Integração Hardware**: Comunicação com impressora Bluetooth
- **Empacotamento**: PyInstaller para distribuição em executável

## 4. Estrutura do Banco de Dados e Fluxo de Dados

### Esquema do Banco de Dados:
1. **mesas** (mesas)
   - id (INTEGER PRIMARY KEY)
   - numero (INTEGER UNIQUE)
   - status (TEXT - 'livre'/'ocupada')
   - criado_em (TIMESTAMP)

2. **pedidos** (pedidos)
   - id (INTEGER PRIMARY KEY AUTOINCREMENT)
   - mesa_id (CHAVE ESTRANGEIRA para mesas)
   - data_hora (TIMESTAMP)
   - status (TEXT - 'ativo'/'preparando'/'pronto'/'finalizado')
   - total (REAL)
   - taxa_embalagem (REAL)
   - observacao (TEXT)

3. **itens_pedido** (itens do pedido)
   - id (INTEGER PRIMARY KEY AUTOINCREMENT)
   - pedido_id (CHAVE ESTRANGEIRA para pedidos)
   - nome_item (TEXT)
   - preco_unitario (REAL)
   - quantidade (INTEGER)
   - tipo (TEXT)
   - para_viagem (INTEGER - 0/1)
   - enviado_para_cozinha (INTEGER - 0/1)
   - entregue (INTEGER - 0/1)

### Fluxo de Dados:
1. Garçom cria pedido via app web/desktop
2. Dados do pedido armazenados na tabela pedidos
3. Itens adicionados à tabela itens_pedido
4. Cozinha recebe notificação via cozinha.html
5. Itens marcados como "enviado_para_cozinha" quando enviados para cozinha
6. Itens marcados como "entregue" quando servidos
7. Pedido finalizado com informações de pagamento e status alterado para "finalizado"
8. Recibo impresso ou salvo no diretório cupoms/

## 5. Endpoints da API e Funcionalidades

### Endpoints do Cardápio:
- `GET /api/cardapio` - Recuperar cardápio completo

### Gerenciamento de Mesas:
- `GET /api/mesas` - Listar todas as mesas com status
- `POST /api/mesa/<mesa_id>/pedido` - Criar novo pedido para mesa

### Gerenciamento de Pedidos:
- `GET /api/pedido/<pedido_id>/itens` - Obter itens do pedido
- `GET /api/pedido/<pedido_id>/total` - Obter total do pedido
- `GET /api/pedido/<pedido_id>/status` - Obter status do pedido
- `POST /api/pedido/<pedido_id>/item` - Adicionar item ao pedido
- `DELETE /api/pedido/<pedido_id>/item/<item_id>` - Remover item do pedido
- `POST /api/pedido/<pedido_id>/enviar` - Enviar pedido para cozinha
- `POST /api/pedido/<pedido_id>/status` - Atualizar status do pedido
- `POST /api/pedido/<pedido_id>/fechar` - Fechar pedido e gerar recibo

### Display da Cozinha:
- `GET /api/pedidos/ativos` - Obter pedidos ativos para display da cozinha

### Histórico de Pedidos:
- `GET /api/cupons/meses` - Listar meses com recibos
- `GET /api/cupons/<mes>` - Listar recibos do mês
- `GET /api/cupons/<mes>/<nome>` - Obter conteúdo de recibo específico

## 6. Recursos da Aplicação Desktop

### Interface Principal:
- UI moderna com temas coloridos
- Navegação por abas para diferentes funções
- Visualização do status das mesas em tempo real
- Integração de criação e gerenciamento de pedidos

### Gerenciamento de Pedidos:
- Seleção intuitiva de itens com controles de quantidade
- Suporte para pedidos "para viagem"
- Cálculo de total em tempo real
- Notas de observação dos pedidos

### Processamento de Pagamentos:
- Suporte a múltiplos métodos de pagamento
- Geração automática de recibos
- Tratamento de transações em dinheiro com cálculo de troco

### Gestão de Entregas:
- Interface dedicada para pedidos para viagem
- Seletores de quantidade de produtos com botões +/- 
- Pré-visualização de pedidos em tempo real

### Funções Administrativas:
- Gerenciamento de mesas (adicionar/remover)
- Capacidades de edição do cardápio
- Configuração da impressora
- Diagnósticos do sistema

## 7. Recursos da Aplicação Web

### Interface para Garçons:
- Layout em grade responsivo para gerenciamento de mesas
- Indicadores de status coloridos (livre/ocupada/preparando/pronta)
- Atualizações em tempo real via polling periódico da API
- Design mobile-friendly para uso em tablets

### Criação de Pedidos:
- Navegação no menu baseada em categorias (Sopas/Tapiocas/Bebidas)
- Opções de personalização de itens
- Controles de ajuste de quantidade
- Pré-visualização e edição de pedidos em tempo real

### Comunicação com Cozinha:
- Separação visual de pedidos novos vs. em preparação
- Marcação de itens para status de preparação
- Visibilidade de notas de observação
- Rastreamento de timestamps

### Visualizador de Histórico:
- Organização mensal de recibos
- Visualização de recibos baseada em texto
- Capacidades de busca e filtragem

## 8. Integração Entre Componentes

### Backend Unificado:
Ambas aplicações desktop e web comunicam-se com a mesma API Flask, garantindo consistência de dados entre plataformas.

### Banco de Dados Compartilhado:
Todos os componentes interagem com o mesmo banco de dados SQLite através da camada de abstração gerenciador_mesas.py.

### Sincronização em Tempo Real:
Interface web usa polling periódico para manter atualizações em tempo real dos status das mesas e informações de pedidos.

### Lógica de Negócio Comum:
Processamento de pedidos, cálculos de pagamento e gerenciamento de status são centralizados no gerenciador de banco de dados.

### Integração de Hardware:
Utilitários de impressão são compartilhados entre aplicações desktop e web para geração consistente de recibos.

## 9. Recursos Especiais

### Impressão Bluetooth:
- Detecção automática de impressoras Bluetooth pareadas
- Fallback para geração de recibos baseada em arquivo
- Comunicação com impressora cross-platform (Windows/Linux)

### Progressive Web App:
- Capacidade offline através de service workers
- Otimização para dispositivos móveis
- Suporte à instalação na tela inicial

### Sistema de Cardápio Flexível:
- Configuração JSON externa para fácil atualização do cardápio
- Suporte para múltiplas categorias de produtos
- Gerenciamento de preços sem alterações de código

### Gerenciamento de Entregas:
- Interface dedicada para pedidos para viagem
- Workflow de cobrança separado
- Cálculo de taxa de embalagem

### Geração de Recibos:
- Formatação profissional de recibos
- Salvamento automático em pastas mensais
- Suporte a Unicode para caracteres especiais

## 10. Melhorias Potenciais e Problemas Identificados

### Considerações de Performance:
1. **Bloqueio do Banco de Dados**: SQLite pode se tornar um gargalo com alto acesso concorrente
2. **Overhead de Polling**: Interface web usa polling periódico que poderia ser otimizado com WebSockets
3. **Uso de Memória**: Grandes históricos de recibos podem impactar performance

### Preocupações de Segurança:
1. **Sem Autenticação**: API carece de mecanismos de autenticação
2. **Acesso Direto ao Banco de Dados**: Sem proteção contra injeção SQL em alguns endpoints
3. **Exposição de Rede**: Servidor escuta em todas as interfaces sem criptografia

### Limitações de Escalabilidade:
1. **Arquivo Único de Banco de Dados**: Difícil escalar através de múltiplos terminais
2. **Limitações de Concorrência**: Limitações de concorrência do SQLite
3. **Sem Balanceamento de Carga**: Instância única de servidor

### Aprimoramentos da Experiência do Usuário:
1. **Atualizações em Tempo Real**: Implementar notificações baseadas em WebSocket
2. **Modificação de Pedidos**: Capacidades aprimoradas de edição de pedidos
3. **Dashboard de Relatórios**: Analytics e relatórios de vendas
4. **Gestão de Inventário**: Integração com rastreamento de nível de estoque

### Débito Técnico:
1. **Duplicação de Código**: Funcionalidade similar existe tanto em api.py quanto server.py
2. **Tratamento de Erros**: Tratamento inconsistente de erros entre componentes
3. **Gestão de Configuração**: Arquivos de configuração espalhados
4. **Documentação**: Comentários de código e documentação limitados

### Dependências de Hardware:
1. **Especificidade da Impressora**: Vinculado a modelos específicos de impressora Bluetooth
2. **Limitações de Plataforma**: Funcionalidade de impressão varia significativamente entre plataformas
3. **Mecanismos de Fallback**: Fallbacks baseados em arquivo podem não ser óbvios para usuários

Este sistema fornece uma base sólida para gerenciamento de pedidos em restaurantes mas beneficiaria de melhorias arquiteturais para implantações maiores e medidas de segurança aprimoradas para uso em produção.