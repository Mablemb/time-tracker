from django.contrib import admin
from .models import Projeto, SessaoTempo


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']
    ordering = ['nome']


@admin.register(SessaoTempo)
class SessaoTempoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'inicio', 'fim', 'duracao_formatada', 'em_andamento']
    list_filter = ['projeto', 'inicio', 'fim']
    search_fields = ['projeto__nome', 'descricao']
    date_hierarchy = 'inicio'
    ordering = ['-inicio']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('projeto')
