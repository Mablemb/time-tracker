#!/bin/bash

# Script para inicializar o TimeTracker
echo "🚀 Iniciando TimeTracker..."

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado!"
fi

# Ativar ambiente virtual
echo "⚙️ Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate

# Iniciar servidor
echo "🌐 Iniciando servidor..."
echo "📍 Acesse: http://127.0.0.1:8000"
echo "⏹️ Para parar: Ctrl+C"
python manage.py runserver
