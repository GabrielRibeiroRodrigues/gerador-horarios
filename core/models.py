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

    def disponivel_para_horario(self, dia_semana=None, turno=None, disciplina=None, data_especifica=None):
        """
        Verifica se o professor está disponível para um horário específico.
        
        Args:
            dia_semana: Dia da semana (0-6)
            turno: Turno ('manha', 'tarde', 'noite')
            disciplina: Disciplina específica
            data_especifica: Data específica para verificar bloqueios (datetime.date)
            
        Returns:
            bool: True se disponível, False caso contrário
        """
        # Verificar bloqueios temporários primeiro
        if data_especifica:
            for bloqueio in self.bloqueios.filter(ativo=True):
                if not bloqueio.professor_disponivel_na_data(data_especifica, turno):
                    return False
        
        # Buscar preferências específicas
        preferencias = self.preferencias.all()
        
        # Se não há preferências configuradas, assume disponível (sem bloqueios)
        if not preferencias.exists():
            return True
        
        # Filtrar preferências relevantes
        filtros = {}
        if dia_semana is not None:
            filtros['dia_semana'] = dia_semana
        if turno:
            filtros['turno'] = turno
        if disciplina:
            filtros['disciplina'] = disciplina
        
        # Buscar preferência específica
        pref_especifica = preferencias.filter(**filtros).first()
        if pref_especifica:
            return pref_especifica.disponivel
        
        # Se não há preferência específica, buscar por padrões mais gerais
        for campo in ['disciplina', 'turno', 'dia_semana']:
            if campo in filtros:
                del filtros[campo]
                pref_geral = preferencias.filter(**filtros).first()
                if pref_geral:
                    return pref_geral.disponivel
        
        # Se não encontrou nenhuma preferência específica, assume disponível
        return True

    def get_preferencia_score(self, dia_semana=None, turno=None, disciplina=None, data_especifica=None):
        """
        Retorna score de preferência para um horário específico.
        
        Returns:
            int: Score de 1-5 (1=indisponível, 5=altamente preferencial)
        """
        if not self.disponivel_para_horario(dia_semana, turno, disciplina, data_especifica):
            return 1
        
        # Buscar preferência mais específica
        preferencias = self.preferencias.all()
        
        filtros = {}
        if dia_semana is not None:
            filtros['dia_semana'] = dia_semana
        if turno:
            filtros['turno'] = turno
        if disciplina:
            filtros['disciplina'] = disciplina
        
        pref = preferencias.filter(**filtros).first()
        if pref:
            return pref.prioridade
        
        return 3  # Score neutro se não há preferência específica

    def get_bloqueios_ativos(self, data_inicio=None, data_fim=None):
        """
        Retorna bloqueios ativos do professor em um período.
        
        Args:
            data_inicio: Data de início do período (opcional)
            data_fim: Data de fim do período (opcional)
            
        Returns:
            QuerySet: Bloqueios ativos no período
        """
        bloqueios = self.bloqueios.filter(ativo=True)
        
        if data_inicio:
            bloqueios = bloqueios.filter(data_fim__gte=data_inicio)
        if data_fim:
            bloqueios = bloqueios.filter(data_inicio__lte=data_fim)
        
        return bloqueios.order_by('data_inicio')


