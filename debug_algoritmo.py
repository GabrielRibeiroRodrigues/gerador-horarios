#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor
from core.algoritmo_horarios import GeradorHorariosRobusto

print("🔍 DEBUG - VERIFICAÇÃO DETALHADA DO ALGORITMO")
print("=" * 60)

# Buscar Paulo
paulo = Professor.objects.get(nome_completo='Paulo')
print(f"👨‍🏫 Professor: {paulo.nome_completo}")

# Verificar preferências
prefs = PreferenciaProfessor.objects.filter(professor=paulo)
print(f"\n📋 Preferências do Paulo ({prefs.count()} registros):")
dias_nomes = {1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta'}
for pref in prefs:
    status = "DISPONÍVEL" if pref.disponivel else "INDISPONÍVEL"
    turno_info = f" | Turno: {pref.turno}" if pref.turno else " | Todos os turnos"
    disciplina_info = f" | Disciplina: {pref.disciplina}" if pref.disciplina else " | Todas as disciplinas"
    print(f"   {dias_nomes[pref.dia_semana]}: {status}{turno_info}{disciplina_info}")

# Testar o método _professor_disponivel diretamente
print(f"\n🧪 TESTE DIRETO DO MÉTODO _professor_disponivel:")
gerador = GeradorHorariosRobusto()

# Testar cada dia da semana
for dia in [1, 2, 3, 4, 5]:
    dia_nome = dias_nomes[dia]
    disponivel = gerador._professor_disponivel(paulo, dia, 'tarde', None)
    status_icon = "✅" if disponivel else "❌"
    print(f"   {dia_nome} (dia {dia}): {status_icon} {disponivel}")

print(f"\n⚠️ NOTA: O algoritmo usa dias 1-5 (Segunda-Sexta)")
print(f"   Preferências cadastradas: {[p.dia_semana for p in prefs]}")
print(f"   Deveria retornar False para dias 1, 2, 3 (Segunda, Terça, Quarta)")
