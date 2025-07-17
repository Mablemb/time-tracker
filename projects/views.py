from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from .models import SessaoTempo

@csrf_exempt
@require_http_methods(["POST"])
def atualizar_horario_fim(request, sessao_id):
    """Permite atualizar o horário de fim de uma sessão já encerrada"""
    try:
        sessao = SessaoTempo.objects.get(id=sessao_id)
    except SessaoTempo.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Sessão não encontrada.'})

    if sessao.fim is None:
        return JsonResponse({'success': False, 'message': 'A sessão ainda está em andamento.'})

    data = json.loads(request.body) if request.body else {}
    novo_fim_str = data.get('novo_horario_fim')
    if not novo_fim_str:
        return JsonResponse({'success': False, 'message': 'Novo horário de fim não informado.'})

    from django.utils.dateparse import parse_datetime
    from django.utils import timezone
    novo_fim = parse_datetime(novo_fim_str)
    # Tenta adicionar segundos se vier só até minutos
    if not novo_fim and len(novo_fim_str) == 16:
        novo_fim = parse_datetime(novo_fim_str + ':00')
    if not novo_fim:
        return JsonResponse({'success': False, 'message': 'Formato de data/hora inválido.'})
    # Corrigir: garantir que novo_fim seja timezone-aware
    if timezone.is_naive(novo_fim):
        novo_fim = timezone.make_aware(novo_fim, timezone.get_current_timezone())
    if timezone.is_naive(sessao.inicio):
        inicio_sessao = timezone.make_aware(sessao.inicio, timezone.get_current_timezone())
    else:
        inicio_sessao = sessao.inicio
    if novo_fim < inicio_sessao:
        return JsonResponse({'success': False, 'message': 'O horário de fim não pode ser anterior ao início da sessão.'})
    if novo_fim > timezone.now():
        return JsonResponse({'success': False, 'message': 'O horário de fim não pode ser no futuro.'})
    duracao = (novo_fim - inicio_sessao).total_seconds()
    if duracao < 300:
        return JsonResponse({'success': False, 'message': 'Sessão não pode ser atualizada para menos de 5 minutos.'})

    sessao.fim = novo_fim
    sessao.save()
    return JsonResponse({'success': True, 'message': 'Horário de fim atualizado com sucesso.'})
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Projeto, SessaoTempo
import json
from datetime import datetime, timedelta
from django.db.models import Sum
from collections import defaultdict


