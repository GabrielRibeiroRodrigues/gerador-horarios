"""
Views para o sistema de horários escolares.

Este módulo contém todas as views da aplicação, implementadas seguindo
os princípios SOLID e padrões de desenvolvimento Django.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import (
    Disciplina, Sala, Professor, Turma, PreferenciaProfessor, Horario, BloqueioTemporario,
    NotificacaoSistema, AuditoriaHorario, PeriodoLetivo, EventoAcademico
)
from .forms import (
    DisciplinaForm, SalaForm, ProfessorForm, TurmaForm, 
    PreferenciaProfessorForm, HorarioForm, GerarHorariosForm, BloqueioTemporarioForm
)
# from .dashboard import DashboardAnalytico  # Comentado temporariamente


def home(request):
    """
    View da página inicial do sistema de gerenciamento de horários escolares.
    
    Args:
        request: Objeto HttpRequest do Django
        
    Returns:
        HttpResponse: Resposta HTTP com a página inicial
    """
    context = {
        'total_disciplinas': Disciplina.objects.filter(ativa=True).count(),
        'total_salas': Sala.objects.filter(ativa=True).count(),
        'total_professores': Professor.objects.filter(ativo=True).count(),
        'total_turmas': Turma.objects.filter(ativa=True).count(),
        'total_horarios': Horario.objects.count(),
    }
    return render(request, 'core/home.html', context)


def dashboard_analitico(request):
    """
    View para o dashboard analítico com relatórios e métricas.
    
    Args:
        request: Objeto HttpRequest do Django
        
    Returns:
        HttpResponse: Resposta HTTP com o dashboard analítico
    """
    # Estatísticas básicas sem depender dos novos modelos
    total_horarios = Horario.objects.count()
    total_professores = Professor.objects.filter(ativo=True).count()
    total_salas = Sala.objects.filter(ativa=True).count()
    total_turmas = Turma.objects.filter(ativa=True).count()
    
    # Estatísticas gerais simuladas
    estatisticas_gerais = {
        'totais': {
            'horarios': total_horarios,
            'professores': total_professores,
            'salas': total_salas,
            'turmas': total_turmas,
        },
        'distribuicao_turnos': {
            'manha': Horario.objects.filter(turno='M').count(),
            'tarde': Horario.objects.filter(turno='T').count(),
            'noite': Horario.objects.filter(turno='N').count(),
        },
        'alertas': {
            'notificacoes_nao_lidas': 0,
            'conflitos_criticos': 0,
        }
    }
    
    # Ocupação de salas básica
    ocupacao_salas = []
    for sala in Sala.objects.filter(ativa=True)[:10]:
        total_horarios_sala = Horario.objects.filter(sala=sala).count()
        ocupacao_salas.append({
            'sala': sala,
            'total_horarios': total_horarios_sala,
            'taxa_ocupacao': min(100, (total_horarios_sala / 25) * 100),  # Assumindo 25 slots por semana
            'status': 'alta' if total_horarios_sala > 20 else 'media' if total_horarios_sala > 10 else 'baixa',
            'status_label': 'Alta' if total_horarios_sala > 20 else 'Média' if total_horarios_sala > 10 else 'Baixa'
        })
    
    # Distribuição de professores básica
    distribuicao_professores = []
    for professor in Professor.objects.filter(ativo=True)[:10]:
        total_aulas = Horario.objects.filter(professor=professor).count()
        total_turmas_prof = Horario.objects.filter(professor=professor).values('turma').distinct().count()
        distribuicao_professores.append({
            'professor': professor,
            'total_aulas': total_aulas,
            'total_turmas': total_turmas_prof,
            'status': 'completo' if total_aulas >= 20 else 'incompleto',
            'status_label': 'Completo' if total_aulas >= 20 else 'Incompleto'
        })
    
    # Métricas de performance básicas
    metricas_performance = {
        'taxa_utilizacao': 75,
        'atividades_semana': total_horarios,
        'conflitos_novos': 0,
        'conflitos_resolvidos': 0,
    }
    
    context = {
        'estatisticas_gerais': estatisticas_gerais,
        'ocupacao_salas': ocupacao_salas,
        'distribuicao_professores': distribuicao_professores,
        'conflitos_frequentes': [],
        'eventos_proximos': [],
        'auditoria_recente': [],
        'relatorio_carga': {},
        'metricas_performance': metricas_performance,
    }
    
    return render(request, 'core/dashboard.html', context)


# Views para Disciplinas
class DisciplinaListView(ListView):
    """View para listagem de disciplinas com busca e paginação."""
    model = Disciplina
    template_name = 'core/disciplina_list.html'
    context_object_name = 'disciplinas'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtra disciplinas por termo de busca."""
        queryset = Disciplina.objects.all().order_by('nome')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(curso_area__icontains=search) |
                Q(periodo_serie__icontains=search)
            )
        return queryset


class DisciplinaDetailView(DetailView):
    """View para detalhes de uma disciplina."""
    model = Disciplina
    template_name = 'core/disciplina_detail.html'
    context_object_name = 'object'


class DisciplinaCreateView(CreateView):
    """View para criação de disciplinas."""
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'core/disciplina_form.html'
    success_url = reverse_lazy('core:disciplina_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Disciplina criada com sucesso!')
        return super().form_valid(form)


class DisciplinaUpdateView(UpdateView):
    """View para edição de disciplinas."""
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'core/disciplina_form.html'
    success_url = reverse_lazy('core:disciplina_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Disciplina atualizada com sucesso!')
        return super().form_valid(form)


