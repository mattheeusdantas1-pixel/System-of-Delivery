# 🚀 Guia de Compilação para EXE

## Pré-requisitos

1. **Python 3.8+** instalado
2. **pip** (gerenciador de pacotes Python)
3. Todas as dependências instaladas

## Instalação de Dependências

```bash
pip install flask flask-cors bcrypt pyjwt pillow pyinstaller
```

## Compilar para EXE

### Opção 1: Usar o script automático (Recomendado)

```bash
python build_exe.py
```

O script irá:
- ✅ Verificar PyInstaller
- ✅ Limpar compilações antigas
- ✅ Compilar o EXE
- ✅ Verificar resultado

### Opção 2: Compilar manualmente

```bash
pyinstaller --onefile --windowed \
  --add-data "webapp;webapp" \
  --add-data "sopadaroxaicone.ico;." \
  --add-data "cardapio.json;." \
  --add-data "config.json;." \
  --hidden-import=flask \
  --hidden-import=flask_cors \
  --hidden-import=bcrypt \
  --hidden-import=jwt \
  --hidden-import=PIL \
  --icon=sopadaroxaicone.ico \
  --name=SopaDaRoxa \
  app.py
```

## Resultado

O arquivo compilado estará em: **`dist/SopaDaRoxa.exe`**

## Como Usar o EXE

1. Clique duas vezes em `SopaDaRoxa.exe`
2. Uma janela de login aparecerá
3. Use as credenciais padrão:
   - Admin: `admin@sopadaroxa.com` / `admin123`
   - Garçom: `garcom@sopadaroxa.com` / `garcom123`
   - Cozinha: `cozinha@sopadaroxa.com` / `cozinha123`
   - Entregador: `entregador@sopadaroxa.com` / `entregador123`

4. O servidor Flask iniciará automaticamente
5. Acesse via navegador: **http://localhost:5000**
6. Use `http://<seu-ip>:5000` para acessar de outros computadores

## Distribuição

Para distribuir o EXE em rede:

1. **Servidor Central**: 
   - Execute o EXE em um computador com IP fixo
   - Permita acesso pela rede (firewall)

2. **Clientes**: 
   - Não precisam instalar nada
   - Basta acessar via navegador: `http://<ip-servidor>:5000`

## Troubleshooting

### EXE não abre
- Verifique se Python 3.8+ está instalado
- Tente executar em modo administrador
- Verifique logs (console do Windows)

### Servidor não inicia
- Porta 5000 já está em uso
- Firewall bloqueando a porta
- Dependências não instaladas

### Banco de dados não encontrado
- O arquivo `database.db` deve estar no mesmo diretório do EXE
- Ou será criado automaticamente na primeira execução

## Tamanho do Arquivo

O EXE compilado tem aproximadamente **40-50 MB** com todas as dependências.

## Notas de Segurança

- **Altere as senhas padrão** antes de usar em produção
- Use `https://` em vez de `http://` se exposto na internet
- Configure firewall adequadamente
- Mantenha backups do banco de dados

---

**Desenvolvido para Sopa da Roxa** 🍲
