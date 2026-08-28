# Casos de Uso - Sistema Sopa da Roxa

## 1. Atores do Sistema

### 1.1. Cliente
- Pessoa que consome os serviços do restaurante (presencial ou delivery)

### 1.2. Garçom
- Responsável por atender clientes presenciais
- Registra pedidos nas mesas
- Gerencia o processo de pagamento
- Reabre mesas para novos pedidos

### 1.3. Cozinheiro
- Prepara os pedidos conforme solicitado
- Atualiza status dos pedidos
- Visualiza observações especiais dos pedidos

### 1.4. Entregador
- Responsável pela entrega dos pedidos delivery
- Atualiza status dos pedidos em rota de entrega

### 1.5. Administrador
- Gerencia configurações do sistema
- Controla o cardápio
- Gerencia usuários e permissões

## 2. Casos de Uso por Módulo

### 2.1. Gestão de Mesas e Pedidos Presenciais

#### UC-01: Gerenciar Mesas
- **Ator Primário**: Garçom, Administrador
- **Descrição**: Controlar o status das mesas (disponível, ocupada, reservada)
- **Pré-condições**: Usuário autenticado
- **Fluxo Principal**:
  1. Usuário acessa a interface de mesas
  2. Sistema exibe grid com mesas e seus status
  3. Usuário pode visualizar status das mesas

#### UC-02: Registrar Pedido na Mesa
- **Ator Primário**: Garçom
- **Descrição**: Criar um novo pedido associado a uma mesa específica
- **Pré-condições**: Mesa disponível
- **Fluxo Principal**:
  1. Garçom seleciona mesa disponível
  2. Sistema abre formulário de pedido
  3. Garçom seleciona itens do cardápio
  4. Sistema calcula total parcial em tempo real
  5. Garçom confirma pedido
  6. Sistema registra timestamp e envia para cozinha

#### UC-03: Adicionar Observações ao Pedido
- **Ator Primário**: Garçom
- **Descrição**: Incluir observações especiais para itens ou pedido completo
- **Pré-condições**: Pedido em criação
- **Fluxo Principal**:
  1. Garçom adiciona item ao pedido
  2. Garçom pode incluir observações (ex: "sem sal", "alergia")
  3. Sistema registra observações e destaca para cozinha

#### UC-04: Enviar Pedido para Cozinha
- **Ator Primário**: Garçom
- **Descrição**: Confirmar pedido e enviar para preparação
- **Pré-condições**: Pedido criado com itens
- **Fluxo Principal**:
  1. Garçom confirma envio do pedido
  2. Sistema altera status para "confirmado"
  3. Sistema marca mesa como "ocupada"
  4. Cozinheiro recebe notificação do novo pedido

#### UC-05: Reabrir Mesa para Novos Itens
- **Ator Primário**: Garçom
- **Descrição**: Adicionar itens a um pedido já existente
- **Pré-condições**: Mesa com pedido em andamento
- **Fluxo Principal**:
  1. Garçom seleciona mesa ocupada
  2. Sistema permite adicionar novos itens ao pedido existente
  3. Sistema recalcula total do pedido

### 2.2. Gestão da Cozinha

#### UC-06: Visualizar Pedidos na Cozinha
- **Ator Primário**: Cozinheiro
- **Descrição**: Visualizar lista de pedidos confirmados organizados por ordem de chegada
- **Pré-condições**: Pedidos confirmados
- **Fluxo Principal**:
  1. Sistema exibe pedidos ordenados por timestamp
  2. Cada pedido mostra itens, quantidades e observações
  3. Sistema destaca observações importantes

#### UC-07: Alterar Status para Preparando
- **Ator Primário**: Cozinheiro
- **Descrição**: Informar que o pedido está em preparação
- **Pré-condições**: Pedido confirmado
- **Fluxo Principal**:
  1. Cozinheiro seleciona pedido
  2. Cozinheiro clica em "Começar"
  3. Sistema altera status para "preparando"
  4. Sistema atualiza interface em tempo real

#### UC-08: Alterar Status para Pronto
- **Ator Primário**: Cozinheiro
- **Descrição**: Informar que o pedido está pronto para entrega
- **Pré-condições**: Pedido em preparação
- **Fluxo Principal**:
  1. Cozinheiro finaliza preparação
  2. Cozinheiro clica em "Pronto"
  3. Sistema altera status para "pronto"
  4. Pedido é removido da tela da cozinha
  5. Garçom recebe notificação

### 2.3. Gestão de Pagamento

