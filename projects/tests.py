from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import json
from datetime import timedelta
from .models import Projeto, SessaoTempo


class ProjetoModelTest(TestCase):
    """Testes para o modelo Projeto"""
    
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Projeto Teste",
            descricao="Descrição do projeto teste",
            cor="#007bff"
        )
    
    def test_projeto_criacao(self):
        """Testa a criação de um projeto"""
        self.assertEqual(self.projeto.nome, "Projeto Teste")
        self.assertEqual(self.projeto.descricao, "Descrição do projeto teste")
        self.assertEqual(self.projeto.cor, "#007bff")
        self.assertTrue(self.projeto.ativo)
        self.assertIsNotNone(self.projeto.criado_em)
    
    def test_projeto_str(self):
        """Testa a representação string do projeto"""
        self.assertEqual(str(self.projeto), "Projeto Teste")
    
    def test_tempo_total_hoje(self):
        """Testa o cálculo de tempo total hoje"""
        # Criar uma sessão finalizada
        inicio = timezone.now() - timedelta(hours=2)
        fim = timezone.now() - timedelta(hours=1)
        SessaoTempo.objects.create(
            projeto=self.projeto,
            inicio=inicio,
            fim=fim
        )
        
        tempo = self.projeto.tempo_total_hoje()
        self.assertEqual(tempo.seconds, 3600)  # 1 hora = 3600 segundos


class SessaoTempoModelTest(TestCase):
    """Testes para o modelo SessaoTempo"""
    
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Projeto Teste",
            descricao="Teste",
            cor="#007bff"
        )
    
    def test_sessao_criacao(self):
        """Testa a criação de uma sessão"""
        sessao = SessaoTempo.objects.create(projeto=self.projeto)
        self.assertEqual(sessao.projeto, self.projeto)
        self.assertIsNotNone(sessao.inicio)
        self.assertIsNone(sessao.fim)
        self.assertEqual(sessao.descricao, "")
    
    def test_duracao_sessao_ativa(self):
        """Testa o cálculo de duração para sessão ativa"""
        sessao = SessaoTempo.objects.create(projeto=self.projeto)
        duracao = sessao.duracao()
        self.assertIsInstance(duracao, timedelta)
        self.assertGreater(duracao.total_seconds(), 0)
    
    def test_duracao_sessao_finalizada(self):
        """Testa o cálculo de duração para sessão finalizada"""
        inicio = timezone.now() - timedelta(hours=2)
        fim = timezone.now() - timedelta(hours=1)
        sessao = SessaoTempo.objects.create(
            projeto=self.projeto,
            inicio=inicio,
            fim=fim
        )
        duracao = sessao.duracao()
        self.assertEqual(duracao.seconds, 3600)  # 1 hora


