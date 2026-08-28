SOPA DA ROXA
Sistema de Comanda Eletrônica
Documento de Requisitos do Sistema Web
Análise e Desenvolvimento de Sistemas — ADS.53
Recife, Pernambuco — 2026

Histórico de Revisões do Documento
Versão
Data
Autor
Descrição
Localização
01.00
20/04/2026
Mattheeus Dantas
Criação deste Documento
Recife, PE


1. Introdução
Este documento de requisitos tem como objetivo detalhar as funcionalidades e necessidades do sistema web a ser desenvolvido para a Sopa da Roxa, um restaurante especializado em sopas localizado em Recife, Pernambuco. O estabelecimento busca otimizar seus processos internos de atendimento e entrega por meio de uma solução tecnológica moderna e eficiente.
O sistema será projetado para atender às demandas específicas do negócio, oferecendo suporte ao gerenciamento de mesas, pedidos presenciais, cozinha, delivery e histórico financeiro. A solução garantirá alta performance por meio de comunicação em tempo real (WebSocket), segurança com autenticação JWT e identidade visual temática na paleta roxo/purple.
Este documento descreve os requisitos funcionais e não funcionais do sistema, incluindo as expectativas da Sopa da Roxa em relação ao design, desempenho e escalabilidade. O objetivo final é criar uma base sólida para o desenvolvimento e também como portfólio acadêmico do Trabalho de Conclusão de Curso (TCC) em Análise e Desenvolvimento de Sistemas do autor.

2. Requisitos Funcionais
São descritos abaixo os requisitos funcionais do sistema, agrupados por módulo para melhor visualização e rastreabilidade.
2.1 Módulo — Mesas e Pedidos Presenciais
[RFW 001] GERENCIAR MESAS
O sistema deve permitir o gerenciamento de 12 mesas, com os seguintes status: disponível, ocupada e reservada. O administrador poderá adicionar e remover mesas dinamicamente conforme necessidade do restaurante.

Requisitos Relacionados: —
Prioridade:	 ■ Essencial	  	□ Importante  	□ Desejável


[RFW 002] VISUALIZAR MESAS EM GRID
O sistema deve exibir as mesas em grid visual com cores indicativas (roxo claro = livre, roxo escuro = ocupada), mostrando o número e a capacidade de cada mesa de forma clara.

Requisitos Relacionados: RFW 001
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 003] REGISTRAR PEDIDO NA MESA
O garçom deve poder clicar em uma mesa disponível e abrir um formulário de pedido para selecionar itens do cardápio e registrar o pedido.

Requisitos Relacionados: RFW 001, RFW 002
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 004] SELECIONAR ITENS DO CARDÁPIO
O sistema deve permitir a seleção de itens do cardápio (sopas e bebidas) com quantidade ajustável através de botões (+) e (-).

Requisitos Relacionados: RFW 003
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 005] ADICIONAR OBSERVAÇÕES AO PEDIDO
O sistema deve permitir adicionar observações obrigatórias ou customizáveis a cada item ou ao pedido inteiro (ex.: "sem sal", "alergia a tomate").

Requisitos Relacionados: RFW 003
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 006] CALCULAR TOTAL PARCIAL DO PEDIDO
O sistema deve calcular automaticamente o valor total do pedido em tempo real à medida que itens são adicionados ou removidos.

Requisitos Relacionados: RFW 003, RFW 004
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 007] ADICIONAR BEBIDA CUSTOMIZADA
O garçom deve poder adicionar ao pedido uma bebida com nome e preço definidos manualmente, para bebidas não cadastradas previamente no cardápio.

Requisitos Relacionados: RFW 003
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


[RFW 008] REGISTRAR TIMESTAMP DO PEDIDO
O sistema deve registrar obrigatoriamente um timestamp (data e hora) em todo pedido no momento da sua criação.

Requisitos Relacionados: RFW 003
Prioridade: 	■ Essencial 		 □ Importante  	□ Desejável


