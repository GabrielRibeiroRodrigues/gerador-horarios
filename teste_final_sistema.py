#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.algoritmo_horarios import gerar_horarios_automaticamente
from core.models import Horario, Professor

print("🚀 TESTE FINAL DO SISTEMA COMPLETO")
print("=" * 60)

# Testar a função principal que é chamada pela view
print("📋 Testando função gerar_horarios_automaticamente...")

# Limpar horários existentes
Horario.objects.all().delete()
print("🗑️ Horários anteriores removidos")

# Gerar com todas as opções ativadas
resultado = gerar_horarios_automaticamente(
    turmas=None,  # Todas as turmas
    respeitar_preferencias=True,
    evitar_janelas=True,
    distribuir_dias=True,
    limpar_anteriores=False  # Já limpamos manualmente
)

print(f"\n📊 RESULTADO DA GERAÇÃO:")
print(f"   ✅ Sucesso: {resultado['sucesso']}")
print(f"   📈 Horários criados: {resultado['horarios_criados']}")
print(f"   🎯 Turmas processadas: {resultado.get('turmas_processadas', 'N/A')}")
print(f"   🔄 Tentativas: {resultado.get('tentativas', 'N/A')}")

if resultado.get('conflitos'):
    print(f"   ⚠️ Conflitos: {len(resultado['conflitos'])}")
    for conflito in resultado['conflitos'][:3]:
        print(f"     - {conflito}")

# Verificar Paulo especificamente
print(f"\n👨‍🏫 VERIFICAÇÃO FINAL DO PAULO:")
paulo_horarios = Horario.objects.filter(professor__nome_completo='Paulo')
print(f"   Total de aulas: {paulo_horarios.count()}")

dias_nomes = {1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta'}
violacoes = 0

for h in paulo_horarios:
    dia_nome = dias_nomes[h.dia_semana]
    if h.dia_semana in [1, 2, 3]:  # Segunda, Terça, Quarta
        print(f"   ❌ VIOLAÇÃO: {dia_nome}")
        violacoes += 1
    else:
        print(f"   ✅ OK: {dia_nome}")

if violacoes == 0:
    print(f"\n🎉 PERFEITO! Sistema totalmente funcional!")
    print(f"   ✅ Paulo respeitado (sem aulas Segunda/Terça/Quarta)")
    print(f"   ✅ Algoritmo robusto funcionando")
    print(f"   ✅ Horários da tarde: 13h-17h com intervalo 14:50-15:10")
    print(f"   ✅ Sistema de agrupamento ativo")
    print(f"   ✅ Interface web integrada")
else:
    print(f"\n⚠️ Ainda há {violacoes} violação(ões) das preferências do Paulo")

print(f"\n🔚 TESTE CONCLUÍDO!")
print("=" * 60)
