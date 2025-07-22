"""
Algoritmo para geração automática de horários escolares.

Este módulo implementa um algoritmo de geração automática de horários
que considera restrições de professores, salas, turmas e preferências.
"""

import random
from datetime import time
from typing import List, Dict, Any, Optional, Tuple
from django.db import transaction
from django.db.models import Q

from .models import (
    Turma, Disciplina, Professor, Sala, Horario, 
    PreferenciaProfessor
)


class GeradorHorarios:
    """
    Classe responsável pela geração automática de horários.
    
    Implementa um algoritmo que considera múltiplas restrições:
    - Disponibilidade de professores
    - Capacidade e disponibilidade de salas
    - Preferências de professores
    - Distribuição equilibrada de aulas
    - Evitar janelas no horário
    """
    
    def __init__(self):
        self.conflitos = []
        self.horarios_criados = 0
        self.turmas_processadas = 0
        
        # Horários padrão por turno
        self.horarios_padrao = {
            'manha': [
                (time(7, 0), time(7, 50)),
                (time(7, 50), time(8, 40)),
                (time(8, 40), time(9, 30)),
                (time(9, 50), time(10, 40)),  # intervalo de 20min
                (time(10, 40), time(11, 30)),
                (time(11, 30), time(12, 20)),
            ],
            'tarde': [
                (time(13, 0), time(13, 50)),
                (time(13, 50), time(14, 40)),
                (time(14, 40), time(15, 30)),
                (time(15, 50), time(16, 40)),  # intervalo de 20min
                (time(16, 40), time(17, 30)),
                (time(17, 30), time(18, 20)),
            ],
            'noite': [
                (time(18, 30), time(19, 20)),
                (time(19, 20), time(20, 10)),
                (time(20, 10), time(21, 0)),
                (time(21, 10), time(22, 0)),   # intervalo de 10min
                (time(22, 0), time(22, 50)),
            ]
        }
        
        # Dias da semana (0=Segunda, 4=Sexta)
        self.dias_uteis = [0, 1, 2, 3, 4]
    
    def gerar_horarios(
        self, 
        turmas: Optional[List[Turma]] = None,
        respeitar_preferencias: bool = True,
        evitar_janelas: bool = True,
        distribuir_dias: bool = True,
        limpar_anteriores: bool = False
    ) -> Dict[str, Any]:
        """
        Gera horários automáticamente para as turmas especificadas.
        
        Args:
            turmas: Lista de turmas para gerar horários. Se None, usa todas as ativas.
            respeitar_preferencias: Se deve considerar preferências dos professores.
            evitar_janelas: Se deve tentar evitar janelas nos horários.
            distribuir_dias: Se deve distribuir aulas ao longo da semana.
            limpar_anteriores: Se deve remover horários existentes antes.
            
        Returns:
            Dicionário com resultado da operação.
        """
        self.conflitos = []
        self.horarios_criados = 0
        self.turmas_processadas = 0
        
        try:
            with transaction.atomic():
                # Obter turmas para processar
                if turmas is None:
                    turmas = list(Turma.objects.filter(ativa=True).prefetch_related('disciplinas'))
                
                if not turmas:
                    return {
                        'sucesso': False,
                        'erro': 'Nenhuma turma encontrada para gerar horários.',
                        'conflitos': [],
                        'horarios_criados': 0,
                        'turmas_processadas': 0
                    }
                
                # Limpar horários anteriores se solicitado
                if limpar_anteriores:
                    count_removidos = Horario.objects.filter(
                        turma__in=turmas
                    ).delete()[0]
                    if count_removidos > 0:
                        self.conflitos.append(f'Removidos {count_removidos} horários anteriores.')
                
                # Processar cada turma
                for turma in turmas:
                    try:
                        self._gerar_horarios_turma(
                            turma, 
                            respeitar_preferencias, 
                            evitar_janelas, 
                            distribuir_dias
                        )
                        self.turmas_processadas += 1
                    except Exception as e:
                        self.conflitos.append(
                            f'Erro ao processar turma {turma.nome_codigo}: {str(e)}'
                        )
                
                return {
                    'sucesso': True,
                    'horarios_criados': self.horarios_criados,
                    'turmas_processadas': self.turmas_processadas,
                    'conflitos': self.conflitos
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'conflitos': self.conflitos,
                'horarios_criados': self.horarios_criados,
                'turmas_processadas': self.turmas_processadas
            }
    
    def _gerar_horarios_turma(
        self, 
        turma: Turma, 
        respeitar_preferencias: bool,
        evitar_janelas: bool,
        distribuir_dias: bool
    ):
        """
        Gera horários para uma turma específica.
        """
        disciplinas = turma.disciplinas.filter(ativa=True)
        
        if not disciplinas.exists():
            self.conflitos.append(f'Turma {turma.nome_codigo} não possui disciplinas ativas.')
            return
        
        # Criar lista de aulas necessárias
        aulas_necessarias = []
        for disciplina in disciplinas:
            # Encontrar professor disponível para a disciplina
            professor = self._encontrar_professor_disciplina(disciplina, respeitar_preferencias)
            if not professor:
                self.conflitos.append(
                    f'Nenhum professor encontrado para {disciplina.nome} - turma {turma.nome_codigo}'
                )
                continue
            
            # Adicionar aulas baseadas na carga horária
            for _ in range(disciplina.carga_horaria_semanal):
                aulas_necessarias.append({
                    'disciplina': disciplina,
                    'professor': professor,
                    'turma': turma
                })
        
        if not aulas_necessarias:
            self.conflitos.append(f'Nenhuma aula pôde ser programada para turma {turma.nome_codigo}.')
            return
        
        # Embaralhar para distribuição aleatória
        random.shuffle(aulas_necessarias)
        
        # Alocar aulas nos horários disponíveis
        slots_alocados = []
        
        for aula in aulas_necessarias:
            slot = self._encontrar_melhor_slot(
                aula, 
                slots_alocados,
                evitar_janelas, 
                distribuir_dias,
                respeitar_preferencias
            )
            
            if slot:
                slots_alocados.append(slot)
                self._criar_horario(aula, slot)
                self.horarios_criados += 1
            else:
                self.conflitos.append(
                    f'Não foi possível alocar aula de {aula["disciplina"].nome} '
                    f'para turma {turma.nome_codigo} com professor {aula["professor"].nome_completo}'
                )
    
    def _encontrar_professor_disciplina(
        self, 
        disciplina: Disciplina, 
        respeitar_preferencias: bool
    ) -> Optional[Professor]:
        """
        Encontra um professor adequado para ministrar a disciplina.
        """
        # Buscar professores ativos
        professores = Professor.objects.filter(ativo=True)
        
        # Se deve respeitar preferências, filtrar por professores que têm preferência pela disciplina
        if respeitar_preferencias:
            professores_com_preferencia = professores.filter(
                preferencias__disciplina=disciplina
            ).distinct()
            
            if professores_com_preferencia.exists():
                return random.choice(list(professores_com_preferencia))
        
        # Se não encontrou com preferência ou não deve respeitar, retorna qualquer professor
        if professores.exists():
            return random.choice(list(professores))
        
        return None
    
    def _encontrar_melhor_slot(
        self,
        aula: Dict[str, Any],
        slots_alocados: List[Dict[str, Any]],
        evitar_janelas: bool,
        distribuir_dias: bool,
        respeitar_preferencias: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Encontra o melhor slot de horário para uma aula.
        """
        turma = aula['turma']
        professor = aula['professor']
        disciplina = aula['disciplina']
        
        # Obter preferências do professor se devem ser respeitadas
        preferencias_professor = []
        if respeitar_preferencias:
            preferencias_professor = list(
                PreferenciaProfessor.objects.filter(professor=professor)
            )
        
        melhores_slots = []
        
        # Iterar sobre todos os turnos e horários possíveis
        for turno in ['manha', 'tarde', 'noite']:
            # Verificar se professor tem preferência de turno
            if respeitar_preferencias and preferencias_professor:
                pref_turnos = [p.turno for p in preferencias_professor if p.turno]
                if pref_turnos and turno not in pref_turnos:
                    continue
            
            for dia in self.dias_uteis:
                # Verificar se professor tem preferência de dia
                if respeitar_preferencias and preferencias_professor:
                    pref_dias = [p.dia_semana for p in preferencias_professor if p.dia_semana is not None]
                    if pref_dias and dia not in pref_dias:
                        continue
                
                for i, (inicio, fim) in enumerate(self.horarios_padrao[turno]):
                    slot = {
                        'dia': dia,
                        'turno': turno,
                        'horario_inicio': inicio,
                        'horario_fim': fim,
                        'posicao': i
                    }
                    
                    # Verificar se slot está disponível
                    if self._slot_disponivel(slot, aula, slots_alocados):
                        score = self._calcular_score_slot(
                            slot, aula, slots_alocados, evitar_janelas, distribuir_dias
                        )
                        melhores_slots.append((slot, score))
        
        if not melhores_slots:
            return None
        
        # Ordenar por score (maior é melhor) e retornar o melhor
        melhores_slots.sort(key=lambda x: x[1], reverse=True)
        return melhores_slots[0][0]
    
    def _slot_disponivel(
        self, 
        slot: Dict[str, Any], 
        aula: Dict[str, Any],
        slots_alocados: List[Dict[str, Any]]
    ) -> bool:
        """
        Verifica se um slot está disponível para uma aula.
        """
        turma = aula['turma']
        professor = aula['professor']
        dia = slot['dia']
        turno = slot['turno']
        inicio = slot['horario_inicio']
        fim = slot['horario_fim']
        
        # Verificar conflito com turma
        conflito_turma = Horario.objects.filter(
            turma=turma,
            dia_semana=dia,
            turno=turno,
            horario_inicio=inicio,
            horario_fim=fim
        ).exists()
        
        if conflito_turma:
            return False
        
        # Verificar conflito com professor
        conflito_professor = Horario.objects.filter(
            professor=professor,
            dia_semana=dia,
            turno=turno,
            horario_inicio=inicio,
            horario_fim=fim
        ).exists()
        
        if conflito_professor:
            return False
        
        # Verificar conflitos com slots já alocados na sessão atual
        for slot_alocado in slots_alocados:
            if (slot_alocado['dia'] == dia and 
                slot_alocado['turno'] == turno and
                slot_alocado['horario_inicio'] == inicio):
                
                # Verificar se é conflito de turma ou professor
                aula_alocada = slot_alocado['aula']
                if (aula_alocada['turma'] == turma or 
                    aula_alocada['professor'] == professor):
                    return False
        
        return True
    
    def _calcular_score_slot(
        self,
        slot: Dict[str, Any],
        aula: Dict[str, Any],
        slots_alocados: List[Dict[str, Any]],
        evitar_janelas: bool,
        distribuir_dias: bool
    ) -> int:
        """
        Calcula um score para o slot baseado nas preferências e restrições.
        """
        score = 100  # Score base
        
        turma = aula['turma']
        professor = aula['professor']
        dia = slot['dia']
        turno = slot['turno']
        posicao = slot['posicao']
        
        # Bonus por distribuição de dias
        if distribuir_dias:
            dias_turma = set()
            dias_professor = set()
            
            # Contar dias já ocupados
            for slot_alocado in slots_alocados:
                aula_alocada = slot_alocado['aula']
                if aula_alocada['turma'] == turma:
                    dias_turma.add(slot_alocado['dia'])
                if aula_alocada['professor'] == professor:
                    dias_professor.add(slot_alocado['dia'])
            
            # Bonus se este dia ainda não está ocupado
            if dia not in dias_turma:
                score += 20
            if dia not in dias_professor:
                score += 10
        
        # Penalidade por janelas (se evitar_janelas está ativo)
        if evitar_janelas:
            # Verificar se criar uma janela no horário da turma
            if self._criaria_janela_turma(slot, turma, slots_alocados):
                score -= 30
            
            # Verificar se criar uma janela no horário do professor
            if self._criaria_janela_professor(slot, professor, slots_alocados):
                score -= 20
        
        # Preferência por horários do meio (evitar primeiro e último)
        total_horarios = len(self.horarios_padrao[turno])
        if posicao == 0 or posicao == total_horarios - 1:
            score -= 10
        elif 1 <= posicao <= total_horarios - 2:
            score += 5
        
        return score
    
    def _criaria_janela_turma(
        self, 
        slot: Dict[str, Any], 
        turma: Turma, 
        slots_alocados: List[Dict[str, Any]]
    ) -> bool:
        """
        Verifica se alocar este slot criaria uma janela no horário da turma.
        """
        dia = slot['dia']
        turno = slot['turno']
        posicao = slot['posicao']
        
        # Encontrar posições ocupadas pela turma no mesmo dia/turno
        posicoes_ocupadas = []
        for slot_alocado in slots_alocados:
            if (slot_alocado['aula']['turma'] == turma and
                slot_alocado['dia'] == dia and
                slot_alocado['turno'] == turno):
                posicoes_ocupadas.append(slot_alocado['posicao'])
        
        if not posicoes_ocupadas:
            return False
        
        # Verificar se criaria janela
        todas_posicoes = sorted(posicoes_ocupadas + [posicao])
        
        for i in range(len(todas_posicoes) - 1):
            if todas_posicoes[i + 1] - todas_posicoes[i] > 1:
                return True
        
        return False
    
    def _criaria_janela_professor(
        self, 
        slot: Dict[str, Any], 
        professor: Professor, 
        slots_alocados: List[Dict[str, Any]]
    ) -> bool:
        """
        Verifica se alocar este slot criaria uma janela no horário do professor.
        """
        dia = slot['dia']
        turno = slot['turno']
        posicao = slot['posicao']
        
        # Encontrar posições ocupadas pelo professor no mesmo dia/turno
        posicoes_ocupadas = []
        for slot_alocado in slots_alocados:
            if (slot_alocado['aula']['professor'] == professor and
                slot_alocado['dia'] == dia and
                slot_alocado['turno'] == turno):
                posicoes_ocupadas.append(slot_alocado['posicao'])
        
        if not posicoes_ocupadas:
            return False
        
        # Verificar se criaria janela
        todas_posicoes = sorted(posicoes_ocupadas + [posicao])
        
        for i in range(len(todas_posicoes) - 1):
            if todas_posicoes[i + 1] - todas_posicoes[i] > 1:
                return True
        
        return False
    
    def _criar_horario(self, aula: Dict[str, Any], slot: Dict[str, Any]):
        """
        Cria um registro de horário no banco de dados.
        """
        # Encontrar uma sala disponível
        sala = self._encontrar_sala_disponivel(slot, aula['turma'])
        
        if not sala:
            # Se não encontrou sala específica, pegar qualquer sala ativa
            sala = Sala.objects.filter(ativa=True).first()
            if not sala:
                raise Exception('Nenhuma sala ativa encontrada no sistema.')
        
        horario = Horario.objects.create(
            turma=aula['turma'],
            disciplina=aula['disciplina'],
            professor=aula['professor'],
            sala=sala,
            dia_semana=slot['dia'],
            turno=slot['turno'],
            horario_inicio=slot['horario_inicio'],
            horario_fim=slot['horario_fim']
        )
        
        # Adicionar informações do horário criado ao slot para rastreamento
        slot['aula'] = aula
        slot['horario_id'] = horario.id
    
    def _encontrar_sala_disponivel(
        self, 
        slot: Dict[str, Any], 
        turma: Turma
    ) -> Optional[Sala]:
        """
        Encontra uma sala disponível para o horário especificado.
        """
        dia = slot['dia']
        turno = slot['turno']
        inicio = slot['horario_inicio']
        fim = slot['horario_fim']
        
        # Buscar salas que não estão ocupadas no horário
        salas_ocupadas = Horario.objects.filter(
            dia_semana=dia,
            turno=turno,
            horario_inicio=inicio,
            horario_fim=fim
        ).values_list('sala_id', flat=True)
        
        salas_disponiveis = Sala.objects.filter(
            ativa=True
        ).exclude(
            id__in=salas_ocupadas
        )
        
        # Preferir salas com capacidade adequada
        salas_adequadas = salas_disponiveis.filter(
            capacidade__gte=turma.numero_alunos
        )
        
        if salas_adequadas.exists():
            return random.choice(list(salas_adequadas))
        elif salas_disponiveis.exists():
            return random.choice(list(salas_disponiveis))
        
        return None


def gerar_horarios_automaticamente(
    turmas: Optional[List[Turma]] = None,
    respeitar_preferencias: bool = True,
    evitar_janelas: bool = True,
    distribuir_dias: bool = True,
    limpar_anteriores: bool = False
) -> Dict[str, Any]:
    """
    Função principal para gerar horários automaticamente.
    
    Args:
        turmas: Lista de turmas para gerar horários. Se None, usa todas as ativas.
        respeitar_preferencias: Se deve considerar preferências dos professores.
        evitar_janelas: Se deve tentar evitar janelas nos horários.
        distribuir_dias: Se deve distribuir aulas ao longo da semana.
        limpar_anteriores: Se deve remover horários existentes antes.
        
    Returns:
        Dicionário com resultado da operação contendo:
        - sucesso: bool indicando se a operação foi bem-sucedida
        - horarios_criados: número de horários criados
        - turmas_processadas: número de turmas processadas
        - conflitos: lista de avisos e conflitos encontrados
        - erro: mensagem de erro (se sucesso=False)
    """
    gerador = GeradorHorarios()
    return gerador.gerar_horarios(
        turmas=turmas,
        respeitar_preferencias=respeitar_preferencias,
        evitar_janelas=evitar_janelas,
        distribuir_dias=distribuir_dias,
        limpar_anteriores=limpar_anteriores
    )