class ProjetoViewsTest(TestCase):
    """Testes para as views de projetos"""
    
    def setUp(self):
        self.client = Client()
        self.projeto = Projeto.objects.create(
            nome="Projeto Teste",
            descricao="Descrição teste",
            cor="#007bff"
        )
    
    def test_dashboard_view(self):
        """Testa a view do dashboard"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Projeto Teste")
    
    def test_gerenciar_projetos_view(self):
        """Testa a view de gerenciar projetos"""
        response = self.client.get(reverse('gerenciar_projetos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Projeto Teste")
    
    def test_criar_projeto_post(self):
        """Testa a criação de projeto via POST"""
        data = {
            'nome': 'Novo Projeto',
            'descricao': 'Nova descrição',
            'cor': '#ff0000'
        }
        response = self.client.post(reverse('gerenciar_projetos'), data)
        self.assertEqual(response.status_code, 302)  # Redirect após criação
        self.assertTrue(Projeto.objects.filter(nome='Novo Projeto').exists())
    
    def test_editar_projeto_get(self):
        """Testa o carregamento de dados para edição"""
        response = self.client.get(
            reverse('editar_projeto', args=[self.projeto.id])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['projeto']['nome'], 'Projeto Teste')
    
    def test_editar_projeto_post(self):
        """Testa a edição de projeto via POST"""
        data = {
            'nome': 'Projeto Editado',
            'descricao': 'Descrição editada',
            'cor': '#ff0000',
            'ativo': True
        }
        response = self.client.post(
            reverse('editar_projeto', args=[self.projeto.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verificar se foi atualizado
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.nome, 'Projeto Editado')
    
    def test_editar_projeto_nome_vazio(self):
        """Testa edição com nome vazio"""
        data = {
            'nome': '',
            'descricao': 'Descrição',
            'cor': '#ff0000',
            'ativo': True
        }
        response = self.client.post(
            reverse('editar_projeto', args=[self.projeto.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('obrigatório', response_data['message'])
    
    def test_editar_projeto_nome_duplicado(self):
        """Testa edição com nome já existente"""
        # Criar outro projeto
        Projeto.objects.create(nome="Outro Projeto", cor="#00ff00")
        
        data = {
            'nome': 'Outro Projeto',
            'descricao': 'Descrição',
            'cor': '#ff0000',
            'ativo': True
        }
        response = self.client.post(
            reverse('editar_projeto', args=[self.projeto.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Já existe', response_data['message'])
    
    def test_excluir_projeto(self):
        """Testa a exclusão de projeto"""
        projeto_id = self.projeto.id
        response = self.client.post(
            reverse('excluir_projeto', args=[projeto_id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertFalse(Projeto.objects.filter(id=projeto_id).exists())
    
    def test_excluir_projeto_com_sessao_ativa(self):
        """Testa que não é possível excluir projeto com sessão ativa"""
        # Criar sessão ativa
        SessaoTempo.objects.create(projeto=self.projeto)
        
        response = self.client.post(
            reverse('excluir_projeto', args=[self.projeto.id])
        )
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('sessão ativa', response_data['message'])
        self.assertTrue(Projeto.objects.filter(id=self.projeto.id).exists())
    
    def test_toggle_projeto_status(self):
        """Testa a alteração de status do projeto"""
        data = {'ativo': False}
        response = self.client.post(
            reverse('toggle_projeto_status', args=[self.projeto.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verificar se foi atualizado
        self.projeto.refresh_from_db()
        self.assertFalse(self.projeto.ativo)


class SessaoViewsTest(TestCase):
    """Testes para as views de sessões"""
    
    def setUp(self):
        self.client = Client()
        self.projeto = Projeto.objects.create(
            nome="Projeto Teste",
            cor="#007bff"
        )
    
    def test_iniciar_sessao(self):
        """Testa iniciar uma sessão"""
        response = self.client.post(
            reverse('iniciar_sessao', args=[self.projeto.id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(SessaoTempo.objects.filter(projeto=self.projeto, fim__isnull=True).exists())
    
    def test_iniciar_sessao_ja_ativa(self):
        """Testa que não é possível iniciar sessão quando já há uma ativa"""
        # Criar sessão ativa
        SessaoTempo.objects.create(projeto=self.projeto)
        
        response = self.client.post(
            reverse('iniciar_sessao', args=[self.projeto.id])
        )
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Já existe', response_data['message'])
    
    def test_finalizar_sessao(self):
        """Testa finalizar uma sessão"""
        # Criar sessão ativa
        sessao = SessaoTempo.objects.create(projeto=self.projeto)
        
        data = {'descricao': 'Trabalho finalizado'}
        response = self.client.post(
            reverse('finalizar_sessao'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verificar se foi finalizada
        sessao.refresh_from_db()
        self.assertIsNotNone(sessao.fim)
        self.assertEqual(sessao.descricao, 'Trabalho finalizado')
    
    def test_finalizar_sessao_inexistente(self):
        """Testa finalizar sessão quando não há nenhuma ativa"""
        data = {'descricao': 'Teste'}
        response = self.client.post(
            reverse('finalizar_sessao'),
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Não há sessão ativa', response_data['message'])
    
    def test_status_sessao_ativa(self):
        """Testa API de status com sessão ativa"""
        sessao = SessaoTempo.objects.create(projeto=self.projeto)
        
        response = self.client.get(reverse('status_sessao'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['ativa'])
        self.assertEqual(response_data['projeto_nome'], self.projeto.nome)
    
    def test_status_sessao_inativa(self):
        """Testa API de status sem sessão ativa"""
        response = self.client.get(reverse('status_sessao'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['ativa'])


class IntegrationTest(TestCase):
    """Testes de integração do sistema completo"""
    
    def setUp(self):
        self.client = Client()
        self.projeto1 = Projeto.objects.create(nome="Projeto 1", cor="#007bff")
        self.projeto2 = Projeto.objects.create(nome="Projeto 2", cor="#28a745")
    
    def test_fluxo_completo_sessao(self):
        """Testa o fluxo completo de uma sessão"""
        # 1. Iniciar sessão
        response = self.client.post(
            reverse('iniciar_sessao', args=[self.projeto1.id])
        )
        self.assertTrue(json.loads(response.content)['success'])
        
        # 2. Verificar status
        response = self.client.get(reverse('status_sessao'))
        data = json.loads(response.content)
        self.assertTrue(data['ativa'])
        
        # 3. Finalizar sessão
        response = self.client.post(
            reverse('finalizar_sessao'),
            data=json.dumps({'descricao': 'Teste completo'}),
            content_type='application/json'
        )
        self.assertTrue(json.loads(response.content)['success'])
        
        # 4. Verificar que não há mais sessão ativa
        response = self.client.get(reverse('status_sessao'))
        data = json.loads(response.content)
        self.assertFalse(data['ativa'])
    
    def test_crud_completo_projeto(self):
        """Testa o CRUD completo de projetos"""
        # 1. Criar projeto
        data = {
            'nome': 'Projeto CRUD',
            'descricao': 'Teste CRUD',
            'cor': '#ff0000'
        }
        response = self.client.post(reverse('gerenciar_projetos'), data)
        self.assertEqual(response.status_code, 302)
        projeto = Projeto.objects.get(nome='Projeto CRUD')
        
        # 2. Editar projeto
        data = {
            'nome': 'Projeto CRUD Editado',
            'descricao': 'Teste CRUD Editado',
            'cor': '#00ff00',
            'ativo': True
        }
        response = self.client.post(
            reverse('editar_projeto', args=[projeto.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertTrue(json.loads(response.content)['success'])
        
        # 3. Verificar edição
        projeto.refresh_from_db()
        self.assertEqual(projeto.nome, 'Projeto CRUD Editado')
        
        # 4. Deletar projeto
        response = self.client.post(
            reverse('excluir_projeto', args=[projeto.id])
        )
        self.assertTrue(json.loads(response.content)['success'])
        self.assertFalse(Projeto.objects.filter(id=projeto.id).exists())
