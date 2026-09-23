"""
simulation.py
--------------
Executa simulações em massa do Penalty Hall para comparar, estatisticamente,
as estratégias "manter" e "trocar", e mostrar a convergência para as
probabilidades teóricas (1/3 e 2/3).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .logic import REGIOES, RodadaPenalti


@dataclass
class ResultadoSimulacao:
    estrategia: str
    total: int
    gols: int

    @property
    def defesas(self) -> int:
        return self.total - self.gols

    @property
    def taxa_sucesso(self) -> float:
        return self.gols / self.total if self.total else 0.0


def simular_rodada(estrategia: str) -> bool:
    """Executa uma rodada completa e retorna True se foi gol."""
    rodada = RodadaPenalti()
    escolha = random.choice(REGIOES)
    rodada.escolher(escolha)
    rodada.revelar_goleiro()
    rodada.decidir(estrategia)
    return rodada.gol


def simular_partidas(n: int, estrategia: str) -> ResultadoSimulacao:
    """Simula n rodadas usando sempre a mesma estratégia."""
    gols = sum(simular_rodada(estrategia) for _ in range(n))
    return ResultadoSimulacao(estrategia=estrategia, total=n, gols=gols)


def simular_comparacao(n: int) -> Dict[str, ResultadoSimulacao]:
    """Simula n rodadas para cada estratégia e retorna os dois resultados."""
    return {
        "manter": simular_partidas(n, "manter"),
        "trocar": simular_partidas(n, "trocar"),
    }


def evolucao_convergencia(
    n_max: int, passo: int = 50, estrategia: str = "trocar"
) -> Tuple[List[int], List[float]]:
    """
    Retorna (x, y) onde x é o número de rodadas jogadas e y é a taxa de
    sucesso acumulada até aquele ponto — útil para visualizar a convergência
    rumo à probabilidade teórica (1/3 ou 2/3).
    """
    xs: List[int] = []
    ys: List[float] = []
    gols = 0
    for i in range(1, n_max + 1):
        gols += simular_rodada(estrategia)
        if i % passo == 0 or i == n_max:
            xs.append(i)
            ys.append(gols / i)
    return xs, ys


if __name__ == "__main__":
    # Demonstração rápida via terminal
    n = 10_000
    resultados = simular_comparacao(n)
    print(f"Simulação com {n:,} rodadas por estratégia".replace(",", "."))
    for nome, r in resultados.items():
        print(f"  {nome.upper():8s} -> {r.gols}/{r.total} gols "
              f"({r.taxa_sucesso:.2%})")
