"""
Dashboard analítico para o sistema de horários escolares.

Módulo responsável por gerar relatórios e análises estatísticas
do sistema de horários.
"""

from django.db.models import Count, Q, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
from .models import (
    Horario, Professor, Sala, Turma, Disciplina, 
    PeriodoLetivo, EventoAcademico, NotificacaoSistema,
    AuditoriaHorario
)


class DashboardAnalytico:
    """
    Classe responsável por gerar análises e relatórios do dashboard.
    """
    
    def __init__(self, periodo_letivo=None):
        """
        Inicializa o dashboard com um período letivo específico.
        
        Args:
            periodo_letivo: Instância de PeriodoLetivo (padrão: período ativo)
        """
        self.periodo_letivo = periodo_letivo or PeriodoLetivo.get_periodo_ativo()
    
    def get_estatisticas_gerais(self):
        """
        Retorna estatísticas gerais do sistema.
        
        Returns:
            dict: Dicionário com estatísticas principais
        """
        filtro_periodo = {'periodo_letivo': self.periodo_letivo} if self.periodo_letivo else {}
        
        total_horarios = Horario.objects.filter(ativo=True, **filtro_periodo).count()
        total_professores = Professor.objects.filter(ativo=True).count()
        total_salas = Sala.objects.filter(ativa=True).count()
        total_turmas = Turma.objects.filter(ativa=True).count()
        total_disciplinas = Disciplina.objects.filter(ativa=True).count()
        
        # Estatísticas de ocupação
        horarios_manha = Horario.objects.filter(
            ativo=True, turno='manha', **filtro_periodo
        ).count()
        horarios_tarde = Horario.objects.filter(
            ativo=True, turno='tarde', **filtro_periodo
        ).count()
        horarios_noite = Horario.objects.filter(
            ativo=True, turno='noite', **filtro_periodo
        ).count()
        
        # Notificações não lidas
        notificacoes_nao_lidas = NotificacaoSistema.objects.filter(
            lida=False, ativa=True
        ).count()
        
        # Conflitos críticos
        conflitos_criticos = NotificacaoSistema.objects.filter(
            tipo='conflito', prioridade='critica', ativa=True
        ).count()
        
        return {
            'totais': {
                'horarios': total_horarios,
                'professores': total_professores,
                'salas': total_salas,
                'turmas': total_turmas,
                'disciplinas': total_disciplinas,
            },
            'distribuicao_turnos': {
                'manha': horarios_manha,
                'tarde': horarios_tarde,
                'noite': horarios_noite,
            },
            'alertas': {
                'notificacoes_nao_lidas': notificacoes_nao_lidas,
                'conflitos_criticos': conflitos_criticos,
            },
            'periodo_atual': {
                'nome': self.periodo_letivo.nome if self.periodo_letivo else 'Nenhum período ativo',
                'id': self.periodo_letivo.id if self.periodo_letivo else None,
            }
        }
    
    def get_ocupacao_salas(self):
        """
        Calcula a taxa de ocupação das salas.
        
        Returns:
            list: Lista com dados de ocupação por sala
        """
        filtro_periodo = {'horarios__periodo_letivo': self.periodo_letivo} if self.periodo_letivo else {}
        
        salas_ocupacao = []
        salas = Sala.objects.filter(ativa=True).annotate(
            total_horarios=Count('horarios', filter=Q(horarios__ativo=True, **filtro_periodo))
        )
        
        # Calcular slots totais disponíveis (5 dias × 3 turnos × 6 horários médios)
        slots_totais_teoricos = 5 * 3 * 6  # 90 slots por semana
        
        for sala in salas:
            taxa_ocupacao = (sala.total_horarios / slots_totais_teoricos * 100) if slots_totais_teoricos > 0 else 0
            
            # Definir status baseado na taxa de ocupação
            if taxa_ocupacao >= 80:
                status = 'alta'
                status_label = 'Alta Ocupação'
            elif taxa_ocupacao >= 50:
                status = 'media'
                status_label = 'Ocupação Média'
            elif taxa_ocupacao >= 20:
                status = 'baixa'
                status_label = 'Baixa Ocupação'
            else:
                status = 'vazia'
                status_label = 'Subutilizada'
            
            salas_ocupacao.append({
                'sala': sala,
                'total_horarios': sala.total_horarios,
                'taxa_ocupacao': round(taxa_ocupacao, 1),
                'status': status,
                'status_label': status_label,
            })
        
        return sorted(salas_ocupacao, key=lambda x: x['taxa_ocupacao'], reverse=True)
    
    def get_distribuicao_professores(self):
        """
        Analisa a distribuição de carga horária dos professores.
        
        Returns:
            list: Lista com dados de carga horária por professor
        """
        filtro_periodo = {'horarios__periodo_letivo': self.periodo_letivo} if self.periodo_letivo else {}
        
        professores_carga = []
        professores = Professor.objects.filter(ativo=True).annotate(
            total_aulas=Count('horarios', filter=Q(horarios__ativo=True, **filtro_periodo)),
            total_turmas=Count('horarios__turma', distinct=True, filter=Q(horarios__ativo=True, **filtro_periodo)),
            total_disciplinas=Count('horarios__disciplina', distinct=True, filter=Q(horarios__ativo=True, **filtro_periodo))
        )
        
        for professor in professores:
            # Calcular distribuição por turnos
            turnos_prof = Horario.objects.filter(
                professor=professor, ativo=True, **filtro_periodo
            ).values('turno').annotate(total=Count('id'))
            
            turnos_dict = {turno['turno']: turno['total'] for turno in turnos_prof}
            
            # Definir status baseado na carga
            if professor.total_aulas >= 25:
                status = 'sobrecarga'
                status_label = 'Sobrecarga'
            elif professor.total_aulas >= 15:
                status = 'ideal'
                status_label = 'Carga Ideal'
            elif professor.total_aulas >= 5:
                status = 'baixa'
                status_label = 'Carga Baixa'
            else:
                status = 'ocioso'
                status_label = 'Ocioso'
            
            professores_carga.append({
                'professor': professor,
                'total_aulas': professor.total_aulas,
                'total_turmas': professor.total_turmas,
                'total_disciplinas': professor.total_disciplinas,
                'turnos': {
                    'manha': turnos_dict.get('manha', 0),
                    'tarde': turnos_dict.get('tarde', 0),
                    'noite': turnos_dict.get('noite', 0),
                },
                'status': status,
                'status_label': status_label,
            })
        
        return sorted(professores_carga, key=lambda x: x['total_aulas'], reverse=True)
    
    def get_conflitos_frequentes(self):
        """
        Analisa os tipos de conflitos mais frequentes.
        
        Returns:
            dict: Análise de conflitos por tipo e frequência
        """
        # Últimos 30 dias
        data_limite = timezone.now() - timedelta(days=30)
        
        conflitos_por_tipo = NotificacaoSistema.objects.filter(
            tipo='conflito',
            data_criacao__gte=data_limite
        ).values('dados_contexto__conflito_tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Conflitos por período do dia
        conflitos_periodo = defaultdict(int)
        notificacoes_conflito = NotificacaoSistema.objects.filter(
            tipo='conflito',
            data_criacao__gte=data_limite
        )
        
        for notif in notificacoes_conflito:
            hora = notif.data_criacao.hour
            if 6 <= hora < 12:
                conflitos_periodo['Manhã'] += 1
            elif 12 <= hora < 18:
                conflitos_periodo['Tarde'] += 1
            else:
                conflitos_periodo['Noite'] += 1
        
        return {
            'por_tipo': list(conflitos_por_tipo),
            'por_periodo': dict(conflitos_periodo),
            'total_conflitos': sum(conflitos_periodo.values()),
        }
    
    def get_eventos_proximos(self, dias_futuro=30):
        """
        Lista eventos acadêmicos próximos.
        
        Args:
            dias_futuro: Número de dias no futuro para buscar eventos
            
        Returns:
            list: Lista de eventos próximos
        """
        hoje = timezone.now().date()
        data_limite = hoje + timedelta(days=dias_futuro)
        
        eventos = EventoAcademico.objects.filter(
            ativo=True,
            data_inicio__gte=hoje,
            data_inicio__lte=data_limite
        ).order_by('data_inicio')
        
        eventos_formatados = []
        for evento in eventos:
            dias_restantes = (evento.data_inicio - hoje).days
            
            # Definir urgência
            if dias_restantes <= 3:
                urgencia = 'alta'
                urgencia_label = 'Urgente'
            elif dias_restantes <= 7:
                urgencia = 'media'
                urgencia_label = 'Próximo'
            else:
                urgencia = 'baixa'
                urgencia_label = 'Planejado'
            
            eventos_formatados.append({
                'evento': evento,
                'dias_restantes': dias_restantes,
                'urgencia': urgencia,
                'urgencia_label': urgencia_label,
            })
        
        return eventos_formatados
    
    def get_auditoria_recente(self, limite=20):
        """
        Retorna as ações mais recentes do sistema.
        
        Args:
            limite: Número máximo de registros
            
        Returns:
            list: Lista de ações recentes
        """
        return AuditoriaHorario.objects.select_related(
            'usuario', 'horario__turma', 'horario__disciplina', 'horario__professor'
        ).order_by('-timestamp')[:limite]
    
    def get_relatorio_carga_horaria(self):
        """
        Gera relatório de carga horária por turma e disciplina.
        
        Returns:
            dict: Relatório detalhado de carga horária
        """
        filtro_periodo = {'periodo_letivo': self.periodo_letivo} if self.periodo_letivo else {}
        
        relatorio = {}
        turmas = Turma.objects.filter(ativa=True)
        
        for turma in turmas:
            disciplinas_turma = turma.disciplinas.all()
            turma_dados = {
                'turma': turma,
                'disciplinas': [],
                'total_aulas': 0,
                'status_geral': 'completo'
            }
            
            for disciplina in disciplinas_turma:
                aulas_alocadas = Horario.objects.filter(
                    turma=turma,
                    disciplina=disciplina,
                    ativo=True,
                    **filtro_periodo
                ).count()
                
                carga_necessaria = disciplina.carga_horaria_semanal
                percentual_completo = (aulas_alocadas / carga_necessaria * 100) if carga_necessaria > 0 else 0
                
                # Definir status da disciplina
                if aulas_alocadas == carga_necessaria:
                    status = 'completo'
                elif aulas_alocadas > carga_necessaria:
                    status = 'excesso'
                else:
                    status = 'incompleto'
                    turma_dados['status_geral'] = 'incompleto'
                
                turma_dados['disciplinas'].append({
                    'disciplina': disciplina,
                    'aulas_alocadas': aulas_alocadas,
                    'carga_necessaria': carga_necessaria,
                    'percentual_completo': round(percentual_completo, 1),
                    'status': status,
                })
                
                turma_dados['total_aulas'] += aulas_alocadas
            
            relatorio[turma.id] = turma_dados
        
        return relatorio
    
    def get_metricas_performance(self):
        """
        Calcula métricas de performance do sistema.
        
        Returns:
            dict: Métricas de performance
        """
        hoje = timezone.now().date()
        semana_passada = hoje - timedelta(days=7)
        
        # Atividades da última semana
        atividades_semana = AuditoriaHorario.objects.filter(
            timestamp__date__gte=semana_passada
        ).count()
        
        # Conflitos resolvidos vs novos conflitos
        conflitos_novos = NotificacaoSistema.objects.filter(
            tipo='conflito',
            data_criacao__date__gte=semana_passada
        ).count()
        
        conflitos_resolvidos = NotificacaoSistema.objects.filter(
            tipo='conflito',
            lida=True,
            data_leitura__date__gte=semana_passada
        ).count()
        
        # Taxa de utilização geral
        filtro_periodo = {'periodo_letivo': self.periodo_letivo} if self.periodo_letivo else {}
        total_horarios_possiveis = Turma.objects.filter(ativa=True).count() * 30  # Estimativa
        total_horarios_ocupados = Horario.objects.filter(ativo=True, **filtro_periodo).count()
        
        taxa_utilizacao = (total_horarios_ocupados / total_horarios_possiveis * 100) if total_horarios_possiveis > 0 else 0
        
        return {
            'atividades_semana': atividades_semana,
            'conflitos_novos': conflitos_novos,
            'conflitos_resolvidos': conflitos_resolvidos,
            'taxa_utilizacao': round(taxa_utilizacao, 1),
            'periodo_analise': {
                'inicio': semana_passada.strftime('%d/%m/%Y'),
                'fim': hoje.strftime('%d/%m/%Y'),
            }
        }
