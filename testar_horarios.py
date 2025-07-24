#!/usr/bin/env python
"""
Teste dos horários ajustados (tarde de 13h às 17h).
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.algoritmo_horarios import gerar_horarios_automaticamente
from core.models import Horario, Professor

def main():
    print("🕐 TESTANDO HORÁRIOS AJUSTADOS - TARDE DE 13H ÀS 17H")
    print("=" * 60)
    
    # Executar geração
    print("Gerando novos horários...")
    resultado = gerar_horarios_automaticamente(limpar_anteriores=True)
    
    print(f"\n📊 RESULTADO:")
    print(f"Sucesso: {'✅ SIM' if resultado['sucesso'] else '❌ NÃO'}")
    print(f"Horários criados: {resultado['horarios_criados']}")
    
    if resultado['sucesso']:
        print(f"\n📅 HORÁRIOS GERADOS:")
        horarios = Horario.objects.all().order_by('dia_semana', 'horario_inicio')
        
        dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        
        for h in horarios:
            dia_nome = dias_nomes[h.dia_semana]
            horario_str = f"{h.horario_inicio.strftime('%H:%M')} - {h.horario_fim.strftime('%H:%M')}"
            print(f"   {dia_nome} | {horario_str} | {h.turno.upper()} | {h.professor.nome_completo} | {h.disciplina.nome} | Sala {h.sala.nome}")
        
        # Verificar especificamente os horários da tarde
        horarios_tarde = horarios.filter(turno='tarde')
        print(f"\n🌅 HORÁRIOS DA TARDE ({horarios_tarde.count()} aulas):")
        
        for h in horarios_tarde:
            dia_nome = dias_nomes[h.dia_semana]
            horario_str = f"{h.horario_inicio.strftime('%H:%M')} - {h.horario_fim.strftime('%H:%M')}"
            print(f"   {dia_nome} | {horario_str} | {h.professor.nome_completo} | {h.disciplina.nome}")
            
            # Verificar se está dentro do intervalo 13h-17h
            if h.horario_inicio.hour < 13 or h.horario_fim.hour > 17:
                print(f"   ⚠️  ATENÇÃO: Horário fora do intervalo 13h-17h!")
        
        # Verificar Paulo especificamente
        print(f"\n👨‍🏫 HORÁRIOS DO PAULO:")
        try:
            paulo = Professor.objects.get(nome_completo="Paulo")
            horarios_paulo = horarios.filter(professor=paulo)
            
            if horarios_paulo.exists():
                for h in horarios_paulo:
                    dia_nome = dias_nomes[h.dia_semana]
                    horario_str = f"{h.horario_inicio.strftime('%H:%M')} - {h.horario_fim.strftime('%H:%M')}"
                    print(f"   {dia_nome} | {horario_str} | {h.turno.upper()} | {h.disciplina.nome}")
                
                # Verificar violações (Segunda, Terça, Quarta = indisponível)
                violacoes = horarios_paulo.filter(dia_semana__in=[0, 1, 2])
                if violacoes.exists():
                    print(f"\n   ❌ VIOLAÇÕES ({violacoes.count()}):")
                    for v in violacoes:
                        dia_nome = dias_nomes[v.dia_semana]
                        print(f"      {dia_nome} - Paulo está indisponível neste dia!")
                else:
                    print(f"\n   ✅ PERFEITO! Paulo só está agendado em dias disponíveis!")
            else:
                print("   Paulo não tem aulas agendadas")
                
        except Professor.DoesNotExist:
            print("   Professor Paulo não encontrado")
    
    else:
        print(f"\n❌ ERRO: {resultado.get('erro', 'Erro desconhecido')}")
        if resultado['conflitos']:
            print("\nConflitos:")
            for conflito in resultado['conflitos']:
                print(f"   - {conflito}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE DOS HORÁRIOS CONCLUÍDO!")

if __name__ == "__main__":
    main()