def dashboard(request):
    """View principal - dashboard com projetos e controle de tempo"""
    projetos = Projeto.objects.filter(ativo=True)
    sessao_ativa = SessaoTempo.objects.filter(fim__isnull=True).first()
    
    # Estatísticas do dia
    hoje = timezone.now().date()
    tempo_total_hoje = timedelta()
    for projeto in projetos:
        tempo_total_hoje += projeto.tempo_total_hoje()
    
    context = {
        'projetos': projetos,
        'sessao_ativa': sessao_ativa,
        'tempo_total_hoje': tempo_total_hoje,
    }
    return render(request, 'projects/dashboard.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def iniciar_sessao(request, projeto_id):
    """Inicia uma nova sessão de trabalho"""
    if request.method == 'POST':
        projeto = get_object_or_404(Projeto, id=projeto_id)
        
        # Verifica se já existe uma sessão ativa
        sessao_ativa = SessaoTempo.objects.filter(fim__isnull=True).first()
        if sessao_ativa:
            return JsonResponse({
                'success': False,
                'message': f'Já existe uma sessão ativa para o projeto "{sessao_ativa.projeto.nome}". Finalize-a primeiro.'
            })
        
        # Cria nova sessão
        sessao = SessaoTempo.objects.create(projeto=projeto)
        
        return JsonResponse({
            'success': True,
            'message': f'Sessão iniciada para o projeto "{projeto.nome}"',
            'sessao_id': sessao.id,
            'projeto_nome': projeto.nome,
            'inicio': sessao.inicio.strftime('%H:%M')
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@csrf_exempt
@require_http_methods(["POST"])
def finalizar_sessao(request):
    """Finaliza a sessão ativa"""
    if request.method == 'POST':
        sessao_ativa = SessaoTempo.objects.filter(fim__isnull=True).first()
        
        if not sessao_ativa:
            return JsonResponse({
                'success': False,
                'message': 'Não há sessão ativa para finalizar.'
            })
        
        # Pega dados do request
        data = json.loads(request.body) if request.body else {}
        descricao = data.get('descricao', '')
        horario_fim_manual = data.get('horario_fim_manual', None)
        
        # Determinar horário de fim
        if horario_fim_manual:
            try:
                # Converter string ISO para datetime
                fim_datetime = parse_datetime(horario_fim_manual)
                # Tenta adicionar segundos se vier só até minutos
                if not fim_datetime and len(horario_fim_manual) == 16:
                    fim_datetime = parse_datetime(horario_fim_manual + ':00')
                if not fim_datetime:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de data/hora inválido.'
                    })
                # Garantir timezone-aware
                if timezone.is_naive(fim_datetime):
                    fim_datetime = timezone.make_aware(fim_datetime, timezone.get_current_timezone())
                if timezone.is_naive(sessao_ativa.inicio):
                    inicio_sessao = timezone.make_aware(sessao_ativa.inicio, timezone.get_current_timezone())
                else:
                    inicio_sessao = sessao_ativa.inicio
                # Validar se não é no futuro
                if fim_datetime > timezone.now():
                    return JsonResponse({
                        'success': False,
                        'message': 'O horário de fim não pode ser no futuro.'
                    })
                # Validar se não é anterior ao início da sessão
                if fim_datetime < inicio_sessao:
                    return JsonResponse({
                        'success': False,
                        'message': 'O horário de fim não pode ser anterior ao início da sessão.'
                    })
                # Usar horário manual
                sessao_ativa.fim = fim_datetime
                horario_usado = "manual"
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao processar horário manual: {str(e)}'
                })
        else:
            # Usar horário atual
            sessao_ativa.fim = timezone.now()
            horario_usado = "atual"
        
        # Salvar descrição e finalizar
        sessao_ativa.descricao = descricao
        sessao_ativa.save()

        # Prevenção de entradas/saídas acidentais: ignorar sessões com menos de 5 minutos
        duracao = sessao_ativa.duracao()
        if duracao.total_seconds() < 300:
            # Excluir a sessão curta
            sessao_ativa.delete()
            return JsonResponse({
                'success': False,
                'message': 'Sessão descartada: duração inferior a 5 minutos. Certifique-se de não registrar entradas/saídas acidentais.'
            })

        # Preparar mensagem de resposta
        duracao_formatada = sessao_ativa.duracao_formatada()
        if horario_usado == "manual":
            fim_formatado = sessao_ativa.fim.strftime('%d/%m/%Y às %H:%M')
            message = f'Sessão finalizada manualmente em {fim_formatado}. Duração: {duracao_formatada}'
        else:
            message = f'Sessão finalizada. Duração: {duracao_formatada}'

        return JsonResponse({
            'success': True,
            'message': message,
            'duracao': duracao_formatada,
            'horario_usado': horario_usado
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


def relatorios(request):
    """View para exibir relatórios com gráficos interativos"""
    periodo = request.GET.get('periodo', 'dia')  # dia, semana, mes
    
    projetos = Projeto.objects.filter(ativo=True)
    dados_relatorio = []
    total_segundos = 0

    # Nome do período para exibição
    nomes_periodo = {'dia': 'Hoje', 'semana': 'Esta Semana', 'mes': 'Este Mês'}
    periodo_nome = nomes_periodo.get(periodo, 'Período')

    for projeto in projetos:
        if periodo == 'dia':
            tempo = projeto.tempo_total_hoje()
        elif periodo == 'semana':
            tempo = projeto.tempo_total_semana()
        elif periodo == 'mes':
            tempo = projeto.tempo_total_mes()
        else:
            tempo = timedelta()

        if tempo.total_seconds() > 0:
            dados_relatorio.append({
                'projeto': projeto,
                'tempo': tempo,
                'tempo_formatado': str(tempo).split('.')[0],  # Remove microssegundos
                'segundos': int(tempo.total_seconds())
            })
            total_segundos += tempo.total_seconds()

    # Calcular porcentagem e largura da barra
    for item in dados_relatorio:
        if total_segundos > 0:
            item['porcentagem'] = (item['segundos'] / total_segundos) * 100
            item['largura_barra'] = item['porcentagem']
        else:
            item['porcentagem'] = 0
            item['largura_barra'] = 0

    # Ordenar por tempo decrescente
    dados_relatorio.sort(key=lambda x: x['segundos'], reverse=True)

    # Estatísticas
    projetos_ativos = projetos.count()
    media_horas = 0
    if len(dados_relatorio) > 0:
        media_horas = (total_segundos / 3600) / len(dados_relatorio)

    # Dados para gráficos baseados no período selecionado
    dados_graficos = _obter_dados_graficos_por_periodo(projetos, periodo)
    
    # Converter para JSON para o JavaScript
    import json
    from django.conf import settings
    dados_graficos_json = json.dumps(dados_graficos)
    
    # Verificar se há dados de teste no sistema
    tem_dados_teste = (
        Projeto.objects.filter(dados_teste=True).exists() or 
        SessaoTempo.objects.filter(dados_teste=True).exists()
    )

    context = {
        'dados_relatorio': dados_relatorio,
        'periodo': periodo,
        'periodo_nome': periodo_nome,
        'total_formatado': str(timedelta(seconds=total_segundos)).split('.')[0],
        'projetos_ativos': projetos_ativos,
        'media_horas': media_horas,
        'tem_dados': len(dados_relatorio) > 0,
        'dados_graficos': dados_graficos,
        'dados_graficos_json': dados_graficos_json,
        'debug': settings.DEBUG,  # Adicionar flag de debug
        'tem_dados_teste': tem_dados_teste,  # Indicador de dados de teste
    }
    return render(request, 'projects/relatorios.html', context)


def historico(request):
    """View para exibir histórico de sessões"""
    # Filtros
    projeto_filtro = request.GET.get('projeto')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Query base
    sessoes = SessaoTempo.objects.filter(fim__isnull=False).order_by('-inicio')
    
    # Aplicar filtros
    if projeto_filtro:
        sessoes = sessoes.filter(projeto_id=projeto_filtro)
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            sessoes = sessoes.filter(inicio__date__gte=data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            sessoes = sessoes.filter(inicio__date__lte=data_fim_obj)
        except ValueError:
            pass
    
    # Paginação (opcional - pode ser implementada depois)
    sessoes = sessoes[:100]  # Limita a 100 registros por enquanto
    
    projetos = Projeto.objects.all().order_by('nome')
    
    context = {
        'sessoes': sessoes,
        'projetos': projetos,
        'projeto_filtro': projeto_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    return render(request, 'projects/historico.html', context)


def gerenciar_projetos(request):
    """View para gerenciar projetos"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        cor = request.POST.get('cor', '#007bff')
        
        if nome:
            projeto = Projeto.objects.create(
                nome=nome,
                descricao=descricao,
                cor=cor
            )
            messages.success(request, f'Projeto "{projeto.nome}" criado com sucesso!')
        else:
            messages.error(request, 'Nome do projeto é obrigatório.')
        
        return redirect('gerenciar_projetos')
    
    projetos = Projeto.objects.all().order_by('nome')
    context = {
        'projetos': projetos
    }
    return render(request, 'projects/gerenciar_projetos.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def editar_projeto(request, projeto_id):
    """Edita um projeto existente"""
    projeto = get_object_or_404(Projeto, id=projeto_id)
    
    if request.method == 'GET':
        # Retorna dados do projeto para popular o modal
        return JsonResponse({
            'success': True,
            'projeto': {
                'id': projeto.id,
                'nome': projeto.nome,
                'descricao': projeto.descricao,
                'cor': projeto.cor,
                'ativo': projeto.ativo
            }
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            nome = data.get('nome', '').strip()
            descricao = data.get('descricao', '').strip()
            cor = data.get('cor', '#007bff')
            ativo = data.get('ativo', True)
            
            if not nome:
                return JsonResponse({
                    'success': False,
                    'message': 'Nome do projeto é obrigatório.'
                })
            
            # Verificar se já existe outro projeto com o mesmo nome
            if Projeto.objects.filter(nome=nome).exclude(id=projeto.id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Já existe um projeto com este nome.'
                })
            
            # Atualizar projeto
            projeto.nome = nome
            projeto.descricao = descricao
            projeto.cor = cor
            projeto.ativo = ativo
            projeto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Projeto "{projeto.nome}" atualizado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar projeto: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@csrf_exempt
@require_http_methods(["POST"])
def excluir_projeto(request, projeto_id):
    """Exclui um projeto"""
    try:
        projeto = get_object_or_404(Projeto, id=projeto_id)
        
        # Verificar se há sessões ativas para este projeto
        sessao_ativa = SessaoTempo.objects.filter(projeto=projeto, fim__isnull=True).first()
        if sessao_ativa:
            return JsonResponse({
                'success': False,
                'message': 'Não é possível excluir um projeto com sessão ativa. Finalize a sessão primeiro.'
            })
        
        # Verificar se há sessões finalizadas para este projeto
        total_sessoes = SessaoTempo.objects.filter(projeto=projeto).count()
        
        nome_projeto = projeto.nome
        
        # Se há sessões, excluí-las junto com o projeto
        if total_sessoes > 0:
            SessaoTempo.objects.filter(projeto=projeto).delete()
        
        projeto.delete()
        
        if total_sessoes > 0:
            return JsonResponse({
                'success': True,
                'message': f'Projeto "{nome_projeto}" e {total_sessoes} sessão(ões) relacionada(s) excluído(s) com sucesso!'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f'Projeto "{nome_projeto}" excluído com sucesso!'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao excluir projeto: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def toggle_projeto_status(request, projeto_id):
    """Ativa/desativa um projeto"""
    try:
        projeto = get_object_or_404(Projeto, id=projeto_id)
        data = json.loads(request.body) if request.body else {}
        novo_status = data.get('ativo', not projeto.ativo)
        
        projeto.ativo = novo_status
        projeto.save()
        
        status_text = "ativado" if novo_status else "desativado"
        return JsonResponse({
            'success': True,
            'message': f'Projeto "{projeto.nome}" {status_text} com sucesso!',
            'ativo': novo_status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao alterar status do projeto: {str(e)}'
        })


def status_sessao(request):
    """API para obter status da sessão atual"""
    sessao_ativa = SessaoTempo.objects.filter(fim__isnull=True).first()
    
    if sessao_ativa:
        duracao = sessao_ativa.duracao()
        horas = int(duracao.total_seconds() // 3600)
        minutos = int((duracao.total_seconds() % 3600) // 60)
        segundos = int(duracao.total_seconds() % 60)
        
        return JsonResponse({
            'ativa': True,
            'projeto_nome': sessao_ativa.projeto.nome,
            'projeto_cor': sessao_ativa.projeto.cor,
            'inicio': sessao_ativa.inicio.strftime('%H:%M'),
            'duracao': f"{horas:02d}:{minutos:02d}:{segundos:02d}",
            'duracao_segundos': int(duracao.total_seconds())
        })
    
    return JsonResponse({'ativa': False})


def _obter_dados_graficos_por_periodo(projetos, periodo):
    """Prepara dados para os gráficos baseados no período selecionado"""
    hoje = timezone.now().date()
    
    # Definir período baseado na seleção
    if periodo == 'dia':
        inicio_periodo = hoje
        titulo_periodo = 'Hoje'
    elif periodo == 'semana':
        inicio_periodo = hoje - timedelta(days=hoje.weekday())
        titulo_periodo = 'Esta Semana'
    elif periodo == 'mes':
        inicio_periodo = hoje.replace(day=1)
        titulo_periodo = 'Este Mês'
    else:
        inicio_periodo = hoje
        titulo_periodo = 'Hoje'
    
    # 1. Gráfico de barras - Tempo por projeto no período selecionado
    dados_barras = {
        'labels': [],
        'cores': [],
        'dados': [],
        'titulo': titulo_periodo
    }
    
    # 2. Gráfico de pizza - Distribuição do tempo no período
    dados_pizza = {
        'labels': [],
        'dados': [],
        'cores': []
    }
    
    total_periodo_segundos = 0
    
    for projeto in projetos:
        # Calcular tempo baseado no período selecionado
        if periodo == 'dia':
            tempo = projeto.tempo_total_hoje()
        elif periodo == 'semana':
            tempo = projeto.tempo_total_semana()
        elif periodo == 'mes':
            tempo = projeto.tempo_total_mes()
        else:
            tempo = projeto.tempo_total_hoje()
        
        # Para gráfico de barras (mostrar todos os projetos, mesmo com 0 horas)
        dados_barras['labels'].append(projeto.nome)
        dados_barras['cores'].append(projeto.cor)
        dados_barras['dados'].append(round(tempo.total_seconds() / 3600, 2))  # em horas
        
        # Para gráfico de pizza (apenas se houver tempo no período)
        if tempo.total_seconds() > 0:
            dados_pizza['labels'].append(projeto.nome)
            dados_pizza['dados'].append(round(tempo.total_seconds() / 3600, 2))
            dados_pizza['cores'].append(projeto.cor)
            total_periodo_segundos += tempo.total_seconds()
    
    # 3. Gráfico de linha - Evolução baseada no período
    if periodo == 'dia':
        # Para "hoje", mostrar últimas 24 horas
        dados_linha = _obter_dados_linha_horas_hoje(projetos)
    elif periodo == 'semana':
        # Para "semana", mostrar últimos 7 dias
        dados_linha = _obter_dados_linha_ultimos_dias(projetos, 7)
    else:  # mês
        # Para "mês", mostrar últimos 30 dias
        dados_linha = _obter_dados_linha_ultimos_dias(projetos, 30)
    
    # 4. Gráfico de heatmap - Atividade por hora baseada no período
    if periodo == 'dia':
        dados_heatmap = _obter_dados_heatmap_horas(projetos, 1)
    elif periodo == 'semana':
        dados_heatmap = _obter_dados_heatmap_horas(projetos, 7)
    else:  # mês
        dados_heatmap = _obter_dados_heatmap_horas(projetos, 30)
    
    return {
        'barras': dados_barras,
        'pizza': dados_pizza,
        'linha': dados_linha,
        'heatmap': dados_heatmap,
        'total_periodo_horas': round(total_periodo_segundos / 3600, 1),
        'periodo': periodo,
        'titulo_periodo': titulo_periodo
    }


def _obter_dados_linha_ultimos_dias(projetos, num_dias):
    """Obtém dados para gráfico de linha dos últimos N dias"""
    hoje = timezone.now().date()
    dados = {
        'labels': [],
        'datasets': []
    }
    
    # Preparar labels (datas)
    for i in range(num_dias - 1, -1, -1):
        data = hoje - timedelta(days=i)
        dados['labels'].append(data.strftime('%d/%m'))
    
    # Preparar datasets por projeto
    for projeto in projetos:
        dataset = {
            'label': projeto.nome,
            'data': [],
            'borderColor': projeto.cor,
            'backgroundColor': projeto.cor + '20',  # cor com transparência
            'tension': 0.4
        }
        
        # Calcular tempo por dia
        for i in range(num_dias - 1, -1, -1):
            data = hoje - timedelta(days=i)
            sessoes = projeto.sessoes.filter(
                inicio__date=data,
                fim__isnull=False
            )
            tempo_total = sum([s.duracao().total_seconds() for s in sessoes], 0)
            dataset['data'].append(round(tempo_total / 3600, 2))  # em horas
        
        # Só adicionar se houver dados
        if any(d > 0 for d in dataset['data']):
            dados['datasets'].append(dataset)
    
    return dados


def _obter_dados_linha_horas_hoje(projetos):
    """Obtém dados para gráfico de linha das últimas horas de hoje"""
    agora = timezone.now()
    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    
    dados = {
        'labels': [],
        'datasets': []
    }
    
    # Preparar labels (últimas 24 horas, de hora em hora)
    for i in range(24):
        hora = inicio_dia + timedelta(hours=i)
        dados['labels'].append(hora.strftime('%H:00'))
    
    # Preparar datasets por projeto
    for projeto in projetos:
        dataset = {
            'label': projeto.nome,
            'data': [],
            'borderColor': projeto.cor,
            'backgroundColor': projeto.cor + '20',  # cor com transparência
            'tension': 0.4
        }
        
        # Calcular tempo por hora
        for i in range(24):
            hora_inicio = inicio_dia + timedelta(hours=i)
            hora_fim = hora_inicio + timedelta(hours=1)
            
            sessoes = projeto.sessoes.filter(
                inicio__gte=hora_inicio,
                inicio__lt=hora_fim,
                fim__isnull=False
            )
            tempo_total = sum([s.duracao().total_seconds() for s in sessoes], 0)
            dataset['data'].append(round(tempo_total / 3600, 2))  # em horas
        
        # Só adicionar se houver dados
        if any(d > 0 for d in dataset['data']):
            dados['datasets'].append(dataset)
    
    return dados


def _obter_dados_heatmap_horas(projetos, num_dias):
    """Obtém dados para heatmap de atividade por hora"""
    hoje = timezone.now().date()
    inicio_periodo = hoje - timedelta(days=num_dias - 1)
    
    # Agrupar sessões por hora do dia
    atividade_por_hora = defaultdict(float)
    
    for projeto in projetos:
        sessoes = projeto.sessoes.filter(
            inicio__date__gte=inicio_periodo,
            inicio__date__lte=hoje,
            fim__isnull=False
        )
        
        for sessao in sessoes:
            # Calcular tempo por hora dentro da sessão
            inicio = sessao.inicio
            fim = sessao.fim
            
            # Simplificado: usar apenas a hora de início
            hora = inicio.hour
            duracao_horas = sessao.duracao().total_seconds() / 3600
            atividade_por_hora[hora] += duracao_horas
    
    # Preparar dados para o gráfico
    dados_heatmap = []
    for hora in range(24):
        dados_heatmap.append({
            'x': hora,
            'y': round(atividade_por_hora.get(hora, 0), 2)
        })
    
    return dados_heatmap


@csrf_exempt
def popular_dados_teste(request):
    """Popula o banco com dados de teste para demonstração dos gráficos"""
    if request.method == 'POST':
        from datetime import timedelta
        import random
        
        # VERIFICAÇÃO DE SEGURANÇA: Não executar se houver muitos dados reais
        projetos_reais = Projeto.objects.filter(dados_teste=False).count()
        sessoes_reais = SessaoTempo.objects.filter(dados_teste=False).count()
        
        if projetos_reais > 10 or sessoes_reais > 50:
            return JsonResponse({
                'success': False,
                'message': f'Operação cancelada por segurança: {projetos_reais} projetos e {sessoes_reais} sessões reais encontradas. Use esta função apenas em ambiente de desenvolvimento.'
            })
        
        # Criar alguns projetos se não existirem
        projetos_dados = [
            {'nome': 'Website Frontend', 'descricao': 'Desenvolvimento do frontend em React', 'cor': '#3498db'},
            {'nome': 'API Backend', 'descricao': 'Desenvolvimento da API em Django', 'cor': '#2ecc71'},
            {'nome': 'Mobile App', 'descricao': 'Aplicativo mobile em React Native', 'cor': '#e74c3c'},
            {'nome': 'Documentação', 'descricao': 'Documentação técnica do projeto', 'cor': '#f39c12'},
            {'nome': 'Testes', 'descricao': 'Testes automatizados', 'cor': '#9b59b6'},
        ]
        
        projetos_criados = []
        for dados in projetos_dados:
            # Tentar encontrar projeto de teste existente primeiro
            projeto_existente = Projeto.objects.filter(
                nome=dados['nome'], 
                dados_teste=True
            ).first()
            
            if projeto_existente:
                # Se já existe um projeto de teste com esse nome, usar ele
                projetos_criados.append(projeto_existente)
            else:
                # Verificar se existe projeto real com esse nome
                projeto_real = Projeto.objects.filter(
                    nome=dados['nome'], 
                    dados_teste=False
                ).first()
                
                if projeto_real:
                    # Se existe projeto real, criar com nome diferente
                    nome_teste = f"{dados['nome']} (Teste)"
                    projeto, criado = Projeto.objects.get_or_create(
                        nome=nome_teste,
                        defaults={
                            'descricao': dados['descricao'] + ' - Dados de teste',
                            'cor': dados['cor'],
                            'dados_teste': True
                        }
                    )
                else:
                    # Se não existe projeto real, criar normalmente
                    projeto, criado = Projeto.objects.get_or_create(
                        nome=dados['nome'],
                        defaults={
                            'descricao': dados['descricao'],
                            'cor': dados['cor'],
                            'dados_teste': True
                        }
                    )
                
                projetos_criados.append(projeto)
        
        # Criar sessões de teste para os últimos 15 dias
        hoje = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(15):
            data_sessao = hoje - timedelta(days=i)
            
            # Para cada dia, criar 1-4 sessões em projetos aleatórios
            num_sessoes = random.randint(1, 4)
            
            for j in range(num_sessoes):
                projeto = random.choice(projetos_criados)
                
                # Horário de início entre 8h e 17h
                hora_inicio = random.randint(8, 17)
                minuto_inicio = random.choice([0, 15, 30, 45])
                
                inicio = data_sessao.replace(
                    hour=hora_inicio, 
                    minute=minuto_inicio
                )
                
                # Duração entre 30 minutos e 4 horas
                duracao_minutos = random.randint(30, 240)
                fim = inicio + timedelta(minutes=duracao_minutos)
                
                # Não criar sessão se já existe uma no mesmo horário
                if not SessaoTempo.objects.filter(
                    projeto=projeto,
                    inicio__date=data_sessao.date(),
                    inicio__hour=hora_inicio
                ).exists():
                    
                    SessaoTempo.objects.create(
                        projeto=projeto,
                        inicio=inicio,
                        fim=fim,
                        descricao=f'Trabalho em {projeto.nome} - sessão de teste',
                        dados_teste=True  # Marcar como dados de teste
                    )
        
        return JsonResponse({
            'success': True,
            'message': f'Dados de teste criados com segurança! {len(projetos_criados)} projetos de teste e múltiplas sessões. Dados reais de usuários preservados.',
            'projetos_criados': [p.nome for p in projetos_criados]
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@csrf_exempt
def limpar_dados_teste(request):
    """Remove todos os dados marcados como teste"""
    if request.method == 'POST':
        try:
            # VERIFICAÇÃO DE SEGURANÇA: Confirmar que só vamos apagar dados de teste
            projetos_teste = Projeto.objects.filter(dados_teste=True)
            sessoes_teste = SessaoTempo.objects.filter(dados_teste=True)
            
            # Verificar se não há mistura acidental
            projetos_reais_impactados = Projeto.objects.filter(dados_teste=False, id__in=projetos_teste.values('id'))
            if projetos_reais_impactados.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Erro de segurança: dados reais foram encontrados na seleção. Operação cancelada.'
                })
            
            count_projetos = projetos_teste.count()
            count_sessoes = sessoes_teste.count()
            
            if count_projetos == 0 and count_sessoes == 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Nenhum dado de teste encontrado para remover.'
                })
            
            # Excluir sessões de teste primeiro
            sessoes_teste.delete()
            
            # Excluir projetos de teste
            projetos_teste.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Dados de teste removidos com segurança: {count_projetos} projeto(s) e {count_sessoes} sessão(ões). Dados reais preservados.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao limpar dados de teste: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})
