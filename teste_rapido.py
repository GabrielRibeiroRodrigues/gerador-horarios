#!/usr/bin/env python
"""
Teste rápido para verificar se Paulo pode ensinar ESW2 em quinta e sexta.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor, Disciplina, Horario

def teste_rapido():
    print("=== TESTE RÁPIDO - PAULO E ESW2 ===")
    
    # Buscar Paulo e ESW2
    paulo = Professor.objects.get(nome_completo="Paulo")
    esw2 = Disciplina.objects.get(nome="ESW2")
    
    print(f"Professor: {paulo.nome_completo}")
    print(f"Disciplina: {esw2.nome}")
    
    # Limpar horários existentes
    Horario.objects.all().delete()
    print("Horários limpos")
    
    # Testar disponibilidade diretamente
    dias = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta'}
    
    print("\n=== TESTE DE DISPONIBILIDADE ===")
    for dia in range(5):
        disponivel = paulo.disponivel_para_horario(dia_semana=dia, disciplina=esw2)
        status = "✅ DISPONÍVEL" if disponivel else "❌ INDISPONÍVEL"
        print(f"{dias[dia]}: {status}")
    
    # Criar horário manualmente para quinta-feira
    print("\n=== CRIANDO HORÁRIO MANUAL ===")
    from core.models import Sala, Turma
    from datetime import time
    
    # Buscar sala e turma
    sala = Sala.objects.first()
    turma = Turma.objects.first()
    
    if sala and turma:
        # Tentar criar horário na quinta (dia 3)
        try:
            horario_quinta = Horario.objects.create(
                turma=turma,
                disciplina=esw2,
                professor=paulo,
                sala=sala,
                dia_semana=3,  # Quinta
                turno='tarde',
                horario_inicio=time(13, 0),
                horario_fim=time(13, 50)
            )
            print(f"✅ Horário criado com sucesso: Quinta-feira, {horario_quinta.turno}")
        except Exception as e:
            print(f"❌ Erro ao criar horário: {e}")
        
        # Tentar criar horário na terça (dia 1) - deve dar erro
        try:
            horario_terca = Horario.objects.create(
                turma=turma,
                disciplina=esw2,
                professor=paulo,
                sala=sala,
                dia_semana=1,  # Terça
                turno='tarde',
                horario_inicio=time(13, 0),
                horario_fim=time(13, 50)
            )
            print(f"⚠️  Horário na terça foi criado (PROBLEMA!): {horario_terca.turno}")
        except Exception as e:
            print(f"✅ Corretamente bloqueado na terça: {e}")
    
    print("\n=== RESULTADO FINAL ===")
    horarios_paulo = Horario.objects.filter(professor=paulo)
    print(f"Paulo tem {horarios_paulo.count()} horários agendados:")
    
    for h in horarios_paulo:
        print(f"   {dias[h.dia_semana]} - {h.turno} - {h.disciplina.nome}")

if __name__ == "__main__":
    teste_rapido()
