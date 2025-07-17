# Correções de Segurança - Sistema de Dados de Teste

## Problema Identificado

O código inicial do sistema de dados de teste tinha uma vulnerabilidade crítica:

```python
# CÓDIGO PERIGOSO (CORRIGIDO)
if not criado and not projeto.dados_teste:
    projeto.dados_teste = True  # ❌ Marcava projetos reais como teste!
    projeto.save()
```

**Riscos:**
- Dados reais de usuários seriam marcados como dados de teste
- Possibilidade de perda acidental de dados em produção
- Comportamento inesperado em ambientes com dados existentes

## Soluções Implementadas

### 1. Lógica Segura de Criação de Projetos

**Antes:**
```python
projeto, criado = Projeto.objects.get_or_create(nome=dados['nome'], ...)
if not criado and not projeto.dados_teste:
    projeto.dados_teste = True  # ❌ PERIGOSO
```

**Depois:**
```python
# Buscar projeto de teste existente primeiro
projeto_existente = Projeto.objects.filter(nome=dados['nome'], dados_teste=True).first()

if projeto_existente:
    # Usar projeto de teste existente
    projetos_criados.append(projeto_existente)
else:
    # Verificar se existe projeto real
    projeto_real = Projeto.objects.filter(nome=dados['nome'], dados_teste=False).first()
    
    if projeto_real:
        # Criar com nome diferente para não conflitar
        nome_teste = f"{dados['nome']} (Teste)"
        projeto = Projeto.objects.create(nome=nome_teste, dados_teste=True, ...)
    else:
        # Criar normalmente se não há conflito
        projeto = Projeto.objects.create(nome=dados['nome'], dados_teste=True, ...)
```

### 2. Verificações de Segurança

#### Limite de Dados Reais
```python
projetos_reais = Projeto.objects.filter(dados_teste=False).count()
sessoes_reais = SessaoTempo.objects.filter(dados_teste=False).count()

if projetos_reais > 10 or sessoes_reais > 50:
    return JsonResponse({
        'success': False,
        'message': 'Operação cancelada por segurança: muitos dados reais encontrados.'
    })
```

#### Verificação de Integridade na Limpeza
```python
# Confirmar que só dados de teste serão removidos
projetos_reais_impactados = Projeto.objects.filter(
    dados_teste=False, 
    id__in=projetos_teste.values('id')
)
if projetos_reais_impactados.exists():
    return JsonResponse({
        'success': False,
        'message': 'Erro de segurança: dados reais na seleção.'
    })
```

### 3. Prevenção de Conflitos

- **Nomes Únicos:** Projetos de teste recebem sufixo "(Teste)" se já existe projeto real
- **Busca Específica:** Sempre busca por `dados_teste=True` primeiro
- **Nunca Sobrescreve:** Jamais modifica projetos existentes que não são de teste

### 4. Mensagens Informativas

```python
return JsonResponse({
    'success': True,
    'message': 'Dados de teste criados com segurança! Dados reais preservados.',
    'projetos_criados': [p.nome for p in projetos_criados]
})
```

## Cenários de Teste

### Cenário 1: Sistema Vazio
- ✅ Cria projetos normalmente
- ✅ Marca como `dados_teste=True`

### Cenário 2: Sistema com Dados Reais
- ✅ Detecta projetos reais existentes
- ✅ Cria projetos de teste com nomes diferentes
- ✅ Preserva todos os dados reais

### Cenário 3: Sistema com Muitos Dados
- ✅ Cancela operação se detectar produção
- ✅ Evita poluição de dados em ambiente real

### Cenário 4: Limpeza de Dados
- ✅ Remove apenas dados marcados como teste
- ✅ Verifica integridade antes da exclusão
- ✅ Preserva todos os dados reais

## Boas Práticas Aplicadas

### 1. Princípio da Segurança por Design
- Operações destrutivas requerem verificações múltiplas
- Falha segura: em caso de dúvida, cancela a operação

### 2. Separação Clara de Responsabilidades
- `dados_teste=True`: Dados criados para demonstração
- `dados_teste=False`: Dados reais dos usuários

### 3. Feedback Claro
- Mensagens informam exatamente o que foi feito
- Contadores mostram quantos itens foram afetados

### 4. Ambiente-Específico
- Funcionalidades perigosas só aparecem em DEBUG=True
- Produção não oferece funcionalidades de teste

## Verificação de Segurança

Para verificar se o sistema está seguro:

```python
# Listar todos os projetos e seu status
for projeto in Projeto.objects.all():
    print(f"{projeto.nome}: {'TESTE' if projeto.dados_teste else 'REAL'}")

# Verificar sessões
for sessao in SessaoTempo.objects.all():
    status = 'TESTE' if sessao.dados_teste else 'REAL'
    print(f"{sessao.projeto.nome} - {sessao.inicio}: {status}")
```

## Rollback de Emergência

Se dados reais foram marcados como teste acidentalmente:

```python
# APENAS EM EMERGÊNCIA - Reverter marcação incorreta
Projeto.objects.filter(
    dados_teste=True,
    # Adicionar filtros específicos para identificar dados reais
    created_date__lt='2025-01-01'  # Exemplo: projetos antigos
).update(dados_teste=False)
```

## Recomendações

1. **Backup Regular:** Sempre fazer backup antes de operações em massa
2. **Teste Local:** Testar funcionalidades de dados em ambiente isolado
3. **Monitoramento:** Acompanhar logs de criação/exclusão de dados
4. **Revisão de Código:** Sempre revisar operações que modificam dados existentes
