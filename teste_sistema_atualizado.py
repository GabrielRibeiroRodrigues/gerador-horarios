#!/usr/bin/env python
"""
Teste do sistema atualizado com novos requisitos:
- Horários da tarde: 13h às 17h com intervalo 14:50-15:10
- Agrupamento de aulas melhorado
- Respeito às preferências do Paulo
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
    print("🎯 TESTE DO SISTEMA ATUALIZADO")
    print("=" * 60)
    print("📋 Requisitos:")
    print("   • Horários da tarde: 13h às 17h")
    print("   • Intervalo: 14:50 às 15:10")
    print("   • Aulas mais agrupadas")
    print("   • Paulo indisponível: Segunda, Terça, Quarta")
    print("=" * 60)
    
    # Executar geração
    print("\n🔄 Gerando horários...")
    resultado = gerar_horarios_automaticamente(limpar_anteriores=True)
    
    print(f"\n📊 RESULTADO:")
    print(f"Sucesso: {'✅ SIM' if resultado['sucesso'] else '❌ NÃO'}")
    print(f"Horários criados: {resultado['horarios_criados']}")
    print(f"Tentativas: {resultado.get('tentativas', 'N/A')}")
    
    if resultado['sucesso']:
        horarios = Horario.objects.all().order_by('dia_semana', 'horario_inicio')
        dias_nomes = {1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta'}
        
        print(f"\n📅 HORÁRIOS GERADOS ({horarios.count()} aulas):")
        print("-" * 80)
        
        for h in horarios:
            dia_nome = dias_nomes[h.dia_semana]
            horario_str = f"{h.horario_inicio.strftime('%H:%M')} - {h.horario_fim.strftime('%H:%M')}"
            print(f"{dia_nome:10} | {horario_str:11} | {h.turno.upper():5} | {h.professor.nome_completo:15} | {h.disciplina.nome:10} | Sala {h.sala.nome_numero}")
        
        # Análise específica dos horários da tarde
        print(f"\n🌅 ANÁLISE DOS HORÁRIOS DA TARDE:")
        horarios_tarde = horarios.filter(turno='tarde')
        print(f"Total de aulas da tarde: {horarios_tarde.count()}")
        
        # Verificar se estão dentro do intervalo correto
        for h in horarios_tarde:
            if h.horario_inicio.hour < 13:
                print(f"⚠️  PROBLEMA: Aula começa antes das 13h - {h}")
            elif h.horario_fim.hour > 17 or (h.horario_fim.hour == 17 and h.horario_fim.minute > 40):
                print(f"⚠️  PROBLEMA: Aula termina depois das 17:40 - {h}")
            elif (h.horario_inicio.hour == 14 and h.horario_inicio.minute >= 50 and 
                  h.horario_inicio.hour < 15 and h.horario_inicio.minute < 10):
                print(f"⚠️  PROBLEMA: Aula durante o intervalo (14:50-15:10) - {h}")
        
        print("✅ Horários da tarde estão dentro do intervalo correto!")
        
        # Verificar agrupamento de aulas
        print(f"\n📊 ANÁLISE DO AGRUPAMENTO:")
        agrupamentos = {}
        for h in horarios:
            key = f"{h.professor.nome_completo}-{dias_nomes[h.dia_semana]}"
            if key not in agrupamentos:
                agrupamentos[key] = []
            agrupamentos[key].append(h)
        
        aulas_consecutivas = 0
        total_professores_dia = 0
        
        for key, aulas_prof_dia in agrupamentos.items():
            if len(aulas_prof_dia) > 1:
                total_professores_dia += 1
                aulas_prof_dia.sort(key=lambda x: x.horario_inicio)
                
                # Verificar consecutividade
                for i in range(len(aulas_prof_dia) - 1):
                    if aulas_prof_dia[i].horario_fim == aulas_prof_dia[i+1].horario_inicio:
                        aulas_consecutivas += 1
                
                print(f"   {key}: {len(aulas_prof_dia)} aulas")
        
        if total_professores_dia > 0:
            taxa_agrupamento = (aulas_consecutivas / total_professores_dia) * 100
            print(f"Taxa de agrupamento: {taxa_agrupamento:.1f}%")
        
        # Verificar Paulo especificamente
        print(f"\n👨‍🏫 VERIFICAÇÃO DO PAULO:")
        try:
            paulo = Professor.objects.get(nome_completo="Paulo")
            horarios_paulo = horarios.filter(professor=paulo)
            
            if horarios_paulo.exists():
                print(f"Paulo tem {horarios_paulo.count()} aulas:")
                for h in horarios_paulo:
                    dia_nome = dias_nomes[h.dia_semana]
                    horario_str = f"{h.horario_inicio.strftime('%H:%M')} - {h.horario_fim.strftime('%H:%M')}"
                    print(f"   {dia_nome} | {horario_str} | {h.turno.upper()} | {h.disciplina.nome}")
                
                # Verificar violações
                violacoes = horarios_paulo.filter(dia_semana__in=[0, 1, 2])
                if violacoes.exists():
                    print(f"\n❌ VIOLAÇÕES ENCONTRADAS ({violacoes.count()}):")
                    for v in violacoes:
                        dia_nome = dias_nomes[v.dia_semana]
                        print(f"   {dia_nome} - Paulo deveria estar indisponível!")
                else:
                    print(f"\n✅ PERFEITO! Paulo só tem aulas em Quinta e Sexta!")
                    
                # Verificar agrupamento do Paulo
                paulo_por_dia = {}
                for h in horarios_paulo:
                    dia = h.dia_semana
                    if dia not in paulo_por_dia:
                        paulo_por_dia[dia] = []
                    paulo_por_dia[dia].append(h)
                
                for dia, aulas in paulo_por_dia.items():
                    if len(aulas) > 1:
                        aulas.sort(key=lambda x: x.horario_inicio)
                        consecutivas = 0
                        for i in range(len(aulas) - 1):
                            if aulas[i].horario_fim == aulas[i+1].horario_inicio:
                                consecutivas += 1
                        print(f"   {dias_nomes[dia]}: {len(aulas)} aulas, {consecutivas} consecutivas")
            else:
                print("Paulo não tem aulas agendadas")
                
        except Professor.DoesNotExist:
            print("Professor Paulo não encontrado")
    
    else:
        print(f"\n❌ FALHA NA GERAÇÃO:")
        print(f"Erro: {resultado.get('erro', 'Erro desconhecido')}")
        if resultado['conflitos']:
            print("Conflitos:")
            for conflito in resultado['conflitos']:
                print(f"   - {conflito}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
