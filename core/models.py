"""
Modelos de dados para o sistema de gerenciamento de horários escolares.

Este módulo contém todos os modelos necessários para gerenciar disciplinas,
salas, professores, turmas, preferências e horários.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class PeriodoLetivo(models.Model):
    """
    Modelo para representar períodos letivos (semestres/anos).
    
    Permite organizar horários por período, facilitando o controle
    de diferentes semestres e anos letivos.
    """
    TIPOS_PERIODO = [
        ('semestre', 'Semestre'),
        ('trimestre', 'Trimestre'),
        ('anual', 'Anual'),
        ('bimestre', 'Bimestre'),
    ]
    
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome do Período",
        help_text="Ex: 2024.1, 2024.2, 1º Semestre 2024"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição detalhada do período letivo",
        blank=True
    )
    tipo_periodo = models.CharField(
        max_length=20,
        choices=TIPOS_PERIODO,
        default='semestre',
        verbose_name="Tipo de Período",
        help_text="Tipo do período letivo"
    )
    data_inicio = models.DateField(
        verbose_name="Data de Início",
        help_text="Data de início do período letivo"
    )
    data_fim = models.DateField(
        verbose_name="Data de Fim",
        help_text="Data de fim do período letivo"
    )
    ativo = models.BooleanField(
        default=False,
        verbose_name="Período Ativo",
        help_text="Apenas um período pode estar ativo por vez"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Período Letivo"
        verbose_name_plural = "Períodos Letivos"
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_periodo_display()})"
    
    def clean(self):
        """Validação customizada do modelo."""
        from django.core.exceptions import ValidationError
        
        if self.data_inicio >= self.data_fim:
            raise ValidationError("Data de início deve ser anterior à data de fim.")
        
        # Apenas um período pode estar ativo
        if self.ativo:
            outros_ativos = PeriodoLetivo.objects.filter(ativo=True).exclude(pk=self.pk)
            if outros_ativos.exists():
                raise ValidationError("Já existe um período letivo ativo. Desative-o primeiro.")
    
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para incluir validação."""
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_periodo_ativo(cls):
        """Retorna o período letivo ativo atual."""
        return cls.objects.filter(ativo=True).first()


