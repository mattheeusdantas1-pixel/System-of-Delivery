import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser
import urllib.parse
import os
import sys
import glob
import threading
import sqlite3

from cardapio import cardapio, tapioca
from logica import calcular_total
import gerenciador_mesas as gm
from utils_impressao import imprimir_com_fallback

# ========== FUNÇÃO AUXILIAR PARA QUEBRA DE LINHA ==========
def quebrar_linha(texto, largura_max=36):
    """Quebra o texto em linhas de no máximo 'largura_max' caracteres."""
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ''
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= largura_max:
            linha_atual += (' ' + palavra) if linha_atual else palavra
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas

# ========== FUNÇÕES AUXILIARES ==========
def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_data_path(relative_path):
    return os.path.join(get_app_path(), relative_path)

# ========== CORES ==========
PRIMARIA      = "#6C5CE7"
PRIMARIA_ESC  = "#5B4BC4"
PRIMARIA_CLAR = "#A29BFE"
SECUNDARIA    = "#FD79A8"
FUNDO         = "#F9F9F9"
FUNDO_CARD    = "#FFFFFF"
TEXTO         = "#2D3436"
TEXTO_SUAVE   = "#636E72"
BORDA         = "#DFE6E9"
SUCESSO       = "#00B894"
AVISO         = "#E17055"

def configurar_estilo():
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("TLabel", background=FUNDO, foreground=TEXTO, font=("Segoe UI", 10))
    estilo.configure("TLabelframe", background=FUNDO_CARD, foreground=PRIMARIA, font=("Segoe UI", 11, "bold"), bordercolor=BORDA, relief="solid", borderwidth=1)
    estilo.configure("TLabelframe.Label", background=FUNDO_CARD, foreground=PRIMARIA, font=("Segoe UI", 11, "bold"))
    estilo.configure("TButton", font=("Segoe UI", 10), padding=6, background=PRIMARIA, foreground="white", relief="flat")
    estilo.map("TButton", background=[("active", PRIMARIA_ESC)])
    estilo.configure("TEntry", fieldbackground=FUNDO_CARD, foreground=TEXTO, font=("Segoe UI", 10), bordercolor=BORDA)
    estilo.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6], background=FUNDO, foreground=TEXTO_SUAVE)
    estilo.map("TNotebook.Tab", background=[("selected", FUNDO_CARD)], foreground=[("selected", PRIMARIA)])
    estilo.configure("TCheckbutton", background=FUNDO_CARD, foreground=TEXTO)
    estilo.configure("TRadiobutton", background=FUNDO_CARD, foreground=TEXTO)
    estilo.configure("TScrollbar", background=PRIMARIA_CLAR, troughcolor=FUNDO)
    estilo.configure("Treeview", background=FUNDO_CARD, foreground=TEXTO, fieldbackground=FUNDO_CARD, rowheight=28)
    estilo.configure("Treeview.Heading", background=PRIMARIA, foreground="white")

# ========== WIDGET PARA DELIVERY ==========
class ItemQuantidadeDelivery(tk.Frame):
    def __init__(self, parent, produto, on_update, **kwargs):
        super().__init__(parent, **kwargs)
        self.produto = produto
        self.on_update = on_update
        self.quantidade = tk.IntVar(value=0)
        self.configure(bg=FUNDO_CARD, pady=2)
        self.label = tk.Label(self, text=produto['nome'], bg=FUNDO_CARD, fg=TEXTO, font=("Segoe UI", 11, "bold"), anchor="w", width=22)
        self.label.pack(side="left", padx=(8,2), fill="x", expand=True)
        self.lbl_preco = tk.Label(self, text=f"R${produto['preco']:.2f}", bg=FUNDO_CARD, fg=SECUNDARIA, font=("Segoe UI", 10, "bold"))
        self.lbl_preco.pack(side="left", padx=(0,6))
        self.btn_menos = tk.Button(self, text="−", width=2, command=self.decrementar, bg=PRIMARIA_CLAR, fg="white", relief="flat", font=("Segoe UI", 11, "bold"), cursor="hand2")
        self.btn_menos.pack(side="left", padx=1)
        self.lbl_qtd = tk.Label(self, textvariable=self.quantidade, width=3, bg=PRIMARIA_ESC, fg="white", font=("Segoe UI", 12, "bold"))
        self.lbl_qtd.pack(side="left")
        self.btn_mais = tk.Button(self, text="+", width=2, command=self.incrementar, bg=PRIMARIA, fg="white", relief="flat", font=("Segoe UI", 11, "bold"), cursor="hand2")
        self.btn_mais.pack(side="left", padx=(1,6))

    def incrementar(self):
        self.quantidade.set(self.quantidade.get() + 1)
        self.on_update()

    def decrementar(self):
        if self.quantidade.get() > 0:
            self.quantidade.set(self.quantidade.get() - 1)
            self.on_update()

