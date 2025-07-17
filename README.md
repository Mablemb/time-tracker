# ⏱️ TimeTracker - Sistema de Controle de Tempo

[![GitHub Stars](https://img.shields.io/github/stars/Mablemb/time-tracker?style=social)](https://github.com/Mablemb/time-tracker)
[![GitHub Issues](https://img.shields.io/github/issues/Mablemb/time-tracker)](https://github.com/Mablemb/time-tracker/issues)
[![License](https://img.shields.io/github/license/Mablemb/time-tracker)](https://github.com/Mablemb/time-tracker/blob/main/LICENSE)

Sistema Django para controle de tempo dedicado a projetos, funcionando como um "ponto eletrônico" pessoal para marcar início e fim de sessões de trabalho.

## 🚀 Início Rápido

### ⚠️ Pré-requisitos para Windows

Para rodar o TimeTracker no Windows, é necessário ter o **Python 3** instalado e disponível no PATH do sistema:

1. Baixe o Python em: https://www.python.org/downloads/windows/
2. Durante a instalação, marque a opção **“Add Python to PATH”** antes de clicar em “Install Now”.
3. Após instalar, feche e reabra o Explorer/Prompt de Comando.
4. Para testar, abra o Prompt e digite:
   ```
   python --version
   pip --version
   ```
   Ambos devem exibir a versão instalada.

Se aparecer mensagem de erro, reinicie o computador ou revise a instalação.


### Método 1: Script Automático (Recomendado)

#### Usuários Windows
1. Clique duas vezes no arquivo `start_windows.bat` (ícone do Windows) na pasta do projeto.
2. O navegador será aberto automaticamente em http://127.0.0.1:8000.
3. Para criar um atalho na área de trabalho, clique com o botão direito no `start_windows.bat` e escolha "Enviar para > Área de trabalho (criar atalho)".

#### Usuários Linux/Mac
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

### 📊 Dashboard e Controle de Tempo
- 📋 **Dashboard** com visão geral dos projetos e estatísticas
- ⏲️ **Cronômetro em tempo real** para sessões ativas
- � **Prevenção de sessões acidentais:** sessões < 5 min são descartadas automaticamente
- ⏱️ **Precisão de 1 segundo** em horários e durações

### 📈 Relatórios e Gráficos Interativos  
- 📊 **4 tipos de gráficos** com Chart.js:
  - 📊 Gráfico de barras - tempo por projeto
  - 🥧 Gráfico de pizza - distribuição percentual
  - 📈 Gráfico de linha - evolução temporal  
  - 🔥 Mapa de calor - atividade por hora/dia
- 🔄 **Filtros responsivos** por dia/semana/mês
- � **Relatórios** detalhados por período

### 📋 Gerenciamento Completo de Projetos
- ➕ **Criar** novos projetos com cores personalizadas
- ✏️ **Editar** projetos existentes (nome, descrição, cor, status)
- 🗑️ **Deletar** projetos com verificações de segurança
- 🔄 **Ativar/Desativar** projetos
- 🎨 **Cores personalizadas** para identificação visual

### 🗂️ Histórico e Edição de Sessões
- 📋 **Histórico** completo de todas as sessões
- ✏️ **Edição** de horários de fim de sessões encerradas
- 🔒 **Validações** de duração mínima e integridade temporal
- 🎨 **Interface responsiva** com Bootstrap

### 🛡️ Segurança e Integridade
- 🔒 **Validações** de segurança em todas as operações
- 🧪 **Sistema de dados de teste** seguro (apenas em desenvolvimento)
- ✅ **Compatibilidade total** com dados existentes
- 🛡️ **Proteções** contra perda acidental de dados
## 🔗 Endpoints Principais

### Páginas da Interface
- `/` - Dashboard principal com estatísticas
- `/projetos/` - Gerenciar projetos (CRUD completo)
- `/historico/` - Histórico de sessões com edição
- `/relatorios/` - Relatórios com gráficos interativos

### APIs de Sessão
- `/sessao/iniciar/<projeto_id>/` - Iniciar nova sessão
- `/sessao/finalizar/` - Finalizar sessão ativa
- `/sessao/status/` - Status da sessão atual
- `/sessao/<id>/atualizar_fim/` - Atualizar horário de fim (POST)

### APIs de Dados (Desenvolvimento)
- `/popular_dados_teste/` - Criar dados de demonstração
- `/limpar_dados_teste/` - Remover dados de teste
## ℹ️ Observações Importantes

### ⚠️ Prevenção de Sessões Acidentais
- O sistema **descarta automaticamente** sessões com duração inferior a 5 minutos
- O usuário recebe um aviso quando isso ocorre
- Evita registros acidentais de "entradas e saídas" rápidas

### ⏱️ Precisão Temporal
- Horários de início/fim salvos com precisão de segundos
- Durações exibidas com mínimo de 1 segundo
- Cálculos precisos para relatórios e estatísticas

### ✏️ Edição de Sessões
- Possível editar horário de fim de sessões já encerradas
- Validações: horário deve ser posterior ao início e não futuro
- Duração mínima de 5 minutos mantida
- Interface intuitiva no histórico de sessões

### 🧪 Dados de Teste (Desenvolvimento)
- Funcionalidades de teste só aparecem em `DEBUG=True`
- Dados de teste claramente marcados e separados
- Remoção segura sem afetar dados reais
- Ideal para demonstrações e desenvolvimento

## 🔧 Tecnologias

- **Backend**: Django 5.2.2, Python 3.12+
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Gráficos**: Chart.js 4.0 para visualizações interativas
- **Banco**: SQLite (desenvolvimento), compatível com PostgreSQL/MySQL
- **Icons**: Bootstrap Icons
- **Responsividade**: Mobile-first design com Bootstrap Grid

## 📚 Documentação

Para documentação completa, consulte a pasta [`docs/`](docs/):

- **[📚 Índice de Documentação](docs/INDEX.md)** - Portal principal da documentação
- **[📖 README Completo](docs/README.md)** - Documentação técnica detalhada
- **[🧪 Testes Finais](docs/TESTE_FINAL.md)** - Relatório de testes e funcionalidades
- **[🗑️ Exclusão de Projetos](docs/EXCLUSAO_PROJETOS.md)** - Implementação de funcionalidades
- **[🔒 Segurança de Dados de Teste](docs/SEGURANCA_DADOS_TESTE.md)** - Sistema seguro de dados de demonstração
- **[✅ Compatibilidade de Dados](docs/COMPATIBILIDADE_DADOS_EXISTENTES.md)** - Garantias para usuários existentes

## ⚠️ Atualização Segura para Usuários Existentes

**Esta atualização é 100% segura!** Se você já usa o TimeTracker:

✅ **Seus dados estão protegidos**: Nenhum projeto ou sessão existente será modificado  
✅ **Zero interrupção**: Sistema continua funcionando exatamente como antes  
✅ **Só melhorias**: Novos gráficos e funcionalidades adicionadas  
✅ **Migração automática**: Apenas adiciona campos novos com valores seguros  

**Para atualizar:**
1. Faça backup do seu `db.sqlite3` (recomendado)
2. Execute `python manage.py migrate`
3. Pronto! Aproveite os novos gráficos em "Relatórios"

📋 [**Ver detalhes completos da compatibilidade**](docs/COMPATIBILIDADE_DADOS_EXISTENTES.md)

## 🎯 Status do Projeto

✅ **Projeto Completo e Pronto para Produção**

### 🚀 Funcionalidades Implementadas
- ✅ Sistema completo de CRUD para projetos
- ✅ Controle de tempo com cronômetro em tempo real
- ✅ Relatórios visuais com 4 tipos de gráficos interativos
- ✅ Histórico completo com edição de sessões
- ✅ Dashboard com estatísticas e métricas
- ✅ Interface responsiva e intuitiva
- ✅ Sistema de dados de teste seguro
- ✅ Validações robustas e prevenção de erros

### 🛡️ Qualidade e Segurança
- ✅ Validações de segurança implementadas
- ✅ Compatibilidade total com dados existentes
- ✅ Testes realizados e aprovados
- ✅ Documentação completa e atualizada
- ✅ Sistema de migração segura
- ✅ Proteções contra perda de dados

### 📱 Experiência do Usuário
- ✅ Interface moderna e responsiva
- ✅ Feedback visual em todas as ações
- ✅ Prevenção de ações acidentais
- ✅ Gráficos interativos e informativos
- ✅ Navegação intuitiva
- ✅ Performance otimizada

## 👨‍💻 Desenvolvimento

Este projeto foi desenvolvido como exercício de aprendizado para:
- Desenvolvimento full-stack com Django
- Integração frontend/backend
- Gerenciamento de estado com JavaScript
- Design responsivo com Bootstrap

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais e de aprendizado de Python/Django.

---

**Status**: 🚀 Pronto para Produção - Sistema Completo  
**Versão**: 1.2.0  
**Data**: Julho 2025

---

### 🆕 Novidades da versão 1.2.0 (Julho/2025)

#### 📊 Gráficos e Relatórios Visuais
- **4 tipos de gráficos interativos** com Chart.js:
  - 📊 Gráfico de barras - tempo por projeto
  - 🥧 Gráfico de pizza - distribuição percentual  
  - 📈 Gráfico de linha - evolução temporal
  - 🔥 Mapa de calor - atividade por hora/dia
- **Filtros responsivos** por dia/semana/mês
- **Interface moderna** com cores e animações suaves

#### 🛡️ Sistema de Dados de Teste Seguro
- **Dados de demonstração** para testar gráficos
- **Separação total** entre dados reais e de teste
- **Remoção segura** sem afetar dados do usuário
- **Disponível apenas** em ambiente de desenvolvimento

#### ✅ Compatibilidade e Segurança
- **100% compatível** com versões anteriores
- **Migração automática** sem perda de dados
- **Proteções múltiplas** contra modificação acidental
- **Verificação de integridade** incluída

#### 🎨 Melhorias de Interface
- **Design responsivo** aprimorado
- **Indicadores visuais** para dados de teste
- **Feedback melhorado** em todas as ações
- **Performance otimizada** dos gráficos

### Novidades da versão 1.1.0 (Julho/2025)

- Novo modal para edição do horário de fim de sessões já encerradas (com validação de duração mínima e UX aprimorada)
- Prevenção automática de sessões acidentais: sessões com menos de 5 minutos são descartadas
- Precisão de 1 segundo em todos os horários e durações
- Correção de problemas de timezone e comparação de datas
- Relatórios e estatísticas revisados: porcentagens, barras e médias exibidas corretamente
- Interface e mensagens aprimoradas
- Documentação e testes atualizados
