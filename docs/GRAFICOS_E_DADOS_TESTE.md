# Sistema de Gráficos e Dados de Teste

## Visão Geral

O TimeTracker agora possui um sistema completo de visualização de dados através de gráficos interativos e um sistema robusto de gerenciamento de dados de teste para desenvolvimento.

## Funcionalidades dos Gráficos

### Tipos de Gráficos Implementados

1. **Gráfico de Barras** - Tempo por Projeto
   - Mostra o tempo dedicado a cada projeto
   - Cores personalizadas por projeto
   - Valores em horas

2. **Gráfico de Pizza** - Distribuição de Tempo
   - Percentual de tempo por projeto
   - Total de horas no período
   - Cores consistentes com outros gráficos

3. **Gráfico de Linha** - Tendência Temporal
   - Evolução do tempo ao longo dos dias
   - Ideal para visualizar padrões de trabalho
   - Responsivo aos filtros de período

4. **Mapa de Calor** - Atividade por Hora do Dia
   - Mostra os horários mais ativos
   - Escala de cores baseada na intensidade
   - Útil para identificar padrões de produtividade

### Filtros de Período

- **Hoje**: Dados do dia atual
- **Esta Semana**: Dados dos últimos 7 dias
- **Este Mês**: Dados do mês atual

Todos os gráficos respondem automaticamente aos filtros selecionados.

## Sistema de Dados de Teste

### Funcionalidades

1. **Criação de Dados de Teste**
   - Gera projetos e sessões de exemplo
   - Dados marcados com flag `dados_teste=True`
   - Variedade de projetos com cores diferentes
   - Sessões distribuídas ao longo do tempo

2. **Identificação Visual**
   - Alerta no topo da página quando há dados de teste
   - Indicação clara para o usuário
   - Diferenciação entre dados reais e de teste

3. **Limpeza de Dados de Teste**
   - Remoção seletiva apenas dos dados marcados como teste
   - Preserva dados reais do usuário
   - Operação segura e reversível

### Controles de Ambiente

- **Ambiente de Desenvolvimento** (`DEBUG=True`):
  - Botões de "Dados de Teste" e "Limpar Teste" visíveis
  - Alertas informativos sobre dados de teste
  - Funcionalidade completa de gerenciamento

- **Ambiente de Produção** (`DEBUG=False`):
  - Botões de teste não aparecem
  - Sistema limpo para usuários finais
  - Dados de teste (se houver) permanecem identificados

## Estrutura Técnica

### Modelos de Dados

```python
# Campos adicionados aos modelos
class Projeto(models.Model):
    # ... campos existentes ...
    dados_teste = models.BooleanField(default=False)

class SessaoTempo(models.Model):
    # ... campos existentes ...
    dados_teste = models.BooleanField(default=False)
```

### Views Principais

- `relatorios()`: View principal com gráficos e relatórios
- `popular_dados_teste()`: Criação de dados de exemplo
- `limpar_dados_teste()`: Remoção de dados de teste
- `_obter_dados_graficos_por_periodo()`: Processamento de dados para gráficos

### URLs

```python
path('popular-dados-teste/', views.popular_dados_teste, name='popular_dados_teste'),
path('limpar-dados-teste/', views.limpar_dados_teste, name='limpar_dados_teste'),
```

## Tecnologias Utilizadas

- **Chart.js**: Biblioteca para gráficos interativos
- **Bootstrap**: Framework CSS para responsividade
- **Django**: Backend e template system
- **SQLite**: Banco de dados com campos de controle

## Segurança e Boas Práticas

1. **Separação de Ambientes**: Funcionalidades de teste apenas em desenvolvimento
2. **Marcação de Dados**: Sistema de flags para identificar dados de teste
3. **Operações Seguras**: Limpeza seletiva que não afeta dados reais
4. **Interface Intuitiva**: Alertas e indicações claras para o usuário

## Como Usar

### Para Desenvolvedores

1. Execute o projeto em modo DEBUG
2. Acesse a página de Relatórios
3. Use "Dados de Teste" para popular o sistema
4. Teste os gráficos com diferentes filtros
5. Use "Limpar Teste" quando necessário

### Para Usuários Finais

1. O sistema funciona automaticamente
2. Gráficos aparecem conforme dados são inseridos
3. Use os filtros para visualizar diferentes períodos
4. Dados de teste não interferem na experiência

## Manutenção

- Os dados de teste são identificados permanentemente
- Migrações futuras preservam a marcação
- Sistema pode ser expandido com novos tipos de gráficos
- Filtros podem ser customizados conforme necessário

## Próximos Passos Sugeridos

1. Adicionar exportação de gráficos em PDF
2. Implementar gráficos de comparação entre períodos
3. Adicionar métricas de produtividade
4. Criar dashboard executivo com KPIs