class AuditoriaHorario(models.Model):
    """
    Modelo para auditoria de mudanças nos horários.
    
    Registra todas as alterações feitas nos horários para
    controle e rastreabilidade.
    """
    ACOES = [
        ('criado', 'Criado'),
        ('modificado', 'Modificado'),
        ('movido', 'Movido'),
        ('deletado', 'Deletado'),
        ('ativado', 'Ativado'),
        ('desativado', 'Desativado'),
    ]
    
    horario = models.ForeignKey(
        'Horario',
        on_delete=models.CASCADE,
        verbose_name="Horário",
        related_name="auditorias",
        null=True,
        blank=True
    )
    acao = models.CharField(
        max_length=20,
        choices=ACOES,
        verbose_name="Ação Realizada"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Usuário",
        null=True,
        blank=True
    )
    dados_anteriores = models.JSONField(
        verbose_name="Dados Anteriores",
        null=True,
        blank=True,
        help_text="Estado anterior do horário (JSON)"
    )
    dados_novos = models.JSONField(
        verbose_name="Dados Novos",
        null=True,
        blank=True,
        help_text="Estado novo do horário (JSON)"
    )
    observacoes = models.TextField(
        verbose_name="Observações",
        blank=True,
        help_text="Observações sobre a mudança"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Endereço IP",
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora"
    )
    
    class Meta:
        verbose_name = "Auditoria de Horário"
        verbose_name_plural = "Auditorias de Horários"
        ordering = ['-timestamp']
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"{self.get_acao_display()} - {usuario_str} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class EventoAcademico(models.Model):
    """
    Modelo para eventos acadêmicos que afetam o calendário.
    
    Permite registrar feriados, períodos de prova, eventos especiais
    que podem impactar a geração de horários.
    """
    TIPOS_EVENTO = [
        ('feriado', 'Feriado'),
        ('recesso', 'Recesso'),
        ('prova', 'Período de Provas'),
        ('evento', 'Evento Especial'),
        ('reuniao', 'Reunião/Conselho'),
        ('formatura', 'Formatura'),
        ('outro', 'Outro'),
    ]
    
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Evento",
        help_text="Nome ou descrição do evento"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        help_text="Descrição detalhada do evento"
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPOS_EVENTO,
        default='evento',
        verbose_name="Tipo de Evento"
    )
    data_inicio = models.DateField(
        verbose_name="Data de Início",
        help_text="Data de início do evento"
    )
    data_fim = models.DateField(
        verbose_name="Data de Fim",
        help_text="Data de fim do evento (igual ao início para eventos de um dia)"
    )
    hora_inicio = models.TimeField(
        verbose_name="Hora de Início",
        null=True,
        blank=True,
        help_text="Hora de início (deixe vazio para o dia todo)"
    )
    hora_fim = models.TimeField(
        verbose_name="Hora de Fim",
        null=True,
        blank=True,
        help_text="Hora de fim (deixe vazio para o dia todo)"
    )
    afeta_aulas = models.BooleanField(
        default=True,
        verbose_name="Afeta Aulas",
        help_text="Se este evento impede a realização de aulas"
    )
    turnos_afetados = models.CharField(
        max_length=50,
        verbose_name="Turnos Afetados",
        blank=True,
        help_text="Turnos afetados (deixe vazio para todos). Ex: 'manha,tarde'"
    )
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo,
        on_delete=models.CASCADE,
        verbose_name="Período Letivo",
        related_name="eventos",
        null=True,
        blank=True
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se o evento está ativo no sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento Acadêmico"
        verbose_name_plural = "Eventos Acadêmicos"
        ordering = ['data_inicio']
    
    def __str__(self):
        if self.data_inicio == self.data_fim:
            data_str = self.data_inicio.strftime("%d/%m/%Y")
        else:
            data_str = f"{self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')}"
        
        return f"{self.nome} - {data_str}"
    
    def clean(self):
        """Validação customizada do modelo."""
        from django.core.exceptions import ValidationError
        
        if self.data_inicio > self.data_fim:
            raise ValidationError("Data de início deve ser anterior ou igual à data de fim.")
        
        if self.hora_inicio and self.hora_fim and self.hora_inicio >= self.hora_fim:
            raise ValidationError("Hora de início deve ser anterior à hora de fim.")
    
    def conflita_com_data(self, data, turno=None):
        """
        Verifica se este evento conflita com uma data específica.
        
        Args:
            data: Data a verificar (datetime.date)
            turno: Turno específico (opcional)
            
        Returns:
            bool: True se há conflito, False caso contrário
        """
        if not self.ativo or not self.afeta_aulas:
            return False
        
        # Verificar se a data está no período do evento
        if not (self.data_inicio <= data <= self.data_fim):
            return False
        
        # Verificar turnos afetados
        if turno and self.turnos_afetados:
            turnos_lista = [t.strip() for t in self.turnos_afetados.split(',')]
            if turno not in turnos_lista:
                return False
        
        return True


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
        periodo_letivo: Período letivo do horário
        ativo: Se o horário está ativo
        observacoes: Observações sobre o horário
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
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo,
        on_delete=models.CASCADE,
        verbose_name="Período Letivo",
        related_name="horarios",
        null=True,
        blank=True,
        help_text="Período letivo deste horário"
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
    observacoes = models.TextField(
        verbose_name="Observações",
        blank=True,
        help_text="Observações sobre este horário específico"
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
        # Evitar duplicatas exatas
        unique_together = [
            ['turma', 'dia_semana', 'horario_inicio', 'horario_fim', 'periodo_letivo'],
            ['professor', 'dia_semana', 'horario_inicio', 'horario_fim', 'periodo_letivo'],
            ['sala', 'dia_semana', 'horario_inicio', 'horario_fim', 'periodo_letivo'],
        ]

    def __str__(self):
        """Representação string do modelo."""
        return f"{self.turma} - {self.disciplina} - {self.get_dia_semana_display()} {self.horario_inicio}-{self.horario_fim}"

    def clean(self):
        """Validação customizada do modelo."""
        from django.core.exceptions import ValidationError
        
        if self.horario_inicio >= self.horario_fim:
            raise ValidationError("Horário de início deve ser anterior ao horário de fim.")
        
        # Verificar se a sala comporta a turma
        if self.sala.capacidade < self.turma.numero_alunos:
            raise ValidationError(
                f"Sala {self.sala.nome_numero} tem capacidade para {self.sala.capacidade} alunos, "
                f"mas a turma {self.turma.nome_codigo} possui {self.turma.numero_alunos} alunos."
            )
        
        # Verificar se a turma pode ter aula neste turno
        if not self.turma.pode_ter_aula_no_turno(self.turno):
            raise ValidationError(
                f"Turma {self.turma.nome_codigo} não pode ter aulas no turno {self.get_turno_display()}."
            )
        
        # Verificar se o professor pode lecionar esta disciplina
        if not self.professor.disciplinas.filter(id=self.disciplina.id).exists():
            # Permitir se não há restrição de disciplinas para o professor
            if self.professor.disciplinas.exists():
                raise ValidationError(
                    f"Professor {self.professor.nome_completo} não está habilitado para lecionar {self.disciplina.nome}."
                )
        
        # Verificar eventos acadêmicos que impedem aulas
        if self.periodo_letivo:
            from datetime import date, timedelta
            # Simulação de uma data para verificação (em um cenário real, seria baseado no período)
            data_exemplo = self.periodo_letivo.data_inicio + timedelta(days=self.dia_semana)
            eventos_conflitantes = EventoAcademico.objects.filter(
                periodo_letivo=self.periodo_letivo,
                ativo=True,
                afeta_aulas=True
            )
            
            for evento in eventos_conflitantes:
                if evento.conflita_com_data(data_exemplo, self.turno):
                    raise ValidationError(
                        f"Conflito com evento acadêmico: {evento.nome} "
                        f"({evento.data_inicio.strftime('%d/%m/%Y')} a {evento.data_fim.strftime('%d/%m/%Y')})"
                    )
        
        # Verificar se o professor está disponível neste horário
        if not self.professor.disponivel_para_horario(
            dia_semana=self.dia_semana,
            turno=self.turno,
            disciplina=self.disciplina
        ):
            raise ValidationError(f"Professor {self.professor} não está disponível neste horário.")
        
        # Verificar conflitos de horário para o professor
        conflitos_professor = Horario.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana,
            periodo_letivo=self.periodo_letivo,
            ativo=True
        ).exclude(pk=self.pk)
        
        for conflito in conflitos_professor:
            if (self.horario_inicio < conflito.horario_fim and 
                self.horario_fim > conflito.horario_inicio):
                raise ValidationError(
                    f"Professor {self.professor} já possui aula neste horário: "
                    f"{conflito.disciplina} ({conflito.horario_inicio}-{conflito.horario_fim})"
                )
        
        # Verificar conflitos de horário para a sala
        conflitos_sala = Horario.objects.filter(
            sala=self.sala,
            dia_semana=self.dia_semana,
            periodo_letivo=self.periodo_letivo,
            ativo=True
        ).exclude(pk=self.pk)
        
        for conflito in conflitos_sala:
            if (self.horario_inicio < conflito.horario_fim and 
                self.horario_fim > conflito.horario_inicio):
                raise ValidationError(
                    f"Sala {self.sala} já está ocupada neste horário: "
                    f"{conflito.turma} - {conflito.disciplina} ({conflito.horario_inicio}-{conflito.horario_fim})"
                )
        
        # Verificar se a turma já tem aula neste horário
        conflitos_turma = Horario.objects.filter(
            turma=self.turma,
            dia_semana=self.dia_semana,
            periodo_letivo=self.periodo_letivo,
            ativo=True
        ).exclude(pk=self.pk)
        
        for conflito in conflitos_turma:
            if (self.horario_inicio < conflito.horario_fim and 
                self.horario_fim > conflito.horario_inicio):
                raise ValidationError(
                    f"Turma {self.turma} já possui aula neste horário: "
                    f"{conflito.disciplina} ({conflito.horario_inicio}-{conflito.horario_fim})"
                )

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para incluir validação e auditoria."""
        # Definir período letivo padrão se não informado
        if not self.periodo_letivo:
            self.periodo_letivo = PeriodoLetivo.get_periodo_ativo()
        
        # Capturar dados para auditoria
        dados_anteriores = None
        acao = 'criado'
        
        if self.pk:
            try:
                obj_anterior = Horario.objects.get(pk=self.pk)
                dados_anteriores = {
                    'turma': str(obj_anterior.turma),
                    'disciplina': str(obj_anterior.disciplina),
                    'professor': str(obj_anterior.professor),
                    'sala': str(obj_anterior.sala),
                    'dia_semana': obj_anterior.dia_semana,
                    'turno': obj_anterior.turno,
                    'horario_inicio': obj_anterior.horario_inicio.strftime('%H:%M'),
                    'horario_fim': obj_anterior.horario_fim.strftime('%H:%M'),
                    'ativo': obj_anterior.ativo,
                }
                acao = 'modificado'
            except Horario.DoesNotExist:
                pass
        
        self.clean()
        super().save(*args, **kwargs)
        
        # Criar registro de auditoria
        dados_novos = {
            'turma': str(self.turma),
            'disciplina': str(self.disciplina),
            'professor': str(self.professor),
            'sala': str(self.sala),
            'dia_semana': self.dia_semana,
            'turno': self.turno,
            'horario_inicio': self.horario_inicio.strftime('%H:%M'),
            'horario_fim': self.horario_fim.strftime('%H:%M'),
            'ativo': self.ativo,
        }
        
        AuditoriaHorario.objects.create(
            horario=self,
            acao=acao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            observacoes=f"Horário {acao} via sistema"
        )
    
    def get_carga_horaria_semanal_turma_disciplina(self):
        """
        Retorna a carga horária semanal atual da disciplina para esta turma.
        """
        return Horario.objects.filter(
            turma=self.turma,
            disciplina=self.disciplina,
            periodo_letivo=self.periodo_letivo,
            ativo=True
        ).count()
    
    def validar_carga_horaria_completa(self):
        """
        Verifica se a carga horária da disciplina está completa para a turma.
        
        Returns:
            tuple: (bool, str) - (está_completa, mensagem)
        """
        carga_atual = self.get_carga_horaria_semanal_turma_disciplina()
        carga_necessaria = self.disciplina.carga_horaria_semanal
        
        if carga_atual < carga_necessaria:
            return False, f"Faltam {carga_necessaria - carga_atual} aulas de {self.disciplina.nome} para a turma {self.turma.nome_codigo}"
        elif carga_atual > carga_necessaria:
            return False, f"Excesso de {carga_atual - carga_necessaria} aulas de {self.disciplina.nome} para a turma {self.turma.nome_codigo}"
        else:
            return True, f"Carga horária completa para {self.disciplina.nome} na turma {self.turma.nome_codigo}"


class NotificacaoSistema(models.Model):
    """
    Modelo para notificações do sistema.
    
    Permite enviar avisos e alertas para usuários sobre
    conflitos, mudanças e eventos importantes.
    """
    TIPOS_NOTIFICACAO = [
        ('conflito', 'Conflito de Horários'),
        ('mudanca', 'Mudança de Horário'),
        ('evento', 'Evento Acadêmico'),
        ('sistema', 'Sistema'),
        ('aviso', 'Aviso Geral'),
        ('erro', 'Erro'),
    ]
    
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name="notificacoes",
        null=True,
        blank=True,
        help_text="Usuário específico (vazio = notificação global)"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título da notificação"
    )
    mensagem = models.TextField(
        verbose_name="Mensagem",
        help_text="Conteúdo da notificação"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_NOTIFICACAO,
        default='aviso',
        verbose_name="Tipo de Notificação"
    )
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADES,
        default='normal',
        verbose_name="Prioridade"
    )
    lida = models.BooleanField(
        default=False,
        verbose_name="Lida",
        help_text="Se a notificação foi lida pelo usuário"
    )
    data_leitura = models.DateTimeField(
        verbose_name="Data de Leitura",
        null=True,
        blank=True
    )
    link_acao = models.URLField(
        verbose_name="Link de Ação",
        blank=True,
        help_text="Link para ação relacionada à notificação"
    )
    dados_contexto = models.JSONField(
        verbose_name="Dados de Contexto",
        null=True,
        blank=True,
        help_text="Dados adicionais sobre a notificação (JSON)"
    )
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a notificação está ativa no sistema"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(
        verbose_name="Data de Expiração",
        null=True,
        blank=True,
        help_text="Data em que a notificação expira (opcional)"
    )
    
    class Meta:
        verbose_name = "Notificação do Sistema"
        verbose_name_plural = "Notificações do Sistema"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'lida']),
            models.Index(fields=['tipo', 'prioridade']),
            models.Index(fields=['data_criacao']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Global"
        return f"{self.titulo} - {usuario_str} ({self.get_tipo_display()})"
    
    def marcar_como_lida(self):
        """Marca a notificação como lida."""
        from django.utils import timezone
        self.lida = True
        self.data_leitura = timezone.now()
        self.save(update_fields=['lida', 'data_leitura'])
    
    def esta_expirada(self):
        """Verifica se a notificação está expirada."""
        from django.utils import timezone
        if self.data_expiracao:
            return timezone.now() > self.data_expiracao
        return False
    
    @classmethod
    def criar_notificacao_conflito(cls, horario, conflito_tipo, mensagem_adicional=""):
        """
        Cria uma notificação de conflito para um horário.
        
        Args:
            horario: Instância do modelo Horario
            conflito_tipo: Tipo de conflito ('professor', 'sala', 'turma')
            mensagem_adicional: Mensagem adicional (opcional)
        """
        titulo = f"Conflito de {conflito_tipo.title()} Detectado"
        mensagem = f"Conflito detectado no horário:\n"
        mensagem += f"• Turma: {horario.turma}\n"
        mensagem += f"• Disciplina: {horario.disciplina}\n"
        mensagem += f"• Professor: {horario.professor}\n"
        mensagem += f"• Sala: {horario.sala}\n"
        mensagem += f"• Horário: {horario.get_dia_semana_display()} {horario.horario_inicio}-{horario.horario_fim}\n"
        
        if mensagem_adicional:
            mensagem += f"\nDetalhes: {mensagem_adicional}"
        
        return cls.objects.create(
            titulo=titulo,
            mensagem=mensagem,
            tipo='conflito',
            prioridade='alta',
            dados_contexto={
                'horario_id': horario.id,
                'conflito_tipo': conflito_tipo,
                'turma_id': horario.turma.id,
                'professor_id': horario.professor.id,
                'sala_id': horario.sala.id,
            }
        )
    
    @classmethod
    def criar_notificacao_mudanca(cls, horario_anterior, horario_novo, usuario=None):
        """
        Cria uma notificação de mudança de horário.
        
        Args:
            horario_anterior: Dados do horário anterior (dict)
            horario_novo: Instância do horário novo
            usuario: Usuário que fez a mudança (opcional)
        """
        titulo = "Horário Alterado"
        mensagem = f"Horário alterado:\n\n"
        
        if horario_anterior:
            mensagem += f"ANTES:\n"
            mensagem += f"• Dia: {dict(Horario.DIAS_SEMANA)[horario_anterior['dia_semana']]}\n"
            mensagem += f"• Horário: {horario_anterior['horario_inicio']}-{horario_anterior['horario_fim']}\n"
            mensagem += f"• Sala: {horario_anterior['sala']}\n\n"
        
        mensagem += f"AGORA:\n"
        mensagem += f"• Dia: {horario_novo.get_dia_semana_display()}\n"
        mensagem += f"• Horário: {horario_novo.horario_inicio}-{horario_novo.horario_fim}\n"
        mensagem += f"• Sala: {horario_novo.sala}\n"
        mensagem += f"• Turma: {horario_novo.turma}\n"
        mensagem += f"• Disciplina: {horario_novo.disciplina}\n"
        mensagem += f"• Professor: {horario_novo.professor}"
        
        return cls.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensagem=mensagem,
            tipo='mudanca',
            prioridade='normal',
            dados_contexto={
                'horario_id': horario_novo.id,
                'horario_anterior': horario_anterior,
                'alterado_por': usuario.username if usuario else 'Sistema',
            }
        )