[RFW 009] ENVIAR PEDIDO PARA COZINHA
Após registrar o pedido, o garçom deve enviá-lo à cozinha. O sistema deve alterar o status do pedido para "confirmado" e marcar a mesa como ocupada automaticamente.

Requisitos Relacionados: RFW 003
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 010] REABRIR MESA PARA NOVOS ITENS
O sistema deve permitir que o garçom reabra uma mesa para adicionar novos itens a um pedido já existente e em andamento.

Requisitos Relacionados: RFW 003, RFW 009
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


2.2 Módulo — Cozinha
[RFW 011] VISUALIZAR PEDIDOS NA COZINHA
O cozinheiro deve visualizar uma lista de pedidos confirmados com itens, quantidades e observações, organizados por ordem de chegada.

Requisitos Relacionados: RFW 009
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 012] ALTERAR STATUS PARA PREPARANDO
O cozinheiro deve poder alterar o status do pedido para "preparando" por meio do botão "Começar" na interface da cozinha.

Requisitos Relacionados: RFW 011
Prioridade: 	■ Essencial  		□ Importante 		□ Desejável


[RFW 013] ALTERAR STATUS PARA PRONTO
O cozinheiro deve poder alterar o status do pedido para "pronto" por meio do botão "Pronto" na interface da cozinha.

Requisitos Relacionados: RFW 012
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 014] REMOVER PEDIDO DA TELA DA COZINHA
O sistema deve remover automaticamente o pedido da tela da cozinha quando o status for alterado para "pronto", mantendo-o visível para o garçom.

Requisitos Relacionados: RFW 013
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 015] DESTACAR PEDIDOS POR COR NA COZINHA
O sistema deve destacar visualmente os pedidos novos (amarelo) e em preparo (azul) na interface da cozinha para facilitar a triagem.

Requisitos Relacionados: RFW 011
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


[RFW 016] DESTACAR OBSERVAÇÕES NA COZINHA
O sistema deve mostrar as observações do pedido em destaque (ex.: cor vermelha ou fundo diferenciado) para garantir atenção da cozinha a restrições alimentares.

Requisitos Relacionados: RFW 005, RFW 011
Prioridade:	 ■ Essencial 		 □ Importante  	□ Desejável


2.3 Módulo — Pagamento
[RFW 017] FECHAR CONTA (PAGAMENTO INTEGRAL)
O garçom deve poder fechar a conta de um pedido pronto, selecionando a forma de pagamento: dinheiro, PIX ou cartão.

Requisitos Relacionados: RFW 013
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 018] CALCULAR TROCO PARA PAGAMENTO EM DINHEIRO
Ao receber pagamento em dinheiro, o sistema deve solicitar o valor recebido e calcular automaticamente o troco a ser devolvido ao cliente.

Requisitos Relacionados: RFW 017
Prioridade: 	■ Essencial 		 □ Importante  	□ Desejável


[RFW 019] REGISTRAR PAGAMENTO NO HISTÓRICO
O sistema deve registrar cada pagamento com método utilizado, valor total, troco (se houver) e data/hora da transação.

Requisitos Relacionados: RFW 017
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 020] LIBERAR MESA APÓS PAGAMENTO
Após o pagamento integral, o sistema deve marcar a mesa como "disponível" e mover o pedido para o histórico automaticamente.

Requisitos Relacionados: RFW 017, RFW 019
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 021] REALIZAR PAGAMENTO SEPARADO POR ITEM
O garçom deve poder selecionar quais itens do pedido cada cliente irá pagar, repetindo o processo até que todos os itens sejam quitados. O sistema deve permitir formas de pagamento diferentes por pessoa.

Requisitos Relacionados: RFW 017
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


[RFW 022] DIVIDIR CONTA IGUALITARIAMENTE
O garçom deve poder dividir o valor total do pedido por um número de pessoas (de 2 a 10) e o sistema deve exibir o valor por pessoa automaticamente.

Requisitos Relacionados: RFW 017
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


2.4 Módulo — Delivery
[RFW 023] CADASTRAR PEDIDO DELIVERY
O sistema deve permitir o cadastro de pedidos de delivery com os seguintes campos obrigatórios: nome do cliente, telefone e endereço.

