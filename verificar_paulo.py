#!/usr/bin/env python
"""
Script para verificar e ajustar as preferências do professor Paulo.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor, Disciplina, Horario

def main():
    print("=== AJUSTANDO PREFERÊNCIAS DO PAULO PARA ESW2 ===")
    
    # Buscar Paulo
    try:
        paulo = Professor.objects.get(nome_completo="Paulo")
        print(f"Professor encontrado: {paulo.nome_completo}")
    except Professor.DoesNotExist:
        print("Professor Paulo não encontrado!")
        return
    
    # Buscar disciplina ESW2
    try:
        esw2 = Disciplina.objects.get(nome="ESW2")
        print(f"Disciplina encontrada: {esw2.nome}")
    except Disciplina.DoesNotExist:
        print("Disciplina ESW2 não encontrada!")
        return
    
    # Verificar preferências atuais
    prefs = PreferenciaProfessor.objects.filter(professor=paulo)
    print(f"\nTotal de preferências atuais: {prefs.count()}")
    
    dias_semana = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta'}
    
    print("\n=== PREFERÊNCIAS ATUAIS ===")
    for pref in prefs:
        status = "DISPONÍVEL" if pref.disponivel else "INDISPONÍVEL"
        disciplina = pref.disciplina.nome if pref.disciplina else "Todas"
        print(f"{dias_semana[pref.dia_semana]} - {status} - {disciplina}")
    
    # Criar preferências específicas para ESW2 em Quinta e Sexta
    print("\n=== CRIANDO PREFERÊNCIAS PARA ESW2 ===")
    
    # Quinta-feira - ESW2 - DISPONÍVEL
    quinta_esw2, created = PreferenciaProfessor.objects.get_or_create(
        professor=paulo,
        dia_semana=3,  # Quinta
        disciplina=esw2,
        defaults={
            'disponivel': True,
            'preferencial': True,
            'prioridade': 1
        }
    )
    if created:
        print("✓ Criada: Quinta-feira - DISPONÍVEL para ESW2")
    else:
        if not quinta_esw2.disponivel:
            quinta_esw2.disponivel = True
            quinta_esw2.save()
            print("✓ Atualizada: Quinta-feira - DISPONÍVEL para ESW2")
        else:
            print("- Quinta-feira já DISPONÍVEL para ESW2")
    
    # Sexta-feira - ESW2 - DISPONÍVEL
    sexta_esw2, created = PreferenciaProfessor.objects.get_or_create(
        professor=paulo,
        dia_semana=4,  # Sexta
        disciplina=esw2,
        defaults={
            'disponivel': True,
            'preferencial': True,
            'prioridade': 1
        }
    )
    if created:
        print("✓ Criada: Sexta-feira - DISPONÍVEL para ESW2")
    else:
        if not sexta_esw2.disponivel:
            sexta_esw2.disponivel = True
            sexta_esw2.save()
            print("✓ Atualizada: Sexta-feira - DISPONÍVEL para ESW2")
        else:
            print("- Sexta-feira já DISPONÍVEL para ESW2")
    
    print("\n=== TESTANDO DISPONIBILIDADE ===")
    # Testar se Paulo está disponível nos diferentes dias para ESW2
    for dia in range(5):  # Segunda a Sexta
        disponivel = paulo.disponivel_para_horario(dia_semana=dia, disciplina=esw2)
        status = "✅ DISPONÍVEL" if disponivel else "❌ INDISPONÍVEL"
        print(f"{dias_semana[dia]} para ESW2: {status}")
    
    print("\n=== LIMPANDO HORÁRIOS CONFLITANTES ===")
    # Remover horários conflitantes (Paulo em dias indisponíveis)
    horarios_conflitantes = Horario.objects.filter(
        professor=paulo,
        dia_semana__in=[0, 1, 2]  # Segunda, Terça, Quarta
    )
    
    if horarios_conflitantes.exists():
        print(f"Removendo {horarios_conflitantes.count()} horários conflitantes...")
        for h in horarios_conflitantes:
            print(f"  - Removido: {dias_semana[h.dia_semana]} - {h.turno} - {h.disciplina.nome}")
        horarios_conflitantes.delete()
        print("✓ Horários conflitantes removidos")
    else:
        print("Nenhum horário conflitante encontrado")
    
    print("\n=== GERANDO NOVOS HORÁRIOS ===")
    from core.algoritmo_horarios import GeradorHorarios
    gerador = GeradorHorarios()
    resultado = gerador.gerar_horarios()
    
    if resultado['sucesso']:
        print(f"✅ Novos horários gerados: {resultado['horarios_criados']} horários")
        
        # Verificar novos horários do Paulo
        novos_horarios_paulo = Horario.objects.filter(professor=paulo)
        print(f"\n📋 Paulo agora tem {novos_horarios_paulo.count()} aulas:")
        
        for h in novos_horarios_paulo:
            print(f"   {dias_semana[h.dia_semana]} - {h.turno} - {h.disciplina.nome}")
        
        # Verificar se ainda há violações
        violacoes = novos_horarios_paulo.filter(dia_semana__in=[0, 1, 2])
        if violacoes.exists():
            print(f"\n❌ AINDA HÁ VIOLAÇÕES: {violacoes.count()}")
            for v in violacoes:
                print(f"   {dias_semana[v.dia_semana]} - {v.turno} - {v.disciplina.nome}")
        else:
            print(f"\n✅ SUCESSO! Paulo não está mais em dias indisponíveis")
            
    else:
        print(f"❌ Erro ao gerar horários: {resultado.get('erro', 'Erro desconhecido')}")
        if resultado.get('conflitos'):
            for conflito in resultado['conflitos'][:3]:
                print(f"   - {conflito}")

if __name__ == "__main__":
    main()

def mostrar_todos_horarios():
    """Mostra todos os horários gerados"""
if __name__ == "__main__":
    main()
