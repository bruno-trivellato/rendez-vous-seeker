#!/bin/bash

set -e

echo "🚀 Configurando Monitor de Rendez-vous..."
echo "=========================================="

# Verifica se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3 primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Cria ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "🛠️  Criando ambiente virtual Python (.venv)..."
    python3 -m venv .venv
fi

echo "✅ Ambiente virtual pronto"

# Ativa o ambiente virtual
source .venv/bin/activate

echo "🐍 Ambiente virtual ativado"

# Atualiza pip
pip install --upgrade pip

# Instala as dependências
echo "📦 Instalando dependências no ambiente virtual..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro ao instalar dependências"
    deactivate
    exit 1
fi

# Torna os scripts executáveis
chmod +x main.py

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "Para ativar o ambiente virtual depois:"
echo "  source .venv/bin/activate"
echo ""
echo "Para executar o monitor:"
echo "  python main.py"
echo ""
echo "Para parar o monitor:"
echo "  Pressione Ctrl+C"
echo ""
echo "Para sair do ambiente virtual:"
echo "  deactivate"
echo "" 