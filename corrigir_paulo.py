#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor

print("🔧 CORRIGINDO PREFERÊNCIAS DO PAULO")
print("=" * 50)

# Buscar Paulo
try:
    paulo = Professor.objects.get(nome_completo='Paulo')
    print(f"✅ Professor encontrado: {paulo.nome_completo}")
except Professor.DoesNotExist:
    print("❌ Professor Paulo não encontrado!")
    exit()

# Remover preferências existentes
prefs_antigas = PreferenciaProfessor.objects.filter(professor=paulo).count()
PreferenciaProfessor.objects.filter(professor=paulo).delete()
print(f"🗑️ Removidas {prefs_antigas} preferências antigas")

# Adicionar novas preferências - Paulo indisponível segunda, terça e quarta
dias_indisponiveis = [1, 2, 3]  # segunda=1, terça=2, quarta=3
dias_nomes = {1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta'}

for dia in dias_indisponiveis:
    pref = PreferenciaProfessor.objects.create(
        professor=paulo,
        dia_semana=dia,
        disponivel=False
    )
    print(f"❌ Paulo INDISPONÍVEL: {dias_nomes[dia]}")

print("\n✅ Preferências do Paulo atualizadas!")
print("Paulo agora está indisponível: Segunda, Terça e Quarta")

# Verificar preferências finais
prefs_finais = PreferenciaProfessor.objects.filter(professor=paulo)
print(f"\n📋 Preferências finais ({prefs_finais.count()} registros):")
for pref in prefs_finais:
    status = "DISPONÍVEL" if pref.disponivel else "INDISPONÍVEL"
    print(f"   {dias_nomes[pref.dia_semana]}: {status}")
