#!/usr/bin/env python
"""
Script de Verificação de Integridade - TimeTracker v1.2.0
Verifica se todos os dados existentes foram preservados corretamente após a atualização.
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetracker.settings')
django.setup()

from projects.models import Projeto, SessaoTempo

def verificar_integridade():
    """Verifica a integridade dos dados após a migração"""
    
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE INTEGRIDADE - TimeTracker v1.2.0")
    print("=" * 60)
    print()
    
    # Verificar projetos
    print("📋 PROJETOS:")
    print("-" * 30)
    
    projetos_total = Projeto.objects.count()
    projetos_reais = Projeto.objects.filter(dados_teste=False).count()
    projetos_teste = Projeto.objects.filter(dados_teste=True).count()
    
    print(f"Total de projetos: {projetos_total}")
    print(f"Projetos reais: {projetos_reais}")
    print(f"Projetos de teste: {projetos_teste}")
    print()
    
    if projetos_total > 0:
        print("Detalhes dos projetos:")
        for projeto in Projeto.objects.all():
            status = "🧪 TESTE" if projeto.dados_teste else "✅ REAL"
            ativo = "Ativo" if projeto.ativo else "Inativo"
            print(f"  • {projeto.nome} - {status} ({ativo})")
        print()
    
    # Verificar sessões
    print("⏱️ SESSÕES:")
    print("-" * 30)
    
    sessoes_total = SessaoTempo.objects.count()
    sessoes_reais = SessaoTempo.objects.filter(dados_teste=False).count()
    sessoes_teste = SessaoTempo.objects.filter(dados_teste=True).count()
    
    print(f"Total de sessões: {sessoes_total}")
    print(f"Sessões reais: {sessoes_reais}")
    print(f"Sessões de teste: {sessoes_teste}")
    print()
    
    # Verificar sessões ativas
    sessoes_ativas = SessaoTempo.objects.filter(fim__isnull=True).count()
    print(f"Sessões ativas no momento: {sessoes_ativas}")
    print()
    
    # Estatísticas de tempo
    if sessoes_reais > 0:
        print("📊 ESTATÍSTICAS DE DADOS REAIS:")
        print("-" * 40)
        
        sessoes_completas = SessaoTempo.objects.filter(
            dados_teste=False, 
            fim__isnull=False
        )
        
        if sessoes_completas.exists():
            primeira_sessao = sessoes_completas.order_by('inicio').first()
            ultima_sessao = sessoes_completas.order_by('-inicio').first()
            
            print(f"Primeira sessão: {primeira_sessao.inicio.strftime('%d/%m/%Y %H:%M')}")
            print(f"Última sessão: {ultima_sessao.inicio.strftime('%d/%m/%Y %H:%M')}")
            
            # Calcular tempo total
            tempo_total = sum([s.duracao().total_seconds() for s in sessoes_completas])
            horas_total = tempo_total / 3600
            print(f"Tempo total registrado: {horas_total:.1f} horas")
        print()
    
    # Verificação de segurança
    print("🛡️ VERIFICAÇÃO DE SEGURANÇA:")
    print("-" * 35)
    
    problemas = []
    
    # Verificar se existem dados sem o campo dados_teste
    try:
        projetos_sem_campo = Projeto.objects.filter(dados_teste__isnull=True).count()
        sessoes_sem_campo = SessaoTempo.objects.filter(dados_teste__isnull=True).count()
        
        if projetos_sem_campo > 0:
            problemas.append(f"❌ {projetos_sem_campo} projeto(s) sem campo dados_teste")
        
        if sessoes_sem_campo > 0:
            problemas.append(f"❌ {sessoes_sem_campo} sessão(ões) sem campo dados_teste")
            
    except Exception as e:
        problemas.append(f"❌ Erro ao verificar campos: {str(e)}")
    
    # Verificar consistência
    if projetos_total == projetos_reais + projetos_teste:
        print("✅ Contagem de projetos consistente")
    else:
        problemas.append("❌ Contagem de projetos inconsistente")
    
    if sessoes_total == sessoes_reais + sessoes_teste:
        print("✅ Contagem de sessões consistente")
    else:
        problemas.append("❌ Contagem de sessões inconsistente")
    
    # Verificar se projetos de teste têm nome indicativo
    projetos_teste_obj = Projeto.objects.filter(dados_teste=True)
    for projeto in projetos_teste_obj:
        if not any(palavra in projeto.nome.lower() for palavra in ['teste', 'test', 'demo', 'exemplo']):
            print(f"⚠️  Projeto de teste sem indicação clara: {projeto.nome}")
    
    print()
    
    # Resultado final
    print("🎯 RESULTADO FINAL:")
    print("-" * 25)
    
    if problemas:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"  {problema}")
        print()
        print("💡 Recomendação: Execute 'python manage.py migrate' novamente")
        return False
    else:
        print("✅ TUDO OK! Seus dados estão seguros e íntegros.")
        print()
        print("🎉 A atualização foi bem-sucedida!")
        print("📊 Aproveite os novos gráficos em 'Relatórios'")
        
        if projetos_teste > 0 or sessoes_teste > 0:
            print()
            print("🧪 Dados de teste detectados.")
            print("   Use 'Limpar Teste' se quiser removê-los.")
        
        return True

def main():
    """Função principal"""
    try:
        sucesso = verificar_integridade()
        print()
        print("=" * 60)
        print(f"Verificação concluída em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        if sucesso:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro durante a verificação: {str(e)}")
        print()
        print("💡 Certifique-se de que:")
        print("   • O ambiente virtual está ativo")
        print("   • As migrações foram aplicadas")
        print("   • O Django está configurado corretamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