class Turma(models.Model):
    """
    Modelo para representar uma turma.
    
    Attributes:
        nome_codigo: Nome ou código da turma
        serie_periodo: Série ou período da turma
        turno_turma: Turno específico da turma (matutino, vespertino, integral, noturno)
        disciplinas: Disciplinas cursadas pela turma
        numero_alunos: Número de alunos na turma
        ativa: Se a turma está ativa no sistema
        criado_em: Data de criação do registro
        atualizado_em: Data da última atualização
    """
    TURNOS_TURMA = [
        ('matutino', 'Matutino (Manhã)'),
        ('vespertino', 'Vespertino (Tarde)'),
        ('noturno', 'Noturno (Noite)'),
        ('integral', 'Integral (Manhã e Tarde)'),
        ('flexivel', 'Flexível (Qualquer Turno)'),
    ]
    
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
    turno_turma = models.CharField(
        max_length=15,
        choices=TURNOS_TURMA,
        default='flexivel',
        verbose_name="Turno da Turma",
        help_text="Turno específico em que a turma estuda"
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
        return f"{self.nome_codigo} ({self.serie_periodo}) - {self.get_turno_turma_display()}"

    def get_turnos_permitidos(self):
        """
        Retorna lista de turnos permitidos baseado no turno da turma.
        
        Returns:
            list: Lista de turnos permitidos para esta turma
        """
        if self.turno_turma == 'matutino':
            return ['manha']
        elif self.turno_turma == 'vespertino':
            return ['tarde']
        elif self.turno_turma == 'noturno':
            return ['noite']
        elif self.turno_turma == 'integral':
            return ['manha', 'tarde']
        else:  # flexivel
            return ['manha', 'tarde', 'noite']

    def pode_ter_aula_no_turno(self, turno):
        """
        Verifica se a turma pode ter aula em um turno específico.
        
        Args:
            turno: Turno a verificar ('manha', 'tarde', 'noite')
            
        Returns:
            bool: True se pode ter aula, False caso contrário
        """
        return turno in self.get_turnos_permitidos()

    def get_horarios_disponiveis_por_turno(self):
        """
        Retorna dicionário com horários disponíveis por turno para esta turma.
        
        Returns:
            dict: Dicionário com turnos como chave e horários como valor
        """
        from datetime import time
        
        horarios_base = {
            'manha': [
                (time(7, 0), time(7, 50)),
                (time(7, 50), time(8, 40)),
                (time(9, 0), time(9, 50)),
                (time(9, 50), time(10, 40)),
                (time(10, 40), time(11, 30)),
                (time(11, 30), time(12, 20)),
            ],
            'tarde': [
                (time(13, 0), time(13, 50)),
                (time(13, 50), time(14, 40)),
                # Intervalo das 14:50 às 15:10
                (time(15, 10), time(16, 0)),
                (time(16, 0), time(16, 50)),
                (time(16, 50), time(17, 40)),
            ],
            'noite': [
                (time(19, 20), time(20, 10)),
                (time(20, 10), time(21, 0)),
                (time(21, 10), time(22, 0)),
                (time(22, 0), time(22, 50)),
            ]
        }
        
        turnos_permitidos = self.get_turnos_permitidos()
        return {turno: horarios for turno, horarios in horarios_base.items() if turno in turnos_permitidos}


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
    disponivel = models.BooleanField(
        default=True,
        verbose_name="Disponível",
        help_text="Se o professor está disponível neste horário/turno/dia"
    )
    preferencial = models.BooleanField(
        default=False,
        verbose_name="Preferencial",
        help_text="Se este é um horário/turno/dia preferencial para o professor"
    )
    prioridade = models.IntegerField(
        default=3,
        choices=[(1, 'Baixa'), (2, 'Média'), (3, 'Normal'), (4, 'Alta'), (5, 'Crítica')],
        verbose_name="Prioridade",
        help_text="Nível de prioridade desta preferência (1=Baixa, 5=Crítica)"
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
        
        # Adicionar status
        status = []
        if not self.disponivel:
            status.append("INDISPONÍVEL")
        elif self.preferencial:
            status.append("PREFERENCIAL")
        if self.prioridade != 3:
            status.append(f"Prioridade: {self.get_prioridade_display()}")
        
        if status:
            partes.append(f"({', '.join(status)})")
        
        return " ".join(partes)

    def clean(self):
        """Validação customizada do modelo."""
        from django.core.exceptions import ValidationError
        
        # Não pode ser preferencial e indisponível ao mesmo tempo
        if not self.disponivel and self.preferencial:
            raise ValidationError("Um horário não pode ser preferencial e indisponível simultaneamente.")
        
        # Se não está disponível, prioridade deve ser baixa
        if not self.disponivel and self.prioridade > 2:
            raise ValidationError("Horários indisponíveis devem ter prioridade baixa (1-2).")
        
        # Se é preferencial, prioridade deve ser alta
        if self.preferencial and self.prioridade < 4:
            raise ValidationError("Horários preferenciais devem ter prioridade alta (4-5).")


class BloqueioTemporario(models.Model):
    """
    Modelo para representar bloqueios temporários de professores.
    
    Permite definir quando um professor não pode dar aula em dias/períodos específicos,
    como licenças, faltas programadas, reuniões, etc.
    """
    TIPOS_BLOQUEIO = [
        ('falta', 'Falta/Ausência'),
        ('licenca', 'Licença'),
        ('reuniao', 'Reunião'),
        ('capacitacao', 'Capacitação/Curso'),
        ('pessoal', 'Motivo Pessoal'),
        ('outros', 'Outros'),
    ]
    
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        verbose_name="Professor",
        related_name="bloqueios"
    )
    data_inicio = models.DateField(
        verbose_name="Data de Início",
        help_text="Data de início do bloqueio"
    )
    data_fim = models.DateField(
        verbose_name="Data de Fim",
        help_text="Data de fim do bloqueio (deixe igual ao início para um dia específico)"
    )
    turno = models.CharField(
        max_length=10,
        choices=PreferenciaProfessor.TURNOS,
        verbose_name="Turno",
        blank=True,
        help_text="Turno específico do bloqueio (deixe vazio para o dia todo)"
    )
    tipo_bloqueio = models.CharField(
        max_length=20,
        choices=TIPOS_BLOQUEIO,
        default='falta',
        verbose_name="Tipo de Bloqueio",
        help_text="Motivo do bloqueio"
    )
    motivo = models.TextField(
        verbose_name="Motivo/Observações",
        help_text="Descrição detalhada do motivo do bloqueio",
        blank=True
    )
    recorrente = models.BooleanField(
        default=False,
        verbose_name="Recorrente",
        help_text="Se este bloqueio se repete semanalmente (ex: toda quarta-feira)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se o bloqueio está ativo"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bloqueio Temporário"
        verbose_name_plural = "Bloqueios Temporários"
        ordering = ['data_inicio', 'professor__nome_completo']

    def __str__(self):
        """Representação string do modelo."""
        if self.data_inicio == self.data_fim:
            data_str = self.data_inicio.strftime("%d/%m/%Y")
        else:
            data_str = f"{self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')}"
        
        turno_str = f" - {self.get_turno_display()}" if self.turno else ""
        recorrente_str = " (Recorrente)" if self.recorrente else ""
        
        return f"{self.professor.nome_completo} - {data_str}{turno_str} - {self.get_tipo_bloqueio_display()}{recorrente_str}"

    def clean(self):
        """Validação customizada do modelo."""
        from django.core.exceptions import ValidationError
        
        if self.data_inicio > self.data_fim:
            raise ValidationError("Data de início deve ser anterior ou igual à data de fim.")

    def professor_disponivel_na_data(self, data, turno=None):
        """
        Verifica se o professor está disponível em uma data específica.
        
        Args:
            data: Data a verificar (datetime.date)
            turno: Turno específico (opcional)
            
        Returns:
            bool: False se bloqueado, True se disponível
        """
        if not self.ativo:
            return True
        
        # Verificar se a data está no período do bloqueio
        if self.recorrente:
            # Para bloqueios recorrentes, verificar dia da semana
            if data.weekday() == self.data_inicio.weekday():
                if not self.turno or not turno or self.turno == turno:
                    return False
        else:
            # Para bloqueios específicos, verificar período
            if self.data_inicio <= data <= self.data_fim:
                if not self.turno or not turno or self.turno == turno:
                    return False
        
        return True


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
