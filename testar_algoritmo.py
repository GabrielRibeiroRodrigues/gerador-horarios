#!/usr/bin/env python
"""
Teste do novo algoritmo de geração de horários.
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
    print("🔄 TESTANDO NOVO ALGORITMO DE GERAÇÃO DE HORÁRIOS")
    print("=" * 60)
    
    # Executar geração
    print("Iniciando geração de horários...")
    resultado = gerar_horarios_automaticamente(limpar_anteriores=True)
    
    print("\n📊 RESULTADO DA GERAÇÃO:")
    print(f"Sucesso: {'✅ SIM' if resultado['sucesso'] else '❌ NÃO'}")
    print(f"Horários criados: {resultado['horarios_criados']}")
    print(f"Turmas processadas: {resultado['turmas_processadas']}")
    print(f"Tentativas: {resultado.get('tentativas', 'N/A')}")
    
    if resultado.get('erro'):
        print(f"\n❌ ERRO: {resultado['erro']}")
    
    if resultado['conflitos']:
        print(f"\n⚠️ CONFLITOS ({len(resultado['conflitos'])}):")
        for i, conflito in enumerate(resultado['conflitos'], 1):
            print(f"   {i}. {conflito}")
    
    # Verificar se Paulo está respeitando as preferências
    if resultado['sucesso']:
        print(f"\n👨‍🏫 VERIFICAÇÃO DAS PREFERÊNCIAS DO PAULO:")
        try:
            paulo = Professor.objects.get(nome_completo="Paulo")
            horarios_paulo = Horario.objects.filter(professor=paulo)
            
            print(f"Paulo tem {horarios_paulo.count()} aulas agendadas:")
            
            dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
            
            for h in horarios_paulo:
                dia_nome = dias_nomes[h.dia_semana]
                print(f"   {dia_nome} - {h.turno} - {h.disciplina.nome}")
            
            # Verificar violações (deve estar indisponível em Segunda, Terça, Quarta)
            violacoes = horarios_paulo.filter(dia_semana__in=[0, 1, 2])
            
            if violacoes.exists():
                print(f"\n❌ VIOLAÇÕES ENCONTRADAS ({violacoes.count()}):")
                for v in violacoes:
                    dia_nome = dias_nomes[v.dia_semana]
                    print(f"   {dia_nome} - {v.turno} - {v.disciplina.nome}")
            else:
                print(f"\n✅ SUCESSO! Paulo não está agendado em dias indisponíveis!")
                
        except Professor.DoesNotExist:
            print("Professor Paulo não encontrado")
        except Exception as e:
            print(f"Erro ao verificar Paulo: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
