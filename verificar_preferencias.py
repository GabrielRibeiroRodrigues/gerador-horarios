#!/usr/bin/env python
"""
Script para verificar as preferências e horários dos professores.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor, Horario

def main():
    print("=== Verificação de Preferências e Horários ===")
    
    # Verificar professor Paulo
    try:
        paulo = Professor.objects.get(nome_completo__icontains="Paulo")
        print(f"\nProfessor: {paulo.nome_completo}")
        
        # Verificar preferências
        prefs = PreferenciaProfessor.objects.filter(professor=paulo)
        print(f"\nPreferências do {paulo.nome_completo}:")
        for pref in prefs:
            print(f"  - {pref.get_dia_semana_display()}: Disponível={pref.disponivel}, Preferencial={pref.preferencial}")
        
        # Verificar horários existentes
        horarios_paulo = Horario.objects.filter(professor=paulo)
        print(f"\nHorários do {paulo.nome_completo} (total: {horarios_paulo.count()}):")
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for h in horarios_paulo.order_by('dia_semana', 'horario_inicio'):
            print(f"  - {dias[h.dia_semana]}: {h.disciplina.nome} às {h.horario_inicio} (Turno: {h.turno})")
        
        # Verificar disponibilidade para quarta-feira
        print(f"\nTeste de disponibilidade:")
        print(f"  - Quarta-feira manhã: {paulo.disponivel_para_horario(dia_semana=2, turno='manha')}")
        print(f"  - Quarta-feira tarde: {paulo.disponivel_para_horario(dia_semana=2, turno='tarde')}")
        print(f"  - Quarta-feira noite: {paulo.disponivel_para_horario(dia_semana=2, turno='noite')}")
        
        # Verificar horários na quarta-feira
        horarios_quarta = Horario.objects.filter(dia_semana=2)
        print(f"\nTodos os horários na quarta-feira (total: {horarios_quarta.count()}):")
        professores_quarta = {}
        for h in horarios_quarta:
            prof = h.professor.nome_completo
            if prof not in professores_quarta:
                professores_quarta[prof] = []
            professores_quarta[prof].append(f"{h.disciplina.nome} às {h.horario_inicio}")
        
        for prof, horarios in professores_quarta.items():
            print(f"  {prof}:")
            for horario in horarios:
                print(f"    - {horario}")
    
    except Professor.DoesNotExist:
        print("Professor Paulo não encontrado")
    
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
