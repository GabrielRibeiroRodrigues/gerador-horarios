"""
URLs do app core para gerenciamento de horários escolares.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
    
    # URLs para Disciplinas
    path('disciplinas/', views.DisciplinaListView.as_view(), name='disciplina_list'),
    path('disciplinas/<int:pk>/', views.DisciplinaDetailView.as_view(), name='disciplina_detail'),
    path('disciplinas/nova/', views.DisciplinaCreateView.as_view(), name='disciplina_create'),
    path('disciplinas/<int:pk>/editar/', views.DisciplinaUpdateView.as_view(), name='disciplina_update'),
    path('disciplinas/<int:pk>/deletar/', views.DisciplinaDeleteView.as_view(), name='disciplina_delete'),
    
    # URLs para Salas
    path('salas/', views.SalaListView.as_view(), name='sala_list'),
    path('salas/<int:pk>/', views.SalaDetailView.as_view(), name='sala_detail'),
    path('salas/nova/', views.SalaCreateView.as_view(), name='sala_create'),
    path('salas/<int:pk>/editar/', views.SalaUpdateView.as_view(), name='sala_update'),
    path('salas/<int:pk>/deletar/', views.SalaDeleteView.as_view(), name='sala_delete'),
    
    # URLs para Professores
    path('professores/', views.ProfessorListView.as_view(), name='professor_list'),
    path('professores/<int:pk>/', views.ProfessorDetailView.as_view(), name='professor_detail'),
    path('professores/novo/', views.ProfessorCreateView.as_view(), name='professor_create'),
    path('professores/<int:pk>/editar/', views.ProfessorUpdateView.as_view(), name='professor_update'),
    path('professores/<int:pk>/deletar/', views.ProfessorDeleteView.as_view(), name='professor_delete'),
    
    # URLs para Turmas
    path('turmas/', views.TurmaListView.as_view(), name='turma_list'),
    path('turmas/<int:pk>/', views.TurmaDetailView.as_view(), name='turma_detail'),
    path('turmas/nova/', views.TurmaCreateView.as_view(), name='turma_create'),
    path('turmas/<int:pk>/editar/', views.TurmaUpdateView.as_view(), name='turma_update'),
    path('turmas/<int:pk>/deletar/', views.TurmaDeleteView.as_view(), name='turma_delete'),
    
    # URLs para Preferências de Professor
    path('preferencias/', views.PreferenciaProfessorListView.as_view(), name='preferencia_list'),
    path('preferencias/nova/', views.PreferenciaProfessorCreateView.as_view(), name='preferencia_create'),
    path('preferencias/<int:pk>/editar/', views.PreferenciaProfessorUpdateView.as_view(), name='preferencia_update'),
    path('preferencias/<int:pk>/deletar/', views.PreferenciaProfessorDeleteView.as_view(), name='preferencia_delete'),
    
    # URLs para Horários
    path('horarios/', views.HorarioListView.as_view(), name='horario_list'),
    path('horarios/novo/', views.HorarioCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/editar/', views.HorarioUpdateView.as_view(), name='horario_update'),
    path('horarios/<int:pk>/deletar/', views.HorarioDeleteView.as_view(), name='horario_delete'),
    
    # URLs para visualização de horários
    path('horario/turma/<int:turma_id>/', views.visualizar_horario_turma, name='horario_turma'),
    path('horario/professor/<int:professor_id>/', views.visualizar_horario_professor, name='horario_professor'),
    path('horario/sala/<int:sala_id>/', views.visualizar_horario_sala, name='horario_sala'),
    
    # URL para geração de horários
    path('gerar-horarios/', views.gerar_horarios, name='gerar_horarios'),
    
    # URLs para Bloqueios Temporários
    path('bloqueios/', views.BloqueioTemporarioListView.as_view(), name='bloqueio_list'),
    path('bloqueios/<int:pk>/', views.BloqueioTemporarioDetailView.as_view(), name='bloqueio_detail'),
    path('bloqueios/novo/', views.BloqueioTemporarioCreateView.as_view(), name='bloqueio_create'),
    path('bloqueios/<int:pk>/editar/', views.BloqueioTemporarioUpdateView.as_view(), name='bloqueio_update'),
    path('bloqueios/<int:pk>/deletar/', views.BloqueioTemporarioDeleteView.as_view(), name='bloqueio_delete'),
    
    # URLs especiais para bloqueios
    path('professor/<int:professor_id>/bloqueios/calendario/', views.professor_bloqueios_calendario, name='professor_bloqueios_calendario'),
    path('ajax/verificar-disponibilidade/', views.verificar_disponibilidade_professor, name='verificar_disponibilidade_professor'),
]

