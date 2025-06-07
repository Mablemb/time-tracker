from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
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
        
        # Pega descrição se fornecida
        data = json.loads(request.body) if request.body else {}
        descricao = data.get('descricao', '')
        
        # Finaliza sessão
        sessao_ativa.fim = timezone.now()
        sessao_ativa.descricao = descricao
        sessao_ativa.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Sessão finalizada. Duração: {sessao_ativa.duracao_formatada()}',
            'duracao': sessao_ativa.duracao_formatada()
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
        else:  # mes
            tempo = projeto.tempo_total_mes()
        
        if tempo.total_seconds() > 0:
            horas = int(tempo.total_seconds() // 3600)
            minutos = int((tempo.total_seconds() % 3600) // 60)
            total_segundos += tempo.total_seconds()
            dados_relatorio.append({
                'projeto': projeto,
                'tempo': tempo,
                'tempo_formatado': f"{horas:02d}:{minutos:02d}",
                'horas_decimais': tempo.total_seconds() / 3600,
                'segundos': tempo.total_seconds()
            })
    
    # Ordena por tempo decrescente
    dados_relatorio.sort(key=lambda x: x['tempo'], reverse=True)
    
    # Calcula porcentagens e barras de progresso
    if dados_relatorio and total_segundos > 0:
        maior_tempo = dados_relatorio[0]['horas_decimais']
        for item in dados_relatorio:
            item['porcentagem'] = (item['segundos'] / total_segundos) * 100
            item['largura_barra'] = (item['horas_decimais'] / maior_tempo) * 100 if maior_tempo > 0 else 0
    
    # Calcula totais
    total_horas = int(total_segundos // 3600)
    total_minutos = int((total_segundos % 3600) // 60)
    total_formatado = f"{total_horas:02d}:{total_minutos:02d}"
    
    # Calcula média por projeto
    media_horas = (total_segundos / 3600) / len(dados_relatorio) if dados_relatorio else 0
    
    context = {
        'dados_relatorio': dados_relatorio,
        'periodo': periodo,
        'periodo_nome': {
            'dia': 'Hoje',
            'semana': 'Esta Semana', 
            'mes': 'Este Mês'
        }.get(periodo, 'Hoje'),
        'total_formatado': total_formatado,
        'total_horas': total_horas,
        'total_minutos': total_minutos,
        'media_horas': media_horas,
        'projetos_ativos': len(dados_relatorio)
    }
    return render(request, 'projects/relatorios.html', context)


def historico(request):
    """View para exibir histórico de sessões"""
    sessoes = SessaoTempo.objects.filter(fim__isnull=False).order_by('-inicio')[:50]
    
    context = {
        'sessoes': sessoes
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
