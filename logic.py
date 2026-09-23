"""
logic.py
--------
Núcleo matemático do Penalty Hall: uma adaptação do Problema de Monty Hall
para o contexto de cobranças de pênalti no futebol.

Regras:
1. Uma região do gol (esquerda, centro, direita) é sorteada como "favorável":
   é a região que o goleiro NÃO consegue defender.
2. O jogador escolhe uma região para bater, sem saber qual é a favorável.
3. O goleiro, que conhece a região favorável, revela uma das duas regiões
   restantes que é desfavorável (nunca revela a favorável).
4. O jogador decide manter a escolha inicial ou trocar para a única região
   que sobrou (não escolhida, não revelada).
5. O resultado é comparado com a região favorável: gol ou defesa.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Regiao(str, Enum):
    ESQUERDA = "esquerda"
    CENTRO = "centro"
    DIREITA = "direita"

    @property
    def label(self) -> str:
        return {
            Regiao.ESQUERDA: "Canto Esquerdo",
            Regiao.CENTRO: "Centro do Gol",
            Regiao.DIREITA: "Canto Direito",
        }[self]

    @property
    def emoji(self) -> str:
        return {
            Regiao.ESQUERDA: "⬅️",
            Regiao.CENTRO: "⬆️",
            Regiao.DIREITA: "➡️",
        }[self]


REGIOES: List[Regiao] = list(Regiao)

Estrategia = str  # "manter" ou "trocar"


class EstrategiaInvalidaError(ValueError):
    pass


@dataclass
class RodadaPenalti:
    """Representa o estado completo de uma rodada do Penalty Hall."""

    regiao_favoravel: Regiao = field(default_factory=lambda: random.choice(REGIOES))
    escolha_inicial: Optional[Regiao] = None
    regiao_revelada: Optional[Regiao] = None
    decisao_final: Optional[Regiao] = None
    estrategia: Optional[Estrategia] = None

    # ---- passos da rodada -------------------------------------------------

    def escolher(self, regiao: Regiao) -> None:
        """Passo 1: o jogador escolhe a região onde vai bater."""
        self.escolha_inicial = regiao
        self.regiao_revelada = None
        self.decisao_final = None
        self.estrategia = None

    def revelar_goleiro(self) -> Regiao:
        """
        Passo 2: o goleiro revela uma região desfavorável, distinta da
        escolha inicial e da região favorável (ele nunca entrega a favorável).
        """
        if self.escolha_inicial is None:
            raise RuntimeError("É preciso escolher uma região antes da revelação.")

        candidatas = [
            r
            for r in REGIOES
            if r != self.escolha_inicial and r != self.regiao_favoravel
        ]
        # Quando a escolha inicial já é a favorável, sobram duas opções
        # desfavoráveis e o goleiro pode revelar qualquer uma delas.
        self.regiao_revelada = random.choice(candidatas)
        return self.regiao_revelada

    def regiao_alternativa(self) -> Regiao:
        """A única região que não foi escolhida nem revelada."""
        if self.regiao_revelada is None:
            raise RuntimeError("É preciso revelar uma região antes de calcular a troca.")
        (restante,) = [
            r
            for r in REGIOES
            if r != self.escolha_inicial and r != self.regiao_revelada
        ]
        return restante

    def decidir(self, estrategia: Estrategia) -> Regiao:
        """Passo 3: o jogador decide manter ou trocar sua escolha."""
        if estrategia == "manter":
            self.decisao_final = self.escolha_inicial
        elif estrategia == "trocar":
            self.decisao_final = self.regiao_alternativa()
        else:
            raise EstrategiaInvalidaError("estrategia deve ser 'manter' ou 'trocar'")
        self.estrategia = estrategia
        return self.decisao_final

    # ---- resultado ----------------------------------------------------

    @property
    def gol(self) -> bool:
        if self.decisao_final is None:
            raise RuntimeError("A rodada ainda não foi decidida.")
        return self.decisao_final == self.regiao_favoravel

    def resumo(self) -> dict:
        return {
            "regiao_favoravel": self.regiao_favoravel.value,
            "escolha_inicial": self.escolha_inicial.value if self.escolha_inicial else None,
            "regiao_revelada": self.regiao_revelada.value if self.regiao_revelada else None,
            "decisao_final": self.decisao_final.value if self.decisao_final else None,
            "estrategia": self.estrategia,
            "gol": self.gol if self.decisao_final else None,
        }