class DisciplinaDeleteView(DeleteView):
    """View para exclusão de disciplinas."""
    model = Disciplina
    template_name = 'core/disciplina_confirm_delete.html'
    success_url = reverse_lazy('core:disciplina_list')
    
    def delete(self, request, *args, **kwargs):
        """Processa exclusão."""
        messages.success(request, 'Disciplina excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Salas
class SalaListView(ListView):
    """View para listagem de salas com busca e paginação."""
    model = Sala
    template_name = 'core/sala_list.html'
    context_object_name = 'salas'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtra salas por termo de busca."""
        queryset = Sala.objects.all().order_by('nome_numero')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_numero__icontains=search) |
                Q(tipo__icontains=search)
            )
        return queryset


class SalaDetailView(DetailView):
    """View para detalhes de uma sala."""
    model = Sala
    template_name = 'core/sala_detail.html'
    context_object_name = 'object'


class SalaCreateView(CreateView):
    """View para criação de salas."""
    model = Sala
    form_class = SalaForm
    template_name = 'core/sala_form.html'
    success_url = reverse_lazy('core:sala_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Sala criada com sucesso!')
        return super().form_valid(form)


class SalaUpdateView(UpdateView):
    """View para edição de salas."""
    model = Sala
    form_class = SalaForm
    template_name = 'core/sala_form.html'
    success_url = reverse_lazy('core:sala_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Sala atualizada com sucesso!')
        return super().form_valid(form)


class SalaDeleteView(DeleteView):
    """View para exclusão de salas."""
    model = Sala
    template_name = 'core/sala_confirm_delete.html'
    success_url = reverse_lazy('core:sala_list')
    
    def delete(self, request, *args, **kwargs):
        """Processa exclusão."""
        messages.success(request, 'Sala excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Professores
class ProfessorListView(ListView):
    """View para listagem de professores com busca e paginação."""
    model = Professor
    template_name = 'core/professor_list.html'
    context_object_name = 'professores'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtra professores por termo de busca."""
        queryset = Professor.objects.all().prefetch_related('disciplinas').order_by('nome_completo')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nome_completo__icontains=search)
        return queryset


class ProfessorDetailView(DetailView):
    """View para detalhes de um professor."""
    model = Professor
    template_name = 'core/professor_detail.html'
    context_object_name = 'object'


class ProfessorCreateView(CreateView):
    """View para criação de professores."""
    model = Professor
    form_class = ProfessorForm
    template_name = 'core/professor_form.html'
    success_url = reverse_lazy('core:professor_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Professor criado com sucesso!')
        return super().form_valid(form)


class ProfessorUpdateView(UpdateView):
    """View para edição de professores."""
    model = Professor
    form_class = ProfessorForm
    template_name = 'core/professor_form.html'
    success_url = reverse_lazy('core:professor_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Professor atualizado com sucesso!')
        return super().form_valid(form)