#### UC-09: Fechar Conta (Pagamento Integral)
- **Ator Primário**: Garçom
- **Descrição**: Processar o pagamento completo do pedido
- **Pré-condições**: Pedido pronto para pagamento
- **Fluxo Principal**:
  1. Garçom seleciona mesa para fechamento
  2. Sistema exibe total do pedido
  3. Garçom seleciona forma de pagamento
  4. Sistema processa pagamento
  5. Sistema libera mesa como disponível

#### UC-10: Calcular Troco para Pagamento em Dinheiro
- **Ator Primário**: Garçom
- **Descrição**: Calcular troco quando pagamento for em dinheiro
- **Pré-condições**: Forma de pagamento = dinheiro
- **Fluxo Principal**:
  1. Garçom informa valor recebido
  2. Sistema calcula troco automaticamente
  3. Sistema exibe valor do troco

#### UC-11: Dividir Conta Igualitariamente
- **Ator Primário**: Garçom
- **Descrição**: Dividir o valor total entre várias pessoas
- **Pré-condições**: Pedido pronto para pagamento
- **Fluxo Principal**:
  1. Garçom seleciona opção de divisão
  2. Garçom informa número de pessoas (2-10)
  3. Sistema calcula valor por pessoa
  4. Sistema permite pagamento individual

### 2.4. Gestão de Delivery

#### UC-12: Cadastrar Pedido Delivery
- **Ator Primário**: Garçom/Administrador
- **Descrição**: Registrar novo pedido para entrega
- **Pré-condições**: Informações do cliente disponíveis
- **Fluxo Principal**:
  1. Usuário acessa seção de delivery
  2. Sistema solicita dados obrigatórios (nome, telefone, endereço)
  3. Usuário adiciona itens ao pedido
  4. Sistema calcula total com taxa de entrega
  5. Sistema registra pedido com status "pendente"

#### UC-13: Atualizar Status de Entrega
- **Ator Primário**: Entregador
- **Descrição**: Atualizar status do pedido durante o processo de entrega
- **Pré-condições**: Pedido delivery registrado
- **Fluxo Principal**:
  1. Entregador seleciona pedido
  2. Entregador atualiza status (pendente → pronto → em entrega → entregue)
  3. Sistema atualiza interface com cores correspondentes

#### UC-14: Pagamento no Delivery
- **Ator Primário**: Entregador
- **Descrição**: Processar pagamento do pedido delivery
- **Pré-condições**: Pedido entregue
- **Fluxo Principal**:
  1. Entregador processa pagamento (dinheiro ou PIX)
  2. Sistema calcula troco se necessário
  3. Sistema registra pagamento e fecha pedido

### 2.5. Gestão de Cardápio

#### UC-15: Gerenciar Cardápio
- **Ator Primário**: Administrador
- **Descrição**: CRUD completo de itens do cardápio
- **Pré-condições**: Usuário com perfil administrador
- **Fluxo Principal**:
  1. Administrador acessa gestão de cardápio
  2. Administrador pode cadastrar, editar ou remover itens
  3. Sistema atualiza cardápio em tempo real

### 2.6. Autenticação e Usuários

#### UC-16: Realizar Login
- **Ator Primário**: Todos os usuários
- **Descrição**: Autenticar usuário no sistema
- **Pré-condições**: Credenciais válidas
- **Fluxo Principal**:
  1. Usuário informa e-mail e senha
  2. Sistema valida credenciais com bcrypt
  3. Sistema gera token JWT
  4. Usuário acessa sistema com perfil específico

### 2.7. Histórico e Relatórios

#### UC-17: Visualizar Histórico de Pedidos
- **Ator Primário**: Garçom, Administrador
- **Descrição**: Consultar pedidos finalizados
- **Pré-condições**: Pedidos finalizados no sistema
- **Fluxo Principal**:
  1. Usuário acessa seção de histórico
  2. Sistema exibe pedidos filtrados por data
  3. Usuário pode visualizar detalhes de cada pedido

## 3. Relacionamentos entre Casos de Uso

### Includes (<<include>>)
- UC-02 inclui UC-03 (Adicionar observações é parte do registro de pedido)
- UC-09 inclui UC-10 (Calcular troco faz parte do fechamento de conta)

### Extends (<<extend>>)
- UC-05 extende UC-02 (Reabrir mesa é uma extensão de registrar pedido)
- UC-11 extende UC-09 (Dividir conta é uma extensão de fechar conta)

## 4. Restrições e Regras de Negócio

1. **Autenticação obrigatória** para todos os acessos
2. **Timestamp automático** em todos os registros
3. **Criptografia AES-256** para dados sensíveis
4. **Atualização em tempo real** via WebSocket
5. **Controle de permissões RBAC** por perfil de usuário