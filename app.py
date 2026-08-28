import tkinter as tk
from tkinter import messagebox
import ctypes
import threading
import sys
import os

import socket
from auth import fazer_login, PERFIS

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

print(f"Servidor rodando em: http://{get_ip()}:5000")

def get_icon_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "sopadaroxaicone.ico")

def iniciar_servidor():
    from server import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🍲 Sopa da Roxa — Login")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.usuario = None
        self.criar_interface_login()
        self.centralizar_janela()

    def centralizar_janela(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def criar_interface_login(self):
        # Configurar cores
        PRIMARIA = "#7c3aed"
        FUNDO = "#f9f7ff"
        FUNDO_CARD = "#ffffff"
        TEXTO = "#1f2937"
        TEXTO_SUAVE = "#6b7280"

        self.root.configure(bg=FUNDO)

        # Header
        header = tk.Frame(self.root, bg=PRIMARIA, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🍲 SOPA DA ROXA",
            font=("Segoe UI", 20, "bold"),
            bg=PRIMARIA,
            fg="white"
        ).pack(pady=20)

        # Container
        container = tk.Frame(self.root, bg=FUNDO)
        container.pack(fill="both", expand=True, padx=20, pady=30)

        # Email
        tk.Label(container, text="📧 E-mail", bg=FUNDO, fg=TEXTO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,5))
        self.entry_email = tk.Entry(container, font=("Segoe UI", 10), width=30)
        self.entry_email.pack(fill="x", pady=(0,20))
        self.entry_email.focus()

        # Senha
        tk.Label(container, text="🔐 Senha", bg=FUNDO, fg=TEXTO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,5))
        self.entry_senha = tk.Entry(container, font=("Segoe UI", 10), width=30, show="•")
        self.entry_senha.pack(fill="x", pady=(0,30))

        # Botão Login
        btn_login = tk.Button(
            container,
            text="🔓 ENTRAR",
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARIA,
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            cursor="hand2",
            command=self.fazer_login
        )
        btn_login.pack(fill="x", pady=10)

        # Credenciais padrão
        info = tk.Frame(container, bg="#ede9fe", relief="flat")
        info.pack(fill="x", pady=20, padx=10)

        tk.Label(
            info,
            text="👤 Credenciais Padrão:",
            bg="#ede9fe",
            fg=PRIMARIA,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(8,4))

        credenciais = [
            ("Admin: admin@sopadaroxa.com / admin123", "🔑"),
            ("Garçom: garcom@sopadaroxa.com / garcom123", "🍽"),
            ("Cozinha: cozinha@sopadaroxa.com / cozinha123", "🍳"),
            ("Entregador: entregador@sopadaroxa.com / entregador123", "🚴")
        ]

        for cred, emoji in credenciais:
            tk.Label(
                info,
                text=f"{emoji} {cred}",
                bg="#ede9fe",
                fg=TEXTO_SUAVE,
                font=("Segoe UI", 8)
            ).pack(anchor="w", padx=20, pady=1)

        tk.Label(info, text="", bg="#ede9fe").pack(pady=4)

        # Bind Enter
        self.entry_email.bind("<Return>", lambda e: self.entry_senha.focus())
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())

    def fazer_login(self):
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get()

        if not email or not senha:
            messagebox.showerror("Erro", "Preencha e-mail e senha!")
            return

        sucesso, token, usuario = fazer_login(email, senha)

        if sucesso:
            self.usuario = usuario
            self.root.destroy()
        else:
            messagebox.showerror("Erro", "E-mail ou senha inválidos!")
            self.entry_senha.delete(0, tk.END)
            self.entry_email.focus()

if __name__ == "__main__":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('SopaDaRoxa.App.1')
    except Exception:
        pass

    t = threading.Thread(target=iniciar_servidor, daemon=True)
    t.start()
    print(f"Servidor web em:")
    print(f"Local: http://localhost:5000")
    print(f"Rede:  http://{get_ip()}:5000")

    # Tela de Login
    root_login = tk.Tk()
    icon_path = get_icon_path()

    def aplicar_icone(root):
        if not os.path.exists(icon_path):
            return
        try:
            root.iconbitmap(default=icon_path)
        except Exception:
            pass

    root_login.after(100, aplicar_icone, root_login)
    login_window = LoginWindow(root_login)
    root_login.mainloop()

    # Se login foi bem-sucedido, abrir interface
    if login_window.usuario:
        from interface import Sistema
        root = tk.Tk()
        root.after(100, aplicar_icone, root)
        app_sistema = Sistema(root, usuario=login_window.usuario)
        root.mainloop()