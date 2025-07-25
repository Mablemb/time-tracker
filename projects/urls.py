from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('iniciar/<int:projeto_id>/', views.iniciar_sessao, name='iniciar_sessao'),
    path('finalizar/', views.finalizar_sessao, name='finalizar_sessao'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('historico/', views.historico, name='historico'),
    path('projetos/', views.gerenciar_projetos, name='gerenciar_projetos'),
    path('projetos/editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('projetos/excluir/<int:projeto_id>/', views.excluir_projeto, name='excluir_projeto'),
    path('projetos/toggle/<int:projeto_id>/', views.toggle_projeto_status, name='toggle_projeto_status'),
    path('api/status/', views.status_sessao, name='status_sessao'),
    path('sessao/<int:sessao_id>/atualizar_fim/', views.atualizar_horario_fim, name='atualizar_horario_fim'),
    path('popular-dados-teste/', views.popular_dados_teste, name='popular_dados_teste'),
    path('limpar-dados-teste/', views.limpar_dados_teste, name='limpar_dados_teste'),
]
