#!/usr/bin/env python3
"""
build_exe.py - Script para compilar Sopa da Roxa para EXE
Uso: python build_exe.py
"""

import os
import sys
import subprocess
import shutil

def verificar_dependencias():
    """Verifica se PyInstaller está instalado"""
    print("🔍 Verificando dependências...")
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado")
        print("Instalando: pip install pyinstaller")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def limpar_compilacoes_antigas():
    """Remove diretórios de compilação anteriores"""
    print("\n🧹 Limpando compilações antigas...")
    for pasta in ['build', 'dist', '__pycache__']:
        if os.path.exists(pasta):
            shutil.rmtree(pasta)
            print(f"   Removido: {pasta}")

def compilar_exe():
    """Compila o projeto com PyInstaller"""
    print("\n🔨 Compilando SopaDaRoxa.exe...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--add-data", "webapp;webapp",
        "--add-data", "sopadaroxaicone.ico;.",
        "--add-data", "cardapio.json;.",
        "--add-data", "config.json;.",
        "--hidden-import=flask",
        "--hidden-import=flask_cors",
        "--hidden-import=bcrypt",
        "--hidden-import=jwt",
        "--hidden-import=PIL",
        "--icon=sopadaroxaicone.ico",
        "--name=SopaDaRoxa",
        "app.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("✅ Compilação concluída com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante compilação: {e}")
        return False

    return True

def verificar_exe():
    """Verifica se o EXE foi criado"""
    print("\n✅ Verificando EXE...")
    exe_path = os.path.join("dist", "SopaDaRoxa.exe")
    if os.path.exists(exe_path):
        tamanho_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ {exe_path}")
        print(f"   Tamanho: {tamanho_mb:.1f} MB")
        return True
    else:
        print(f"❌ {exe_path} não encontrado")
        return False

def main():
    print("=" * 50)
    print("🍲 COMPILADOR SOPA DA ROXA")
    print("=" * 50)

    # Verificar dependências
    verificar_dependencias()

    # Limpar compilações antigas
    limpar_compilacoes_antigas()

    # Compilar
    sucesso = compilar_exe()

    if sucesso:
        # Verificar
        verificar_exe()

        print("\n" + "=" * 50)
        print("✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        print("\n📁 Arquivo gerado em: dist/SopaDaRoxa.exe")
        print("\n🚀 Para usar:")
        print("   1. Copie dist/SopaDaRoxa.exe para onde deseja")
        print("   2. Clique duas vezes para iniciar")
        print("   3. O servidor Flask iniciará automaticamente")
        print("   4. Acesse em http://localhost:5000 no navegador")
        print("\n🔐 Credenciais padrão:")
        print("   - admin@sopadaroxa.com / admin123")
        print("   - garcom@sopadaroxa.com / garcom123")
        print("   - cozinha@sopadaroxa.com / cozinha123")
        print("   - entregador@sopadaroxa.com / entregador123")
        return 0
    else:
        print("\n❌ ERRO DURANTE COMPILAÇÃO")
        return 1

if __name__ == "__main__":
    sys.exit(main())