class ProfessorDeleteView(DeleteView):
    """View para exclusão de professores."""
    model = Professor
    template_name = 'core/professor_confirm_delete.html'
    success_url = reverse_lazy('core:professor_list')
    
    def delete(self, request, *args, **kwargs):
        """Processa exclusão."""
        messages.success(request, 'Professor excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Turmas
class TurmaListView(ListView):
    """View para listagem de turmas com busca e paginação."""
    model = Turma
    template_name = 'core/turma_list.html'
    context_object_name = 'turmas'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtra turmas por termo de busca."""
        queryset = Turma.objects.all().prefetch_related('disciplinas').order_by('nome_codigo')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_codigo__icontains=search) |
                Q(serie_periodo__icontains=search)
            )
        return queryset


class TurmaDetailView(DetailView):
    """View para detalhes de uma turma."""
    model = Turma
    template_name = 'core/turma_detail.html'
    context_object_name = 'object'


class TurmaCreateView(CreateView):
    """View para criação de turmas."""
    model = Turma
    form_class = TurmaForm
    template_name = 'core/turma_form.html'
    success_url = reverse_lazy('core:turma_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Turma criada com sucesso!')
        return super().form_valid(form)


class TurmaUpdateView(UpdateView):
    """View para edição de turmas."""
    model = Turma
    form_class = TurmaForm
    template_name = 'core/turma_form.html'
    success_url = reverse_lazy('core:turma_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Turma atualizada com sucesso!')
        return super().form_valid(form)


class TurmaDeleteView(DeleteView):
    """View para exclusão de turmas."""
    model = Turma
    template_name = 'core/turma_confirm_delete.html'
    success_url = reverse_lazy('core:turma_list')
    
    def delete(self, request, *args, **kwargs):
        """Processa exclusão."""
        messages.success(request, 'Turma excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Preferências
class PreferenciaProfessorListView(ListView):
    """View para listagem de preferências de professores."""
    model = PreferenciaProfessor
    template_name = 'core/preferencia_list.html'
    context_object_name = 'preferencias'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtra preferências por professor."""
        queryset = PreferenciaProfessor.objects.all().select_related('professor', 'disciplina')
        professor_id = self.request.GET.get('professor')
        if professor_id:
            queryset = queryset.filter(professor_id=professor_id)
        return queryset.order_by('professor__nome_completo', 'dia_semana', 'turno')
    
    def get_context_data(self, **kwargs):
        """Adiciona professores ao contexto."""
        context = super().get_context_data(**kwargs)
        context['professores'] = Professor.objects.filter(ativo=True).order_by('nome_completo')
        return context


class PreferenciaProfessorCreateView(CreateView):
    """View para criação de preferências."""
    model = PreferenciaProfessor
    form_class = PreferenciaProfessorForm
    template_name = 'core/preferencia_form.html'
    success_url = reverse_lazy('core:preferencia_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Preferência configurada com sucesso!')
        return super().form_valid(form)


class PreferenciaProfessorUpdateView(UpdateView):
    """View para edição de preferências."""
    model = PreferenciaProfessor
    form_class = PreferenciaProfessorForm
    template_name = 'core/preferencia_form.html'
    success_url = reverse_lazy('core:preferencia_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Preferência atualizada com sucesso!')
        return super().form_valid(form)


class PreferenciaProfessorDeleteView(DeleteView):
    """View para exclusão de preferências."""
    model = PreferenciaProfessor
    template_name = 'core/preferencia_confirm_delete.html'
    success_url = reverse_lazy('core:preferencia_list')
    
    def delete(self, request, *args, **kwargs):
        """Processa exclusão."""
        messages.success(request, 'Preferência excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Horários
class HorarioListView(ListView):
    """View para listagem de horários."""
    model = Horario
    template_name = 'core/horario_list.html'
    context_object_name = 'horarios'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtra horários por parâmetros."""
        queryset = Horario.objects.all().select_related(
            'turma', 'disciplina', 'professor', 'sala'
        ).order_by('dia_semana', 'horario_inicio')
        
        # Filtros
        turma_id = self.request.GET.get('turma')
        professor_id = self.request.GET.get('professor')
        sala_id = self.request.GET.get('sala')
        disciplina_id = self.request.GET.get('disciplina')
        
        if turma_id:
            queryset = queryset.filter(turma_id=turma_id)
        if professor_id:
            queryset = queryset.filter(professor_id=professor_id)
        if sala_id:
            queryset = queryset.filter(sala_id=sala_id)
        if disciplina_id:
            queryset = queryset.filter(disciplina_id=disciplina_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Adiciona dados para os filtros."""
        context = super().get_context_data(**kwargs)
        context['turmas'] = Turma.objects.filter(ativa=True).order_by('nome_codigo')
        context['professores'] = Professor.objects.filter(ativo=True).order_by('nome_completo')
        context['salas'] = Sala.objects.filter(ativa=True).order_by('nome_numero')
        context['disciplinas'] = Disciplina.objects.filter(ativa=True).order_by('nome')
        return context


class HorarioCreateView(CreateView):
    """View para criação de horários."""
    model = Horario
    form_class = HorarioForm
    template_name = 'core/horario_form.html'
    success_url = reverse_lazy('core:horario_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Horário criado com sucesso!')
        return super().form_valid(form)


class HorarioUpdateView(UpdateView):
    """View para edição de horários."""
    model = Horario
    form_class = HorarioForm
    template_name = 'core/horario_form.html'
    success_url = reverse_lazy('core:horario_list')
    
    def form_valid(self, form):
        """Processa formulário válido."""
        messages.success(self.request, 'Horário atualizado com sucesso!')
        return super().form_valid(form)


class HorarioDeleteView(DeleteView):
    """View para exclusão de horários."""
    model = Horario
    template_name = 'core/horario_confirm_delete.html'
    success_url = reverse_lazy('core:horario_list')
    
    def delete(self, request, *args, **kwargs):
        """Processa exclusão."""
        messages.success(request, 'Horário excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# View para Geração de Horários
def gerar_horarios(request):
    """
    View para geração automática de horários.
    
    Processa o formulário de configuração e executa o algoritmo
    de geração automática de horários.
    """
    from .algoritmo_horarios import gerar_horarios_automaticamente
    
    if request.method == 'POST':
        form = GerarHorariosForm(request.POST)
        if form.is_valid():
            try:
                # Obter parâmetros do formulário
                turmas_selecionadas = form.cleaned_data.get('turmas_selecionadas')
                if not turmas_selecionadas:
                    turmas_selecionadas = None  # Usar todas as turmas ativas
                
                # Executar algoritmo de geração
                resultado = gerar_horarios_automaticamente(
                    turmas=turmas_selecionadas,
                    respeitar_preferencias=form.cleaned_data.get('respeitar_preferencias', True),
                    evitar_janelas=form.cleaned_data.get('evitar_janelas', True),
                    distribuir_dias=form.cleaned_data.get('distribuir_dias', True),
                    limpar_anteriores=form.cleaned_data.get('limpar_anteriores', False)
                )
                
                if resultado['sucesso']:
                    messages.success(
                        request, 
                        f'Horários gerados com sucesso! '
                        f'{resultado["horarios_criados"]} horários criados para '
                        f'{resultado["turmas_processadas"]} turmas.'
                    )
                    
                    # Mostrar avisos sobre conflitos se houver
                    if resultado.get('conflitos'):
                        for conflito in resultado['conflitos'][:5]:  # Mostrar apenas os primeiros 5
                            messages.warning(request, f'Aviso: {conflito}')
                        
                        if len(resultado['conflitos']) > 5:
                            messages.info(
                                request, 
                                f'E mais {len(resultado["conflitos"]) - 5} avisos...'
                            )
                    
                    return redirect('core:horario_list')
                else:
                    messages.error(
                        request, 
                        f'Erro ao gerar horários: {resultado.get("erro", "Erro desconhecido")}'
                    )
                    
                    # Mostrar conflitos específicos
                    if resultado.get('conflitos'):
                        for conflito in resultado['conflitos'][:3]:
                            messages.error(request, conflito)
                            
            except Exception as e:
                messages.error(request, f'Erro inesperado ao gerar horários: {str(e)}')
                
            return redirect('core:gerar_horarios')
    else:
        form = GerarHorariosForm()
    
    # Dados para o template
    context = {
        'form': form,
        'total_disciplinas': Disciplina.objects.filter(ativa=True).count(),
        'total_salas': Sala.objects.filter(ativa=True).count(),
        'total_professores': Professor.objects.filter(ativo=True).count(),
        'total_turmas': Turma.objects.filter(ativa=True).count(),
    }
    
    return render(request, 'core/gerar_horarios.html', context)


# Views para visualização de horários
def visualizar_horario_turma(request, turma_id):
    """
    View para visualizar horário de uma turma específica.
    
    Args:
        request: Objeto HttpRequest do Django
        turma_id: ID da turma
        
    Returns:
        HttpResponse: Página com horário da turma
    """
    from collections import defaultdict
    
    turma = get_object_or_404(Turma, id=turma_id)
    horarios = Horario.objects.filter(turma=turma).order_by('dia_semana', 'horario_inicio')
    
    # Criar grade de horários
    grade_horarios = _criar_grade_horarios(horarios)
    
    # Resumos
    resumo_disciplinas = defaultdict(lambda: {'aulas_semana': 0})
    resumo_professores = defaultdict(lambda: {'aulas_semana': 0})
    
    for horario in horarios:
        resumo_disciplinas[horario.disciplina.nome]['aulas_semana'] += 1
        resumo_professores[horario.professor.nome_completo]['aulas_semana'] += 1
    
    context = {
        'turma': turma,
        'horarios': horarios,
        'grade_horarios': grade_horarios,
        'resumo_disciplinas': dict(resumo_disciplinas),
        'resumo_professores': dict(resumo_professores),
    }
    return render(request, 'core/horario_turma.html', context)


def visualizar_horario_professor(request, professor_id):
    """
    View para visualizar horário de um professor específico.
    
    Args:
        request: Objeto HttpRequest do Django
        professor_id: ID do professor
        
    Returns:
        HttpResponse: Página com horário do professor
    """
    from collections import defaultdict
    
    professor = get_object_or_404(Professor, id=professor_id)
    horarios = Horario.objects.filter(professor=professor).order_by('dia_semana', 'horario_inicio')
    
    # Criar grade de horários
    grade_horarios = _criar_grade_horarios(horarios)
    
    # Resumos
    resumo_turmas = defaultdict(lambda: {'aulas': 0})
    resumo_turnos = defaultdict(lambda: {'aulas': 0})
    resumo_dias = defaultdict(lambda: {'aulas': 0, 'nome': ''})
    
    dias_semana = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    for horario in horarios:
        resumo_turmas[horario.turma.nome_codigo]['aulas'] += 1
        resumo_turnos[horario.turno]['aulas'] += 1
        resumo_dias[horario.dia_semana]['aulas'] += 1
        resumo_dias[horario.dia_semana]['nome'] = dias_semana.get(horario.dia_semana, '')
    
    context = {
        'professor': professor,
        'horarios': horarios,
        'grade_horarios': grade_horarios,
        'resumo_turmas': dict(resumo_turmas),
        'resumo_turnos': dict(resumo_turnos),
        'resumo_dias': dict(resumo_dias),
    }
    return render(request, 'core/horario_professor.html', context)


def visualizar_horario_sala(request, sala_id):
    """
    View para visualizar horário de uma sala específica.
    
    Args:
        request: Objeto HttpRequest do Django
        sala_id: ID da sala
        
    Returns:
        HttpResponse: Página com horário da sala
    """
    from collections import defaultdict
    from datetime import time
    
    sala = get_object_or_404(Sala, id=sala_id)
    horarios = Horario.objects.filter(sala=sala).order_by('dia_semana', 'horario_inicio')
    
    # Criar grade de horários
    grade_horarios = _criar_grade_horarios(horarios)
    
    # Calcular taxa de ocupação
    total_slots = len(grade_horarios) * 5  # 5 dias da semana
    slots_ocupados = horarios.count()
    taxa_ocupacao = (slots_ocupados / total_slots * 100) if total_slots > 0 else 0
    
    # Resumos
    resumo_turmas = defaultdict(lambda: {'aulas': 0})
    resumo_disciplinas = defaultdict(lambda: {'aulas': 0})
    resumo_turnos = defaultdict(lambda: {'aulas': 0, 'percentual': 0})
    
    for horario in horarios:
        resumo_turmas[horario.turma.nome_codigo]['aulas'] += 1
        resumo_disciplinas[horario.disciplina.nome]['aulas'] += 1
        resumo_turnos[horario.turno]['aulas'] += 1
    
    # Calcular percentuais dos turnos
    total_aulas = horarios.count()
    for turno in resumo_turnos:
        if total_aulas > 0:
            resumo_turnos[turno]['percentual'] = (resumo_turnos[turno]['aulas'] / total_aulas * 100)
    
    # Encontrar maior turma que usa a sala
    maior_turma = None
    if horarios.exists():
        turmas_na_sala = Turma.objects.filter(horarios__sala=sala).distinct()
        maior_turma = turmas_na_sala.order_by('-numero_alunos').first()
    
    # Horários livres (simplificado)
    horarios_livres = _calcular_horarios_livres(sala, horarios)
    
    context = {
        'sala': sala,
        'horarios': horarios,
        'grade_horarios': grade_horarios,
        'taxa_ocupacao': taxa_ocupacao,
        'resumo_turmas': dict(resumo_turmas),
        'resumo_disciplinas': dict(resumo_disciplinas),
        'resumo_turnos': dict(resumo_turnos),
        'maior_turma': maior_turma,
        'horarios_livres': horarios_livres[:10],  # Primeiros 10
    }
    return render(request, 'core/horario_sala.html', context)


def _criar_grade_horarios(horarios):
    """
    Cria uma grade de horários organizada por slots de tempo.
    
    Args:
        horarios: QuerySet de horários
        
    Returns:
        list: Lista de slots organizados
    """
    from collections import defaultdict
    from datetime import time
    
    # Horários padrão
    slots_padrao = [
        (time(7, 0), time(7, 50)),
        (time(7, 50), time(8, 40)),
        (time(9, 0), time(9, 50)),
        (time(9, 50), time(10, 40)),
        (time(11, 0), time(11, 50)),
        (time(13, 0), time(13, 50)),
        (time(13, 50), time(14, 40)),
        (time(15, 0), time(15, 50)),
        (time(15, 50), time(16, 40)),
        (time(17, 0), time(17, 50)),
        (time(19, 0), time(19, 50)),
        (time(19, 50), time(20, 40)),
        (time(21, 0), time(21, 50)),
        (time(21, 50), time(22, 40)),
    ]
    
    # Organizar horários por slot e dia
    horarios_por_slot = defaultdict(lambda: defaultdict(lambda: None))
    
    for horario in horarios:
        key = (horario.horario_inicio, horario.horario_fim)
        horarios_por_slot[key][horario.dia_semana] = horario
    
    # Cores para diferentes disciplinas
    cores_disciplinas = {
        'Matemática': '#e3f2fd',
        'Português': '#f3e5f5',
        'História': '#e8f5e8',
        'Geografia': '#fff3e0',
        'Ciências': '#fce4ec',
        'Física': '#e0f2f1',
        'Química': '#f1f8e9',
        'Biologia': '#e8eaf6',
    }
    
    # Construir grade
    grade = []
    for inicio, fim in slots_padrao:
        slot_key = (inicio, fim)
        if slot_key in horarios_por_slot:
            dias = []
            for dia in range(5):  # Segunda a Sexta
                horario = horarios_por_slot[slot_key][dia]
                cor = cores_disciplinas.get(
                    horario.disciplina.nome if horario else None, 
                    '#f8f9fa'
                )
                dias.append({
                    'horario': horario,
                    'cor': cor
                })
            
            grade.append({
                'horario_inicio': inicio,
                'horario_fim': fim,
                'dias': dias
            })
    
    return grade


def _calcular_horarios_livres(sala, horarios_ocupados):
    """
    Calcula horários livres para uma sala.
    
    Args:
        sala: Sala para calcular
        horarios_ocupados: Horários já ocupados
        
    Returns:
        list: Lista de horários livres
    """
    from datetime import time
    
    slots_padrao = [
        (time(7, 0), time(7, 50)),
        (time(7, 50), time(8, 40)),
        (time(9, 0), time(9, 50)),
        (time(9, 50), time(10, 40)),
        (time(11, 0), time(11, 50)),
        (time(13, 0), time(13, 50)),
        (time(13, 50), time(14, 40)),
        (time(15, 0), time(15, 50)),
        (time(15, 50), time(16, 40)),
        (time(17, 0), time(17, 50)),
    ]
    
    dias_semana = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira'
    }
    
    # Criar set de horários ocupados
    ocupados = set()
    for horario in horarios_ocupados:
        ocupados.add((horario.dia_semana, horario.horario_inicio, horario.horario_fim))
    
    # Encontrar horários livres
    livres = []
    for dia in range(5):  # Segunda a Sexta
        for inicio, fim in slots_padrao:
            if (dia, inicio, fim) not in ocupados:
                livres.append({
                    'dia': dia,
                    'dia_nome': dias_semana[dia],
                    'horario_inicio': inicio,
                    'horario_fim': fim
                })
    
    return livres


# Views para Bloqueios Temporários
class BloqueioTemporarioListView(ListView):
    """View para listagem de bloqueios temporários com filtros."""
    model = BloqueioTemporario
    template_name = 'core/bloqueio_list.html'
    context_object_name = 'bloqueios'
    paginate_by = 15
    
    def get_queryset(self):
        """Filtra bloqueios por professor, tipo ou período."""
        queryset = BloqueioTemporario.objects.select_related('professor').order_by('-data_inicio')
        
        # Filtro por professor
        professor_id = self.request.GET.get('professor')
        if professor_id:
            queryset = queryset.filter(professor_id=professor_id)
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_bloqueio=tipo)
        
        # Filtro por status (ativo/inativo)
        ativo = self.request.GET.get('ativo')
        if ativo:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        # Filtro por período
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio:
            queryset = queryset.filter(data_fim__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_inicio__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['professores'] = Professor.objects.filter(ativo=True).order_by('nome_completo')
        context['tipos_bloqueio'] = BloqueioTemporario.TIPOS_BLOQUEIO
        return context


class BloqueioTemporarioDetailView(DetailView):
    """View para detalhes de um bloqueio temporário."""
    model = BloqueioTemporario
    template_name = 'core/bloqueio_detail.html'
    context_object_name = 'bloqueio'


class BloqueioTemporarioCreateView(CreateView):
    """View para criação de bloqueios temporários."""
    model = BloqueioTemporario
    form_class = BloqueioTemporarioForm
    template_name = 'core/bloqueio_form.html'
    success_url = reverse_lazy('core:bloqueio_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bloqueio temporário criado com sucesso!')
        return super().form_valid(form)
    
    def get_initial(self):
        """Define valores iniciais baseados nos parâmetros da URL."""
        initial = super().get_initial()
        
        # Se professor foi especificado na URL
        professor_id = self.request.GET.get('professor')
        if professor_id:
            try:
                professor = Professor.objects.get(id=professor_id)
                initial['professor'] = professor
            except Professor.DoesNotExist:
                pass
        
        return initial


class BloqueioTemporarioUpdateView(UpdateView):
    """View para edição de bloqueios temporários."""
    model = BloqueioTemporario
    form_class = BloqueioTemporarioForm
    template_name = 'core/bloqueio_form.html'
    success_url = reverse_lazy('core:bloqueio_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bloqueio temporário atualizado com sucesso!')
        return super().form_valid(form)


class BloqueioTemporarioDeleteView(DeleteView):
    """View para exclusão de bloqueios temporários."""
    model = BloqueioTemporario
    template_name = 'core/bloqueio_confirm_delete.html'
    success_url = reverse_lazy('core:bloqueio_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Bloqueio temporário removido com sucesso!')
        return super().delete(request, *args, **kwargs)


def professor_bloqueios_calendario(request, professor_id):
    """
    View para exibir bloqueios de um professor em formato de calendário.
    """
    professor = get_object_or_404(Professor, id=professor_id)
    
    # Obter bloqueios do professor
    from datetime import datetime, timedelta
    hoje = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    bloqueios = professor.bloqueios.filter(
        ativo=True,
        data_fim__gte=inicio_mes,
        data_inicio__lte=fim_mes
    ).order_by('data_inicio')
    
    # Preparar dados para o calendário
    bloqueios_calendario = []
    for bloqueio in bloqueios:
        bloqueios_calendario.append({
            'id': bloqueio.id,
            'title': f"{bloqueio.get_tipo_bloqueio_display()}" + (f" - {bloqueio.get_turno_display()}" if bloqueio.turno else ""),
            'start': bloqueio.data_inicio.isoformat(),
            'end': (bloqueio.data_fim + timedelta(days=1)).isoformat(),
            'color': '#dc3545' if bloqueio.tipo_bloqueio == 'falta' else '#6c757d',
            'description': bloqueio.motivo
        })
    
    context = {
        'professor': professor,
        'bloqueios_json': bloqueios_calendario,
        'mes_atual': inicio_mes,
    }
    
    return render(request, 'core/professor_bloqueios_calendario.html', context)


def verificar_disponibilidade_professor(request):
    """
    View AJAX para verificar disponibilidade de professores em tempo real.
    """
    if request.method == 'GET':
        from datetime import datetime
        
        professor_id = request.GET.get('professor_id')
        data_str = request.GET.get('data')
        turno = request.GET.get('turno', '')
        
        if not professor_id or not data_str:
            return JsonResponse({'erro': 'Parâmetros insuficientes'}, status=400)
        
        try:
            professor = Professor.objects.get(id=professor_id)
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            dia_semana = data.weekday()
            
            # Verificar disponibilidade
            disponivel = professor.disponivel_para_horario(
                dia_semana=dia_semana,
                turno=turno if turno else None,
                data_especifica=data
            )
            
            # Buscar bloqueios ativos na data
            bloqueios_data = professor.get_bloqueios_ativos(data, data)
            bloqueios_info = []
            
            for bloqueio in bloqueios_data:
                if bloqueio.professor_disponivel_na_data(data, turno if turno else None) == False:
                    bloqueios_info.append({
                        'tipo': bloqueio.get_tipo_bloqueio_display(),
                        'motivo': bloqueio.motivo,
                        'turno': bloqueio.get_turno_display() if bloqueio.turno else 'Dia todo'
                    })
            
            return JsonResponse({
                'disponivel': disponivel,
                'bloqueios': bloqueios_info,
                'professor_nome': professor.nome_completo
            })
            
        except (Professor.DoesNotExist, ValueError) as e:
            return JsonResponse({'erro': str(e)}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def mover_horario(request):
    """
    View AJAX para mover um horário para uma nova posição.
    
    Permite arrastar e soltar horários na interface, alterando
    dia da semana e/ou horário do mesmo.
    """
    if request.method == 'POST':
        try:
            import json
            
            data = json.loads(request.body)
            
            horario_id = data.get('horario_id')
            novo_dia = data.get('novo_dia')
            novo_inicio = data.get('novo_inicio')
            novo_fim = data.get('novo_fim')
            
            # Validar dados
            if not all([horario_id, novo_dia, novo_inicio, novo_fim]):
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'Dados incompletos'
                }, status=400)
            
            # Buscar horário
            horario = get_object_or_404(Horario, id=horario_id)
            
            # Converter dados
            from datetime import datetime
            novo_dia = int(novo_dia)
            novo_inicio_time = datetime.strptime(novo_inicio, '%H:%M').time()
            novo_fim_time = datetime.strptime(novo_fim, '%H:%M').time()
            
            # Verificar se a nova posição já está ocupada (conflito de horário exato)
            conflitos_exatos = Horario.objects.filter(
                dia_semana=novo_dia,
                horario_inicio=novo_inicio_time,
                horario_fim=novo_fim_time
            ).exclude(id=horario_id)
            
            # Verificar conflitos de professor no mesmo horário
            conflitos_professor = conflitos_exatos.filter(professor=horario.professor)
            if conflitos_professor.exists():
                return JsonResponse({
                    'sucesso': False,
                    'erro': f'Professor {horario.professor.nome_completo} já tem aula nesse horário'
                }, status=400)
            
            # Verificar conflitos de sala no mesmo horário
            conflitos_sala = conflitos_exatos.filter(sala=horario.sala)
            if conflitos_sala.exists():
                return JsonResponse({
                    'sucesso': False,
                    'erro': f'Sala {horario.sala.nome_numero} já está ocupada nesse horário'
                }, status=400)
            
            # Verificar conflitos de turma no mesmo horário
            conflitos_turma = conflitos_exatos.filter(turma=horario.turma)
            if conflitos_turma.exists():
                return JsonResponse({
                    'sucesso': False,
                    'erro': f'Turma {horario.turma.nome_codigo} já tem aula nesse horário'
                }, status=400)
            
            # Determinar turno baseado no horário
            turno = 'M' if novo_inicio_time.hour < 12 else ('T' if novo_inicio_time.hour < 18 else 'N')
            
            # Atualizar horário
            horario.dia_semana = novo_dia
            horario.horario_inicio = novo_inicio_time
            horario.horario_fim = novo_fim_time
            horario.turno = turno
            
            # Salvar
            horario.save()
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': f'Horário movido com sucesso para {horario.get_dia_semana_display()} às {novo_inicio}'
            })
            
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro ao mover horário: {str(e)}'
            }, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def horario_grade_view(request):
    """
    View para exibir horários em formato de grade com drag & drop.
    
    Mostra uma grade semanal onde os horários podem ser movidos
    através de arrastar e soltar.
    """
    import json
    
    # Buscar todos os horários
    horarios = Horario.objects.all().select_related(
        'turma', 'disciplina', 'professor', 'sala'
    ).order_by('dia_semana', 'horario_inicio')
    
    # Definir slots de horário disponíveis
    slots_horario = [
        ('07:00', '07:50'),
        ('07:50', '08:40'),
        ('08:40', '09:30'),
        ('09:50', '10:40'),  # Intervalo 09:30-09:50
        ('10:40', '11:30'),
        ('11:30', '12:20'),
        ('13:00', '13:50'),  # Tarde
        ('13:50', '14:40'),
        ('15:10', '16:00'),  # Intervalo 14:50-15:10
        ('16:00', '16:50'),
        ('16:50', '17:40'),
    ]
    
    # Dias da semana
    dias_semana = [
        (1, 'Segunda'),
        (2, 'Terça'),
        (3, 'Quarta'),
        (4, 'Quinta'),
        (5, 'Sexta'),
    ]
    
    # Serializar horários para JSON
    horarios_json = []
    for horario in horarios:
        horarios_json.append({
            'id': horario.id,
            'dia_semana': horario.dia_semana,
            'horario_inicio': horario.horario_inicio.strftime('%H:%M'),
            'horario_fim': horario.horario_fim.strftime('%H:%M'),
            'professor': {
                'id': horario.professor.id,
                'nome': horario.professor.nome_completo
            },
            'disciplina': horario.disciplina.nome,
            'turma': {
                'id': horario.turma.id,
                'codigo': horario.turma.nome_codigo
            },
            'sala': {
                'id': horario.sala.id,
                'numero': horario.sala.nome_numero
            }
        })
    
    context = {
        'slots_horario': slots_horario,
        'dias_semana': dias_semana,
        'horarios_json': json.dumps(horarios_json),
    }
    
    return render(request, 'core/horario_grade.html', context)


