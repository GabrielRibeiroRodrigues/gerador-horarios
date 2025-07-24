#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Horario
import json

print("🔍 TESTE FUNCIONALIDADE MOVER HORÁRIOS")
print("=" * 60)

# Verificar horários existentes
horarios = Horario.objects.all()
print(f"📊 Total de horários: {horarios.count()}")

if horarios.exists():
    h = horarios.first()
    print(f"\n📋 Exemplo de horário:")
    print(f"   ID: {h.id}")
    print(f"   Professor: {h.professor.nome_completo}")
    print(f"   Dia: {h.dia_semana}")
    print(f"   Horário: {h.horario_inicio} - {h.horario_fim}")
    print(f"   Disciplina: {h.disciplina.nome}")
    
    # Simular dados JSON como enviados pelo frontend
    dados_json = {
        'horario_id': h.id,
        'novo_dia': 5,  # Sexta-feira
        'novo_inicio': '15:10',
        'novo_fim': '16:00'
    }
    
    print(f"\n🧪 SIMULANDO MOVIMENTAÇÃO:")
    print(f"   Mover para: Sexta-feira, 15:10-16:00")
    
    # Verificar se existe conflito
    from datetime import datetime
    novo_inicio_time = datetime.strptime('15:10', '%H:%M').time()
    novo_fim_time = datetime.strptime('16:00', '%H:%M').time()
    
    conflitos_exatos = Horario.objects.filter(
        dia_semana=5,
        horario_inicio=novo_inicio_time,
        horario_fim=novo_fim_time
    ).exclude(id=h.id)
    
    print(f"   Conflitos encontrados: {conflitos_exatos.count()}")
    
    if conflitos_exatos.exists():
        for c in conflitos_exatos:
            print(f"     - {c.professor.nome_completo}: {c.disciplina.nome}")
    else:
        print(f"   ✅ Nenhum conflito! Movimento seria permitido.")

else:
    print("❌ Nenhum horário encontrado! Execute a geração de horários primeiro.")

print("\n" + "=" * 60)
