# ⏱️ TimeTracker - Sistema de Controle de Tempo

Sistema Django para controle de tempo dedicado a projetos, funcionando como um "ponto eletrônico" pessoal para marcar início e fim de sessões de trabalho.

## 🚀 Início Rápido

### Método 1: Script Automático (Recomendado)
```bash
# Torna o script executável e executa
chmod +x start.sh
./start.sh
```

### Método 2: Instalação Manual
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd dedicatedTime

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate

# Inicie o servidor
python manage.py runserver
```

### Acesso
- **Interface Web**: http://127.0.0.1:8000
- **Admin Django**: http://127.0.0.1:8000/admin

## ✨ Funcionalidades Principais

- 📊 **Dashboard** com visão geral dos projetos
- ⏲️ **Cronômetro em tempo real** para sessões ativas
- 📈 **Relatórios** por dia/semana/mês
- 📋 **Gerenciamento de projetos** completo
- 🗂️ **Histórico** de todas as sessões
- 🎨 **Interface responsiva** com Bootstrap

## 🔧 Tecnologias

- **Backend**: Django 5.2.2, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco**: SQLite (desenvolvimento)
- **Icons**: Bootstrap Icons

## 📚 Documentação

Para documentação completa, consulte a pasta [`docs/`](docs/):

- **[📚 Índice de Documentação](docs/INDEX.md)** - Portal principal da documentação
- **[📖 README Completo](docs/README.md)** - Documentação técnica detalhada
- **[🧪 Testes Finais](docs/TESTE_FINAL.md)** - Relatório de testes e funcionalidades
- **[🗑️ Exclusão de Projetos](docs/EXCLUSAO_PROJETOS.md)** - Implementação de funcionalidades

## 🎯 Status do Projeto

✅ **Projeto Completo e Funcional**
- Todas as funcionalidades principais implementadas
- Interface responsiva e intuitiva
- Testes realizados e aprovados
- Documentação completa

## 👨‍💻 Desenvolvimento

Este projeto foi desenvolvido como exercício de aprendizado para:
- Desenvolvimento full-stack com Django
- Integração frontend/backend
- Gerenciamento de estado com JavaScript
- Design responsivo com Bootstrap

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais e de aprendizado de Python/Django.

---

**Status**: ✅ Projeto completo e funcional  
**Versão**: 1.0.0  
**Data**: Junho 2025
