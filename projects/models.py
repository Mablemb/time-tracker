from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Projeto(models.Model):
    """Modelo para representar um projeto"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=7, default='#007bff', help_text='Cor em formato hex (ex: #007bff)')
    ativo = models.BooleanField(default=True)
    dados_teste = models.BooleanField(default=False, help_text='Marca se este projeto foi criado como dados de teste')
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nome']
        
    def __str__(self):
        return self.nome
    
    def tempo_total_hoje(self):
        """Retorna o tempo total trabalhado hoje neste projeto"""
        hoje = timezone.now().date()
        sessoes = self.sessoes.filter(inicio__date=hoje, fim__isnull=False)
        total = timezone.timedelta()
        for sessao in sessoes:
            total += sessao.duracao()
        return total
    
    def tempo_total_semana(self):
        """Retorna o tempo total trabalhado nesta semana neste projeto"""
        hoje = timezone.now().date()
        inicio_semana = hoje - timezone.timedelta(days=hoje.weekday())
        sessoes = self.sessoes.filter(
            inicio__date__gte=inicio_semana,
            inicio__date__lte=hoje,
            fim__isnull=False
        )
        total = timezone.timedelta()
        for sessao in sessoes:
            total += sessao.duracao()
        return total
    
    def tempo_total_mes(self):
        """Retorna o tempo total trabalhado neste mês neste projeto"""
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        sessoes = self.sessoes.filter(
            inicio__date__gte=inicio_mes,
            inicio__date__lte=hoje,
            fim__isnull=False
        )
        total = timezone.timedelta()
        for sessao in sessoes:
            total += sessao.duracao()
        return total


class SessaoTempo(models.Model):
    """Modelo para representar uma sessão de trabalho em um projeto"""
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='sessoes')
    inicio = models.DateTimeField(default=timezone.now)
    fim = models.DateTimeField(null=True, blank=True)
    descricao = models.TextField(blank=True, help_text='Opcional: descrição do que foi feito')
    dados_teste = models.BooleanField(default=False, help_text='Marca se esta sessão foi criada como dados de teste')
    
    class Meta:
        ordering = ['-inicio']
        
    def __str__(self):
        if self.fim:
            return f"{self.projeto.nome} - {self.inicio.strftime('%d/%m/%Y %H:%M')} até {self.fim.strftime('%H:%M')}"
        return f"{self.projeto.nome} - {self.inicio.strftime('%d/%m/%Y %H:%M')} (em andamento)"
    
    def duracao(self):
        """Retorna a duração da sessão, truncada para segundos (ignora microssegundos)"""
        from datetime import timedelta
        if self.fim:
            delta = self.fim - self.inicio
        else:
            delta = timezone.now() - self.inicio
        # Remove microssegundos
        return timedelta(seconds=int(delta.total_seconds()))

    def duracao_formatada(self):
        """Retorna a duração formatada como string, nunca mostra menos de 1 segundo"""
        duracao = self.duracao()
        total_segundos = int(duracao.total_seconds())
        if total_segundos < 1:
            return "00:00:01"
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segundos = total_segundos % 60
        if horas > 0:
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        else:
            return f"{minutos:02d}:{segundos:02d}"
    
    def em_andamento(self):
        """Verifica se a sessão está em andamento"""
        return self.fim is None
    
    def clean(self):
        """Validações customizadas"""
        if self.fim and self.fim <= self.inicio:
            raise ValidationError('O fim deve ser posterior ao início.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