Requisitos Relacionados: —
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 024] ADICIONAR ITENS AO PEDIDO DELIVERY
O sistema deve permitir adicionar itens do cardápio e bebidas customizadas ao pedido de delivery, com ajuste de quantidades.

Requisitos Relacionados: RFW 004, RFW 023
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 025] DEFINIR TAXA DE ENTREGA
O sistema deve permitir definir uma taxa de entrega customizável (padrão R$ 5,00) para cada pedido de delivery.

Requisitos Relacionados: RFW 023
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 026] ADICIONAR OBSERVAÇÕES DO CLIENTE (DELIVERY)
O sistema deve permitir incluir observações específicas do cliente no pedido de delivery.

Requisitos Relacionados: RFW 023
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


[RFW 027] CALCULAR TOTAL DO PEDIDO DELIVERY
O sistema deve calcular automaticamente o total do pedido de delivery, somando o subtotal dos itens com a taxa de entrega.

Requisitos Relacionados: RFW 024, RFW 025
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 028] PAGAMENTO NO DELIVERY
O sistema deve aceitar pagamento em dinheiro (com cálculo de troco quando necessário) ou PIX para pedidos de delivery.

Requisitos Relacionados: RFW 023, RFW 018
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 029] ATUALIZAR STATUS DE ENTREGA
O entregador deve poder atualizar o status do pedido de delivery nos seguintes estágios: pendente, pronto para entrega, em entrega e entregue.

Requisitos Relacionados: RFW 023
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 030] EXIBIR PEDIDOS DELIVERY POR COR
O sistema deve exibir os pedidos de delivery com cards coloridos por status: amarelo = pendente, azul = pronto, roxo = em entrega, verde = entregue.

Requisitos Relacionados: RFW 029
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


2.5 Módulo — Histórico e Relatórios
[RFW 031] MANTER HISTÓRICO DE PEDIDOS
O sistema deve manter um histórico completo de pedidos finalizados, tanto presenciais quanto de delivery.

Requisitos Relacionados: RFW 020
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 032] FILTRAR HISTÓRICO POR DATA
O sistema deve permitir filtrar o histórico de pedidos por data, com o padrão sendo o dia atual.

Requisitos Relacionados: RFW 031
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 033] EXIBIR RESUMO DIÁRIO
O sistema deve exibir um resumo diário no histórico contendo: total de pedidos, faturamento total e ticket médio.

Requisitos Relacionados: RFW 031, RFW 032
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 034] VISUALIZAR DETALHES DO PEDIDO NO HISTÓRICO
O sistema deve permitir visualizar os detalhes de cada pedido do histórico, incluindo itens, valores, forma de pagamento e data/hora.

Requisitos Relacionados: RFW 031
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável


2.6 Módulo — Cardápio
[RFW 035] EXIBIR CARDÁPIO POR CATEGORIAS
O sistema deve exibir o cardápio separado por categorias: Sopas Tradicionais, Cremes de Macaxeira, Especiais e Bebidas.

Requisitos Relacionados: —
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 036] CADASTRAR ITEM NO CARDÁPIO
O administrador deve poder cadastrar itens no cardápio definindo: nome, descrição, categoria, preço, tempo de preparo e disponibilidade.

Requisitos Relacionados: —
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 037] EDITAR ITEM DO CARDÁPIO
O administrador deve poder editar itens existentes no cardápio, alterando nome, descrição, preço, categoria e disponibilidade.

Requisitos Relacionados: RFW 036
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 038] REMOVER ITEM DO CARDÁPIO
O administrador deve poder remover itens do cardápio ou apenas marcá-los como indisponíveis temporariamente.

Requisitos Relacionados: RFW 036
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 039] MARCAR ITEM COMO BEBIDA
O sistema deve permitir marcar um item do cardápio como "bebida" para tratamento diferenciado na interface de pedido.

Requisitos Relacionados: RFW 036
Prioridade: 	□ Essencial  		■ Importante  	□ Desejável




