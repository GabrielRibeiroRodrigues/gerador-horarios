#!/usr/bin/env python
"""
Análise completa do sistema de preferências e geração de horários.
Vamos identificar todos os problemas e corrigir como um dev sênior.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor, Horario, Turma, Disciplina
from core.algoritmo_horarios import gerar_horarios_automaticamente

def analisar_problema():
    print("=== ANÁLISE COMPLETA DO SISTEMA ===")
    
    # 1. Verificar professor Paulo
    try:
        paulo = Professor.objects.get(nome_completo__icontains="Paulo")
        print(f"\n1. Professor: {paulo.nome_completo}")
        
        # Verificar preferências detalhadamente
        prefs = PreferenciaProfessor.objects.filter(professor=paulo)
        print(f"\n2. Preferências do {paulo.nome_completo}:")
        for pref in prefs:
            print(f"   - Dia: {pref.get_dia_semana_display()}")
            print(f"     Disponível: {pref.disponivel}")
            print(f"     Preferencial: {pref.preferencial}")
            print(f"     Prioridade: {pref.prioridade}")
            print(f"     Turno: {pref.turno or 'Qualquer'}")
            print(f"     Disciplina: {pref.disciplina or 'Qualquer'}")
            print(f"     Criado em: {pref.criado_em}")
            print()
        
        # 3. Verificar horários existentes do Paulo
        horarios_paulo = Horario.objects.filter(professor=paulo)
        print(f"3. Horários existentes do {paulo.nome_completo} ({horarios_paulo.count()}):")
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for h in horarios_paulo.order_by('dia_semana', 'horario_inicio'):
            print(f"   - {dias[h.dia_semana]}: {h.disciplina.nome} às {h.horario_inicio} (Turno: {h.turno})")
            print(f"     Turma: {h.turma.nome_codigo}, Sala: {h.sala.nome_numero}")
        
        # 4. Testar método de disponibilidade em detalhes
        print(f"\n4. Teste detalhado de disponibilidade:")
        for dia in range(5):  # Segunda a Sexta
            for turno in ['manha', 'tarde', 'noite']:
                disponivel = paulo.disponivel_para_horario(dia_semana=dia, turno=turno)
                print(f"   - {dias[dia]} {turno}: {disponivel}")
        
        # 5. Verificar se há horários conflitantes
        print(f"\n5. Verificação de conflitos:")
        for h in horarios_paulo:
            disponivel = paulo.disponivel_para_horario(
                dia_semana=h.dia_semana, 
                turno=h.turno, 
                disciplina=h.disciplina
            )
            status = "✅ OK" if disponivel else "❌ CONFLITO"
            print(f"   {status} - {dias[h.dia_semana]} {h.turno}: {h.disciplina.nome}")
        
        # 6. Verificar último processo de geração
        print(f"\n6. Análise do último processo de geração:")
        all_horarios = Horario.objects.all()
        print(f"   Total de horários no sistema: {all_horarios.count()}")
        
        # Contar por professor
        from collections import defaultdict
        horarios_por_professor = defaultdict(int)
        for h in all_horarios:
            horarios_por_professor[h.professor.nome_completo] += 1
        
        print("   Horários por professor:")
        for prof, count in horarios_por_professor.items():
            print(f"     - {prof}: {count} aulas")
        
        # 7. Verificar se as preferências estão sendo respeitadas por outros professores
        print(f"\n7. Verificação geral de preferências:")
        todos_profs = Professor.objects.filter(ativo=True)
        for prof in todos_profs:
            prefs_prof = PreferenciaProfessor.objects.filter(professor=prof, disponivel=False)
            if prefs_prof.exists():
                horarios_prof = Horario.objects.filter(professor=prof)
                print(f"\n   Professor: {prof.nome_completo}")
                print(f"   Preferências de indisponibilidade: {prefs_prof.count()}")
                print(f"   Horários atuais: {horarios_prof.count()}")
                
                for pref in prefs_prof:
                    conflitos = horarios_prof.filter(dia_semana=pref.dia_semana)
                    if pref.turno:
                        conflitos = conflitos.filter(turno=pref.turno)
                    if conflitos.exists():
                        print(f"     ❌ CONFLITO: {pref.get_dia_semana_display()} {pref.turno or 'qualquer turno'}")
                        for conf in conflitos:
                            print(f"        -> {conf.disciplina.nome} às {conf.horario_inicio}")
        
        # 8. Verificar método de score de preferência
        print(f"\n8. Teste do método get_preferencia_score:")
        for dia in range(3):  # Testar seg, ter, qua
            score = paulo.get_preferencia_score(dia_semana=dia, turno='tarde')
            print(f"   - {dias[dia]} tarde: score = {score}")
        
    except Exception as e:
        print(f"Erro na análise: {e}")
        import traceback
        traceback.print_exc()

def testar_geracao_limpa():
    print(f"\n=== TESTE DE GERAÇÃO LIMPA ===")
    
    try:
        # Limpar todos os horários
        print("1. Limpando horários existentes...")
        Horario.objects.all().delete()
        print("   ✅ Horários limpos")
        
        # Verificar preferências antes da geração
        paulo = Professor.objects.get(nome_completo__icontains="Paulo")
        prefs = PreferenciaProfessor.objects.filter(professor=paulo, disponivel=False)
        print(f"\n2. Preferências de indisponibilidade do Paulo: {prefs.count()}")
        for pref in prefs:
            print(f"   - {pref.get_dia_semana_display()} {pref.turno or 'qualquer turno'}")
        
        # Gerar horários novamente
        print(f"\n3. Gerando horários com preferências...")
        resultado = gerar_horarios_automaticamente(
            turmas=None,
            respeitar_preferencias=True,  # IMPORTANTE: respeitando preferências
            evitar_janelas=True,
            distribuir_dias=True,
            limpar_anteriores=False  # Já limpamos manualmente
        )
        
        print(f"4. Resultado da geração:")
        print(f"   Sucesso: {resultado['sucesso']}")
        print(f"   Horários criados: {resultado.get('horarios_criados', 0)}")
        print(f"   Turmas processadas: {resultado.get('turmas_processadas', 0)}")
        
        if resultado.get('conflitos'):
            print(f"   Conflitos ({len(resultado['conflitos'])}):")
            for conflito in resultado['conflitos'][:5]:
                print(f"     - {conflito}")
        
        if not resultado['sucesso']:
            print(f"   Erro: {resultado.get('erro', 'Erro desconhecido')}")
        
        # Verificar resultado
        print(f"\n5. Verificação pós-geração:")
        horarios_paulo_novo = Horario.objects.filter(professor=paulo)
        print(f"   Horários do Paulo: {horarios_paulo_novo.count()}")
        
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        for h in horarios_paulo_novo:
            print(f"     - {dias[h.dia_semana]}: {h.disciplina.nome} às {h.horario_inicio}")
        
        # Verificar se violou preferências
        for h in horarios_paulo_novo:
            disponivel = paulo.disponivel_para_horario(
                dia_semana=h.dia_semana,
                turno=h.turno,
                disciplina=h.disciplina
            )
            if not disponivel:
                print(f"     ❌ VIOLAÇÃO: {dias[h.dia_semana]} {h.turno} - {h.disciplina.nome}")
    
    except Exception as e:
        print(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analisar_problema()
    
    resposta = input("\nDeseja executar teste de geração limpa? (s/n): ")
    if resposta.lower() == 's':
        testar_geracao_limpa()