def notificacoes_view(request):
    """
    View para a página de notificações do sistema.
    
    Args:
        request: Objeto HttpRequest do Django
        
    Returns:
        HttpResponse: Página de notificações
    """
    return render(request, 'core/notificacoes.html')


def api_notificacoes(request):
    """
    API para gerenciar notificações do usuário.
    
    GET: Lista notificações não lidas
    POST: Marca notificação como lida
    """
    from datetime import datetime, timedelta
    
    if request.method == 'GET':
        # Gerar notificações dinâmicas baseadas no estado do sistema
        notificacoes_data = []
        
        # Verificar conflitos de horário
        conflitos_horario = []
        horarios = Horario.objects.select_related('professor', 'sala', 'turma')
        
        for horario in horarios:
            # Conflitos de professor
            conflitos_professor = Horario.objects.filter(
                professor=horario.professor,
                dia_semana=horario.dia_semana,
                horario_inicio=horario.horario_inicio
            ).exclude(id=horario.id)
            
            if conflitos_professor.exists():
                conflito = conflitos_professor.first()
                conflitos_horario.append({
                    'tipo': 'professor',
                    'descricao': f'Professor {horario.professor.nome_completo} tem conflito de horário',
                    'detalhes': f'Turmas {horario.turma.nome_codigo} e {conflito.turma.nome_codigo}'
                })
        
        # Adicionar notificações de conflitos
        for i, conflito in enumerate(conflitos_horario[:5]):  # Máximo 5 conflitos
            notificacoes_data.append({
                'id': f'conflito_{i}',
                'titulo': 'Conflito de Horário Detectado',
                'mensagem': conflito['descricao'],
                'tipo': 'erro',
                'prioridade': 'alta',
                'data_criacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'link_acao': '/core/horarios/',
                'lida': False
            })
        
        # Verificar problemas de capacidade
        horarios_capacidade = Horario.objects.select_related('sala', 'turma')
        for horario in horarios_capacidade:
            if horario.sala.capacidade < horario.turma.numero_alunos:
                notificacoes_data.append({
                    'id': f'capacidade_{horario.id}',
                    'titulo': 'Problema de Capacidade',
                    'mensagem': f'Sala {horario.sala.nome_numero} (cap. {horario.sala.capacidade}) insuficiente para turma {horario.turma.nome_codigo} ({horario.turma.numero_alunos} alunos)',
                    'tipo': 'aviso',
                    'prioridade': 'media',
                    'data_criacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'link_acao': f'/core/horarios/{horario.id}/edit/',
                    'lida': False
                })
        
        # Verificar professores sem horários
        professores_sem_horarios = Professor.objects.filter(
            ativo=True
        ).exclude(horarios__isnull=False).distinct()
        
        for professor in professores_sem_horarios:
            notificacoes_data.append({
                'id': f'prof_sem_horario_{professor.id}',
                'titulo': 'Professor sem Horários',
                'mensagem': f'Professor {professor.nome_completo} não possui horários atribuídos',
                'tipo': 'aviso',
                'prioridade': 'baixa',
                'data_criacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'link_acao': f'/core/professores/{professor.id}/',
                'lida': False
            })
        
        # Verificar salas sub-utilizadas
        salas_subutilizadas = []
        for sala in Sala.objects.filter(ativa=True):
            total_horarios = Horario.objects.filter(sala=sala).count()
            if total_horarios < 5:  # Menos de 5 horários por semana
                salas_subutilizadas.append(sala)
        
        for sala in salas_subutilizadas[:3]:  # Máximo 3
            notificacoes_data.append({
                'id': f'sala_subutilizada_{sala.id}',
                'titulo': 'Sala Sub-utilizada',
                'mensagem': f'Sala {sala.nome_numero} tem baixa ocupação ({Horario.objects.filter(sala=sala).count()} horários)',
                'tipo': 'info',
                'prioridade': 'baixa',
                'data_criacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'link_acao': f'/core/salas/{sala.id}/',
                'lida': False
            })
        
        # Adicionar notificação de boas-vindas se não houver outras
        if not notificacoes_data:
            notificacoes_data.append({
                'id': 'boas_vindas',
                'titulo': 'Sistema Funcionando Corretamente',
                'mensagem': 'Bem-vindo ao sistema de horários! Tudo está funcionando corretamente.',
                'tipo': 'sucesso',
                'prioridade': 'baixa',
                'data_criacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'link_acao': None,
                'lida': False
            })
        
        # Limitar número total de notificações
        notificacoes_data = notificacoes_data[:10]
        
        return JsonResponse({
            'notificacoes': notificacoes_data,
            'total': len(notificacoes_data),
            'nao_lidas': len([n for n in notificacoes_data if not n.get('lida', False)])
        })
    
    elif request.method == 'POST':
        # Simular marcar como lida
        import json
        try:
            data = json.loads(request.body)
            notificacao_id = data.get('notificacao_id')
            
            if not notificacao_id:
                return JsonResponse({'erro': 'ID da notificação não fornecido'}, status=400)
            
            # Em uma implementação real, aqui salvaria no banco de dados
            # Por enquanto apenas simular sucesso
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Notificação marcada como lida'
            })
        except json.JSONDecodeError:
            return JsonResponse({'erro': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'erro': f'Erro interno: {str(e)}'}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def relatorio_carga_horaria(request):
    """
    View para relatório detalhado de carga horária.
    """
    from datetime import datetime
    
    # Relatório básico sem depender do dashboard complexo
    professores = Professor.objects.filter(ativo=True)
    salas = Sala.objects.filter(ativa=True)
    turmas = Turma.objects.filter(ativa=True)
    
    relatorio_professores = []
    for professor in professores:
        total_horarios = Horario.objects.filter(professor=professor).count()
        total_turmas_prof = Horario.objects.filter(professor=professor).values('turma').distinct().count()
        total_disciplinas = Horario.objects.filter(professor=professor).values('disciplina').distinct().count()
        
        relatorio_professores.append({
            'professor': professor,
            'total_horarios': total_horarios,
            'total_turmas': total_turmas_prof,
            'total_disciplinas': total_disciplinas,
            'carga_semanal': total_horarios,
            'percentual_carga': min(100, (total_horarios / 25) * 100),
            'status': 'completo' if total_horarios >= 20 else 'incompleto',
            'status_color': 'success' if total_horarios >= 20 else 'warning'
        })
    
    relatorio_salas = []
    for sala in salas:
        total_horarios = Horario.objects.filter(sala=sala).count()
        total_turmas_sala = Horario.objects.filter(sala=sala).values('turma').distinct().count()
        taxa_ocupacao = min(100, (total_horarios / 25) * 100)
        
        relatorio_salas.append({
            'sala': sala,
            'total_horarios': total_horarios,
            'total_turmas': total_turmas_sala,
            'taxa_ocupacao': taxa_ocupacao,
            'horas_utilizadas': total_horarios,
            'horas_disponiveis': 25,
            'status': 'alta' if taxa_ocupacao > 80 else 'media' if taxa_ocupacao > 50 else 'baixa'
        })
    
    relatorio_turmas = []
    for turma in turmas:
        total_horarios = Horario.objects.filter(turma=turma).count()
        total_professores = Horario.objects.filter(turma=turma).values('professor').distinct().count()
        total_disciplinas = Horario.objects.filter(turma=turma).values('disciplina').distinct().count()
        
        relatorio_turmas.append({
            'turma': turma,
            'total_disciplinas': total_disciplinas,
            'total_professores': total_professores,
            'carga_semanal': total_horarios,
            'percentual_completude': min(100, (total_horarios / 25) * 100),
            'status_label': 'Completo' if total_horarios >= 20 else 'Incompleto',
            'status_color': 'success' if total_horarios >= 20 else 'warning',
            'conflitos': 0
        })
    
    relatorio_disciplinas = []
    disciplinas = Disciplina.objects.filter(ativa=True)
    for disciplina in disciplinas:
        total_horarios = Horario.objects.filter(disciplina=disciplina).count()
        total_professores = Horario.objects.filter(disciplina=disciplina).values('professor').distinct().count()
        total_turmas_disc = Horario.objects.filter(disciplina=disciplina).values('turma').distinct().count()
        
        relatorio_disciplinas.append({
            'disciplina': disciplina,
            'total_professores': total_professores,
            'total_turmas': total_turmas_disc,
            'total_horarios': total_horarios,
            'carga_total': total_horarios,
            'distribuicao': {
                'manha': Horario.objects.filter(disciplina=disciplina, turno='M').count(),
                'tarde': Horario.objects.filter(disciplina=disciplina, turno='T').count(),
                'noite': Horario.objects.filter(disciplina=disciplina, turno='N').count(),
            }
        })
    
    # Resumo geral
    resumo = {
        'total_professores': professores.count(),
        'total_horarios': Horario.objects.count(),
        'carga_total': Horario.objects.count(),
        'media_carga': Horario.objects.count() / max(1, professores.count()),
        'taxa_ocupacao': 75
    }
    
    context = {
        'relatorio': {
            'professores': relatorio_professores,
            'salas': relatorio_salas,
            'turmas': relatorio_turmas,
            'disciplinas': relatorio_disciplinas,
            'resumo': resumo
        },
        'data_geracao': datetime.now(),
        'periodos': [],
        'professores': professores,
    }
    
    return render(request, 'core/relatorio_carga_horaria.html', context)


def verificar_integridade_dados(request):
    """
    View para verificar a integridade dos dados do sistema.
    """
    from django.core.exceptions import ValidationError
    from datetime import datetime
    import time
    
    inicio = time.time()
    
    conflitos_horario = []
    inconsistencias = []
    validacoes_negocio = []
    alertas_performance = []
    
    # Verificar conflitos de horário básicos
    horarios = Horario.objects.select_related('professor', 'sala', 'turma', 'disciplina')
    
    # Conflitos de professor (mesmo professor, mesmo horário)
    for horario in horarios:
        conflitos_professor = Horario.objects.filter(
            professor=horario.professor,
            dia_semana=horario.dia_semana,
            horario_inicio=horario.horario_inicio,
            horario_fim=horario.horario_fim
        ).exclude(id=horario.id)
        
        if conflitos_professor.exists():
            conflito = conflitos_professor.first()
            conflitos_horario.append({
                'id': f'prof_{horario.id}_{conflito.id}',
                'tipo_display': 'Conflito de Professor',
                'descricao': f'Professor {horario.professor.nome_completo} tem aulas simultâneas',
                'horario1': f'{horario.turma.nome_codigo} - {horario.disciplina.nome}',
                'horario2': f'{conflito.turma.nome_codigo} - {conflito.disciplina.nome}'
            })
    
    # Conflitos de sala (mesma sala, mesmo horário)
    for horario in horarios:
        conflitos_sala = Horario.objects.filter(
            sala=horario.sala,
            dia_semana=horario.dia_semana,
            horario_inicio=horario.horario_inicio,
            horario_fim=horario.horario_fim
        ).exclude(id=horario.id)
        
        if conflitos_sala.exists():
            conflito = conflitos_sala.first()
            conflitos_horario.append({
                'id': f'sala_{horario.id}_{conflito.id}',
                'tipo_display': 'Conflito de Sala',
                'descricao': f'Sala {horario.sala.nome_numero} ocupada por duas turmas',
                'horario1': f'{horario.turma.nome_codigo} - {horario.disciplina.nome}',
                'horario2': f'{conflito.turma.nome_codigo} - {conflito.disciplina.nome}'
            })
    
    # Conflitos de turma (mesma turma, mesmo horário)
    for horario in horarios:
        conflitos_turma = Horario.objects.filter(
            turma=horario.turma,
            dia_semana=horario.dia_semana,
            horario_inicio=horario.horario_inicio,
            horario_fim=horario.horario_fim
        ).exclude(id=horario.id)
        
        if conflitos_turma.exists():
            conflito = conflitos_turma.first()
            conflitos_horario.append({
                'id': f'turma_{horario.id}_{conflito.id}',
                'tipo_display': 'Conflito de Turma',
                'descricao': f'Turma {horario.turma.nome_codigo} tem aulas simultâneas',
                'horario1': f'{horario.disciplina.nome} com {horario.professor.nome_completo}',
                'horario2': f'{conflito.disciplina.nome} com {conflito.professor.nome_completo}'
            })
    
    # Verificar inconsistências básicas
    # Professores sem disciplinas
    professores_sem_disciplinas = Professor.objects.filter(
        ativo=True,
        disciplinas__isnull=True
    )
    for professor in professores_sem_disciplinas:
        inconsistencias.append({
            'id': f'prof_sem_disc_{professor.id}',
            'tipo_display': 'Professor sem Disciplinas',
            'descricao': f'Professor {professor.nome_completo} não tem disciplinas associadas',
            'detalhes': 'Professor ativo deve ter ao menos uma disciplina'
        })
    
    # Turmas sem disciplinas
    turmas_sem_disciplinas = Turma.objects.filter(
        ativa=True,
        disciplinas__isnull=True
    )
    for turma in turmas_sem_disciplinas:
        inconsistencias.append({
            'id': f'turma_sem_disc_{turma.id}',
            'tipo_display': 'Turma sem Disciplinas',
            'descricao': f'Turma {turma.nome_codigo} não tem disciplinas associadas',
            'detalhes': 'Turma ativa deve ter disciplinas definidas'
        })
    
    # Verificar capacidade das salas
    for horario in horarios:
        if horario.sala.capacidade < horario.turma.numero_alunos:
            validacoes_negocio.append({
                'regra': 'Capacidade de Sala',
                'descricao': f'Sala {horario.sala.nome_numero} (cap. {horario.sala.capacidade}) alocada para turma {horario.turma.nome_codigo} ({horario.turma.numero_alunos} alunos)',
                'sugestao': 'Realocar para sala com maior capacidade'
            })
    
    # Alertas de performance
    total_horarios = horarios.count()
    if total_horarios > 1000:
        alertas_performance.append({
            'area': 'Volume de Dados',
            'descricao': f'Sistema tem {total_horarios} horários cadastrados',
            'otimizacao': 'Considere arquivar horários antigos'
        })
    
    # Calcular métricas
    fim = time.time()
    tempo_execucao = int((fim - inicio) * 1000)
    
    totais_criticos = len(conflitos_horario)
    totais_avisos = len(inconsistencias) + len(validacoes_negocio)
    total_verificacoes = totais_criticos + totais_avisos + len(alertas_performance)
    verificacoes_ok = total_verificacoes - totais_criticos - totais_avisos
    
    status_geral = 'CRITICO' if totais_criticos > 0 else 'AVISO' if totais_avisos > 0 else 'OK'
    
    # Estatísticas do sistema
    estatisticas = {
        'horarios_total': total_horarios,
        'professores_ativos': Professor.objects.filter(ativo=True).count(),
        'salas_utilizadas': Horario.objects.values('sala').distinct().count(),
        'turmas_ativas': Turma.objects.filter(ativa=True).count(),
        'taxa_ocupacao': 75,  # Simulado
        'carga_media': round(total_horarios / max(1, Professor.objects.filter(ativo=True).count()), 1),
        'eficiencia_alocacao': 85,  # Simulado
    }
    
    resultado = {
        'status_geral': status_geral,
        'totais': {
            'criticos': totais_criticos,
            'avisos': totais_avisos,
            'verificacoes_ok': verificacoes_ok,
            'total_verificacoes': total_verificacoes,
        },
        'conflitos_horario': conflitos_horario[:10],  # Limitar para performance
        'inconsistencias': inconsistencias[:10],
        'validacoes_negocio': validacoes_negocio[:10],
        'alertas_performance': alertas_performance,
        'estatisticas': estatisticas,
        'timestamp': datetime.now(),
        'tempo_execucao': tempo_execucao,
    }
    
    context = {
        'resultado': resultado,
    }
    
    return render(request, 'core/verificar_integridade.html', context)

