"""
Configuração do Django Admin para o sistema de gerenciamento de horários escolares.
"""
from django.contrib import admin
from .models import Disciplina, Sala, Professor, Turma, PreferenciaProfessor, Horario


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Disciplina."""
    list_display = ['nome', 'curso_area', 'periodo_serie', 'carga_horaria_semanal', 'ativa']
    list_filter = ['curso_area', 'periodo_serie', 'ativa']
    search_fields = ['nome', 'curso_area']
    list_editable = ['ativa']


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Sala."""
    list_display = ['nome_numero', 'tipo', 'capacidade', 'ativa']
    list_filter = ['tipo', 'ativa']
    search_fields = ['nome_numero']
    list_editable = ['ativa']


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Professor."""
    list_display = ['nome_completo', 'especialidade', 'email', 'ativo']
    list_filter = ['ativo', 'especialidade', 'disciplinas']
    search_fields = ['nome_completo', 'email', 'especialidade']
    list_editable = ['ativo']
    filter_horizontal = ['disciplinas']


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Turma."""
    list_display = ['nome_codigo', 'serie_periodo', 'numero_alunos', 'ativa']
    list_filter = ['serie_periodo', 'ativa']
    search_fields = ['nome_codigo', 'serie_periodo']
    list_editable = ['ativa']
    filter_horizontal = ['disciplinas']


@admin.register(PreferenciaProfessor)
class PreferenciaProfessorAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo PreferenciaProfessor."""
    list_display = ['professor', 'disciplina', 'dia_semana', 'turno']
    list_filter = ['dia_semana', 'turno', 'disciplina']
    search_fields = ['professor__nome_completo', 'disciplina__nome']
    raw_id_fields = ['professor', 'disciplina']


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Horario."""
    list_display = ['turma', 'disciplina', 'professor', 'sala', 'dia_semana', 'turno', 'horario_inicio', 'horario_fim', 'ativo']
    list_filter = ['dia_semana', 'turno', 'ativo', 'disciplina', 'professor']
    search_fields = ['turma__nome_codigo', 'disciplina__nome', 'professor__nome_completo']
    list_editable = ['ativo']
