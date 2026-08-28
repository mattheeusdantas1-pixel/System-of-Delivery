import os
import sys
import json
import socket
import tempfile
import subprocess
import platform

CONFIG_FILE = "impressora_config.json"

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def testar_conexao_bluetooth(mac):
    """Testa se a impressora Bluetooth está pareada e disponível."""
    if platform.system() == "Windows":
        # No Windows, tenta encontrar a porta COM associada ao MAC
        porta = encontrar_porta_com_por_mac(mac)
        if porta:
            try:
                with open(porta, "wb") as f:
                    f.write(b"\x1b\x40")  # teste de inicialização
                return True, f"Impressora encontrada na porta {porta}"
            except Exception as e:
                return False, f"Erro ao abrir porta {porta}: {str(e)}"
        else:
            return False, "Impressora não está pareada ou porta COM não encontrada."
    else:
        # Linux/Mac: usa socket RFCOMM
        try:
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            sock.connect((mac, 1))
            sock.close()
            return True, "Conectado via RFCOMM"
        except Exception as e:
            return False, f"Erro: {str(e)}"

def encontrar_porta_com_por_mac(mac):
    """No Windows, localiza a porta COM associada a um dispositivo Bluetooth pelo MAC."""
    try:
        # Usa PowerShell para listar portas COM Bluetooth
        cmd = f'powershell -Command "Get-PnpDevice -Class Ports | Where-Object {{$_.FriendlyName -like \'*{mac}*\'}} | Select-Object -ExpandProperty FriendlyName"'
        resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0 and resultado.stdout.strip():
            nome_porta = resultado.stdout.strip()
            # Extrai COMx do nome (ex: "COM3")
            import re
            match = re.search(r'(COM\d+)', nome_porta)
            if match:
                return f"\\\\.\\{match.group(1)}"
        # Fallback: tenta encontrar qualquer porta COM Bluetooth recente
        cmd2 = 'powershell -Command "Get-WmiObject Win32_SerialPort | Where-Object {$_.Name -like \'*Bluetooth*\'} | Select-Object -ExpandProperty DeviceID"'
        resultado2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        if resultado2.returncode == 0 and resultado2.stdout.strip():
            portas = resultado2.stdout.strip().split('\n')
            if portas:
                return f"\\\\.\\{portas[0].strip()}"
    except Exception as e:
        print(f"Erro ao buscar porta COM: {e}")
    return None

def imprimir_com_fallback(texto, pasta_cupoms=None):
    """Imprime o texto na impressora configurada ou salva em arquivo."""
    config = carregar_config()
    mac = config.get("printer_mac")
    
    if not mac:
        # Salva em arquivo
        if pasta_cupoms:
            arquivo = os.path.join(pasta_cupoms, "cupom_sem_impressora.txt")
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(texto)
            return "Cupom salvo em arquivo (nenhuma impressora configurada)."
        else:
            return "Nenhuma impressora configurada e nenhuma pasta de cupom fornecida."
    
    if platform.system() == "Windows":
        porta = encontrar_porta_com_por_mac(mac)
        if porta:
            try:
                with open(porta, "wb") as f:
                    # Envia o texto formatado para a impressora
                    f.write(texto.encode("cp850", errors="replace"))
                    # Comandos de corte (se suportado)
                    f.write(b"\x1d\x56\x42\x00")  # corte parcial
                return f"Impresso com sucesso na porta {porta}"
            except Exception as e:
                # Fallback: salva em arquivo
                if pasta_cupoms:
                    arquivo = os.path.join(pasta_cupoms, "cupom_erro_impressao.txt")
                    with open(arquivo, "w", encoding="utf-8") as f:
                        f.write(texto)
                    return f"Erro na impressão: {str(e)}. Cupom salvo em arquivo."
                else:
                    return f"Erro na impressão: {str(e)}"
        else:
            # Salva em arquivo
            if pasta_cupoms:
                arquivo = os.path.join(pasta_cupoms, "cupom_sem_porta.txt")
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write(texto)
                return "Porta COM não encontrada. Cupom salvo em arquivo."
            else:
                return "Porta COM não encontrada."
    else:
        # Linux/Mac: socket RFCOMM
        try:
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            sock.connect((mac, 1))
            sock.send(texto.encode("cp850", errors="replace"))
            sock.close()
            return "Impresso via Bluetooth (RFCOMM)"
        except Exception as e:
            if pasta_cupoms:
                arquivo = os.path.join(pasta_cupoms, "cupom_erro.txt")
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write(texto)
                return f"Erro Bluetooth: {str(e)}. Cupom salvo em arquivo."
            else:
                return f"Erro Bluetooth: {str(e)}"