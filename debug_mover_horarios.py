#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Horario, Professor
from core.algoritmo_horarios import GeradorHorariosRobusto

print("🔍 DEBUG - FUNCIONALIDADE MOVER HORÁRIOS")
print("=" * 60)

# Buscar alguns horários para testar
horarios = Horario.objects.all()[:3]
print(f"📊 Horários encontrados: {horarios.count()}")

for h in horarios:
    print(f"\nHorário ID {h.id}:")
    print(f"  Professor: {h.professor.nome_completo}")
    print(f"  Dia: {h.dia_semana} ({h.get_dia_semana_display()})")
    print(f"  Horário: {h.horario_inicio} - {h.horario_fim}")
    print(f"  Turno: {h.turno}")
    print(f"  Disciplina: {h.disciplina.nome}")
    print(f"  Turma: {h.turma.nome_codigo}")
    print(f"  Sala: {h.sala.nome_numero}")

# Testar a verificação de disponibilidade do professor
if horarios.exists():
    h = horarios.first()
    gerador = GeradorHorariosRobusto()
    
    print(f"\n🧪 TESTANDO VERIFICAÇÃO DE DISPONIBILIDADE:")
    print(f"Professor: {h.professor.nome_completo}")
    
    # Testar no mesmo dia e turno (deveria ser True)
    disponivel = gerador._professor_disponivel(h.professor, h.dia_semana, h.turno, h.disciplina)
    print(f"Mesmo dia/turno: {disponivel}")
    
    # Testar em outro dia
    outro_dia = 5 if h.dia_semana != 5 else 4
    disponivel_outro_dia = gerador._professor_disponivel(h.professor, outro_dia, 'tarde', h.disciplina)
    print(f"Outro dia ({outro_dia}): {disponivel_outro_dia}")

print("\n" + "=" * 60)
