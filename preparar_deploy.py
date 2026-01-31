"""
Prepara a estrutura de deploy para PRUDENTE no GitHub Pages
Copia os arquivos gerados para a pasta docs/
"""

import shutil
import sys
from pathlib import Path
from datetime import datetime

# Configura encoding UTF-8 para o console Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DEPLOY_DIR = Path(__file__).parent / "docs"

# Pastas de origem
APP_WEB_ORIGEM = BASE_DIR / "App Pedidos Prudente" / "app_pedidos_web.html"
APP_JSON_ORIGEM = BASE_DIR / "App Pedidos Prudente" / "dados.json"

# Pastas de destino
APP_DESTINO = DEPLOY_DIR / "app" / "index.html"
APP_JSON_DESTINO = DEPLOY_DIR / "app" / "dados.json"

print("="*60)
print("PREPARANDO DEPLOY - PRUDENTE")
print("="*60)
print(f"Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print()

# Função auxiliar para copiar arquivo
def copiar_arquivo(origem, destino, descricao):
    """Copia um arquivo e exibe resultado"""
    if not origem.exists():
        print(f"❌ {descricao}")
        print(f"   Arquivo não encontrado: {origem}")
        return False

    # Cria diretório de destino se não existir
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Copia o arquivo
    shutil.copy2(origem, destino)

    tamanho_kb = destino.stat().st_size / 1024
    if tamanho_kb > 1024:
        tamanho_str = f"{tamanho_kb/1024:.2f} MB"
    else:
        tamanho_str = f"{tamanho_kb:.1f} KB"

    print(f"✅ {descricao}")
    print(f"   Origem: {origem.name}")
    print(f"   Destino: {destino.relative_to(DEPLOY_DIR.parent)}")
    print(f"   Tamanho: {tamanho_str}")
    print()
    return True

# Copia os arquivos
sucessos = 0

if copiar_arquivo(APP_WEB_ORIGEM, APP_DESTINO, "App de Pedidos (HTML)"):
    sucessos += 1

if copiar_arquivo(APP_JSON_ORIGEM, APP_JSON_DESTINO, "App de Pedidos (JSON)"):
    sucessos += 1

# Resumo
print("="*60)
print("RESUMO")
print("="*60)
print(f"Arquivos copiados: {sucessos}/2")

if sucessos == 2:
    print("\n✅ Deploy preparado com sucesso!")
    print("\nEstrutura criada em docs/:")
    print("  docs/")
    print("  ├── index.html        (landing page)")
    print("  └── app/")
    print("      ├── index.html    (app de pedidos)")
    print("      └── dados.json    (dados dos produtos)")
    print("\nPróximos passos:")
    print("  1. cd prudente-deploy")
    print("  2. git add .")
    print("  3. git commit -m 'Atualização'")
    print("  4. git push")
else:
    print(f"\n⚠️ Alguns arquivos não foram encontrados ({2-sucessos} faltando)")
    print("Execute primeiro:")
    print("  1. python exportar_tabela_prudente_app.py")
    print("  2. cd 'App Pedidos Prudente' && python gerar_app.py")

print("="*60)
