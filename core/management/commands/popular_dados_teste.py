"""
Comando para popular dados de teste para o sistema de horários.

Este comando cria dados de exemplo incluindo disciplinas, professores, 
salas, turmas e algumas preferências para testar o gerador de horários.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Disciplina, Professor, Sala, Turma, PreferenciaProfessor


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste para o gerador de horários'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa dados existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['limpar']:
            self.stdout.write('Limpando dados existentes...')
            Disciplina.objects.all().delete()
            Professor.objects.all().delete()
            Sala.objects.all().delete()
            Turma.objects.all().delete()
            PreferenciaProfessor.objects.all().delete()

        with transaction.atomic():
            # Criar disciplinas
            self.stdout.write('Criando disciplinas...')
            disciplinas = [
                {'nome': 'Matemática', 'carga': 5, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Português', 'carga': 4, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Física', 'carga': 3, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Química', 'carga': 3, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Biologia', 'carga': 2, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'História', 'carga': 2, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Geografia', 'carga': 2, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Inglês', 'carga': 2, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Educação Física', 'carga': 2, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
                {'nome': 'Arte', 'carga': 1, 'curso': 'Ensino Médio', 'periodo': '1º Ano'},
            ]

            disciplinas_obj = []
            for disc_data in disciplinas:
                disciplina = Disciplina.objects.create(
                    nome=disc_data['nome'],
                    carga_horaria_semanal=disc_data['carga'],
                    curso_area=disc_data['curso'],
                    periodo_serie=disc_data['periodo'],
                    ativa=True
                )
                disciplinas_obj.append(disciplina)
                self.stdout.write(f'  ✓ {disciplina.nome}')

            # Criar professores
            self.stdout.write('Criando professores...')
            professores_data = [
                {'nome': 'Prof. João Silva', 'email': 'joao@escola.com', 'especialidade': 'Matemática'},
                {'nome': 'Prof.ª Maria Santos', 'email': 'maria@escola.com', 'especialidade': 'Português'},
                {'nome': 'Prof. Carlos Oliveira', 'email': 'carlos@escola.com', 'especialidade': 'Física'},
                {'nome': 'Prof.ª Ana Costa', 'email': 'ana@escola.com', 'especialidade': 'Química'},
                {'nome': 'Prof. Pedro Rodrigues', 'email': 'pedro@escola.com', 'especialidade': 'Biologia'},
                {'nome': 'Prof.ª Luciana Alves', 'email': 'luciana@escola.com', 'especialidade': 'História'},
                {'nome': 'Prof. Roberto Lima', 'email': 'roberto@escola.com', 'especialidade': 'Geografia'},
                {'nome': 'Prof.ª Patricia Brown', 'email': 'patricia@escola.com', 'especialidade': 'Inglês'},
                {'nome': 'Prof. Marcos Fitness', 'email': 'marcos@escola.com', 'especialidade': 'Educação Física'},
                {'nome': 'Prof.ª Clara Arte', 'email': 'clara@escola.com', 'especialidade': 'Arte'},
            ]

            professores_obj = []
            for prof_data in professores_data:
                professor = Professor.objects.create(
                    nome_completo=prof_data['nome'],
                    email=prof_data['email'],
                    telefone='(11) 99999-9999',
                    especialidade=prof_data['especialidade'],
                    ativo=True
                )
                professores_obj.append(professor)
                self.stdout.write(f'  ✓ {professor.nome_completo}')

            # Criar salas
            self.stdout.write('Criando salas...')
            salas_data = [
                {'nome': 'Sala 101', 'capacidade': 35, 'tipo': 'normal'},
                {'nome': 'Sala 102', 'capacidade': 35, 'tipo': 'normal'},
                {'nome': 'Sala 103', 'capacidade': 35, 'tipo': 'normal'},
                {'nome': 'Sala 201', 'capacidade': 40, 'tipo': 'normal'},
                {'nome': 'Sala 202', 'capacidade': 40, 'tipo': 'normal'},
                {'nome': 'Lab. Física', 'capacidade': 25, 'tipo': 'laboratorio'},
                {'nome': 'Lab. Química', 'capacidade': 25, 'tipo': 'laboratorio'},
                {'nome': 'Lab. Biologia', 'capacidade': 25, 'tipo': 'laboratorio'},
                {'nome': 'Quadra Esportiva', 'capacidade': 50, 'tipo': 'auditorio'},
                {'nome': 'Sala de Arte', 'capacidade': 30, 'tipo': 'normal'},
            ]

            salas_obj = []
            for sala_data in salas_data:
                sala = Sala.objects.create(
                    nome_numero=sala_data['nome'],
                    capacidade=sala_data['capacidade'],
                    tipo=sala_data['tipo'],
                    ativa=True
                )
                salas_obj.append(sala)
                self.stdout.write(f'  ✓ {sala.nome_numero}')

            # Criar turmas
            self.stdout.write('Criando turmas...')
            turmas_data = [
                {'nome': '1º A', 'serie': '1º Ano', 'alunos': 32},
                {'nome': '1º B', 'serie': '1º Ano', 'alunos': 30},
                {'nome': '1º C', 'serie': '1º Ano', 'alunos': 28},
            ]

            turmas_obj = []
            for turma_data in turmas_data:
                turma = Turma.objects.create(
                    nome_codigo=turma_data['nome'],
                    serie_periodo=turma_data['serie'],
                    numero_alunos=turma_data['alunos'],
                    ativa=True
                )
                # Adicionar todas as disciplinas à turma
                turma.disciplinas.set(disciplinas_obj)
                turmas_obj.append(turma)
                self.stdout.write(f'  ✓ {turma.nome_codigo} ({turma.numero_alunos} alunos)')

            # Criar algumas preferências de professores
            self.stdout.write('Criando preferências dos professores...')
            
            # Preferências baseadas nas especialidades
            especialidade_map = {
                'Matemática': disciplinas_obj[0],  # Matemática
                'Português': disciplinas_obj[1],   # Português
                'Física': disciplinas_obj[2],      # Física
                'Química': disciplinas_obj[3],     # Química
                'Biologia': disciplinas_obj[4],    # Biologia
                'História': disciplinas_obj[5],    # História
                'Geografia': disciplinas_obj[6],   # Geografia
                'Inglês': disciplinas_obj[7],      # Inglês
                'Educação Física': disciplinas_obj[8],  # Educação Física
                'Arte': disciplinas_obj[9],        # Arte
            }

            preferencias_criadas = 0
            for professor in professores_obj:
                # Criar preferência pela disciplina da especialidade
                if professor.especialidade in especialidade_map:
                    disciplina = especialidade_map[professor.especialidade]
                    
                    # Preferência de disciplina
                    PreferenciaProfessor.objects.create(
                        professor=professor,
                        disciplina=disciplina,
                        turno='manha',  # Alguns preferem manhã
                        dia_semana=None,  # Sem preferência específica de dia
                        observacoes=f'Professor especialista em {professor.especialidade}'
                    )
                    preferencias_criadas += 1

                    # Alguns professores têm preferências de turno
                    if professor.nome.startswith('Prof.ª'):
                        # Professoras preferem tarde
                        PreferenciaProfessor.objects.create(
                            professor=professor,
                            disciplina=disciplina,
                            turno='tarde',
                            dia_semana=None,
                            observacoes='Preferência por turno da tarde'
                        )
                        preferencias_criadas += 1

            self.stdout.write(f'  ✓ {preferencias_criadas} preferências criadas')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Dados de teste criados com sucesso!\n'
                f'📚 {len(disciplinas_obj)} disciplinas\n'
                f'👨‍🏫 {len(professores_obj)} professores\n'
                f'🏫 {len(salas_obj)} salas\n'
                f'🎓 {len(turmas_obj)} turmas\n'
                f'⚙️ {preferencias_criadas} preferências\n\n'
                f'Agora você pode testar o gerador de horários!'
            )
        )
