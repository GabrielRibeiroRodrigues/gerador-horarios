#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, Disciplina, Sala, Horario
from core.algoritmo_horarios import GeradorHorariosRobusto

print("🧪 TESTE RÁPIDO - VERIFICAÇÃO PAULO")
print("=" * 50)

# Limpar horários existentes
Horario.objects.all().delete()
print("🗑️ Horários limpos")

# Gerar novos horários
gerador = GeradorHorariosRobusto()
resultado = gerador.gerar_horarios()

print(f"✅ Resultado: {resultado['sucesso']}")
print(f"📊 Horários criados: {resultado['horarios_criados']}")

# Verificar horários do Paulo
horarios_paulo = Horario.objects.filter(professor__nome_completo='Paulo')
print(f"\n👨‍🏫 PAULO tem {horarios_paulo.count()} aulas:")

dias_nomes = {1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta'}
violacoes = 0

for h in horarios_paulo:
    dia_nome = dias_nomes[h.dia_semana]
    horario_str = f"{h.horario_inicio.strftime('%H:%M')} - {h.horario_fim.strftime('%H:%M')}"
    
    # Verificar se é violação (Segunda=1, Terça=2, Quarta=3)
    if h.dia_semana in [1, 2, 3]:
        print(f"❌ VIOLAÇÃO: {dia_nome} | {horario_str} | {h.disciplina.nome}")
        violacoes += 1
    else:
        print(f"✅ OK: {dia_nome} | {horario_str} | {h.disciplina.nome}")

print(f"\n📊 RESUMO:")
print(f"   Total de aulas do Paulo: {horarios_paulo.count()}")
print(f"   Violações encontradas: {violacoes}")

if violacoes == 0:
    print("🎉 SUCESSO! Paulo não tem aulas em Segunda, Terça ou Quarta!")
else:
    print("⚠️ PROBLEMA! Paulo ainda tem aulas em dias indisponíveis!")
