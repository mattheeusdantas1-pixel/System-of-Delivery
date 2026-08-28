# Prompt de Alta Precisão para Diagrama UML - Casos de Uso
## Sistema Sopa da Roxa - Comanda Eletrônica

---

## 📋 INSTRUÇÕES GERAIS

Crie um **diagrama UML de Casos de Uso** seguindo **rigorosamente** as especificações abaixo.

### Especificações Técnicas:
- **Tipo**: Diagrama de Casos de Uso (UML 2.5)
- **Nome do Sistema**: "Sistema Sopa da Roxa"
- **Estilo Visual**: 
  - Paleta de cores: Roxo/Purple (#7c3aed, #6d28d9)
  - Fonte clara e legível
  - Layout hierárquico top-down
  - Sem linhas cruzadas (zero poluição visual)

---

## 🔐 PONTO 1: FLUXO DE AUTENTICAÇÃO (OBRIGATÓRIO)

**No TOPO da caixa do sistema:**

- **UC-16: Realizar Login**
  - Descrição: Autenticação obrigatória com email e senha
  - Gera token JWT
  - Controla acesso por perfil (RBAC)
  - **Esta é a porta de entrada de TODOS os atores**

**Após UC-16, cada ator recebe acesso específico aos seus casos de uso**

---

## 👤 PONTO 2: ATOR 1 - GARÇOM

**Posição**: Lado esquerdo, após login

**Casos de Uso Diretos:**

1. **UC-01: Gerenciar Mesas**
   - Permite visualizar status das 12 mesas (disponível, ocupada, reservada)
   - Acesso direto do ator GARÇOM

2. **UC-02: Registrar Pedido na Mesa**
   - Cria novo pedido associado a mesa específica
   - Permite seleção de itens do cardápio
   - Acesso direto do ator GARÇOM
   - **RELACIONAMENTO**: `<<include>> UC-03`

3. **UC-03: Adicionar Observações ao Pedido**
   - Adição de observações especiais (sem sal, alergia, etc.)
   - **Obrigatoriamente INCLUÍDO em**: UC-02 E UC-12
   - Acesso indireto (através de UC-02 ou UC-12)

4. **UC-04: Enviar Pedido para Cozinha**
   - Confirma pedido e envia para preparação
   - Altera status para "confirmado"
   - Marca mesa como "ocupada"
   - Acesso direto do ator GARÇOM

5. **UC-05: Reabrir Mesa para Novos Itens**
   - Adiciona novos itens a pedido em andamento
   - Recalcula total
   - Acesso direto do ator GARÇOM
   - **OPCIONAL**: Pode ser mostrado como extensão de UC-02

6. **UC-09: Fechar Conta (Pagamento Integral)**
   - Processa pagamento completo do pedido
   - Seleciona forma de pagamento (dinheiro, PIX, cartão)
   - Libera mesa como disponível
   - Acesso direto do ator GARÇOM
   - **RELACIONAMENTO**: `<<include>> UC-10`

7. **UC-10: Calcular Troco para Pagamento em Dinheiro**
   - Calcula automaticamente o troco
   - **Obrigatoriamente INCLUÍDO em**: UC-09
   - Acesso indireto (apenas se forma de pagamento = dinheiro)

8. **UC-12: Cadastrar Pedido Delivery**
   - Registra novo pedido para entrega
   - Campos obrigatórios: nome cliente, telefone, endereço
   - Adiciona itens do cardápio + taxa de entrega
   - Acesso direto do ator GARÇOM
   - **RELACIONAMENTO**: `<<include>> UC-03`

9. **UC-11: Dividir Conta Igualitariamente** *(OPCIONAL - Importante)*
   - Divide valor entre 2-10 pessoas
   - **RELACIONAMENTO**: `<<extend>> UC-09` (estende fechar conta)
   - Acesso direto do ator GARÇOM

---

## 👨‍🍳 PONTO 3: ATOR 2 - COZINHEIRO

**Posição**: Lado direito superior, após login

**Casos de Uso Diretos:**

1. **UC-06: Visualizar Pedidos na Cozinha**
   - Lista de pedidos confirmados por ordem de chegada
   - Mostra itens, quantidades e observações
   - Observações destacadas em cor diferenciada
   - Acesso direto do ator COZINHEIRO

2. **UC-07: Alterar Status para Preparando**
   - Botão "Começar" na interface
   - Altera status do pedido para "preparando"
   - Atualiza interface em tempo real
   - Acesso direto do ator COZINHEIRO

3. **UC-08: Alterar Status para Pronto**
   - Botão "Pronto" na interface
   - Altera status do pedido para "pronto"
   - Remove pedido automaticamente da tela da cozinha
   - Acesso direto do ator COZINHEIRO

---

## 🏃 PONTO 4: ATOR 3 - ENTREGADOR

**Posição**: Lado direito inferior, após login

**Casos de Uso Diretos:**

1. **UC-13: Atualizar Status de Entrega**
   - Atualiza status nos estágios: pendente → pronto → em entrega → entregue
   - Cards coloridos por status no sistema
   - Acesso direto do ator ENTREGADOR

---

## 👨‍💼 PONTO 5: ATOR 4 - ADMINISTRADOR

**Posição**: Lado esquerdo inferior, após login

**Casos de Uso Diretos:**

1. **UC-15: Gerenciar Cardápio**
   - CRUD completo: Create, Read, Update, Delete
   - Define: nome, descrição, categoria, preço, tempo preparo, disponibilidade
   - Marca itens como "bebida"
   - Acesso direto do ator ADMINISTRADOR

2. **Acesso Total**: Admin tem acesso a todos os outros UCs conforme necessário

---

## 🔗 PONTO 6: RELACIONAMENTOS UML (RESUMO)

### Include (<<include>>)
- **UC-02** `<<include>>` **UC-03** *(Observações são PARTE obrigatória de registrar pedido)*
- **UC-09** `<<include>>` **UC-10** *(Cálculo de troco é PARTE de fechar conta)*
- **UC-12** `<<include>>` **UC-03** *(Observações são PARTE obrigatória de delivery)*

### Extend (<<extend>>)
- **UC-11** `<<extend>>` **UC-09** *(Dividir conta ESTENDE fechar conta como variação opcional)*
- **UC-05** `<<extend>>` **UC-02** *(OPCIONAL: Reabrir mesa é variação de registrar pedido)*

**Observação Importante**: Não mostrar relacionamento direto entre UCs de atores diferentes (ex: Garçom com Cozinheiro). Eles se comunicam através do sistema, não do diagrama de casos de uso.

---

## 📐 PONTO 7: ESTRUTURA VISUAL DO LAYOUT

**REGRA FUNDAMENTAL UML:**
- ✅ **ATORES ficam FORA** da caixa (à esquerda e direita)
- ✅ **CASOS DE USO ficam DENTRO** da caixa (elipses)
- ✅ **TODO SISTEMA dentro do retângulo** (boundary)

```
                    GARÇOM                           COZINHEIRO
                      │                                    │
                      │      ┌─────────────────────────────┼─────────────────┐
                      │      │                             │                 │
                      ├─────→│ UC-01: Gerenciar Mesas      │                 │
                      │      │                             │                 │
                      ├─────→│ UC-02: Registrar Pedido ─inc─ UC-03: Obs     │
                      │      │                             │                 │
                      ├─────→│ UC-04: Enviar Cozinha       │                 │
                      │      │                             │                 │
                      ├─────→│ UC-05: Reabrir Mesa         │                 │
                      │      │                             │                 │
                      ├─────→│ ┌─────────────────────────┐ │                 │
                      │      │ │   UC-16: Login (TOPO)   │ │                 │
                      │      │ └─────────────────────────┘ │                 │
                      │      │                             │                 │
                      ├─────→│ UC-09: Fechar Conta ───inc─ UC-10: Troco     │
                      │      │                             │                 │
                      ├─────→│ UC-12: Delivery ───────inc─ UC-03: Obs   │   ├──→│ UC-06: Visualizar
                      │      │                             │                 │
                      ├─────→│ UC-11: Dividir ────ext────➜ UC-09         │   ├──→│ UC-07: Preparando
                      │      │                             │                 │
                      └─────→└─────────────────────────────┼─────────────────┘   └──→│ UC-08: Pronto
                                                           │
                                                      ADMIN │
                                                      ENTREGADOR
                                                           │
                   ┌──────────────────────────────────────┼─────────────────────┐
                   │                                      │                     │
                   ├─────➜ UC-15: Gerenciar Cardápio      │                     │
                   │                                      │                     │
                   └──────────────────────────────────────┼─────────────────────┘
                                                           │
                                                           ├─────➜ UC-13: Atualizar Entrega
                                                           │
```

**Diagrama Simplificado (mais claro):**

```
   GARÇOM                                            COZINHEIRO
     │                                                    │
     │      ┌─── SISTEMA SOPA DA ROXA ──────────────────┼────┐
     │      │                                            │    │
     ├─────→│         UC-16: Realizar Login             │    │
     │      │              (TOPO)                       │    │
     │      │                                            │    │
     ├─────→│ UC-01: Gerenciar Mesas                    │    │
     │      │ UC-02: Registrar Pedido ──inc── UC-03    │    ├──→│ UC-06
     │      │ UC-04: Enviar Cozinha                    │    │    │ UC-07
     │      │ UC-05: Reabrir Mesa                      │    │    │ UC-08
     │      │ UC-09: Fechar Conta ──inc── UC-10        │    │
     │      │ UC-12: Delivery ──inc── UC-03            │    │
     │      │ UC-11: Dividir ──ext── UC-09             │    │
     │      │                                            │    │
     └──────┴────────────────────────────────────────────┼────┘
            ADMINISTRADOR          ENTREGADOR
                  │                     │
            ┌─────┼─────────────────────┼─────┐
            │     │                     │     │
            ├────→│ UC-15: Cardápio    │     ├──→│ UC-13: Delivery
            │     │                    │     │
            └─────┴────────────────────┴─────┘
```

---

## 🎨 PONTO 8: INSTRUÇÕES DE ESTILO

**ESTRUTURA FUNDAMENTAL:**
- **Retângulo grande** = System Boundary (limite do sistema)
- **Tudo DENTRO** = Casos de Uso (elipses/óvalos)
- **Tudo FORA** = Atores (stick figures à esquerda e direita)
- **Setas** = Conectam atores (fora) aos UCs (dentro)

**Detalhes Visuais:**
- **Cores**: Usar roxo/purple com variações claras e escuras
- **Fonte**: Sans-serif (Arial, Helvetica ou similar)
- **Tamanho**: UC-16 levemente maior que os outros
- **Elipses**: Óvalos/elipses para UCs (TODOS DENTRO da caixa)
- **Atores**: Stick figures (bonecos simples) À ESQUERDA OU DIREITA (FORA da caixa)
- **Setas**: 
  - Linhas sólidas para `<<include>>`
  - Linhas tracejadas para `<<extend>>`
  - Seta simples de ator (fora) para UC (dentro)
- **Caixa do Sistema**: Retângulo com borda clara, nome no topo
- **Espaçamento**: Adequado para legibilidade, zero linhas cruzadas
- **Posicionamento dos Atores**:
  - GARÇOM: lado esquerdo (superior)
  - COZINHEIRO: lado direito (superior)
  - ENTREGADOR: lado direito (inferior)
  - ADMINISTRADOR: lado esquerdo (inferior)

---

## ✅ PONTO 9: CHECKLIST DE VALIDAÇÃO

Antes de confirmar o diagrama, verificar se:

- [ ] UC-16 está no topo como pré-requisito
- [ ] 4 atores claramente identificados (Garçom, Cozinheiro, Entregador, Admin)
- [ ] Todos os 12 principais UCs aparecem
- [ ] UC-03 aparece associado a UC-02 E UC-12 (via <<include>>)
- [ ] UC-10 aparece como <<include>> de UC-09
- [ ] UC-11 aparece como <<extend>> de UC-09
- [ ] Sem linhas cruzadas desnecessárias
- [ ] Relacionamentos claramente marcados com labels
- [ ] Layout hierárquico (top-down) e organizado
- [ ] Estilo visual profissional e acadêmico

---

## 📝 PONTO 10: CONTEXTO DO PROJETO

Este diagrama é parte de um **TCC (Trabalho de Conclusão de Curso)** em **Análise e Desenvolvimento de Sistemas** para o sistema de **Comanda Eletrônica da Sopa da Roxa**, um restaurante real em Recife, Pernambuco.

**Requisitos de qualidade para TCC:**
- Precisão técnica UML
- Clareza visual
- Rastreabilidade com documento de requisitos
- Profissionalismo acadêmico

---

## 🚀 PROMPT FINAL PARA O GEMINI

**Copie e cole exatamente isto no Gemini:**

---

Crie um diagrama UML **PRECISO** de Casos de Uso seguindo **RIGOROSAMENTE** estas especificações:

### SISTEMA: "Sopa da Roxa - Comanda Eletrônica"

### ⚠️ ESTRUTURA FUNDAMENTAL:
- **ATORES ficam FORA do retângulo** (à esquerda e direita)
- **CASOS DE USO ficam DENTRO do retângulo** (elipses/óvalos)
- **Setas conectam atores (fora) aos UCs (dentro)**
- **TODO sistema dentro de um retângulo grande (system boundary)**

### AUTENTICAÇÃO (NO TOPO - DENTRO):
- UC-16: Realizar Login (obrigatório para todos os atores)

### ATOR 1 - GARÇOM (FORA - lado esquerdo superior):
Conecta às seguintes UCs DENTRO:
- UC-01: Gerenciar Mesas
- UC-02: Registrar Pedido na Mesa
  - UC-02 <<include>> UC-03
- UC-03: Adicionar Observações ao Pedido
- UC-04: Enviar Pedido para Cozinha
- UC-05: Reabrir Mesa para Novos Itens
- UC-09: Fechar Conta
  - UC-09 <<include>> UC-10
- UC-10: Calcular Troco para Pagamento
- UC-12: Cadastrar Pedido Delivery
  - UC-12 <<include>> UC-03
- UC-11: Dividir Conta Igualitariamente
  - UC-11 <<extend>> UC-09

### ATOR 2 - COZINHEIRO (FORA - lado direito superior):
Conecta às seguintes UCs DENTRO:
- UC-06: Visualizar Pedidos na Cozinha
- UC-07: Alterar Status para Preparando
- UC-08: Alterar Status para Pronto

### ATOR 3 - ENTREGADOR (FORA - lado direito inferior):
Conecta à seguinte UC DENTRO:
- UC-13: Atualizar Status de Entrega

### ATOR 4 - ADMINISTRADOR (FORA - lado esquerdo inferior):
Conecta à seguinte UC DENTRO:
- UC-15: Gerenciar Cardápio

### REQUISITOS DE LAYOUT CRÍTICOS:
1. **Retângulo grande** envolve TODO o sistema (system boundary)
2. **UC-16 NO TOPO** dentro do retângulo
3. **Atores FORA do retângulo** nas posições especificadas
4. Todos os outros UCs DENTRO do retângulo
5. **Setas** saem dos atores (fora) e entram nos UCs (dentro)
6. Atores como stick figures
7. Relacionamentos com labels <<include>> e <<extend>>
8. ZERO linhas cruzadas
9. Cores: Roxo/Purple (#7c3aed para destaque)
10. Estilo: Profissional, acadêmico, para TCC

### VALIDAÇÃO FINAL:
Confirme que:
- [ ] Todos os 12 UCs estão DENTRO do retângulo do sistema
- [ ] Todos os 4 atores estão FORA do retângulo
- [ ] Todos os relacionamentos estão marcados corretamente
- [ ] Setas vêm de atores (fora) para UCs (dentro)

---

**Fim do prompt.**

Se o Gemini não gerar perfeitamente na primeira tentativa, você pode ajustar com: "Refaça corrigindo [especificar o erro]"

