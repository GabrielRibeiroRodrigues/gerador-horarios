"""
Formulários para o sistema de horários escolares.

Este módulo contém todos os formulários Django utilizados na aplicação,
seguindo os princípios SOLID e boas práticas de desenvolvimento.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Disciplina, Sala, Professor, Turma, PreferenciaProfessor, Horario


class DisciplinaForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de disciplinas.
    
    Permite o gerenciamento completo dos dados de uma disciplina,
    incluindo validações personalizadas.
    """
    
    class Meta:
        model = Disciplina
        fields = ['nome', 'carga_horaria_semanal', 'curso_area', 'periodo_serie', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Matemática, Português, História...'
            }),
            'carga_horaria_semanal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'curso_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ensino Fundamental, Ensino Médio...'
            }),
            'periodo_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1º Ano, 2º Período...'
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'nome': 'Nome da disciplina que será exibido nos horários',
            'carga_horaria_semanal': 'Número de aulas por semana (1-20)',
            'curso_area': 'Curso ou área de conhecimento da disciplina',
            'periodo_serie': 'Período ou série em que a disciplina é lecionada',
            'ativa': 'Disciplinas inativas não aparecem na geração de horários'
        }

    def clean_nome(self):
        """
        Valida o nome da disciplina.
        
        Returns:
            str: Nome da disciplina validado
            
        Raises:
            ValidationError: Se o nome for inválido
        """
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip().title()
            if len(nome) < 2:
                raise ValidationError('O nome deve ter pelo menos 2 caracteres.')
        return nome

    def clean_carga_horaria_semanal(self):
        """
        Valida a carga horária semanal.
        
        Returns:
            int: Carga horária validada
            
        Raises:
            ValidationError: Se a carga horária for inválida
        """
        carga_horaria = self.cleaned_data.get('carga_horaria_semanal')
        if carga_horaria and (carga_horaria < 1 or carga_horaria > 20):
            raise ValidationError('A carga horária deve estar entre 1 e 20 aulas por semana.')
        return carga_horaria


class SalaForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de salas.
    
    Gerencia os dados das salas incluindo tipo e capacidade,
    com validações específicas para cada tipo.
    """
    
    class Meta:
        model = Sala
        fields = ['nome_numero', 'tipo', 'capacidade', 'ativa']
        widgets = {
            'nome_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sala 101, Lab. Informática...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'capacidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 200
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'nome_numero': 'Nome ou número de identificação da sala',
            'tipo': 'Tipo da sala determina seu uso específico',
            'capacidade': 'Número máximo de alunos que a sala comporta',
            'ativa': 'Salas inativas não aparecem na geração de horários'
        }

    def clean_capacidade(self):
        """
        Valida a capacidade da sala baseada no tipo.
        
        Returns:
            int: Capacidade validada
            
        Raises:
            ValidationError: Se a capacidade for inadequada para o tipo
        """
        capacidade = self.cleaned_data.get('capacidade')
        tipo = self.cleaned_data.get('tipo')
        
        if capacidade and tipo:
            if tipo == 'auditorio' and capacidade < 50:
                raise ValidationError('Auditórios devem ter capacidade mínima de 50 pessoas.')
            elif tipo == 'laboratorio' and capacidade < 10:
                raise ValidationError('Laboratórios devem ter capacidade mínima de 10 pessoas.')
                
        return capacidade


class ProfessorForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de professores.
    
    Permite associar disciplinas ao professor e gerenciar
    suas informações básicas.
    """
    
    class Meta:
        model = Professor
        fields = ['nome_completo', 'disciplinas', 'ativo']
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do professor'
            }),
            'disciplinas': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'nome_completo': 'Nome completo do professor',
            'disciplinas': 'Disciplinas que o professor pode lecionar',
            'ativo': 'Professores inativos não aparecem na geração de horários'
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com disciplinas ativas.
        """
        super().__init__(*args, **kwargs)
        self.fields['disciplinas'].queryset = Disciplina.objects.filter(ativa=True)

    def clean_nome_completo(self):
        """
        Valida e formata o nome completo do professor.
        
        Returns:
            str: Nome completo validado
            
        Raises:
            ValidationError: Se o nome for inválido
        """
        nome = self.cleaned_data.get('nome_completo')
        if nome:
            nome = nome.strip().title()
            if len(nome.split()) < 2:
                raise ValidationError('Informe o nome completo do professor.')
        return nome


class TurmaForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de turmas.
    
    Gerencia dados das turmas incluindo disciplinas cursadas
    e número de alunos.
    """
    
    class Meta:
        model = Turma
        fields = ['nome_codigo', 'serie_periodo', 'disciplinas', 'numero_alunos', 'ativa']
        widgets = {
            'nome_codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1A, 2B, Turma 301...'
            }),
            'serie_periodo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1º Ano, 2º Período...'
            }),
            'disciplinas': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 6
            }),
            'numero_alunos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'nome_codigo': 'Nome ou código de identificação da turma',
            'serie_periodo': 'Série ou período da turma',
            'disciplinas': 'Disciplinas cursadas pela turma',
            'numero_alunos': 'Número de alunos matriculados na turma',
            'ativa': 'Turmas inativas não aparecem na geração de horários'
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com disciplinas ativas.
        """
        super().__init__(*args, **kwargs)
        self.fields['disciplinas'].queryset = Disciplina.objects.filter(ativa=True)

    def clean_numero_alunos(self):
        """
        Valida o número de alunos da turma.
        
        Returns:
            int: Número de alunos validado
            
        Raises:
            ValidationError: Se o número for inválido
        """
        numero_alunos = self.cleaned_data.get('numero_alunos')
        if numero_alunos and numero_alunos < 1:
            raise ValidationError('A turma deve ter pelo menos 1 aluno.')
        return numero_alunos


class PreferenciaProfessorForm(forms.ModelForm):
    """
    Formulário para configuração de preferências do professor.
    
    Permite definir preferências de disciplina, dia e turno
    que serão consideradas na geração automática.
    """
    
    class Meta:
        model = PreferenciaProfessor
        fields = [
            'professor', 'disciplina', 'dia_semana', 'turno', 'observacoes'
        ]
        widgets = {
            'professor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'disciplina': forms.Select(attrs={
                'class': 'form-select'
            }),
            'dia_semana': forms.Select(attrs={
                'class': 'form-select'
            }),
            'turno': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre preferências...'
            })
        }
        help_texts = {
            'professor': 'Professor para configurar preferências',
            'disciplina': 'Disciplina específica (opcional)',
            'dia_semana': 'Dia da semana específico (opcional)',
            'turno': 'Turno específico (opcional)',
            'observacoes': 'Observações adicionais sobre as preferências'
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com dados filtrados.
        """
        super().__init__(*args, **kwargs)
        self.fields['professor'].queryset = Professor.objects.filter(ativo=True)
        self.fields['disciplina'].queryset = Disciplina.objects.filter(ativa=True)


