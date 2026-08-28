import tkinter as tk
import ctypes
import threading
import sys
import os

import socket

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

    from interface import Sistema
    root = tk.Tk()

    icon_path = get_icon_path()
    def aplicar_icone():
        if not os.path.exists(icon_path):
            return
        try:
            root.iconbitmap(default=icon_path)
        except Exception:
            pass
        try:
            from PIL import Image, ImageTk
            img = Image.open(icon_path)
            root._icon_large = ImageTk.PhotoImage(img.copy().convert("RGBA").resize((256,256)))
            root._icon_small = ImageTk.PhotoImage(img.copy().convert("RGBA").resize((32,32)))
            root.iconphoto(True, root._icon_large, root._icon_small)
        except Exception:
            pass

    root.after(150, aplicar_icone)
    app_sistema = Sistema(root)
    root.mainloop()