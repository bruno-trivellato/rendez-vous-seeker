#!/bin/bash

set -e

echo "🎯 Iniciando Monitor de Rendez-vous..."
echo "======================================"

# Se não existir o ambiente virtual, roda o setup
if [ ! -d ".venv" ]; then
    echo "🛠️  Ambiente virtual não encontrado. Executando setup.sh..."
    ./setup.sh
fi

# Ativa o ambiente virtual
source .venv/bin/activate

echo "🐍 Ambiente virtual ativado"

echo "🚀 Iniciando monitor..."
python main.py

# Ao sair do monitor, desativa o ambiente virtual
deactivate 