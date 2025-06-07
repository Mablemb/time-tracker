# TimeTracker - Sistema de Controle de Tempo para Projetos

Um sistema web desenvolvido em Django para controlar o tempo dedicado a diferentes projetos, funcionando como um "ponto eletrônico" pessoal.

## 🚀 Funcionalidades

- **Dashboard Principal**: Visualização geral dos projetos e controle de sessões
- **Ponto Eletrônico**: Sistema para iniciar e finalizar sessões de trabalho
- **Gerenciamento de Projetos**: Criação e organização de projetos com cores personalizadas
- **Relatórios**: Visualização de tempo por dia, semana e mês
- **Histórico**: Registro detalhado de todas as sessões de trabalho
- **Interface Responsiva**: Design moderno com Bootstrap

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2.2
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3
- **Banco de Dados**: SQLite (desenvolvimento)
- **Icons**: Bootstrap Icons
- **Linguagem**: Python 3.12+

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação e Configuração

1. **Clone o repositório** (ou baixe os arquivos):
   ```bash
   # Se usando git
   git clone <url-do-repositorio>
   cd dedicatedTime
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python3 -m venv venv
   ```

3. **Ative o ambiente virtual**:
   ```bash
   # No Linux/Mac
   source venv/bin/activate
   
   # No Windows
   venv\Scripts\activate
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute as migrações**:
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário** (opcional):
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicie o servidor de desenvolvimento**:
   ```bash
   python manage.py runserver
   ```

8. **Acesse a aplicação**:
   Abra seu navegador e vá para `http://127.0.0.1:8000`

## 📖 Como Usar

### 1. Criando Projetos
- Acesse "Projetos" no menu
- Clique em "Novo Projeto"
- Preencha nome, descrição e escolha uma cor
- Salve o projeto

### 2. Controlando o Tempo
- No Dashboard, clique em "Iniciar" no projeto desejado
- Trabalhe normalmente no seu projeto
- Quando terminar, clique em "Finalizar" no topo da página
- Adicione uma descrição opcional do que foi realizado

### 3. Visualizando Relatórios
- Acesse "Relatórios" para ver estatísticas por período
- Use os filtros "Hoje", "Esta Semana" ou "Este Mês"
- Visualize gráficos e distribuição de tempo

### 4. Consultando Histórico
- Acesse "Histórico" para ver todas as sessões registradas
- Visualize detalhes de cada sessão
- Use filtros para encontrar sessões específicas

## 🎯 Estrutura do Projeto

```
dedicatedTime/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── timetracker/          # Configurações do Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── projects/             # App principal
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── templates/            # Templates HTML
│   ├── base.html
│   └── projects/
│       ├── dashboard.html
│       ├── gerenciar_projetos.html
│       ├── relatorios.html
│       └── historico.html
└── static/              # Arquivos estáticos (CSS, JS, imagens)
```

## 📊 Modelos de Dados

### Projeto
- Nome (único)
- Descrição
- Cor (para identificação visual)
- Status (ativo/inativo)
- Data de criação

### SessaoTempo
- Projeto relacionado
- Data/hora de início
- Data/hora de fim
- Descrição do trabalho realizado

## 🎨 Interface

A interface foi desenvolvida com foco na usabilidade:

- **Design Limpo**: Interface minimalista e intuitiva
- **Cores Personalizadas**: Cada projeto tem sua cor para fácil identificação
- **Responsivo**: Funciona bem em desktop, tablet e mobile
- **Feedback Visual**: Animações e indicadores de status
- **Cronômetro em Tempo Real**: Mostra o tempo da sessão atual

## 🔮 Funcionalidades Futuras

- [ ] Exportação de relatórios (CSV, PDF)
- [ ] Metas de tempo por projeto
- [ ] Notificações de intervalos
- [ ] Integração com calendário
- [ ] API REST para aplicações móveis
- [ ] Dashboard com gráficos mais avançados
- [ ] Sistema de tags para categorização
- [ ] Backup automático de dados

## 🤝 Contribuindo

Este é um projeto educacional para aprender Django. Sugestões e melhorias são bem-vindas!

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é open source e está disponível sob a [MIT License](LICENSE).

## 👨‍💻 Autor

Desenvolvido como projeto de aprendizado em Django e Python full-stack.

---

**TimeTracker** - Transforme seu tempo em dados! ⏰📊