2.7 Módulo — Autenticação e Usuários
[RFW 040] REALIZAR LOGIN
O sistema deve permitir login com e-mail e senha, gerando um token JWT para controle e validação de sessão.

Requisitos Relacionados: —
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


[RFW 041] CONTROLAR PERFIS DE ACESSO
O sistema deve diferenciar perfis de acesso com permissões específicas: garçom, cozinheiro, entregador e administrador.

Requisitos Relacionados: RFW 040
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável


2.8 Módulo — Tempo Real
[RFW 042] ATUALIZAR INTERFACES EM TEMPO REAL
O sistema deve atualizar em tempo real (WebSocket via Socket.IO) as interfaces do garçom e da cozinha sempre que um pedido for criado ou tiver seu status alterado.

Requisitos Relacionados: RFW 009, RFW 011, RFW 012, RFW 013
Prioridade: 	■ Essencial  		□ Importante  	□ Desejável



3. Requisitos Não Funcionais
São descritos abaixo os requisitos não funcionais que definem as qualidades técnicas, de segurança, usabilidade e desempenho esperadas para o sistema Sopa da Roxa.
[RNF 001] Desempenho — Tempo Real
• O sistema deve atualizar as interfaces do garçom e da cozinha com atraso inferior a 1 segundo utilizando WebSocket (Socket.IO).



[RNF 002] Desempenho — Tempo de Resposta
• O tempo de resposta para operações de criação de pedido deve ser inferior a 2 segundos.


[RNF 003] Segurança — Senhas
• As senhas dos usuários devem ser armazenadas com hash bcrypt com 10 rounds, nunca em texto plano.


[RNF 004] Segurança — Autenticação JWT
• O acesso ao sistema deve ser protegido por autenticação JWT (JSON Web Tokens) com prazo de expiração definido.


[RNF 005] Segurança — Controle de Perfis (RBAC)
• Diferentes perfis de usuário (garçom, cozinha, delivery, admin) devem ter permissões distintas e verificadas a cada requisição.


[RNF 006] Segurança — Criptografia de Dados
• Dados sensíveis dos clientes, como endereços de delivery, devem ser armazenados criptografados com AES-256.


[RNF 007] Usabilidade — Responsividade
• A interface deve ser responsiva, funcionando adequadamente em tablets de 10 polegadas e desktops.
• O layout deve adaptar-se ao tamanho da tela sem perda de funcionalidade.


[RNF 008] Usabilidade — Eficiência Operacional
• O garçom deve conseguir finalizar um pedido completo em no máximo 4 cliques após selecionar a mesa.


[RNF 009] Usabilidade — Identidade Visual
• O sistema deve seguir o tema visual roxo/purple definido, com as cores primárias: #7c3aed, #6d28d9 e #5b21b6.
• Todos os componentes visuais devem manter coerência com a identidade da marca Sopa da Roxa.


[RNF 010] Disponibilidade
• O sistema deve estar disponível durante todo o horário de funcionamento do restaurante (11h às 22h).
• Deve haver recuperação automática em caso de falha de conexão com o banco de dados.


[RNF 011] Escalabilidade
• A arquitetura deve ser multi-tenant, suportando múltiplos restaurantes ou franquias no futuro sem necessidade de reescrita.


[RNF 012] Manutenibilidade
• O código deve ser modular, com separação clara entre frontend (React 18 + Vite), backend (Node.js + Express) e banco de dados (PostgreSQL 16).


[RNF 013] Auditoria
• Toda alteração de status de pedido deve ser registrada na tabela order_history com timestamp e identificador do usuário responsável pela ação.


[RNF 014] Impressão
• O sistema deve suportar impressão em bobina térmica de 58mm com formatação adequada para cupons de cozinha e de delivery.
• A impressão deve ser gerada automaticamente ao confirmar pedidos de delivery.





Resumo do Documento
42 Requisitos Funcionais (RFW 001 — RFW 042)   |   14 Requisitos Não Funcionais 
(RNF 001 — RNF 014)   |   4 Atores: Garçom, Cozinheiro, Entregador, Administrador
