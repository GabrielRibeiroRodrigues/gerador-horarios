#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import PreferenciaProfessor

print("🔍 VERIFICAÇÃO DOS CAMPOS TURNO")
print("=" * 40)

prefs = PreferenciaProfessor.objects.all()
for p in prefs:
    print(f"Pref: dia={p.dia_semana}, turno=\"{p.turno}\", repr={repr(p.turno)}, is_none={p.turno is None}, is_empty={p.turno == ''}")

print("\n🔧 CORREÇÃO: Vou atualizar para None quando for string vazia")

# Corrigir registros com turno como string vazia
for pref in prefs:
    if pref.turno == '':
        pref.turno = None
        pref.save()
        print(f"✅ Corrigido registro dia {pref.dia_semana}")

print("\n📋 VERIFICAÇÃO APÓS CORREÇÃO:")
prefs = PreferenciaProfessor.objects.all()
for p in prefs:
    print(f"Pref: dia={p.dia_semana}, turno={repr(p.turno)}, is_none={p.turno is None}")