class HorarioForm(forms.ModelForm):
    """
    Formulário para cadastro e edição manual de horários.
    
    Permite criar e editar horários manualmente,
    com validações para evitar conflitos.
    """
    
    class Meta:
        model = Horario
        fields = [
            'turma', 'disciplina', 'professor', 'sala',
            'dia_semana', 'horario_inicio', 'horario_fim'
        ]
        widgets = {
            'turma': forms.Select(attrs={
                'class': 'form-select'
            }),
            'disciplina': forms.Select(attrs={
                'class': 'form-select'
            }),
            'professor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sala': forms.Select(attrs={
                'class': 'form-select'
            }),
            'dia_semana': forms.Select(attrs={
                'class': 'form-select'
            }),
            'horario_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'horario_fim': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            })
        }
        help_texts = {
            'turma': 'Turma que terá a aula',
            'disciplina': 'Disciplina a ser lecionada',
            'professor': 'Professor que ministrará a aula',
            'sala': 'Sala onde ocorrerá a aula',
            'dia_semana': 'Dia da semana da aula',
            'horario_inicio': 'Horário de início da aula',
            'horario_fim': 'Horário de término da aula'
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com dados ativos.
        """
        super().__init__(*args, **kwargs)
        self.fields['turma'].queryset = Turma.objects.filter(ativa=True)
        self.fields['disciplina'].queryset = Disciplina.objects.filter(ativa=True)
        self.fields['professor'].queryset = Professor.objects.filter(ativo=True)
        self.fields['sala'].queryset = Sala.objects.filter(ativa=True)

    def clean(self):
        """
        Valida o formulário completo verificando conflitos.
        
        Returns:
            dict: Dados limpos e validados
            
        Raises:
            ValidationError: Se houver conflitos de horário
        """
        cleaned_data = super().clean()
        
        turma = cleaned_data.get('turma')
        disciplina = cleaned_data.get('disciplina')
        professor = cleaned_data.get('professor')
        sala = cleaned_data.get('sala')
        dia_semana = cleaned_data.get('dia_semana')
        horario_inicio = cleaned_data.get('horario_inicio')
        horario_fim = cleaned_data.get('horario_fim')

        if not all([turma, disciplina, professor, sala, dia_semana, horario_inicio, horario_fim]):
            return cleaned_data

        # Validar horários
        if horario_inicio >= horario_fim:
            raise ValidationError('O horário de início deve ser anterior ao horário de fim.')

        # Verificar se a disciplina está na turma
        if disciplina not in turma.disciplinas.all():
            raise ValidationError('A disciplina selecionada não está associada à turma.')

        # Verificar se o professor leciona a disciplina
        if disciplina not in professor.disciplinas.all():
            raise ValidationError('O professor selecionado não leciona esta disciplina.')

        # Verificar conflitos de horário (excluindo o próprio objeto se for edição)
        conflitos = Horario.objects.filter(
            dia_semana=dia_semana,
            horario_inicio__lt=horario_fim,
            horario_fim__gt=horario_inicio
        )
        
        if self.instance.pk:
            conflitos = conflitos.exclude(pk=self.instance.pk)

        # Verificar conflito de professor
        if conflitos.filter(professor=professor).exists():
            raise ValidationError('O professor já possui aula neste horário.')

        # Verificar conflito de sala
        if conflitos.filter(sala=sala).exists():
            raise ValidationError('A sala já está ocupada neste horário.')

        # Verificar conflito de turma
        if conflitos.filter(turma=turma).exists():
            raise ValidationError('A turma já possui aula neste horário.')

        return cleaned_data


class GerarHorariosForm(forms.Form):
    """
    Formulário para configuração da geração automática de horários.
    
    Permite configurar parâmetros para o algoritmo de geração
    automática de horários.
    """
    
    respeitar_preferencias = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Considerar as preferências dos professores na geração'
    )
    
    evitar_janelas = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Tentar evitar janelas nos horários dos professores'
    )
    
    distribuir_dias = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Distribuir aulas ao longo dos dias da semana'
    )
    
    limpar_anteriores = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Remover horários existentes antes de gerar novos'
    )
    
    turmas_selecionadas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.filter(ativa=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 5
        }),
        help_text='Deixe vazio para gerar horários para todas as turmas ativas'
    )

