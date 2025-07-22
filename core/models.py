"""
Modelos de dados para o sistema de gerenciamento de horários escolares.

Este módulo contém todos os modelos necessários para gerenciar disciplinas,
salas, professores, turmas, preferências e horários.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Disciplina(models.Model):
    """
    Modelo para representar uma disciplina escolar.
    
    Attributes:
        nome: Nome da disciplina
        carga_horaria_semanal: Número de aulas por semana
        curso_area: Curso ou área da disciplina
        periodo_serie: Período ou série da disciplina
        ativa: Se a disciplina está ativa no sistema
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome da Disciplina",
        help_text="Nome completo da disciplina"
    )
    carga_horaria_semanal = models.PositiveIntegerField(
        verbose_name="Carga Horária Semanal",
        help_text="Número de aulas por semana",
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    curso_area = models.CharField(
        max_length=100,
        verbose_name="Curso/Área",
        help_text="Curso ou área da disciplina"
    )
    periodo_serie = models.CharField(
        max_length=50,
        verbose_name="Período/Série",
        help_text="Período ou série da disciplina"
    )
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a disciplina está ativa no sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ['nome']

    def __str__(self):
        """Representação string do modelo."""
        return f"{self.nome} ({self.periodo_serie})"


class Sala(models.Model):
    """
    Modelo para representar uma sala de aula.
    
    Attributes:
        nome_numero: Nome ou número da sala
        tipo: Tipo da sala (normal, laboratório, auditório)
        capacidade: Capacidade máxima de alunos
        ativa: Se a sala está ativa no sistema
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    TIPOS_SALA = [
        ('normal', 'Sala Normal'),
        ('laboratorio', 'Laboratório'),
        ('auditorio', 'Auditório'),
    ]
    
    nome_numero = models.CharField(
        max_length=50,
        verbose_name="Nome/Número da Sala",
        help_text="Nome ou número identificador da sala"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_SALA,
        default='normal',
        verbose_name="Tipo da Sala",
        help_text="Tipo da sala de aula"
    )
    capacidade = models.PositiveIntegerField(
        verbose_name="Capacidade",
        help_text="Capacidade máxima de alunos",
        validators=[MinValueValidator(1), MaxValueValidator(200)]
    )
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a sala está ativa no sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        ordering = ['nome_numero']

    def __str__(self):
        """Representação string do modelo."""
        return f"{self.nome_numero} ({self.get_tipo_display()})"


class Professor(models.Model):
    """
    Modelo para representar um professor.
    
    Attributes:
        nome_completo: Nome completo do professor
        email: Email do professor
        telefone: Telefone do professor
        especialidade: Área de especialidade do professor
        disciplinas: Disciplinas que o professor pode lecionar
        ativo: Se o professor está ativo no sistema
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    nome_completo = models.CharField(
        max_length=150,
        verbose_name="Nome Completo",
        help_text="Nome completo do professor"
    )
    email = models.EmailField(
        max_length=100,
        verbose_name="E-mail",
        help_text="Endereço de e-mail do professor",
        blank=True
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        help_text="Telefone de contato do professor",
        blank=True
    )
    especialidade = models.CharField(
        max_length=100,
        verbose_name="Especialidade",
        help_text="Área de especialidade ou formação principal",
        blank=True
    )
    disciplinas = models.ManyToManyField(
        Disciplina,
        verbose_name="Disciplinas",
        help_text="Disciplinas que o professor pode lecionar",
        blank=True
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se o professor está ativo no sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ['nome_completo']

    def __str__(self):
        """Representação string do modelo."""
        return self.nome_completo


class Turma(models.Model):
    """
    Modelo para representar uma turma.
    
    Attributes:
        nome_codigo: Nome ou código da turma
        serie_periodo: Série ou período da turma
        disciplinas: Disciplinas cursadas pela turma
        numero_alunos: Número de alunos na turma
        ativa: Se a turma está ativa no sistema
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    nome_codigo = models.CharField(
        max_length=50,
        verbose_name="Nome/Código",
        help_text="Nome ou código identificador da turma"
    )
    serie_periodo = models.CharField(
        max_length=50,
        verbose_name="Série/Período",
        help_text="Série ou período da turma"
    )
    disciplinas = models.ManyToManyField(
        Disciplina,
        verbose_name="Disciplinas",
        help_text="Disciplinas cursadas pela turma",
        blank=True
    )
    numero_alunos = models.PositiveIntegerField(
        verbose_name="Número de Alunos",
        help_text="Quantidade de alunos na turma",
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a turma está ativa no sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ['nome_codigo']

    def __str__(self):
        """Representação string do modelo."""
        return f"{self.nome_codigo} ({self.serie_periodo})"


class PreferenciaProfessor(models.Model):
    """
    Modelo para representar preferências e restrições de um professor.
    
    Attributes:
        professor: Professor relacionado
        dia_semana: Dia da semana (0=Segunda, 6=Domingo)
        turno: Turno (manhã, tarde, noite)
        disponivel: Se o professor está disponível neste horário
        preferencial: Se é um horário preferencial
        observacoes: Observações adicionais
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    TURNOS = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    ]
    
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        verbose_name="Professor",
        related_name="preferencias"
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        verbose_name="Disciplina",
        related_name="preferencias_professores",
        null=True,
        blank=True,
        help_text="Disciplina específica (deixe vazio para qualquer disciplina)"
    )
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA,
        verbose_name="Dia da Semana",
        null=True,
        blank=True,
        help_text="Dia da semana específico (deixe vazio para qualquer dia)"
    )
    turno = models.CharField(
        max_length=10,
        choices=TURNOS,
        verbose_name="Turno",
        blank=True,
        help_text="Turno específico (deixe vazio para qualquer turno)"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Observações adicionais sobre esta preferência"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferência do Professor"
        verbose_name_plural = "Preferências dos Professores"
        ordering = ['professor__nome_completo', 'dia_semana', 'turno']

    def __str__(self):
        """Representação string do modelo."""
        partes = [str(self.professor)]
        if self.disciplina:
            partes.append(f"- {self.disciplina.nome}")
        if self.dia_semana is not None:
            partes.append(f"- {self.get_dia_semana_display()}")
        if self.turno:
            partes.append(f"- {self.get_turno_display()}")
        return " ".join(partes)


class Horario(models.Model):
    """
    Modelo para representar um horário de aula.
    
    Attributes:
        turma: Turma que terá a aula
        disciplina: Disciplina da aula
        professor: Professor que ministrará a aula
        sala: Sala onde ocorrerá a aula
        dia_semana: Dia da semana (0=Segunda, 6=Domingo)
        turno: Turno da aula
        horario_inicio: Horário de início da aula
        horario_fim: Horário de fim da aula
        ativo: Se o horário está ativo
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    TURNOS = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    ]
    
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        verbose_name="Turma",
        related_name="horarios"
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        verbose_name="Disciplina",
        related_name="horarios"
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        verbose_name="Professor",
        related_name="horarios"
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        verbose_name="Sala",
        related_name="horarios"
    )
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA,
        verbose_name="Dia da Semana"
    )
    turno = models.CharField(
        max_length=10,
        choices=TURNOS,
        verbose_name="Turno"
    )
    horario_inicio = models.TimeField(
        verbose_name="Horário de Início"
    )
    horario_fim = models.TimeField(
        verbose_name="Horário de Fim"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se o horário está ativo"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Horário"
        verbose_name_plural = "Horários"
        ordering = ['dia_semana', 'horario_inicio']

    def __str__(self):
        """Representação string do modelo."""
        return f"{self.turma} - {self.disciplina} - {self.get_dia_semana_display()} {self.horario_inicio}-{self.horario_fim}"

    def clean(self):
        """Validação customizada do modelo."""
        from django.core.exceptions import ValidationError
        
        if self.horario_inicio >= self.horario_fim:
            raise ValidationError("Horário de início deve ser anterior ao horário de fim.")
        
        # Verificar se o professor pode dar aula neste horário
        preferencia = PreferenciaProfessor.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana,
            turno=self.turno
        ).first()
        
        if preferencia and not preferencia.disponivel:
            raise ValidationError(f"Professor {self.professor} não está disponível neste horário.")
        
        # Verificar conflitos de horário para o professor
        conflitos_professor = Horario.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana,
            ativo=True
        ).exclude(pk=self.pk)
        
        for conflito in conflitos_professor:
            if (self.horario_inicio < conflito.horario_fim and 
                self.horario_fim > conflito.horario_inicio):
                raise ValidationError(f"Professor {self.professor} já possui aula neste horário.")
        
        # Verificar conflitos de horário para a sala
        conflitos_sala = Horario.objects.filter(
            sala=self.sala,
            dia_semana=self.dia_semana,
            ativo=True
        ).exclude(pk=self.pk)
        
        for conflito in conflitos_sala:
            if (self.horario_inicio < conflito.horario_fim and 
                self.horario_fim > conflito.horario_inicio):
                raise ValidationError(f"Sala {self.sala} já está ocupada neste horário.")
        
        # Verificar se a turma já tem aula neste horário
        conflitos_turma = Horario.objects.filter(
            turma=self.turma,
            dia_semana=self.dia_semana,
            ativo=True
        ).exclude(pk=self.pk)
        
        for conflito in conflitos_turma:
            if (self.horario_inicio < conflito.horario_fim and 
                self.horario_fim > conflito.horario_inicio):
                raise ValidationError(f"Turma {self.turma} já possui aula neste horário.")

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para incluir validação."""
        self.clean()
        super().save(*args, **kwargs)
