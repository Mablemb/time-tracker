# ⏱️ TimeTracker - Sistema de Controle de Tempo

[![GitHub Stars](https://img.shields.io/github/stars/Mablemb/time-tracker?style=social)](https://github.com/Mablemb/time-tracker)
[![GitHub Issues](https://img.shields.io/github/issues/Mablemb/time-tracker)](https://github.com/Mablemb/time-tracker/issues)
[![License](https://img.shields.io/github/license/Mablemb/time-tracker)](https://github.com/Mablemb/time-tracker/blob/main/LICENSE)

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
git clone https://github.com/Mablemb/time-tracker.git
cd time-tracker

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
  - ➕ **Criar** novos projetos
  - ✏️ **Editar** projetos existentes (nome, descrição, cor, status)
  - 🗑️ **Deletar** projetos com verificações de segurança
  - 🔄 **Ativar/Desativar** projetos
- 🗂️ **Histórico** de todas as sessões
- 🎨 **Interface responsiva** com Bootstrap
- 🔒 **Validações de segurança** e integridade de dados

- 🚫 **Prevenção de sessões acidentais:** sessões com duração menor que 5 minutos são automaticamente descartadas e não contam para o tempo total. O usuário é avisado quando isso ocorre.
- ⏱️ **Ajuste de precisão:** horários de início/fim e duração das sessões são exibidos com precisão de 1 segundo (mínimo exibido: 1s).
- ✏️ **Edição de sessões finalizadas:** é possível editar o horário de término de sessões já encerradas, para corrigir registros antigos. O novo horário deve respeitar as regras de duração mínima (>= 5 minutos) e não pode ser anterior ao início ou no futuro.
## 🔗 Endpoints principais

- `/` - Dashboard
- `/projetos/` - Gerenciar projetos
- `/historico/` - Histórico de sessões
- `/relatorios/` - Relatórios
- `/sessao/iniciar/<projeto_id>/` - Iniciar sessão
- `/sessao/finalizar/` - Finalizar sessão
- `/sessao/status/` - Status da sessão atual
- `/sessao/<id>/atualizar_fim/` - **Atualizar horário de fim de uma sessão já encerrada** (POST, JSON: `{ "novo_horario_fim": "YYYY-MM-DDTHH:MM:SS" }`)
## ℹ️ Observações

- O sistema **descarta automaticamente** sessões com duração inferior a 5 minutos para evitar registros acidentais. O usuário recebe um aviso quando isso ocorre.
- O horário de início/fim é salvo e exibido com precisão de segundos (mínimo exibido: 1s).
- Para editar o horário de fim de uma sessão já encerrada, utilize o novo endpoint `/sessao/<id>/atualizar_fim/` ou a interface de histórico (ver instruções abaixo).
## ✏️ Edição do horário de fim de sessões (interface)

No histórico de sessões, agora é possível editar o horário de término de sessões já encerradas:

1. Clique no ícone de edição (🖉) ao lado do horário de fim da sessão desejada.
2. Um modal será exibido para selecionar o novo horário de fim.
3. O novo horário deve ser posterior ao início, não pode ser no futuro e a duração total deve ser de pelo menos 5 minutos.
4. Após salvar, a sessão será atualizada e o histórico será recarregado.

Se a alteração não for válida, uma mensagem de erro será exibida.

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
- Sistema completo de CRUD para projetos
- Funcionalidades de edição e exclusão implementadas
- Validações de segurança e integridade
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

**Status**: ✅ Projeto completo e funcional com CRUD completo  
**Versão**: 1.1.0  
**Data**: Julho 2025

---

### Novidades da versão 1.1.0 (Julho/2025)

- Novo modal para edição do horário de fim de sessões já encerradas (com validação de duração mínima e UX aprimorada)
- Prevenção automática de sessões acidentais: sessões com menos de 5 minutos são descartadas
- Precisão de 1 segundo em todos os horários e durações
- Correção de problemas de timezone e comparação de datas
- Relatórios e estatísticas revisados: porcentagens, barras e médias exibidas corretamente
- Interface e mensagens aprimoradas
- Documentação e testes atualizados
