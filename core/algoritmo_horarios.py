"""
Algoritmo para geração automática de horários escolares - VERSÃO REFATORADA.

Este módulo implementa um algoritmo de geração automática de horários
que considera restrições de professores, salas, turmas e preferências.
"""

import random
from datetime import time, datetime, date
from typing import List, Dict, Any, Optional, Tuple
from django.db import transaction
from django.db.models import Q
from collections import defaultdict

from .models import (
    Turma, Disciplina, Professor, Sala, Horario, 
    PreferenciaProfessor, BloqueioTemporario
)


class GeradorHorariosRobusto:
    """
    Classe responsável pela geração automática de horários com algoritmo robusto.
    """
    
    TURNOS_HORARIOS = {
        'manha': [
            ('07:00', '07:50'),
            ('07:50', '08:40'),
            ('09:00', '09:50'),
            ('09:50', '10:40'),
            ('10:40', '11:30'),
            ('11:30', '12:20')
        ],
        'tarde': [
            ('13:00', '13:50'),
            ('13:50', '14:40'),
            # Intervalo das 14:50 às 15:10
            ('15:10', '16:00'),
            ('16:00', '16:50'),
            ('16:50', '17:40')
        ],
        'noite': [
            ('19:20', '20:10'),
            ('20:10', '21:00'),
            ('21:10', '22:00'),
            ('22:00', '22:50')
        ]
    }
    
    DIAS_SEMANA = [
        (1, 'segunda'),
        (2, 'terca'),
        (3, 'quarta'),
        (4, 'quinta'),
        (5, 'sexta')
    ]
    
    def __init__(self):
        self.reset_stats()
    
    def reset_stats(self):
        """Reset das estatísticas de geração."""
        self.conflitos = []
        self.horarios_criados = 0
        self.turmas_processadas = 0
        self.tentativas = 0
        
    def gerar_horarios(
        self, 
        turmas: Optional[List[Turma]] = None,
        respeitar_preferencias: bool = True,
        evitar_janelas: bool = True,
        distribuir_dias: bool = True,
        limpar_anteriores: bool = False,
        max_tentativas: int = 100
    ) -> Dict[str, Any]:
        """
        Método principal para geração de horários.
        """
        try:
            self.reset_stats()
            
            with transaction.atomic():
                # Limpar horários anteriores se solicitado
                if limpar_anteriores:
                    Horario.objects.all().delete()
                
                # Buscar turmas se não fornecidas
                if turmas is None:
                    turmas = list(Turma.objects.filter(ativa=True).prefetch_related(
                        'disciplinas',
                        'disciplinas__professor_set'
                    ))
                
                # Validar dados básicos
                if not self._validar_dados(turmas):
                    return {
                        'sucesso': False,
                        'erro': 'Dados insuficientes para gerar horários',
                        'conflitos': self.conflitos,
                        'horarios_criados': 0
                    }
                
                # Gerar horários usando algoritmo simplificado mas robusto
                sucesso = self._gerar_horarios_robusto(
                    turmas, 
                    respeitar_preferencias,
                    evitar_janelas,
                    distribuir_dias,
                    max_tentativas
                )
                
                return {
                    'sucesso': sucesso,
                    'horarios_criados': self.horarios_criados,
                    'turmas_processadas': self.turmas_processadas,
                    'conflitos': self.conflitos,
                    'tentativas': self.tentativas
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro interno: {str(e)}',
                'conflitos': self.conflitos,
                'horarios_criados': self.horarios_criados
            }
    
    def _validar_dados(self, turmas: List[Turma]) -> bool:
        """Valida se há dados suficientes para gerar horários."""
        if not turmas:
            self.conflitos.append("Nenhuma turma ativa encontrada")
            return False
            
        if not Professor.objects.filter(ativo=True).exists():
            self.conflitos.append("Nenhum professor ativo encontrado")
            return False
            
        if not Sala.objects.filter(ativa=True).exists():
            self.conflitos.append("Nenhuma sala ativa encontrada")
            return False
            
        # Verificar se todas as turmas têm disciplinas
        for turma in turmas:
            if not turma.disciplinas.exists():
                self.conflitos.append(f"Turma {turma.nome_codigo} não possui disciplinas")
                return False
                
        return True
    
    def _gerar_horarios_robusto(
        self, 
        turmas: List[Turma],
        respeitar_preferencias: bool,
        evitar_janelas: bool,
        distribuir_dias: bool,
        max_tentativas: int
    ) -> bool:
        """
        Algoritmo robusto de geração de horários.
        """
        # Criar lista de todas as aulas necessárias
        aulas_necessarias = self._preparar_aulas(turmas)
        
        if not aulas_necessarias:
            self.conflitos.append("Nenhuma aula para ser programada")
            return False
        
        # Algoritmo de tentativa e erro com flexibilidade crescente
        for tentativa in range(max_tentativas):
            self.tentativas = tentativa + 1
            
            # Tentar gerar horários com nível de flexibilidade baseado na tentativa
            flexibilidade = min(0.1 + (tentativa * 0.01), 0.8)  # 10% a 80% de flexibilidade
            
            if self._tentar_gerar_completo(
                aulas_necessarias.copy(),
                respeitar_preferencias and flexibilidade < 0.5,  # Após 50 tentativas, relaxa preferências
                evitar_janelas and flexibilidade < 0.3,  # Após 30 tentativas, permite janelas
                distribuir_dias,
                flexibilidade
            ):
                return True
                
        # Se chegou aqui, não conseguiu gerar
        self.conflitos.append(f"Não foi possível gerar horário completo após {max_tentativas} tentativas")
        return False
    
    def _preparar_aulas(self, turmas: List[Turma]) -> List[Dict]:
        """Prepara lista de todas as aulas que precisam ser agendadas."""
        aulas = []
        
        for turma in turmas:
            self.turmas_processadas += 1
            
            for disciplina in turma.disciplinas.all():
                # Obter professores para a disciplina
                professores = Professor.objects.filter(
                    disciplinas=disciplina,
                    ativo=True
                )
                
                if not professores.exists():
                    # Se não há professor específico, buscar qualquer professor ativo
                    professores = Professor.objects.filter(ativo=True)
                    if not professores.exists():
                        self.conflitos.append(f"Nenhum professor disponível para {disciplina.nome}")
                        continue
                
                # Calcular quantas aulas por semana
                aulas_por_semana = getattr(disciplina, 'carga_horaria_semanal', None) or getattr(disciplina, 'aulas_por_semana', None) or 2
                
                for i in range(aulas_por_semana):
                    aulas.append({
                        'turma': turma,
                        'disciplina': disciplina,
                        'professores_possiveis': list(professores),
                        'professor': None,  # Será escolhido durante a geração
                        'dia': None,
                        'turno': None,
                        'horario_inicio': None,
                        'horario_fim': None,
                        'sala': None
                    })
        
        return aulas
    
    def _tentar_gerar_completo(
        self, 
        aulas: List[Dict],
        respeitar_preferencias: bool,
        evitar_janelas: bool,
        distribuir_dias: bool,
        flexibilidade: float
    ) -> bool:
        """
        Tenta gerar um horário completo para todas as aulas.
        """
        # Embaralhar aulas para variar a ordem de tentativa
        random.shuffle(aulas)
        
        aulas_alocadas = []
        
        for aula in aulas:
            slot_encontrado = self._encontrar_slot_para_aula(
                aula,
                aulas_alocadas,
                respeitar_preferencias,
                evitar_janelas,
                distribuir_dias,
                flexibilidade
            )
            
            if slot_encontrado:
                aulas_alocadas.append(aula)
            else:
                # Não conseguiu alocar esta aula, falhar
                return False
        
        # Se chegou aqui, conseguiu alocar todas as aulas
        self._salvar_horarios(aulas_alocadas)
        return True
    
    def _encontrar_slot_para_aula(
        self,
        aula: Dict,
        aulas_alocadas: List[Dict],
        respeitar_preferencias: bool,
        evitar_janelas: bool,
        distribuir_dias: bool,
        flexibilidade: float
    ) -> bool:
        """
        Encontra um slot válido para uma aula específica.
        Prioriza agrupamento de aulas do mesmo professor/turma.
        """
        # Gerar todos os slots possíveis
        slots_possiveis = self._gerar_slots_possiveis(aula['turma'])
        
        # Tentar cada professor possível
        professores = aula['professores_possiveis'].copy()
        random.shuffle(professores)
        
        for professor in professores:
            # Avaliar e ordenar slots por score de agrupamento
            slots_com_score = []
            
            for slot in slots_possiveis:
                dia, turno, horario_inicio, horario_fim = slot
                
                # Verificar se o slot é válido para este professor e configuração
                if self._slot_valido(
                    professor,
                    aula['turma'],
                    aula['disciplina'],
                    dia,
                    turno,
                    horario_inicio,
                    horario_fim,
                    aulas_alocadas,
                    respeitar_preferencias,
                    evitar_janelas,
                    flexibilidade
                ):
                    # Calcular score de agrupamento
                    score = self._calcular_score_agrupamento(
                        professor,
                        aula['turma'],
                        dia,
                        turno,
                        horario_inicio,
                        horario_fim,
                        aulas_alocadas
                    )
                    
                    slots_com_score.append((slot, score))
            
            # Ordenar por score (maior score = melhor agrupamento)
            slots_com_score.sort(key=lambda x: x[1], reverse=True)
            
            # Tentar slots em ordem de score
            for slot, score in slots_com_score:
                dia, turno, horario_inicio, horario_fim = slot
                
                # Encontrar sala disponível
                sala = self._encontrar_sala_disponivel(
                    aula['turma'],
                    dia,
                    horario_inicio,
                    horario_fim,
                    aulas_alocadas
                )
                
                if sala:
                    # Alocar a aula
                    aula['professor'] = professor
                    aula['dia'] = dia
                    aula['turno'] = turno
                    aula['horario_inicio'] = horario_inicio
                    aula['horario_fim'] = horario_fim
                    aula['sala'] = sala
                    return True
        
        return False
    
    def _calcular_score_agrupamento(
        self,
        professor: Professor,
        turma: Turma,
        dia: int,
        turno: str,
        horario_inicio: str,
        horario_fim: str,
        aulas_alocadas: List[Dict]
    ) -> float:
        """
        Calcula score de agrupamento para favorecer aulas consecutivas.
        """
        score = 0.0
        
        # Bonus por aulas consecutivas do mesmo professor no mesmo dia
        for aula_alocada in aulas_alocadas:
            if (aula_alocada['professor'] == professor and 
                aula_alocada['dia'] == dia):
                
                # Verificar se são horários consecutivos
                if self._horarios_consecutivos(
                    aula_alocada['horario_inicio'], aula_alocada['horario_fim'],
                    horario_inicio, horario_fim
                ):
                    score += 10.0  # Bonus alto para consecutividade
                
                # Bonus menor para aulas no mesmo turno
                if aula_alocada['turno'] == turno:
                    score += 5.0
        
        # Bonus por aulas consecutivas da mesma turma
        for aula_alocada in aulas_alocadas:
            if (aula_alocada['turma'] == turma and 
                aula_alocada['dia'] == dia):
                
                # Verificar se são horários consecutivos
                if self._horarios_consecutivos(
                    aula_alocada['horario_inicio'], aula_alocada['horario_fim'],
                    horario_inicio, horario_fim
                ):
                    score += 8.0  # Bonus para consecutividade da turma
                
                # Bonus menor para aulas no mesmo turno
                if aula_alocada['turno'] == turno:
                    score += 3.0
        
        # Penalidade por criar janelas (gaps entre aulas)
        score -= self._calcular_penalidade_janelas(
            professor, turma, dia, turno, horario_inicio, horario_fim, aulas_alocadas
        )
        
        # Bonus por preferências do professor
        if hasattr(professor, 'get_preferencia_score'):
            pref_score = professor.get_preferencia_score(dia_semana=dia, turno=turno)
            score += (pref_score - 3) * 2  # Normalizar e amplificar
        
        return score
    
    def _horarios_consecutivos(self, inicio1: str, fim1: str, inicio2: str, fim2: str) -> bool:
        """
        Verifica se dois horários são consecutivos (um termina quando o outro começa).
        """
        try:
            h1_fim = datetime.strptime(fim1, '%H:%M').time()
            h2_inicio = datetime.strptime(inicio2, '%H:%M').time()
            h2_fim = datetime.strptime(fim2, '%H:%M').time()
            h1_inicio = datetime.strptime(inicio1, '%H:%M').time()
            
            # Verificar se h1 termina quando h2 começa, ou vice-versa
            return h1_fim == h2_inicio or h2_fim == h1_inicio
        except:
            return False
    
    def _calcular_penalidade_janelas(
        self,
        professor: Professor,
        turma: Turma,
        dia: int,
        turno: str,
        horario_inicio: str,
        horario_fim: str,
        aulas_alocadas: List[Dict]
    ) -> float:
        """
        Calcula penalidade por criar janelas (gaps) entre aulas.
        """
        penalidade = 0.0
        
        # Buscar aulas do professor no mesmo dia
        aulas_professor_dia = [
            aula for aula in aulas_alocadas
            if aula['professor'] == professor and aula['dia'] == dia
        ]
        
        # Buscar aulas da turma no mesmo dia
        aulas_turma_dia = [
            aula for aula in aulas_alocadas
            if aula['turma'] == turma and aula['dia'] == dia
        ]
        
        try:
            inicio_novo = datetime.strptime(horario_inicio, '%H:%M').time()
            fim_novo = datetime.strptime(horario_fim, '%H:%M').time()
            
            # Verificar janelas com aulas do professor
            for aula in aulas_professor_dia:
                inicio_existente = datetime.strptime(aula['horario_inicio'], '%H:%M').time()
                fim_existente = datetime.strptime(aula['horario_fim'], '%H:%M').time()
                
                # Calcular gap entre aulas
                if fim_existente < inicio_novo:
                    gap_minutes = (datetime.combine(date.today(), inicio_novo) - 
                                 datetime.combine(date.today(), fim_existente)).seconds / 60
                    if 0 < gap_minutes <= 120:  # Gap de até 2 horas
                        penalidade += gap_minutes / 10  # Penalidade proporcional
                elif fim_novo < inicio_existente:
                    gap_minutes = (datetime.combine(date.today(), inicio_existente) - 
                                 datetime.combine(date.today(), fim_novo)).seconds / 60
                    if 0 < gap_minutes <= 120:
                        penalidade += gap_minutes / 10
            
            # Verificar janelas com aulas da turma (penalidade menor)
            for aula in aulas_turma_dia:
                inicio_existente = datetime.strptime(aula['horario_inicio'], '%H:%M').time()
                fim_existente = datetime.strptime(aula['horario_fim'], '%H:%M').time()
                
                if fim_existente < inicio_novo:
                    gap_minutes = (datetime.combine(date.today(), inicio_novo) - 
                                 datetime.combine(date.today(), fim_existente)).seconds / 60
                    if 0 < gap_minutes <= 120:
                        penalidade += gap_minutes / 20  # Penalidade menor para turma
                elif fim_novo < inicio_existente:
                    gap_minutes = (datetime.combine(date.today(), inicio_existente) - 
                                 datetime.combine(date.today(), fim_novo)).seconds / 60
                    if 0 < gap_minutes <= 120:
                        penalidade += gap_minutes / 20
        
        except:
            pass  # Em caso de erro, não aplicar penalidade
        
        return penalidade
    
    def _gerar_slots_possiveis(self, turma: Turma) -> List[Tuple]:
        """Gera todos os slots possíveis baseado no turno da turma."""
        slots = []
        
        # Definir turnos permitidos para a turma
        turnos_permitidos = self._get_turnos_permitidos(turma)
        
        for dia_num, dia_nome in self.DIAS_SEMANA:
            for turno in turnos_permitidos:
                for horario_inicio, horario_fim in self.TURNOS_HORARIOS[turno]:
                    slots.append((dia_num, turno, horario_inicio, horario_fim))
        
        return slots
    
    def _get_turnos_permitidos(self, turma: Turma) -> List[str]:
        """Retorna os turnos permitidos para a turma."""
        turno_turma = getattr(turma, 'turno', None) or getattr(turma, 'turno_turma', 'flexivel')
        
        if turno_turma == 'matutino' or turno_turma == 'manha':
            return ['manha']
        elif turno_turma == 'vespertino' or turno_turma == 'tarde':
            return ['tarde']
        elif turno_turma == 'noturno' or turno_turma == 'noite':
            return ['noite']
        elif turno_turma == 'integral':
            return ['manha', 'tarde']
        else:  # flexivel
            return ['manha', 'tarde', 'noite']
    
    def _slot_valido(
        self,
        professor: Professor,
        turma: Turma,
        disciplina: Disciplina,
        dia: int,
        turno: str,
        horario_inicio: str,
        horario_fim: str,
        aulas_alocadas: List[Dict],
        respeitar_preferencias: bool,
        evitar_janelas: bool,
        flexibilidade: float
    ) -> bool:
        """
        Verifica se um slot é válido para o professor, turma e configurações.
        """
        # Verificar disponibilidade do professor
        if respeitar_preferencias:
            if not self._professor_disponivel(professor, dia, turno, disciplina):
                return False
        
        # Verificar conflitos com aulas já alocadas
        for aula_alocada in aulas_alocadas:
            # Conflito de professor
            if (aula_alocada['professor'] == professor and 
                aula_alocada['dia'] == dia and
                self._horarios_sobrepoem(
                    aula_alocada['horario_inicio'], aula_alocada['horario_fim'],
                    horario_inicio, horario_fim
                )):
                return False
            
            # Conflito de turma
            if (aula_alocada['turma'] == turma and 
                aula_alocada['dia'] == dia and
                self._horarios_sobrepoem(
                    aula_alocada['horario_inicio'], aula_alocada['horario_fim'],
                    horario_inicio, horario_fim
                )):
                return False
        
        return True
    
    def _professor_disponivel(
        self, 
        professor: Professor, 
        dia: int, 
        turno: str, 
        disciplina: Disciplina
    ) -> bool:
        """
        Verifica se o professor está disponível no dia/turno específico.
        """
        # Verificar bloqueios temporários
        hoje = date.today()
        bloqueios = BloqueioTemporario.objects.filter(
            professor=professor,
            ativo=True,
            data_inicio__lte=hoje,
            data_fim__gte=hoje
        )
        
        for bloqueio in bloqueios:
            if bloqueio.turno is None or bloqueio.turno == turno:
                if bloqueio.recorrente:
                    # Verificar se o dia da semana coincide
                    if dia == hoje.weekday():  # Simplificado
                        return False
                else:
                    return False
        
        # Verificar preferências - LÓGICA CORRIGIDA
        preferencias = PreferenciaProfessor.objects.filter(
            professor=professor,
            dia_semana=dia
        )
        
        # Se há preferências específicas para este dia, verificar disponibilidade
        if preferencias.exists():
            for pref in preferencias:
                # Se o turno não está especificado na preferência (None ou string vazia), se aplica a todos os turnos
                # Se o turno está especificado, só se aplica a esse turno
                if pref.turno is None or pref.turno == '' or pref.turno == turno:
                    # Se a disciplina não está especificada, se aplica a todas as disciplinas
                    # Se a disciplina está especificada, só se aplica a essa disciplina
                    if pref.disciplina is None or pref.disciplina == disciplina:
                        if not pref.disponivel:  # Se marcado como INDISPONÍVEL
                            return False
        
        # Se não há preferências específicas OU todas as preferências permitiram, assume disponível
        return True
    
    def _horarios_sobrepoem(self, inicio1: str, fim1: str, inicio2: str, fim2: str) -> bool:
        """Verifica se dois horários se sobrepõem."""
        try:
            h1_inicio = datetime.strptime(inicio1, '%H:%M').time()
            h1_fim = datetime.strptime(fim1, '%H:%M').time()
            h2_inicio = datetime.strptime(inicio2, '%H:%M').time()
            h2_fim = datetime.strptime(fim2, '%H:%M').time()
            
            return not (h1_fim <= h2_inicio or h2_fim <= h1_inicio)
        except:
            return True  # Em caso de erro, assume sobreposição
    
    def _encontrar_sala_disponivel(
        self,
        turma: Turma,
        dia: int,
        horario_inicio: str,
        horario_fim: str,
        aulas_alocadas: List[Dict]
    ) -> Optional[Sala]:
        """
        Encontra uma sala disponível para o horário.
        """
        salas = Sala.objects.filter(ativa=True).order_by('capacidade')
        
        for sala in salas:
            # Verificar capacidade
            capacidade_turma = getattr(turma, 'numero_alunos', None) or getattr(turma, 'capacidade', 30)
            if sala.capacidade < capacidade_turma:
                continue
            
            # Verificar disponibilidade
            sala_ocupada = False
            for aula_alocada in aulas_alocadas:
                if (aula_alocada['sala'] == sala and 
                    aula_alocada['dia'] == dia and
                    self._horarios_sobrepoem(
                        aula_alocada['horario_inicio'], aula_alocada['horario_fim'],
                        horario_inicio, horario_fim
                    )):
                    sala_ocupada = True
                    break
            
            if not sala_ocupada:
                return sala
        
        return None
    
    def _salvar_horarios(self, aulas_alocadas: List[Dict]) -> None:
        """Salva os horários no banco de dados."""
        for aula in aulas_alocadas:
            try:
                horario = Horario.objects.create(
                    turma=aula['turma'],
                    disciplina=aula['disciplina'],
                    professor=aula['professor'],
                    sala=aula['sala'],
                    dia_semana=aula['dia'],
                    turno=aula['turno'],
                    horario_inicio=datetime.strptime(aula['horario_inicio'], '%H:%M').time(),
                    horario_fim=datetime.strptime(aula['horario_fim'], '%H:%M').time(),
                    ativo=True
                )
                self.horarios_criados += 1
            except Exception as e:
                self.conflitos.append(f"Erro ao salvar horário: {str(e)}")


# Mantém compatibilidade com a classe anterior
GeradorHorarios = GeradorHorariosRobusto


# Função principal para compatibilidade
def gerar_horarios_automaticamente(
    turmas=None,
    respeitar_preferencias=True,
    evitar_janelas=True,
    distribuir_dias=True,
    limpar_anteriores=False
):
    """
    Função principal para geração de horários (compatibilidade).
    """
    gerador = GeradorHorariosRobusto()
    return gerador.gerar_horarios(
        turmas=turmas,
        respeitar_preferencias=respeitar_preferencias,
        evitar_janelas=evitar_janelas,
        distribuir_dias=distribuir_dias,
        limpar_anteriores=limpar_anteriores,
        max_tentativas=50  # Reduzido para ser mais rápido
    )
