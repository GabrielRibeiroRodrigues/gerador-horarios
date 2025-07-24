#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Horario

print("🔍 VERIFICAÇÃO DOS DIAS NA BASE DE DADOS")
print("=" * 50)

horarios = Horario.objects.all()
dias_encontrados = set()

for h in horarios:
    dias_encontrados.add(h.dia_semana)
    print(f"Horário: Professor={h.professor.nome_completo}, Dia={h.dia_semana}")

print(f"\n📊 Dias únicos encontrados: {sorted(dias_encontrados)}")
print(f"✅ Esperado: [1, 2, 3, 4, 5] (Segunda a Sexta)")
print(f"❌ Encontrado: {sorted(dias_encontrados)}")

if 0 in dias_encontrados:
    print(f"\n⚠️ PROBLEMA: Existe dia 0 no banco!")
    print(f"   Isso sugere que há uma inconsistência na numeração de dias")
    print(f"   O algoritmo deve usar 1-5, mas está salvando 0-4")
