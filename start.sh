#!/bin/bash
# AgentKit — Script de inicio
# El usuario ejecuta: bash start.sh

set -e

echo ""
echo "==========================================================="
echo "   AgentKit — WhatsApp AI Agent Builder"
echo "==========================================================="
echo ""
echo "  Preparando tu entorno para construir tu agente de IA..."
echo ""

# ── Preparar Python 3.11 con uv ───────────────────────────────
# Usamos uv en vez de depender del python3 del sistema: instala su propia copia
# de Python 3.11 (no importa que version tengas instalada, o si no tienes ninguna)
# y crea un entorno virtual aislado. Esto evita el error "externally-managed-environment"
# que tira pip al instalar contra el Python global en macOS (Homebrew) y Linux recientes.
echo "  [1/4] Preparando Python 3.11 con uv..."
if ! command -v uv &> /dev/null; then
    echo ""
    echo "  ERROR: uv no esta instalado."
    echo "  uv es el gestor que instala Python 3.11 y prepara el entorno virtual"
    echo "  del agente, sin que tengas que instalar nada de Python a mano."
    echo ""
    echo "  Instalalo con:"
    echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "  Despues cierra y abre tu terminal (o corre 'source ~/.zshrc' /"
    echo "  'source ~/.bashrc') y vuelve a correr: bash start.sh"
    echo ""
    exit 1
fi

uv python install 3.11
uv venv --python 3.11 .venv
echo "  OK — $(.venv/bin/python --version) (entorno virtual en .venv/)"

# ── Verificar Claude Code ────────────────────────────────────
echo "  [2/4] Verificando Claude Code..."
if ! command -v claude &> /dev/null; then
    echo ""
    echo "  Claude Code no esta instalado."
    echo ""
    echo "  Para instalarlo:"
    echo "    npm install -g @anthropic-ai/claude-code"
    echo ""
    echo "  Si no tienes npm/Node.js:"
    echo "    https://nodejs.org (descarga LTS)"
    echo ""
    echo "  Despues de instalar, ejecuta 'claude' una vez para autenticarte"
    echo "  y luego vuelve a correr: bash start.sh"
    echo ""
    exit 1
fi
echo "  OK — Claude Code instalado"

# ── Crear carpetas base ──────────────────────────────────────
echo "  [3/4] Preparando carpetas..."
mkdir -p knowledge
echo "  OK — Estructura lista"

# ── Preparar .env ────────────────────────────────────────────
echo "  [4/4] Preparando variables de entorno..."
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "  OK — .env creado desde .env.example (todavia vacio, lo llenamos en el setup)"
else
    echo "  OK — .env ya existe, no se toca"
fi

echo ""
echo "==========================================================="
echo ""
echo "  Todo listo. Activa el entorno virtual y abre Claude Code:"
echo ""
echo "    source .venv/bin/activate"
echo "    claude"
echo ""
echo "  Y escribe:"
echo ""
echo "    /build-agent"
echo ""
echo "  Claude Code te guiara paso a paso para construir"
echo "  tu agente de WhatsApp personalizado con IA."
echo ""
echo "  Vas a necesitar:"
echo "    - Una API key de Anthropic  (platform.anthropic.com)"
echo "    - Una cuenta de Zernio      (zernio.com — plan free, sin tarjeta)"
echo "      o credenciales de Meta Cloud API si prefieres conectarte tu mismo"
echo ""
echo "==========================================================="
echo ""