# ========== CLASSE PRINCIPAL ==========
class Sistema:
    def __init__(self, root):
        self.root = root
        self.root.title("🍲 Sopa da Roxa - PDV")
        self.root.geometry("1100x800")
        self.root.minsize(800, 600)
        self.root.configure(bg=FUNDO)
        configurar_estilo()
        self.root.option_add("*Background", FUNDO)
        self.root.option_add("*Foreground", TEXTO)
        self.centralizar_janela()

        self.pagamento_var = tk.StringVar(value="pix")
        self.precisa_troco_var = tk.BooleanVar(value=False)
        self.valor_recebido_var = tk.DoubleVar(value=0.0)
        self.troco_var = tk.DoubleVar(value=0.0)
        self.status_impressora = tk.StringVar(value="🔍 Verificando impressora...")

        self.criar_interface()
        self.atualizar_status_impressora_async()

    def centralizar_janela(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def criar_interface(self):
        top_bar = tk.Frame(self.root, bg=PRIMARIA, height=60)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        tk.Label(top_bar, text="🍲 Sopa da Roxa — Sistema de Pedidos", font=("Segoe UI", 16, "bold"), bg=PRIMARIA, fg="white").pack(pady=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Aba Delivery
        self.frame_pedido = tk.Frame(self.notebook, bg=FUNDO)
        self.notebook.add(self.frame_pedido, text="  📝 Delivery  ")
        self.construir_aba_pedido()

        # Aba Mesas
        self.frame_mesas = self.criar_frame_mesas()
        self.notebook.add(self.frame_mesas, text="  🪑 Mesas  ")

        # Aba Cozinha
        self.frame_cozinha = self.criar_frame_cozinha()
        self.notebook.add(self.frame_cozinha, text="  🍳 Cozinha  ")

        # Aba Histórico
        self.frame_historico = tk.Frame(self.notebook, bg=FUNDO)
        self.notebook.add(self.frame_historico, text="  📜 Histórico  ")
        self.construir_aba_historico()

        self.status_bar = tk.Frame(self.root, bg=PRIMARIA_CLAR, height=25)
        self.status_bar.pack(side="bottom", fill="x")
        self.status_label = tk.Label(self.status_bar, textvariable=self.status_impressora, bg=PRIMARIA_CLAR, fg=TEXTO, font=("Segoe UI", 9), anchor="w")
        self.status_label.pack(side="left", padx=10)

    # ------------------------------------------------------------
    # ABA DELIVERY
    # ------------------------------------------------------------
    def construir_aba_pedido(self):
        self.canvas_pedido = tk.Canvas(self.frame_pedido, highlightthickness=0, bg=FUNDO)
        scrollbar = ttk.Scrollbar(self.frame_pedido, orient="vertical", command=self.canvas_pedido.yview)
        self.scrollable_frame = tk.Frame(self.canvas_pedido, bg=FUNDO)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas_pedido.configure(scrollregion=self.canvas_pedido.bbox("all")))
        self.canvas_pedido.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_pedido.configure(yscrollcommand=scrollbar.set)
        self.canvas_pedido.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas_pedido.bind("<MouseWheel>", lambda e: self.canvas_pedido.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas_pedido.bind("<Configure>", lambda e: self.canvas_pedido.itemconfig(1, width=e.width))

        self.criar_frame_cliente()
        self.criar_categorias()
        self.criar_frame_bebida()
        self.criar_frame_entrega_obs()
        self.criar_frame_pagamento()
        self.criar_frame_total_botoes()
        self.atualizar_total()

    def criar_frame_cliente(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="♡ Dados do Cliente")
        frame.pack(fill="x", padx=10, pady=(0,10))
        inner = tk.Frame(frame, bg=FUNDO_CARD)
        inner.pack(fill="x", padx=10, pady=10)
        row1 = tk.Frame(inner, bg=FUNDO_CARD)
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="Nome:", bg=FUNDO_CARD, fg=TEXTO_SUAVE).pack(side="left")
        self.entry_nome = ttk.Entry(row1, width=35)
        self.entry_nome.pack(side="left", padx=5)
        tk.Label(row1, text="Telefone:", bg=FUNDO_CARD, fg=TEXTO_SUAVE).pack(side="left", padx=(15,0))
        self.entry_tel = ttk.Entry(row1, width=18)
        self.entry_tel.pack(side="left", padx=5)
        row2 = tk.Frame(inner, bg=FUNDO_CARD)
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="Endereço:", bg=FUNDO_CARD, fg=TEXTO_SUAVE).pack(side="left")
        self.entry_end = ttk.Entry(row2, width=70)
        self.entry_end.pack(side="left", padx=5)

    def criar_categorias(self):
        self.notebook_cat = ttk.Notebook(self.scrollable_frame)
        self.notebook_cat.pack(fill="both", expand=True, padx=10, pady=10)
        frame_sopas = tk.Frame(self.notebook_cat, bg=FUNDO)
        self.notebook_cat.add(frame_sopas, text="🥣 Sopas")
        self.sopas_frame = CategoriaScrollDelivery(frame_sopas, "Cardápio de Sopas", cardapio, self.atualizar_total)
        self.sopas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        frame_tapiocas = tk.Frame(self.notebook_cat, bg=FUNDO)
        self.notebook_cat.add(frame_tapiocas, text="🌮 Tapiocas")
        self.tapioca_frame = CategoriaScrollDelivery(frame_tapiocas, "Cardápio de Tapiocas", tapioca, self.atualizar_total)
        self.tapioca_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def criar_frame_bebida(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="🥤 Bebida Avulsa")
        frame.pack(fill="x", padx=10, pady=(0,10))
        inner = tk.Frame(frame, bg=FUNDO_CARD)
        inner.pack(fill="x", padx=10, pady=10)
        self.bebida_var = tk.BooleanVar()
        self.chk_bebida = ttk.Checkbutton(inner, text="Adicionar bebida", variable=self.bebida_var, command=self.toggle_bebida)
        self.chk_bebida.pack(anchor="w")
        self.frame_bebida_detalhes = tk.Frame(inner, bg=FUNDO_CARD)
        self.frame_bebida_detalhes.pack(fill="x", pady=5)
        self.frame_bebida_detalhes.pack_forget()
        tk.Label(self.frame_bebida_detalhes, text="Nome:", bg=FUNDO_CARD, fg=TEXTO_SUAVE).pack(side="left")
        self.entry_bebida_nome = ttk.Entry(self.frame_bebida_detalhes, width=25)
        self.entry_bebida_nome.pack(side="left", padx=5)
        tk.Label(self.frame_bebida_detalhes, text="Valor (R$):", bg=FUNDO_CARD, fg=TEXTO_SUAVE).pack(side="left", padx=(10,0))
        self.entry_bebida_valor = ttk.Entry(self.frame_bebida_detalhes, width=10)
        self.entry_bebida_valor.pack(side="left", padx=5)
        self.entry_bebida_valor.bind("<KeyRelease>", lambda e: self.atualizar_total())

    def criar_frame_entrega_obs(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="🚚 Entrega")
        frame.pack(fill="x", padx=10, pady=(0,10))
        inner = tk.Frame(frame, bg=FUNDO_CARD)
        inner.pack(fill="x", padx=10, pady=10)
        row = tk.Frame(inner, bg=FUNDO_CARD)
        row.pack(fill="x")
        tk.Label(row, text="Taxa de entrega (R$):", bg=FUNDO_CARD, fg=TEXTO_SUAVE, width=18, anchor="w").pack(side="left")
        self.entry_entrega = ttk.Entry(row, width=12)
        self.entry_entrega.pack(side="left", padx=5)
        self.entry_entrega.insert(0, "0")
        self.entry_entrega.bind("<KeyRelease>", lambda e: self.atualizar_total())
        frame_obs = ttk.LabelFrame(self.scrollable_frame, text="📝 Observações")
        frame_obs.pack(fill="x", padx=10, pady=(0,10))
        inner_obs = tk.Frame(frame_obs, bg=FUNDO_CARD)
        inner_obs.pack(fill="x", padx=10, pady=10)
        self.txt_obs = tk.Text(inner_obs, height=3, width=80, font=("Segoe UI", 10), wrap="word", bg=FUNDO_CARD, fg=TEXTO, insertbackground=TEXTO, relief="flat", bd=0)
        self.txt_obs.pack(fill="x")

    def criar_frame_pagamento(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="💳 Forma de Pagamento")
        frame.pack(fill="x", padx=10, pady=(0,10))
        inner = tk.Frame(frame, bg=FUNDO_CARD)
        inner.pack(fill="x", padx=10, pady=10)
        radio_frame = tk.Frame(inner, bg=FUNDO_CARD)
        radio_frame.pack(anchor="w")
        self.radio_pix = ttk.Radiobutton(radio_frame, text="PIX", variable=self.pagamento_var, value="pix", command=self.on_pagamento_change)
        self.radio_pix.pack(side="left", padx=5)
        self.radio_dinheiro = ttk.Radiobutton(radio_frame, text="Dinheiro", variable=self.pagamento_var, value="dinheiro", command=self.on_pagamento_change)
        self.radio_dinheiro.pack(side="left", padx=5)
        self.frame_dinheiro = tk.Frame(inner, bg=FUNDO_CARD)
        self.frame_dinheiro.pack(fill="x", pady=5)
        self.frame_dinheiro.pack_forget()
        self.chk_troco = ttk.Checkbutton(self.frame_dinheiro, text="Precisa de troco?", variable=self.precisa_troco_var, command=self.on_troco_change)
        self.chk_troco.pack(anchor="w")
        self.frame_valor_recebido = tk.Frame(self.frame_dinheiro, bg=FUNDO_CARD)
        self.frame_valor_recebido.pack(fill="x", pady=5)
        self.frame_valor_recebido.pack_forget()
        tk.Label(self.frame_valor_recebido, text="Valor recebido (R$):", bg=FUNDO_CARD, fg=TEXTO_SUAVE).pack(side="left")
        self.entry_valor_recebido = ttk.Entry(self.frame_valor_recebido, width=12)
        self.entry_valor_recebido.pack(side="left", padx=5)
        self.entry_valor_recebido.bind("<KeyRelease>", lambda e: self.calcular_troco())
        self.label_troco = tk.Label(self.frame_valor_recebido, text="Troco: R$ 0,00", bg=FUNDO_CARD, fg=SUCESSO)
        self.label_troco.pack(side="left", padx=10)
        self.on_pagamento_change()

    def criar_frame_total_botoes(self):
        sep = tk.Frame(self.scrollable_frame, bg=BORDA, height=2)
        sep.pack(fill="x", padx=10, pady=(5,0))
        frame = tk.Frame(self.scrollable_frame, bg=FUNDO_CARD)
        frame.pack(fill="x", padx=10, pady=(0,10))
        self.label_total = tk.Label(frame, text="Total: R$ 0,00", font=("Segoe UI", 20, "bold"), bg=FUNDO_CARD, fg=PRIMARIA)
        self.label_total.pack(side="left", padx=12, pady=8)
        btn_frame = tk.Frame(frame, bg=FUNDO_CARD)
        btn_frame.pack(side="right", pady=6, padx=6)
        def criar_botao(texto, comando, cor):
            btn = tk.Button(btn_frame, text=texto, command=comando, bg=cor, fg="white", font=("Segoe UI", 10, "bold"), padx=12, pady=6, relief="flat", cursor="hand2")
            btn.pack(side="left", padx=4)
        criar_botao("🖨️ Imprimir", self.imprimir, PRIMARIA)
        criar_botao("📲 WhatsApp", self.enviar_whatsapp, SUCESSO)
        criar_botao("🧹 Novo Pedido", self.novo_pedido, PRIMARIA_ESC)
        criar_botao("📝 Cardápio", self.abrir_editor_cardapio, PRIMARIA_CLAR)
        criar_botao("🔧 Impressora", self.configurar_impressora, PRIMARIA_ESC)

    def on_pagamento_change(self):
        if self.pagamento_var.get() == "dinheiro":
            self.frame_dinheiro.pack(fill="x", pady=5)
            self.on_troco_change()
        else:
            self.frame_dinheiro.pack_forget()
            self.precisa_troco_var.set(False)
            self.valor_recebido_var.set(0.0)
            self.troco_var.set(0.0)
            self.label_troco.config(text="Troco: R$ 0,00")

    def on_troco_change(self):
        if self.precisa_troco_var.get():
            self.frame_valor_recebido.pack(fill="x", pady=5)
        else:
            self.frame_valor_recebido.pack_forget()
            self.valor_recebido_var.set(0.0)
            self.troco_var.set(0.0)
            self.label_troco.config(text="Troco: R$ 0,00")
        self.calcular_troco()

    def calcular_troco(self):
        if self.pagamento_var.get() != "dinheiro" or not self.precisa_troco_var.get():
            self.troco_var.set(0.0)
            self.valor_recebido_var.set(0.0)
            self.label_troco.config(text="Troco: R$ 0,00")
            return
        try:
            total_str = self.label_total.cget("text").split("R$")[1].strip().replace(",", ".")
            total = float(total_str)
            valor = float(self.entry_valor_recebido.get().replace(",", "."))
            self.valor_recebido_var.set(valor)
            if valor >= total:
                troco = valor - total
                self.troco_var.set(troco)
                self.label_troco.config(text=f"Troco: R$ {troco:.2f}", fg=SUCESSO)
            else:
                self.troco_var.set(0.0)
                self.label_troco.config(text="Valor insuficiente!", fg=AVISO)
        except:
            self.troco_var.set(0.0)
            self.valor_recebido_var.set(0.0)
            self.label_troco.config(text="Troco: R$ 0,00")

    def toggle_bebida(self):
        if self.bebida_var.get():
            self.frame_bebida_detalhes.pack(fill="x", pady=5)
        else:
            self.frame_bebida_detalhes.pack_forget()
        self.atualizar_total()

    def atualizar_total(self):
        vars_sopas = self.sopas_frame.get_quantidades_vars()
        vars_tapiocas = self.tapioca_frame.get_quantidades_vars()
        bebida = 0.0
        if self.bebida_var.get():
            try:
                bebida = float(self.entry_bebida_valor.get().replace(",", "."))
            except:
                bebida = 0.0
        try:
            entrega = float(self.entry_entrega.get().replace(",", "."))
        except:
            entrega = 0.0
        total = calcular_total(vars_sopas, cardapio, vars_tapiocas, tapioca, bebida, entrega)
        self.label_total.config(text=f"Total: R$ {total:.2f}")
        self.calcular_troco()

    def gerar_cupom_texto(self):
        L = []
        L.append("=" * 25)
        L.append("         🍲 SOPA DA ROXA")
        L.append("=" * 25)
        L.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        L.append(f"Cliente: {self.entry_nome.get() or 'NÃO INFORMADO'}")
        if self.entry_tel.get():
            L.append(f"Tel: {self.entry_tel.get()}")
        if self.entry_end.get():
            end_queb = quebrar_linha(self.entry_end.get(), 34)
            L.append("Endereço:")
            for linha in end_queb:
                L.append(f"  {linha}")
        L.append("-" * 25)
        L.append(f"{'ITEM':<10} {'QTD':>3} {'R$':>6} {'TOTAL':>9}")
        L.append("-" * 25)
    
        for prod, qtd in self.sopas_frame.get_itens():
            nome = prod['nome']
            preco = prod['preco']
            sub = preco * qtd
            linhas_nome = quebrar_linha(nome, 26)
            for i, ln in enumerate(linhas_nome):
                if i == 0:
                    L.append(f"{ln:<10} {qtd:>3}  {preco:>6.2f} {sub:>9.2f}")
                else:
                    L.append(f"{ln:<26}")
        for prod, qtd in self.tapioca_frame.get_itens():
            nome = prod['nome']
            preco = prod['preco']
            sub = preco * qtd
            linhas_nome = quebrar_linha(nome, 26)
            for i, ln in enumerate(linhas_nome):
                if i == 0:
                    L.append(f"{ln:<10} {qtd:>3}  {preco:>6.2f} {sub:>9.2f}")
                else:
                    L.append(f"{ln:<26}")
    
        if self.bebida_var.get() and self.entry_bebida_nome.get():
            nome = self.entry_bebida_nome.get()
            val = float(self.entry_bebida_valor.get().replace(",", ".")) if self.entry_bebida_valor.get() else 0
            if val > 0:
                linhas_nome = quebrar_linha(nome, 26)
                for i, ln in enumerate(linhas_nome):
                    if i == 0:
                        L.append(f"{ln:<10} {1:>3}  {val:>6.2f} {val:>9.2f}")
                    else:
                        L.append(f"{ln:<26}")
    
        try:
            entrega = float(self.entry_entrega.get().replace(",", "."))
            if entrega > 0:
                L.append(f"{'Taxa de entrega':<3}       {entrega:>3.2f}")
        except:
            pass
        
        L.append("-" * 30)
        total_str = self.label_total.cget("text").split("R$")[1].strip()
        L.append(f"TOTAL: R$ {total_str}")
        L.append("-" * 30)
        pagamento = "PIX" if self.pagamento_var.get() == "pix" else "Dinheiro"
        L.append(f"Pagamento: {pagamento}")
        if pagamento == "Dinheiro":
            if self.precisa_troco_var.get() and self.valor_recebido_var.get() > 0:
                L.append(f"Recebido: R$ {self.valor_recebido_var.get():.2f}")
                if self.troco_var.get() > 0:
                    L.append(f"Troco: R$ {self.troco_var.get():.2f}")
                else:
                    L.append("Valor insuficiente")
            elif self.precisa_troco_var.get():
                L.append("Valor recebido não informado")
            else:
                L.append("Sem troco")
        L.append("=" * 30)
        obs = self.txt_obs.get("1.0", "end-1c").strip()
        if obs:
            L.append("OBSERVAÇÕES:")
            obs_queb = quebrar_linha(obs, 34)
            for linha in obs_queb:
                L.append(f"  {linha}")
            L.append("=" * 30)
        L.append("")
        L.append("   Obrigado pela preferência!")
        L.append("   Sopa da Roxa")
        L.append("   (81) 99623-5992")
        L.append("   @sopadaroxa_82")
        L.append("=" * 30)
        return "\n".join(L)

    def imprimir(self):
        cupom = self.gerar_cupom_texto()
        self.mostrar_preview(cupom)
        agora = datetime.now()
        pasta = get_data_path(os.path.join("cupoms", agora.strftime("%Y-%m")))
        os.makedirs(pasta, exist_ok=True)
        arquivo = os.path.join(pasta, agora.strftime("cupom_%Y%m%d_%H%M%S.txt"))
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(cupom)
        resultado = imprimir_com_fallback(cupom, pasta)
        self.status_impressora.set(f"✅ {resultado}")
        self.atualizar_lista_meses()
        self.atualizar_status_impressora_async()

    def mostrar_preview(self, texto):
        preview = tk.Toplevel(self.root)
        preview.title("Pré-visualização do Cupom")
        preview.geometry("520x650")
        preview.configure(bg=FUNDO)
        text_w = tk.Text(preview, wrap="none", font=("Courier New", 10), bg=FUNDO_CARD, fg=TEXTO)
        text_w.insert("1.0", texto)
        text_w.config(state="disabled")
        scroll_y = ttk.Scrollbar(preview, orient="vertical", command=text_w.yview)
        scroll_x = ttk.Scrollbar(preview, orient="horizontal", command=text_w.xview)
        text_w.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        text_w.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        preview.grid_rowconfigure(0, weight=1)
        preview.grid_columnconfigure(0, weight=1)
        btn_fechar = tk.Button(preview, text="Fechar", command=preview.destroy, bg=PRIMARIA, fg="white", padx=10, pady=5, relief="flat")
        btn_fechar.grid(row=2, column=0, pady=10)

    def enviar_whatsapp(self):
        cupom = self.gerar_cupom_texto()
        msg = urllib.parse.quote(cupom)
        numero = self.entry_tel.get().strip()
        if numero:
            numero = ''.join(filter(str.isdigit, numero))
            if not numero.startswith("55"):
                numero = "55" + numero
            link = f"https://wa.me/{numero}?text={msg}"
        else:
            link = f"https://wa.me/?text={msg}"
        webbrowser.open(link)

    def novo_pedido(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_tel.delete(0, tk.END)
        self.entry_end.delete(0, tk.END)
        for item in self.sopas_frame.itens_widgets:
            item.quantidade.set(0)
        for item in self.tapioca_frame.itens_widgets:
            item.quantidade.set(0)
        self.bebida_var.set(False)
        self.toggle_bebida()
        self.entry_bebida_nome.delete(0, tk.END)
        self.entry_bebida_valor.delete(0, tk.END)
        self.entry_entrega.delete(0, tk.END)
        self.entry_entrega.insert(0, "0")
        self.txt_obs.delete("1.0", tk.END)
        self.pagamento_var.set("pix")
        self.precisa_troco_var.set(False)
        self.valor_recebido_var.set(0.0)
        self.troco_var.set(0.0)
        if hasattr(self, 'entry_valor_recebido'):
            self.entry_valor_recebido.delete(0, tk.END)
        self.on_pagamento_change()
        self.atualizar_total()

    def abrir_editor_cardapio(self):
        from editor_cardapio import EditorCardapio
        def recarregar_cardapio():
            from cardapio import carregar_cardapio
            new_sopas, new_tapiocas = carregar_cardapio()
            import cardapio as cardapio_mod
            cardapio_mod.cardapio = new_sopas
            cardapio_mod.tapioca = new_tapiocas
            self.sopas_frame.recarregar(new_sopas)
            self.tapioca_frame.recarregar(new_tapiocas)
            self.atualizar_total()
        EditorCardapio(self.root, recarregar_cardapio)

    def configurar_impressora(self):
        from utils_impressao import carregar_config, salvar_config, testar_conexao_bluetooth
        janela = tk.Toplevel(self.root)
        janela.title("Configurar Impressora Bluetooth")
        janela.geometry("550x450")
        janela.configure(bg=FUNDO)
        config = carregar_config()
        mac_atual = config.get("printer_mac")
        frame_status = tk.LabelFrame(janela, text="Status Atual", bg=FUNDO, fg=PRIMARIA)
        frame_status.pack(fill="x", padx=10, pady=5)
        status_texto = tk.StringVar()
        if mac_atual:
            if testar_conexao_bluetooth(mac_atual):
                status_texto.set(f"✅ Conectado à: {mac_atual}")
            else:
                status_texto.set(f"❌ Desconectado: {mac_atual}")
        else:
            status_texto.set("⚠️ Nenhuma impressora configurada")
        tk.Label(frame_status, textvariable=status_texto, bg=FUNDO).pack(pady=5)
        frame_novo = tk.LabelFrame(janela, text="Configurar Nova Impressora", bg=FUNDO, fg=PRIMARIA)
        frame_novo.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_novo, text="Endereço MAC:", bg=FUNDO).pack(pady=2)
        entry_mac = ttk.Entry(frame_novo, width=35)
        entry_mac.pack(pady=5)
        if mac_atual:
            entry_mac.insert(0, mac_atual)
        def testar_novo():
            mac = entry_mac.get().strip().upper()
            if not mac:
                messagebox.showwarning("Aviso", "Digite um endereço MAC.")
                return
            import re
            if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", mac):
                messagebox.showwarning("Aviso", "Formato inválido. Use XX:XX:XX:XX:XX:XX")
                return
            ok, msg = testar_conexao_bluetooth(mac)
            if ok:
                messagebox.showinfo("Teste", msg)
            else:
                messagebox.showerror("Teste", msg)
        def salvar():
            mac = entry_mac.get().strip().upper()
            if not mac:
                salvar_config({"printer_mac": None})
                janela.destroy()
                self.atualizar_status_impressora_async()
                messagebox.showinfo("Sucesso", "Impressora removida.")
                return
            import re
            if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", mac):
                messagebox.showwarning("Aviso", "Formato inválido.")
                return
            salvar_config({"printer_mac": mac})
            janela.destroy()
            self.atualizar_status_impressora_async()
            messagebox.showinfo("Sucesso", "Impressora configurada.")
        btn_frame = tk.Frame(janela, bg=FUNDO)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Testar Conexão", command=testar_novo, bg=PRIMARIA, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Salvar", command=salvar, bg=SUCESSO, fg="white", relief="flat").pack(side="left", padx=5)
        if mac_atual:
            def limpar():
                salvar_config({"printer_mac": None})
                janela.destroy()
                self.atualizar_status_impressora_async()
                messagebox.showinfo("Sucesso", "Impressora removida.")
            tk.Button(btn_frame, text="Desconectar", command=limpar, bg=AVISO, fg="white", relief="flat").pack(side="left", padx=5)
        instrucoes = "Para descobrir o MAC:\n1. Configurações > Bluetooth e dispositivos\n2. Mais opções de Bluetooth > Hardware\n3. Selecione a impressora > Propriedades\n4. Detalhes > Endereço do dispositivo"
        tk.Label(janela, text=instrucoes, bg=FUNDO, font=("Segoe UI", 9), justify="left", wraplength=500).pack(pady=10)

    def atualizar_status_impressora_async(self):
        def task():
            from utils_impressao import carregar_config, testar_conexao_bluetooth
            config = carregar_config()
            mac = config.get("printer_mac")
            if mac:
                ok, msg = testar_conexao_bluetooth(mac)
                if ok:
                    self.status_impressora.set(f"🟢 Impressora: {mac}")
                else:
                    self.status_impressora.set(f"🟡 Impressora: {mac} (desconectada)")
            else:
                self.status_impressora.set("🔴 Nenhuma impressora configurada")
        threading.Thread(target=task, daemon=True).start()

    # ------------------------------------------------------------
    # MESAS
    # ------------------------------------------------------------
    def criar_frame_mesas(self):
        frame = tk.Frame(self.notebook, bg=FUNDO)
        top_frame = tk.Frame(frame, bg=FUNDO)
        top_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(top_frame, text="➕ Adicionar Mesa", command=self.adicionar_mesa, bg=PRIMARIA, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(top_frame, text="➖ Remover Mesa", command=self.remover_mesa, bg=AVISO, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(top_frame, text="🔄 Atualizar", command=self.atualizar_grid_mesas, bg=PRIMARIA_CLAR, fg="white", relief="flat").pack(side="left", padx=5)

        canvas = tk.Canvas(frame, bg=FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.frame_mesas_grid = tk.Frame(canvas, bg=FUNDO)
        canvas.create_window((0, 0), window=self.frame_mesas_grid, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.frame_mesas_grid.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind("<Enter>", lambda e: canvas.focus_set())
        canvas.bind("<Configure>", self._on_canvas_configure_mesas)

        self.mesas_botoes = {}
        self.atualizar_grid_mesas()
        return frame

    def _on_canvas_configure_mesas(self, event):
        self.atualizar_grid_mesas()

    def atualizar_grid_mesas(self):
        for widget in self.frame_mesas_grid.winfo_children():
            widget.destroy()
        self.mesas_botoes.clear()
        mesas = gm.get_mesas()
        if not mesas:
            return
        canvas = self.frame_mesas_grid.master
        largura = canvas.winfo_width()
        if largura <= 0:
            largura = 800
        card_width = 250
        padding = 30
        n_cols = max(1, largura // (card_width + padding))
        n_cols = min(n_cols, len(mesas))
        for i, (mid, num, status) in enumerate(mesas):
            row = i // n_cols
            col = i % n_cols
            card = tk.Frame(self.frame_mesas_grid, bg=FUNDO_CARD, relief="flat", bd=0, highlightbackground=BORDA, highlightthickness=1)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            card.columnconfigure(0, weight=1)
            icone = "🟢" if status == "livre" else "🔴"
            cor_status = SUCESSO if status == "livre" else AVISO
            lbl_icone = tk.Label(card, text=icone, bg=FUNDO_CARD, font=("Segoe UI", 16))
            lbl_icone.pack(pady=(10,0))
            lbl_num = tk.Label(card, text=f"Mesa {num}", bg=FUNDO_CARD, fg=PRIMARIA, font=("Segoe UI", 14, "bold"))
            lbl_num.pack(pady=5)
            lbl_status = tk.Label(card, text=status.upper(), bg=FUNDO_CARD, fg=cor_status, font=("Segoe UI", 10, "bold"))
            lbl_status.pack()
            if status != "livre":
                pedido_status = gm.obter_pedido_status(mid)
                if pedido_status == "preparando":
                    status_pedido = "🟡 Preparando"
                    cor_pedido = SECUNDARIA
                elif pedido_status == "pronto":
                    status_pedido = "🟢 Pronto"
                    cor_pedido = SUCESSO
                else:
                    status_pedido = "⚪ Aguardando"
                    cor_pedido = TEXTO_SUAVE
                lbl_pedido_status = tk.Label(card, text=status_pedido, bg=FUNDO_CARD, fg=cor_pedido, font=("Segoe UI", 9, "bold"))
                lbl_pedido_status.pack()
            btn = tk.Button(card, text="Abrir Mesa", command=lambda m=mid, n=num, s=status: self.abrir_mesa(m, n, s), bg=PRIMARIA, fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, relief="flat", cursor="hand2")
            btn.pack(pady=(10,10))
            self.mesas_botoes[mid] = btn
        for col in range(n_cols):
            self.frame_mesas_grid.grid_columnconfigure(col, weight=1)

    def adicionar_mesa(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Mesa")
        dialog.geometry("300x150")
        dialog.configure(bg=FUNDO_CARD)
        tk.Label(dialog, text="Número da mesa:", bg=FUNDO_CARD, fg=TEXTO).pack(pady=10)
        entry = ttk.Entry(dialog)
        entry.pack(pady=5)
        def salvar():
            try:
                num = int(entry.get())
                if gm.adicionar_mesa(num):
                    self.atualizar_grid_mesas()
                    dialog.destroy()
                else:
                    messagebox.showerror("Erro", "Mesa já existe ou inválida.")
            except:
                messagebox.showerror("Erro", "Número inválido.")
        tk.Button(dialog, text="Adicionar", command=salvar, bg=PRIMARIA, fg="white").pack(pady=10)

    def remover_mesa(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Remover Mesa")
        dialog.geometry("300x150")
        dialog.configure(bg=FUNDO_CARD)
        tk.Label(dialog, text="Número da mesa a remover:", bg=FUNDO_CARD, fg=TEXTO).pack(pady=10)
        entry = ttk.Entry(dialog)
        entry.pack(pady=5)
        def remover():
            try:
                num = int(entry.get())
                if gm.remover_mesa(num):
                    self.atualizar_grid_mesas()
                    dialog.destroy()
                else:
                    messagebox.showerror("Erro", "Mesa não está livre ou não existe.")
            except:
                messagebox.showerror("Erro", "Número inválido.")
        tk.Button(dialog, text="Remover", command=remover, bg=AVISO, fg="white").pack(pady=10)

    def abrir_mesa(self, mesa_id, numero, status):
        pedido = gm.get_pedido_aberto(mesa_id)
        if pedido:
            self.abrir_popup_pedido(mesa_id, pedido["id"], numero)
        else:
            pedido_id = gm.criar_pedido(mesa_id)
            if pedido_id:
                self.atualizar_grid_mesas()
                self.abrir_popup_pedido(mesa_id, pedido_id, numero)
            else:
                messagebox.showerror("Erro", "Não foi possível criar pedido para esta mesa.")
    
    # ------------------------------------------------------------
    # POPUP DA MESA
    # ------------------------------------------------------------
    def abrir_popup_pedido(self, mesa_id, pedido_id, numero_mesa):
        popup = tk.Toplevel(self.root)
        popup.title(f"Mesa {numero_mesa} - Pedido")
        popup.geometry("800x600")
        popup.configure(bg=FUNDO_CARD)

        canvas = tk.Canvas(popup, bg=FUNDO_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        frame_interior = tk.Frame(canvas, bg=FUNDO_CARD)
        canvas.create_window((0, 0), window=frame_interior, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        frame_interior.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        notebook = ttk.Notebook(frame_interior)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        frame_sopas = tk.Frame(notebook, bg=FUNDO_CARD)
        notebook.add(frame_sopas, text="🥣 Sopas")
        frame_tapiocas = tk.Frame(notebook, bg=FUNDO_CARD)
        notebook.add(frame_tapiocas, text="🌮 Tapiocas")
        frame_bebidas = tk.Frame(notebook, bg=FUNDO_CARD)
        notebook.add(frame_bebidas, text="🥤 Bebidas")

        # Lista de itens do pedido com checkboxes
        frame_lista = tk.LabelFrame(frame_interior, text="Itens do Pedido", bg=FUNDO_CARD, fg=PRIMARIA)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas_itens = tk.Canvas(frame_lista, bg=FUNDO_CARD, highlightthickness=0)
        scrollbar_itens = ttk.Scrollbar(frame_lista, orient="vertical", command=canvas_itens.yview)
        frame_itens = tk.Frame(canvas_itens, bg=FUNDO_CARD)
        canvas_itens.create_window((0, 0), window=frame_itens, anchor="nw")
        canvas_itens.configure(yscrollcommand=scrollbar_itens.set)
        canvas_itens.pack(side="left", fill="both", expand=True)
        scrollbar_itens.pack(side="right", fill="y")
        frame_itens.bind("<Configure>", lambda e: canvas_itens.configure(scrollregion=canvas_itens.bbox("all")))
        canvas_itens.bind("<MouseWheel>", lambda e: canvas_itens.yview_scroll(int(-1*(e.delta/120)), "units"))

        total_var = tk.StringVar(value="Total: R$ 0.00")
        lbl_total = tk.Label(frame_interior, textvariable=total_var, font=("Segoe UI", 14, "bold"), bg=FUNDO_CARD, fg=PRIMARIA)
        lbl_total.pack(pady=5)

        status_var = tk.StringVar(value="Status: Carregando...")
        lbl_status = tk.Label(frame_interior, textvariable=status_var, font=("Segoe UI", 12, "bold"), bg=FUNDO_CARD, fg=AVISO)
        lbl_status.pack(pady=2)

        def obter_status_pedido():
            conn = sqlite3.connect(gm.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM pedidos WHERE id=?", (pedido_id,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else "ativo"

        def atualizar_status():
            status = obter_status_pedido()
            if status == "ativo":
                status_var.set("Status: Aguardando envio para cozinha")
                lbl_status.config(fg=AVISO)
            elif status == "preparando":
                status_var.set("Status: Em preparação")
                lbl_status.config(fg=SECUNDARIA)
            elif status == "pronto":
                status_var.set("Status: Pronto para servir")
                lbl_status.config(fg=SUCESSO)
            else:
                status_var.set(f"Status: {status.upper()}")

        btn_enviar = tk.Button(frame_interior, text="🍳 Enviar para Cozinha", command=lambda: None,
                               bg=PRIMARIA, fg="white", font=("Segoe UI", 12, "bold"), relief="flat")
        btn_enviar.pack_forget()

        # Campo de observações
        frame_obs = tk.LabelFrame(frame_interior, text="📝 Observações do Pedido", bg=FUNDO_CARD, fg=PRIMARIA)
        frame_obs.pack(fill="x", padx=10, pady=5)
        obs_text = tk.Text(frame_obs, height=3, font=("Segoe UI", 10), bg=FUNDO_CARD, fg=TEXTO, wrap="word")
        obs_text.pack(fill="x", padx=5, pady=5)
        obs_atual = gm.obter_observacao(pedido_id)
        obs_text.insert("1.0", obs_atual)
        def salvar_obs(event=None):
            obs = obs_text.get("1.0", "end-1c")
            gm.salvar_observacao(pedido_id, obs)
        obs_text.bind("<FocusOut>", salvar_obs)

        def remover_item_e_atualizar(item_id):
            gm.remover_item(item_id)
            atualizar_interface()
            self.atualizar_pedidos_cozinha(self.cozinha_tree)
            self.atualizar_grid_mesas()

        def atualizar_interface():
            nonlocal btn_enviar
            pedido = gm.get_pedido_aberto(mesa_id)
            if not pedido:
                return
            for widget in frame_itens.winfo_children():
                widget.destroy()
            total = 0
            for item in pedido["itens"]:
                item_id, nome, preco, qtd, tipo, para_viagem, enviado, entregue = item
                subtotal = preco * qtd
                total += subtotal
                viagem = " (viagem)" if para_viagem else ""
                item_frame = tk.Frame(frame_itens, bg=FUNDO_CARD)
                item_frame.pack(fill="x", pady=2)
                # Checkbox "Entregue"
                var = tk.BooleanVar(value=entregue == 1)
                chk = tk.Checkbutton(item_frame, variable=var, bg=FUNDO_CARD,
                                     command=lambda iid=item_id, v=var: gm.marcar_item_entregue(iid, 1 if v.get() else 0))
                chk.pack(side="left", padx=2)
                # Nome e quantidade
                lbl = tk.Label(item_frame, text=f"{nome}{viagem} - {qtd}x", bg=FUNDO_CARD, fg=TEXTO, font=("Segoe UI", 10))
                lbl.pack(side="left", padx=5)
                # Preço
                lbl_preco = tk.Label(item_frame, text=f"R${preco:.2f}", bg=FUNDO_CARD, fg=SECUNDARIA)
                lbl_preco.pack(side="right", padx=5)
                # Botão de remover (X)
                btn_remover = tk.Button(item_frame, text="❌", command=lambda iid=item_id: remover_item_e_atualizar(iid),
                                        bg=AVISO, fg="white", relief="flat", font=("Segoe UI", 8, "bold"), cursor="hand2")
                btn_remover.pack(side="right", padx=2)
            total_var.set(f"Total: R$ {total:.2f}")
            atualizar_status()
            self.atualizar_grid_mesas()
            if hasattr(self, 'cozinha_tree'):
                self.atualizar_pedidos_cozinha(self.cozinha_tree)
            tem_nao_entregue = any(not item[7] for item in pedido["itens"])
            if tem_nao_entregue and obter_status_pedido() in ("ativo", "preparando", "pronto"):
                btn_enviar.pack(pady=5)
            else:
                btn_enviar.pack_forget()
        def adicionar_item_dialog(produto, tipo):
            dialog = tk.Toplevel(popup)
            dialog.title("Adicionar Item")
            dialog.geometry("300x220")
            dialog.configure(bg=FUNDO_CARD)
            tk.Label(dialog, text=f"Item: {produto['nome']}", bg=FUNDO_CARD, font=("Segoe UI", 10, "bold")).pack(pady=5)
            tk.Label(dialog, text="Quantidade:", bg=FUNDO_CARD).pack()
            spin_qtd = tk.Spinbox(dialog, from_=1, to=99, width=5)
            spin_qtd.pack(pady=5)
            tk.Label(dialog, text="Tipo:", bg=FUNDO_CARD).pack()
            var_tipo = tk.StringVar(value="mesa")
            frame_tipo = tk.Frame(dialog, bg=FUNDO_CARD)
            frame_tipo.pack(pady=5)
            tk.Radiobutton(frame_tipo, text="Consumir no local (mesa)", variable=var_tipo, value="mesa", bg=FUNDO_CARD).pack(side="left", padx=5)
            tk.Radiobutton(frame_tipo, text="Para viagem", variable=var_tipo, value="viagem", bg=FUNDO_CARD).pack(side="left", padx=5)
            def confirmar():
                qtd = int(spin_qtd.get())
                para_viagem = 1 if var_tipo.get() == "viagem" else 0
                nome_completo = f"{produto['nome']} (viagem)" if para_viagem else f"{produto['nome']} (mesa)"
                gm.adicionar_item(pedido_id, nome_completo, produto['preco'], qtd, tipo, para_viagem)
                atualizar_interface()
                self.atualizar_pedidos_cozinha(self.cozinha_tree)
                dialog.destroy()
            tk.Button(dialog, text="Adicionar", command=confirmar, bg=SUCESSO, fg="white").pack(pady=10)

        from cardapio import cardapio, tapioca
        for prod in cardapio:
            btn = tk.Button(frame_sopas, text=f"{prod['nome']} - R${prod['preco']:.2f}",
                            command=lambda p=prod, t="sopa": adicionar_item_dialog(p, t),
                            bg=PRIMARIA_CLAR, fg="white", font=("Segoe UI", 10), relief="flat")
            btn.pack(fill="x", padx=5, pady=2)
        for prod in tapioca:
            btn = tk.Button(frame_tapiocas, text=f"{prod['nome']} - R${prod['preco']:.2f}",
                            command=lambda p=prod, t="tapioca": adicionar_item_dialog(p, t),
                            bg=PRIMARIA_CLAR, fg="white", font=("Segoe UI", 10), relief="flat")
            btn.pack(fill="x", padx=5, pady=2)

        def adicionar_bebida_personalizada():
            dialog = tk.Toplevel(popup)
            dialog.title("Adicionar Bebida")
            dialog.geometry("350x280")
            dialog.configure(bg=FUNDO_CARD)
            tk.Label(dialog, text="Nome da bebida:", bg=FUNDO_CARD).pack(pady=5)
            entry_nome = ttk.Entry(dialog, width=30)
            entry_nome.pack(pady=5)
            tk.Label(dialog, text="Valor (R$):", bg=FUNDO_CARD).pack(pady=5)
            entry_valor = ttk.Entry(dialog, width=15)
            entry_valor.pack(pady=5)
            tk.Label(dialog, text="Quantidade:", bg=FUNDO_CARD).pack(pady=5)
            spin_qtd = tk.Spinbox(dialog, from_=1, to=99, width=5)
            spin_qtd.pack(pady=5)
            tk.Label(dialog, text="Tipo:", bg=FUNDO_CARD).pack()
            var_tipo = tk.StringVar(value="mesa")
            frame_tipo = tk.Frame(dialog, bg=FUNDO_CARD)
            frame_tipo.pack(pady=5)
            tk.Radiobutton(frame_tipo, text="Consumir no local (mesa)", variable=var_tipo, value="mesa", bg=FUNDO_CARD).pack(side="left", padx=5)
            tk.Radiobutton(frame_tipo, text="Para viagem", variable=var_tipo, value="viagem", bg=FUNDO_CARD).pack(side="left", padx=5)
            def salvar():
                nome = entry_nome.get().strip()
                if not nome:
                    messagebox.showerror("Erro", "Digite o nome da bebida.")
                    return
                try:
                    valor = float(entry_valor.get().replace(",", "."))
                    qtd = int(spin_qtd.get())
                    para_viagem = 1 if var_tipo.get() == "viagem" else 0
                    nome_completo = f"{nome} (viagem)" if para_viagem else f"{nome} (mesa)"
                    gm.adicionar_item(pedido_id, nome_completo, valor, qtd, "bebida_personalizada", para_viagem)
                    atualizar_interface()
                    self.atualizar_pedidos_cozinha(self.cozinha_tree)
                    dialog.destroy()
                except:
                    messagebox.showerror("Erro", "Valor inválido.")
            tk.Button(dialog, text="Adicionar", command=salvar, bg=SUCESSO, fg="white").pack(pady=10)

        btn_add_bebida = tk.Button(frame_bebidas, text="➕ Adicionar Bebida Personalizada", command=adicionar_bebida_personalizada, bg=PRIMARIA, fg="white", font=("Segoe UI", 10), relief="flat")
        btn_add_bebida.pack(pady=10)

        def enviar_para_cozinha():
            nonlocal btn_enviar
            current_status = obter_status_pedido()
            conn = sqlite3.connect(gm.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE itens_pedido SET enviado_para_cozinha=1 WHERE pedido_id=? AND entregue=0", (pedido_id,))
            conn.commit()
            conn.close()
            if current_status == "pronto":
                gm.atualizar_status_pedido(pedido_id, "preparando")
            atualizar_interface()
            self.atualizar_pedidos_cozinha(self.cozinha_tree)
            self.atualizar_grid_mesas()
            messagebox.showinfo("Enviado", "Itens não entregues foram enviados para a cozinha.")
            btn_enviar.pack_forget()

        btn_enviar.config(command=enviar_para_cozinha)

        def fechar_conta():
            pag_window = tk.Toplevel(popup)
            pag_window.title("Fechar Conta")
            pag_window.geometry("400x550")
            pag_window.configure(bg=FUNDO_CARD)

            forma = tk.StringVar(value="pix")
            tk.Label(pag_window, text="Forma de pagamento:", bg=FUNDO_CARD).pack(pady=5)
            ttk.Radiobutton(pag_window, text="PIX", variable=forma, value="pix").pack()
            ttk.Radiobutton(pag_window, text="Dinheiro", variable=forma, value="dinheiro").pack()
            ttk.Radiobutton(pag_window, text="Cartão", variable=forma, value="cartao").pack()

            dividir_var = tk.BooleanVar(value=False)
            frame_div = tk.Frame(pag_window, bg=FUNDO_CARD)
            ttk.Checkbutton(pag_window, text="Dividir conta entre pessoas", variable=dividir_var,
                            command=lambda: frame_div.pack(fill="x", pady=5) if dividir_var.get() else frame_div.pack_forget()).pack()
            tk.Label(frame_div, text="Número de pessoas:", bg=FUNDO_CARD).pack()
            spin_pessoas = tk.Spinbox(frame_div, from_=2, to=50, width=5)
            spin_pessoas.pack()
            lbl_por_pessoa = tk.Label(frame_div, text="", bg=FUNDO_CARD, fg=PRIMARIA, font=("Segoe UI", 10, "bold"))
            lbl_por_pessoa.pack(pady=5)

            def atualizar_previa(*args):
                if dividir_var.get():
                    try:
                        total = float(total_var.get().split("R$")[1].strip())
                        pessoas = int(spin_pessoas.get())
                        if pessoas > 0:
                            valor_por_pessoa = total / pessoas
                            lbl_por_pessoa.config(text=f"Valor por pessoa: R$ {valor_por_pessoa:.2f}")
                        else:
                            lbl_por_pessoa.config(text="")
                    except:
                        lbl_por_pessoa.config(text="")
                else:
                    lbl_por_pessoa.config(text="")
            spin_pessoas.bind("<KeyRelease>", atualizar_previa)
            dividir_var.trace_add("write", lambda *a: atualizar_previa())

            frame_embalagem = tk.Frame(pag_window, bg=FUNDO_CARD)
            frame_embalagem.pack(pady=10)
            tk.Label(frame_embalagem, text="Teve embalagem para viagem?", bg=FUNDO_CARD).pack()
            var_embalagem = tk.BooleanVar(value=False)
            chk_embalagem = ttk.Checkbutton(frame_embalagem, text="Sim", variable=var_embalagem)
            chk_embalagem.pack()
            frame_qtd_embalagem = tk.Frame(pag_window, bg=FUNDO_CARD)
            tk.Label(frame_qtd_embalagem, text="Quantidade de embalagens (R$2 cada):", bg=FUNDO_CARD).pack()
            spin_embalagem = tk.Spinbox(frame_qtd_embalagem, from_=1, to=20, width=5)
            spin_embalagem.pack()
            frame_qtd_embalagem.pack_forget()

            def toggle_embalagem():
                if var_embalagem.get():
                    frame_qtd_embalagem.pack(pady=5)
                else:
                    frame_qtd_embalagem.pack_forget()
            var_embalagem.trace_add("write", lambda *a: toggle_embalagem())

            frame_troco = tk.Frame(pag_window, bg=FUNDO_CARD)
            frame_troco.pack(pady=10)
            tk.Label(frame_troco, text="Valor recebido (se dinheiro):", bg=FUNDO_CARD).pack()
            entry_recebido = ttk.Entry(frame_troco, width=15)
            entry_recebido.pack()
            lbl_troco = tk.Label(frame_troco, text="Troco: R$ 0,00", bg=FUNDO_CARD, fg=SUCESSO)
            lbl_troco.pack()

            def calcular_troco():
                try:
                    total = float(total_var.get().split("R$")[1].strip())
                    if var_embalagem.get():
                        qtd = int(spin_embalagem.get())
                        total += qtd * 2
                    recebido = float(entry_recebido.get().replace(",", "."))
                    troco = recebido - total
                    if troco < 0:
                        lbl_troco.config(text="Valor insuficiente!", fg="red")
                    else:
                        lbl_troco.config(text=f"Troco: R$ {troco:.2f}", fg=SUCESSO)
                except:
                    lbl_troco.config(text="Digite um valor válido", fg="red")
            entry_recebido.bind("<KeyRelease>", lambda e: calcular_troco())

            def confirmar_fechamento():
                total = float(total_var.get().split("R$")[1].strip())
                forma_pag = forma.get()
                recebido = None
                taxa_embalagem = 0
                if var_embalagem.get():
                    try:
                        qtd = int(spin_embalagem.get())
                        taxa_embalagem = qtd * 2
                        total += taxa_embalagem
                    except:
                        messagebox.showerror("Erro", "Quantidade de embalagens inválida.")
                        return
                if forma_pag == "dinheiro":
                    try:
                        recebido = float(entry_recebido.get().replace(",", "."))
                        if recebido < total:
                            messagebox.showerror("Erro", "Valor recebido insuficiente.")
                            return
                    except:
                        messagebox.showerror("Erro", "Digite o valor recebido.")
                        return
                pedido_fechado = gm.fechar_pedido(pedido_id, forma_pag, recebido, taxa_embalagem)
                if pedido_fechado:
                    cupom = self.gerar_cupom_mesa(pedido_fechado)
                    self.mostrar_preview(cupom)
                    agora = datetime.now()
                    pasta = get_data_path(os.path.join("cupoms", agora.strftime("%Y-%m")))
                    os.makedirs(pasta, exist_ok=True)
                    arquivo = os.path.join(pasta, agora.strftime("cupom_mesa_%Y%m%d_%H%M%S.txt"))
                    with open(arquivo, "w", encoding="utf-8") as f:
                        f.write(cupom)
                    self.status_impressora.set(f"✅ Cupom da mesa {numero_mesa} salvo em {arquivo}")
                    if dividir_var.get():
                        try:
                            pessoas = int(spin_pessoas.get())
                            por_pessoa = total / pessoas
                            messagebox.showinfo("Conta fechada", f"Total: R$ {total:.2f}\nDividido por {pessoas} pessoas: R$ {por_pessoa:.2f} cada.\nCupom salvo.")
                        except:
                            messagebox.showinfo("Conta fechada", f"Total: R$ {total:.2f}\nCupom salvo.")
                    else:
                        messagebox.showinfo("Conta fechada", f"Total: R$ {total:.2f}\nCupom salvo.")
                    popup.destroy()
                    self.atualizar_grid_mesas()
                    self.atualizar_pedidos_cozinha(self.cozinha_tree)
                else:
                    messagebox.showerror("Erro", "Falha ao fechar pedido.")
            tk.Button(pag_window, text="Fechar Conta", command=confirmar_fechamento, bg=SUCESSO, fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

        btn_fechar = tk.Button(frame_interior, text="💳 Fechar Conta", command=fechar_conta, bg=SECUNDARIA, fg="white", font=("Segoe UI", 12, "bold"), relief="flat")
        btn_fechar.pack(pady=10)

        atualizar_interface()

    def gerar_cupom_mesa(self, pedido_fechado):
        linhas = []
        linhas.append("="*36)
        linhas.append("         🍲 SOPA DA ROXA")
        linhas.append("="*36)
        linhas.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        linhas.append(f"Mesa: {pedido_fechado['mesa']}")
        linhas.append("-"*36)
        linhas.append(f"{'ITEM':<26} {'QTD':>3} {'R$':>6} {'TOTAL':>7}")
        linhas.append("-"*36)
        for item in pedido_fechado["itens"]:
            nome = item[0]
            preco = item[1]
            qtd = item[2]
            viagem = item[3]
            subtotal = preco * qtd
            linhas_nome = quebrar_linha(nome, 26)
            for i, ln in enumerate(linhas_nome):
                if i == 0:
                    tag = " (V)" if viagem else ""
                    ln_exib = (ln + tag)[:26]
                    linhas.append(f"{ln_exib:<26} {qtd:>3}  {preco:>5.2f} {subtotal:>7.2f}")
                else:
                    linhas.append(f"{ln:<26}")
        if pedido_fechado['taxa_embalagem'] > 0:
            linhas.append(f"{'Embalagem':<26}       {pedido_fechado['taxa_embalagem']:>6.2f}")
        linhas.append("-"*36)
        linhas.append(f"TOTAL: R$ {pedido_fechado['total']:.2f}")
        if pedido_fechado['taxa_embalagem'] > 0:
            linhas.append(f"(inclui R$ {pedido_fechado['taxa_embalagem']:.2f})")
        linhas.append("-"*36)
        linhas.append(f"Pagamento: {pedido_fechado['forma_pagamento'].upper()}")
        if pedido_fechado.get('valor_recebido'):
            linhas.append(f"Recebido: R$ {pedido_fechado['valor_recebido']:.2f}")
            troco = pedido_fechado['valor_recebido'] - pedido_fechado['total']
            linhas.append(f"Troco: R$ {troco:.2f}")
        linhas.append("="*36)
        linhas.append("")
        linhas.append("   Obrigado pela preferência!")
        linhas.append("   Sopa da Roxa")
        linhas.append("   (81) 99623-5992")
        linhas.append("   @sopadaroxa_82")
        linhas.append("="*36)
        return "\n".join(linhas)

    # ------------------------------------------------------------
    # COZINHA
    # ------------------------------------------------------------
    def criar_frame_cozinha(self):
        frame = tk.Frame(self.notebook, bg=FUNDO)
        paned = tk.PanedWindow(frame, orient="horizontal", bg=FUNDO, sashrelief="flat", sashwidth=4)
        paned.pack(fill="both", expand=True)

        left_frame = tk.Frame(paned, bg=FUNDO)
        paned.add(left_frame, width=500)
        tree = ttk.Treeview(left_frame, columns=("Mesa", "Data/Hora", "Status", "Total"), show="headings", height=20)
        tree.heading("Mesa", text="Mesa")
        tree.heading("Data/Hora", text="Data/Hora")
        tree.heading("Status", text="Status")
        tree.heading("Total", text="Total (R$)")
        tree.column("Mesa", width=80)
        tree.column("Data/Hora", width=150)
        tree.column("Status", width=120)
        tree.column("Total", width=100)
        tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(left_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.bind("<MouseWheel>", lambda e: tree.yview_scroll(int(-1*(e.delta/120)), "units"))

        right_frame = tk.Frame(paned, bg=FUNDO)
        paned.add(right_frame, width=400)
        tk.Label(right_frame, text="Detalhes do Pedido:", bg=FUNDO, fg=PRIMARIA, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        self.detalhes_text = tk.Text(right_frame, wrap="word", font=("Segoe UI", 20), bg=FUNDO_CARD, fg=TEXTO, relief="flat", height=15)
        self.detalhes_text.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_detalhes = ttk.Scrollbar(self.detalhes_text, orient="vertical", command=self.detalhes_text.yview)
        self.detalhes_text.configure(yscrollcommand=scroll_detalhes.set)
        scroll_detalhes.pack(side="right", fill="y")

        btn_frame = tk.Frame(frame, bg=FUNDO)
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="🔄 Atualizar", command=lambda: self.atualizar_pedidos_cozinha(tree), bg=PRIMARIA, fg="white", font=("Segoe UI", 12, "bold"), height=2, width=15, relief="flat").pack(side="left", padx=5)
        tk.Button(btn_frame, text="✅ Preparando", command=lambda: self.marcar_status_pedido(tree, "preparando"), bg=SECUNDARIA, fg="white", font=("Segoe UI", 12, "bold"), height=2, width=15, relief="flat").pack(side="left", padx=5)
        tk.Button(btn_frame, text="🍽️ Pronto", command=lambda: self.marcar_status_pedido(tree, "pronto"), bg=SUCESSO, fg="white", font=("Segoe UI", 12, "bold"), height=2, width=15, relief="flat").pack(side="left", padx=5)

        self.cozinha_tree = tree
        self.atualizar_pedidos_cozinha(tree)
        tree.bind("<<TreeviewSelect>>", lambda e: self.mostrar_detalhes_pedido(tree))
        return frame

    def atualizar_pedidos_cozinha(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        pedidos = gm.listar_pedidos_ativos()
        for pid, mesa_num, data_hora, status, total in pedidos:
            data_str = data_hora[:16]
            tree.insert("", "end", iid=pid, values=(mesa_num, data_str, status.upper(), f"{total:.2f}"))
        self.detalhes_text.delete("1.0", tk.END)

    def mostrar_detalhes_pedido(self, tree):
        selecionado = tree.selection()
        if not selecionado:
            self.detalhes_text.delete("1.0", tk.END)
            return
        pid = selecionado[0]
        itens = gm.obter_itens_com_status(pid)
        observacao = gm.obter_observacao(pid)
        detalhes = []
        if observacao and observacao.strip():
            detalhes.append(f"📝 Observação: {observacao}")
            detalhes.append("")
        for item in itens:
            nome = item[1]
            qtd = item[3]
            para_viagem = item[5]
            entregue = item[7]
            viagem = " (viagem)" if para_viagem else ""
            if entregue:
                detalhes.append(f"✅ {nome}{viagem} - {qtd}x (já foi feito)")
            else:
                detalhes.append(f"🆕 {nome}{viagem} - {qtd}x")
        self.detalhes_text.delete("1.0", tk.END)
        self.detalhes_text.insert("1.0", "\n".join(detalhes))

    def marcar_status_pedido(self, tree, novo_status):
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um pedido.")
            return
        pid = selecionado[0]
        gm.atualizar_status_pedido(pid, novo_status)
        self.atualizar_pedidos_cozinha(tree)
        self.atualizar_grid_mesas()

    # ------------------------------------------------------------
    # HISTÓRICO
    # ------------------------------------------------------------
    def construir_aba_historico(self):
        paned = tk.PanedWindow(self.frame_historico, orient="horizontal", bg=FUNDO, sashrelief="flat", sashwidth=4)
        paned.pack(fill="both", expand=True)
        left_frame = tk.Frame(paned, bg=FUNDO)
        paned.add(left_frame, width=300)
        tk.Label(left_frame, text="📁 Meses disponíveis:", bg=FUNDO, fg=PRIMARIA, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5, pady=5)
        self.lista_meses = tk.Listbox(left_frame, height=6, font=("Segoe UI", 10), bg=FUNDO_CARD, fg=TEXTO, selectbackground=PRIMARIA, selectforeground="white", relief="flat", bd=0)
        self.lista_meses.pack(fill="x", padx=5, pady=5)
        self.lista_meses.bind("<<ListboxSelect>>", self.on_mes_selecionado)
        tk.Label(left_frame, text="📄 Pedidos do mês:", bg=FUNDO, fg=PRIMARIA, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5, pady=5)
        self.lista_pedidos = tk.Listbox(left_frame, height=15, font=("Segoe UI", 10), bg=FUNDO_CARD, fg=TEXTO, selectbackground=PRIMARIA, selectforeground="white", relief="flat", bd=0)
        self.lista_pedidos.pack(fill="both", expand=True, padx=5, pady=5)
        self.lista_pedidos.bind("<<ListboxSelect>>", self.on_pedido_selecionado)
        right_frame = tk.Frame(paned, bg=FUNDO)
        paned.add(right_frame, width=600)
        tk.Label(right_frame, text="📄 Conteúdo do cupom:", bg=FUNDO, fg=PRIMARIA, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5, pady=5)
        self.text_cupom = tk.Text(right_frame, wrap="word", font=("Courier New", 10), bg=FUNDO_CARD, fg=TEXTO, insertbackground=TEXTO, relief="flat")
        self.text_cupom.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_cupom = ttk.Scrollbar(self.text_cupom, orient="vertical", command=self.text_cupom.yview)
        self.text_cupom.configure(yscrollcommand=scroll_cupom.set)
        scroll_cupom.pack(side="right", fill="y")
        btn_frame = tk.Frame(right_frame, bg=FUNDO)
        btn_frame.pack(fill="x", pady=5)
        btn_reimprimir = tk.Button(btn_frame, text="🖨️ Reimprimir", command=self.reimprimir_cupom, bg=PRIMARIA, fg="white", font=("Segoe UI", 10, "bold"), padx=10, relief="flat", cursor="hand2")
        btn_reimprimir.pack(side="left", padx=5)
        btn_whatsapp_hist = tk.Button(btn_frame, text="📲 Enviar WhatsApp", command=self.enviar_cupom_historico, bg=SUCESSO, fg="white", font=("Segoe UI", 10, "bold"), padx=10, relief="flat", cursor="hand2")
        btn_whatsapp_hist.pack(side="left", padx=5)
        self.atualizar_lista_meses()

    def atualizar_lista_meses(self):
        meses = set()
        pasta_cupoms = get_data_path("cupoms")
        if os.path.exists(pasta_cupoms):
            for item in os.listdir(pasta_cupoms):
                caminho = os.path.join(pasta_cupoms, item)
                if os.path.isdir(caminho) and len(item) == 7 and item[4] == '-':
                    meses.add(item)
        self.meses_list = sorted(meses, reverse=True)
        self.lista_meses.delete(0, tk.END)
        for mes in self.meses_list:
            self.lista_meses.insert(tk.END, mes)
        self.lista_pedidos.delete(0, tk.END)
        self.text_cupom.delete("1.0", tk.END)
        self.cupom_atual = None
        self.mes_atual = None

    def on_mes_selecionado(self, event):
        selecao = self.lista_meses.curselection()
        if not selecao:
            return
        self.mes_atual = self.lista_meses.get(selecao[0])
        caminho_mes = get_data_path(os.path.join("cupoms", self.mes_atual))
        if not os.path.isdir(caminho_mes):
            return
        arquivos = glob.glob(os.path.join(caminho_mes, "cupom_*.txt"))
        arquivos.sort(reverse=True)
        self.lista_pedidos.delete(0, tk.END)
        for arq in arquivos:
            nome = os.path.basename(arq)
            self.lista_pedidos.insert(tk.END, nome)
        self.text_cupom.delete("1.0", tk.END)
        self.cupom_atual = None

    def on_pedido_selecionado(self, event):
        if not self.mes_atual:
            messagebox.showwarning("Aviso", "Selecione um mês primeiro.")
            return
        selecao_pedido = self.lista_pedidos.curselection()
        if not selecao_pedido:
            return
        nome_arquivo = self.lista_pedidos.get(selecao_pedido[0])
        caminho_completo = get_data_path(os.path.join("cupoms", self.mes_atual, nome_arquivo))
        if not os.path.isfile(caminho_completo):
            self.text_cupom.delete("1.0", tk.END)
            self.text_cupom.insert("1.0", f"ERRO: Arquivo não encontrado:\n{caminho_completo}")
            self.cupom_atual = None
            return
        try:
            with open(caminho_completo, "r", encoding="utf-8") as f:
                conteudo = f.read()
            self.text_cupom.delete("1.0", tk.END)
            self.text_cupom.insert("1.0", conteudo)
            self.cupom_atual = caminho_completo
        except Exception as e:
            self.text_cupom.delete("1.0", tk.END)
            self.text_cupom.insert("1.0", f"Erro ao ler arquivo:\n{e}")
            self.cupom_atual = None

    def reimprimir_cupom(self):
        if self.cupom_atual and os.path.exists(self.cupom_atual):
            with open(self.cupom_atual, "r", encoding="utf-8") as f:
                cupom = f.read()
            # Usa a mesma função de impressão do delivery (suporta porta COM)
            resultado = imprimir_com_fallback(cupom, os.path.dirname(self.cupom_atual))
            self.status_impressora.set(f"✅ {resultado}")
            # Opcional: ainda mostra a pré-visualização
            self.mostrar_preview(cupom)
        else:
            messagebox.showwarning("Aviso", "Nenhum cupom selecionado ou arquivo não encontrado.")

    def enviar_cupom_historico(self):
        if self.cupom_atual and os.path.exists(self.cupom_atual):
            with open(self.cupom_atual, "r", encoding="utf-8") as f:
                cupom = f.read()
            msg = urllib.parse.quote(cupom)
            link = f"https://wa.me/?text={msg}"
            webbrowser.open(link)
        else:
            messagebox.showwarning("Aviso", "Nenhum cupom selecionado.")

# ========== CLASSE CATEGORIASCROLLDELIVERY ==========
class CategoriaScrollDelivery(ttk.LabelFrame):
    def __init__(self, parent, titulo, lista_produtos, on_update, **kwargs):
        super().__init__(parent, text=titulo, **kwargs)
        self.lista_produtos = lista_produtos
        self.on_update = on_update
        self.itens_widgets = []

        self.canvas = tk.Canvas(self, highlightthickness=0, bg=FUNDO_CARD)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame_interno = tk.Frame(self.canvas, bg=FUNDO_CARD)

        self.frame_interno.bind("<Configure>", self._on_frame_configure)
        self.canvas.create_window((0, 0), window=self.frame_interno, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        self._produtos = lista_produtos
        self._create_widgets()

    def _create_widgets(self):
        for w in self.itens_widgets:
            w.destroy()
        self.itens_widgets = []
        for i, produto in enumerate(self._produtos):
            item = ItemQuantidadeDelivery(self.frame_interno, produto, self.on_update)
            self.itens_widgets.append(item)
        self._arrange_widgets()

    def _arrange_widgets(self):
        width = self.canvas.winfo_width()
        if width <= 0:
            return
        n_cols = max(1, width // 380)
        for idx, item in enumerate(self.itens_widgets):
            row = idx // n_cols
            col = idx % n_cols
            item.grid(row=row, column=col, padx=10, pady=8, sticky="ew")
            self.frame_interno.grid_columnconfigure(col, weight=1)

    def _on_canvas_configure(self, event):
        self._arrange_widgets()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def recarregar(self, nova_lista):
        self._produtos = nova_lista
        self._create_widgets()
        self.canvas.after(50, self._arrange_widgets)

    def get_itens(self):
        return [(item.produto, item.quantidade.get()) for item in self.itens_widgets if item.quantidade.get() > 0]

    def get_quantidades_vars(self):
        return [item.quantidade for item in self.itens_widgets]