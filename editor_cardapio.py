import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

def get_cardapio_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "cardapio.json")

def carregar_dados():
    caminho = get_cardapio_path()
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    caminho = get_cardapio_path()
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

class EditorCardapio:
    def __init__(self, parent, on_salvar_callback):
        self.parent = parent
        self.on_salvar_callback = on_salvar_callback
        self.janela = tk.Toplevel(parent)
        self.janela.title("Editar Cardápio")
        self.janela.geometry("900x700")
        self.janela.configure(bg="#F8F9FA")

        # Carrega dados atuais
        self.dados = carregar_dados()

        # Notebook para abas
        self.notebook = ttk.Notebook(self.janela)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # Cria abas
        self.criar_aba_sopas()
        self.criar_aba_tapiocas()

        # Botões principais
        frame_botoes = tk.Frame(self.janela, bg="#F8F9FA")
        frame_botoes.pack(pady=8)
        tk.Button(frame_botoes, text="💾 Salvar Alterações", command=self.salvar,
                  bg="#6A0DAD", fg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=5).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="❌ Cancelar", command=self.janela.destroy,
                  bg="#495057", fg="white", font=("Segoe UI", 10), padx=15, pady=5).pack(side="left", padx=5)

    def _criar_aba(self, categoria, label_categoria):
        """Cria uma aba genérica para sopas ou tapiocas."""
        container = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(container, text=label_categoria)

        # Frame da treeview (ocupa a maior parte)
        frame_tree = tk.Frame(container, bg="#F8F9FA")
        frame_tree.pack(fill="both", expand=True, padx=5, pady=5)

        colunas = ("Nome", "Preço")
        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", height=20)
        tree.heading("Nome", text="Nome do Produto")
        tree.heading("Preço", text="Preço (R$)")
        tree.column("Nome", width=500)
        tree.column("Preço", width=150)

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Preenche com os dados
        for item in self.dados[categoria]:
            tree.insert("", "end", values=(item["nome"], f"{item['preco']:.2f}"))

        # Bind duplo clique para editar inline
        tree.bind("<Double-1>", lambda e: self.editar_item(tree, categoria))

        # Painel de edição inline na parte inferior
        frame_painel = tk.LabelFrame(container, text="Adicionar / Editar Item",
                                     bg="#F8F9FA", fg="#6A0DAD", font=("Segoe UI", 9, "bold"))
        frame_painel.pack(fill="x", padx=5, pady=(0, 5))

        inner = tk.Frame(frame_painel, bg="#F8F9FA")
        inner.pack(fill="x", padx=8, pady=6)

        tk.Label(inner, text="Nome:", bg="#F8F9FA", font=("Segoe UI", 10)).pack(side="left")
        entry_nome = ttk.Entry(inner, width=35)
        entry_nome.pack(side="left", padx=5)

        tk.Label(inner, text="Preço (R$):", bg="#F8F9FA", font=("Segoe UI", 10)).pack(side="left", padx=(10, 0))
        entry_preco = ttk.Entry(inner, width=10)
        entry_preco.pack(side="left", padx=5)

        def limpar_campos():
            entry_nome.delete(0, tk.END)
            entry_preco.delete(0, tk.END)
            tree.selection_remove(tree.selection())

        def preencher_campos_da_selecao(event=None):
            sel = tree.selection()
            if sel:
                vals = tree.item(sel[0], "values")
                entry_nome.delete(0, tk.END)
                entry_nome.insert(0, vals[0])
                entry_preco.delete(0, tk.END)
                entry_preco.insert(0, vals[1])

        tree.bind("<<TreeviewSelect>>", preencher_campos_da_selecao)

        def salvar_item():
            nome = entry_nome.get().strip()
            try:
                preco = float(entry_preco.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Preço inválido.", parent=self.janela)
                return
            if not nome:
                messagebox.showerror("Erro", "Nome não pode estar vazio.", parent=self.janela)
                return

            sel = tree.selection()
            if sel:
                # Edita o item selecionado
                idx = tree.index(sel[0])
                tree.item(sel[0], values=(nome, f"{preco:.2f}"))
                self.dados[categoria][idx] = {"nome": nome, "preco": preco}
            else:
                # Adiciona novo item
                self.dados[categoria].append({"nome": nome, "preco": preco})
                tree.insert("", "end", values=(nome, f"{preco:.2f}"))

            limpar_campos()

        def excluir_item():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            tree.delete(sel[0])
            del self.dados[categoria][idx]
            limpar_campos()

        btn_frame = tk.Frame(frame_painel, bg="#F8F9FA")
        btn_frame.pack(fill="x", padx=8, pady=(0, 6))

        tk.Button(btn_frame, text="✅ Salvar Item", command=salvar_item,
                  bg="#6A0DAD", fg="white", font=("Segoe UI", 10), relief="flat", padx=10).pack(side="left", padx=3)
        tk.Button(btn_frame, text="➕ Novo (Limpar)", command=limpar_campos,
                  bg="#28A745", fg="white", font=("Segoe UI", 10), relief="flat", padx=10).pack(side="left", padx=3)
        tk.Button(btn_frame, text="🗑️ Excluir Selecionado", command=excluir_item,
                  bg="#DC3545", fg="white", font=("Segoe UI", 10), relief="flat", padx=10).pack(side="left", padx=3)

        return tree

    def criar_aba_sopas(self):
        self.tree_sopas = self._criar_aba("sopas", "🍲 Sopas")

    def criar_aba_tapiocas(self):
        self.tree_tapiocas = self._criar_aba("tapiocas", "🌮 Tapiocas")

    def editar_item(self, tree, categoria):
        """Duplo clique: apenas seleciona o item (campos já são preenchidos pelo <<TreeviewSelect>>)."""
        pass  # O bind <<TreeviewSelect>> já cuida de preencher os campos

    def salvar(self):
        salvar_dados(self.dados)
        self.janela.destroy()
        if self.on_salvar_callback:
            self.on_salvar_callback()