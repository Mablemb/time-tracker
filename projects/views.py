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
                
                if not fim_datetime:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de data/hora inválido.'
                    })
                
                # Validar se não é no futuro
                if fim_datetime > timezone.now():
                    return JsonResponse({
                        'success': False,
                        'message': 'O horário de fim não pode ser no futuro.'
                    })
                
                # Validar se não é anterior ao início da sessão
                if fim_datetime < sessao_ativa.inicio:
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
    """View para exibir relatórios"""
    periodo = request.GET.get('periodo', 'dia')  # dia, semana, mes
    
    projetos = Projeto.objects.filter(ativo=True)
    dados_relatorio = []
    total_segundos = 0
    
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
    
    # Calcular percentuais
    for item in dados_relatorio:
        if total_segundos > 0:
            item['percentual'] = (item['segundos'] / total_segundos) * 100
        else:
            item['percentual'] = 0
    
    # Ordenar por tempo decrescente
    dados_relatorio.sort(key=lambda x: x['segundos'], reverse=True)
    
    context = {
        'dados_relatorio': dados_relatorio,
        'periodo': periodo,
        'total_formatado': str(timedelta(seconds=total_segundos)).split('.')[0],
        'tem_dados': len(dados_relatorio) > 0
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
