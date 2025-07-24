#!/usr/bin/env python
"""
Script de teste para verificar se o algoritmo de geração de horários funciona.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Turma, Disciplina, Professor, Sala
from core.algoritmo_horarios import gerar_horarios_automaticamente

def main():
    print("=== Teste do Algoritmo de Geração de Horários ===")
    
    try:
        # Verificar se existem dados básicos
        turmas = Turma.objects.filter(ativa=True)
        disciplinas = Disciplina.objects.filter(ativa=True)
        professores = Professor.objects.filter(ativo=True)
        salas = Sala.objects.filter(ativa=True)
        
        print(f"Turmas ativas: {turmas.count()}")
        print(f"Disciplinas ativas: {disciplinas.count()}")
        print(f"Professores ativos: {professores.count()}")
        print(f"Salas ativas: {salas.count()}")
        
        if turmas.count() == 0:
            print("⚠️  Não há turmas cadastradas. Criando dados de teste...")
            
            # Criar dados básicos de teste
            disciplina_teste = Disciplina.objects.create(
                nome="Matemática",
                carga_horaria_semanal=4,
                curso_area="Ensino Fundamental",
                periodo_serie="6º Ano"
            )
            
            professor_teste = Professor.objects.create(
                nome_completo="Professor Teste",
                email="teste@escola.com",
                especialidade="Matemática"
            )
            professor_teste.disciplinas.add(disciplina_teste)
            
            sala_teste = Sala.objects.create(
                nome_numero="Sala 101",
                tipo="normal",
                capacidade=30
            )
            
            turma_teste = Turma.objects.create(
                nome_codigo="6A",
                serie_periodo="6º Ano",
                turno_turma="matutino",
                numero_alunos=25
            )
            turma_teste.disciplinas.add(disciplina_teste)
            
            print("✅ Dados de teste criados!")
        
        # Testar geração de horários
        print("\n--- Testando geração de horários ---")
        resultado = gerar_horarios_automaticamente(
            turmas=None,
            respeitar_preferencias=True,
            evitar_janelas=True,
            distribuir_dias=True,
            limpar_anteriores=True
        )
        
        if resultado['sucesso']:
            print(f"✅ Geração bem-sucedida!")
            print(f"   - Horários criados: {resultado['horarios_criados']}")
            print(f"   - Turmas processadas: {resultado['turmas_processadas']}")
            
            if resultado.get('conflitos'):
                print(f"   - Conflitos encontrados: {len(resultado['conflitos'])}")
                for conflito in resultado['conflitos'][:3]:
                    print(f"     • {conflito}")
        else:
            print(f"❌ Erro na geração: {resultado.get('erro', 'Erro desconhecido')}")
            
            if resultado.get('conflitos'):
                print("Conflitos:")
                for conflito in resultado['conflitos'][:5]:
                    print(f"  • {conflito}")
    
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
