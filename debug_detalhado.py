#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarios_escolares.settings')
django.setup()

from core.models import Professor, PreferenciaProfessor
from core.algoritmo_horarios import GeradorHorariosRobusto

class DebugGerador(GeradorHorariosRobusto):
    def _professor_disponivel(self, professor, dia, turno, disciplina):
        """Versão com debug do método original"""
        print(f"\n🔍 DEBUG _professor_disponivel:")
        print(f"   Professor: {professor.nome_completo}")
        print(f"   Dia: {dia} | Turno: {turno} | Disciplina: {disciplina}")
        
        # Verificar preferências
        preferencias = PreferenciaProfessor.objects.filter(
            professor=professor,
            dia_semana=dia
        )
        
        print(f"   Preferências encontradas: {preferencias.count()}")
        
        if preferencias.exists():
            for i, pref in enumerate(preferencias):
                print(f"   Pref {i+1}: dia={pref.dia_semana}, turno={pref.turno}, disciplina={pref.disciplina}, disponivel={pref.disponivel}")
                
                # Verificar se se aplica
                turno_aplica = pref.turno is None or pref.turno == '' or pref.turno == turno
                disciplina_aplica = pref.disciplina is None or pref.disciplina == disciplina
                
                print(f"     Turno se aplica: {turno_aplica} | Disciplina se aplica: {disciplina_aplica}")
                
                if turno_aplica and disciplina_aplica:
                    if not pref.disponivel:
                        print(f"     ❌ BLOQUEADO por esta preferência!")
                        return False
                    else:
                        print(f"     ✅ Permitido por esta preferência")
        else:
            print(f"   Nenhuma preferência específica encontrada para dia {dia}")
        
        print(f"   ✅ RESULTADO FINAL: DISPONÍVEL")
        return True

print("🔍 DEBUG DETALHADO - MÉTODO _professor_disponivel")
print("=" * 60)

paulo = Professor.objects.get(nome_completo='Paulo')
gerador = DebugGerador()

# Testar segunda-feira (dia 1)
print("\n🧪 TESTANDO SEGUNDA-FEIRA (dia 1):")
resultado = gerador._professor_disponivel(paulo, 1, 'tarde', None)
print(f"RESULTADO: {resultado}")

print("\n" + "="*60)
