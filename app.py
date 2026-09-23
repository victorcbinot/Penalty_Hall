"""
app.py
------
Front-end interativo do Penalty Hall, construído com Streamlit.

Executar com:
    streamlit run penalty_hall/app.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from penalty_hall.logic import REGIOES, Regiao, RodadaPenalti
from penalty_hall.simulation import evolucao_convergencia, simular_comparacao

# --------------------------------------------------------------------------
# Configuração da página e estilo (tema futebol)
# --------------------------------------------------------------------------

st.set_page_config(page_title="Penalty Hall", page_icon="⚽", layout="wide")

CSS = """
<style>
.stApp { background-color: #0b3d1e; }
h1, h2, h3, p, label, span { color: #f3f6f4 !important; }
div[data-testid="stMetricValue"] { color: #ffd60a !important; }
.gol-box {
    display:flex; gap:10px; margin: 12px 0 20px 0;
}
.regiao {
    flex:1; padding: 34px 8px; border-radius: 10px; text-align:center;
    font-weight:700; font-size:1.05rem; color:white;
}
.disponivel { background:#2d6a4f; border: 2px solid #74c69d; }
.escolhida  { background:#ffb703; color:#0b3d1e; border: 2px solid #fff; }
.revelada   { background:#6c757d; opacity:0.55; text-decoration: line-through; }
.resultado-gol    { background:#2d6a4f; padding:16px; border-radius:10px; font-size:1.3rem; text-align:center;}
.resultado-defesa { background:#9d0208; padding:16px; border-radius:10px; font-size:1.3rem; text-align:center;}
.card {
    background:#124f2c; padding:16px 20px; border-radius:12px; margin-bottom:10px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Estado da sessão
# --------------------------------------------------------------------------

def estado_inicial() -> None:
    st.session_state.setdefault("rodada", None)
    st.session_state.setdefault("fase", "escolha")  # escolha -> revelacao -> resultado
    st.session_state.setdefault(
        "stats", {"manter": {"gols": 0, "total": 0}, "trocar": {"gols": 0, "total": 0}}
    )


estado_inicial()

# --------------------------------------------------------------------------
# Cabeçalho
# --------------------------------------------------------------------------

st.title("⚽ Penalty Hall")
st.caption(
    "O Problema de Monty Hall aplicado a cobranças de pênalti — "
    "modelagem probabilística com Python."
)

aba_jogo, aba_simulacao, aba_sobre = st.tabs(["🎮 Jogar", "📊 Simulação", "ℹ️ Como funciona"])

# --------------------------------------------------------------------------
# ABA 1 — Jogo interativo, rodada a rodada
# --------------------------------------------------------------------------

with aba_jogo:
    col_jogo, col_stats = st.columns([2, 1])

    with col_jogo:
        rodada: RodadaPenalti | None = st.session_state["rodada"]
        fase = st.session_state["fase"]

        if fase == "escolha" or rodada is None:
            st.subheader("Escolha onde bater o pênalti")
            st.markdown('<div class="gol-box">', unsafe_allow_html=True)
            cols = st.columns(3)
            for c, regiao in zip(cols, REGIOES):
                with c:
                    st.markdown(
                        f'<div class="regiao disponivel">{regiao.emoji}<br>{regiao.label}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Bater no {regiao.label}", key=f"escolha_{regiao.value}"):
                        nova = RodadaPenalti()
                        nova.escolher(regiao)
                        nova.revelar_goleiro()
                        st.session_state["rodada"] = nova
                        st.session_state["fase"] = "decisao"
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        elif fase == "decisao":
            st.subheader("O goleiro estudou o lance...")
            cols = st.columns(3)
            for c, regiao in zip(cols, REGIOES):
                with c:
                    classe = "disponivel"
                    if regiao == rodada.escolha_inicial:
                        classe = "escolhida"
                    if regiao == rodada.regiao_revelada:
                        classe = "revelada"
                    st.markdown(
                        f'<div class="regiao {classe}">{regiao.emoji}<br>{regiao.label}</div>',
                        unsafe_allow_html=True,
                    )
            st.info(
                f"O goleiro revelou que **{rodada.regiao_revelada.label}** é desfavorável "
                f"(ele nunca revela a região favorável). "
                f"Sua escolha inicial foi **{rodada.escolha_inicial.label}**."
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🔒 Manter escolha", use_container_width=True):
                    rodada.decidir("manter")
                    st.session_state["fase"] = "resultado"
                    st.rerun()
            with b2:
                alvo = rodada.regiao_alternativa()
                if st.button(f"🔁 Trocar para {alvo.label}", use_container_width=True):
                    rodada.decidir("trocar")
                    st.session_state["fase"] = "resultado"
                    st.rerun()

        elif fase == "resultado":
            stats = st.session_state["stats"]
            stats[rodada.estrategia]["total"] += 1
            if rodada.gol:
                stats[rodada.estrategia]["gols"] += 1

            cols = st.columns(3)
            for c, regiao in zip(cols, REGIOES):
                with c:
                    classe = "disponivel"
                    if regiao == rodada.decisao_final:
                        classe = "escolhida"
                    if regiao == rodada.regiao_revelada:
                        classe = "revelada"
                    marca = " 🎯" if regiao == rodada.regiao_favoravel else ""
                    st.markdown(
                        f'<div class="regiao {classe}">{regiao.emoji}<br>{regiao.label}{marca}</div>',
                        unsafe_allow_html=True,
                    )

            if rodada.gol:
                st.markdown('<div class="resultado-gol">⚽ GOOOL!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="resultado-defesa">🧤 DEFESA!</div>', unsafe_allow_html=True)

            st.write(
                f"Estratégia usada: **{rodada.estrategia}** · "
                f"Região favorável era: **{rodada.regiao_favoravel.label}**"
            )

            if st.button("▶️ Próxima rodada"):
                st.session_state["rodada"] = None
                st.session_state["fase"] = "escolha"
                st.rerun()

    with col_stats:
        st.subheader("📈 Estatísticas da sessão")
        stats = st.session_state["stats"]
        for estrategia in ("manter", "trocar"):
            total = stats[estrategia]["total"]
            gols = stats[estrategia]["gols"]
            taxa = gols / total if total else 0
            st.markdown(
                f'<div class="card"><b>{estrategia.capitalize()}</b><br>'
                f"{gols}/{total} gols · {taxa:.1%} de sucesso</div>",
                unsafe_allow_html=True,
            )
        st.caption("Jogue algumas rodadas com cada estratégia para ver a diferença.")

# --------------------------------------------------------------------------
# ABA 2 — Simulação em massa
# --------------------------------------------------------------------------

with aba_simulacao:
    st.subheader("Simule milhares de pênaltis instantaneamente")

    n = st.slider("Número de rodadas por estratégia", 100, 100_000, 5_000, step=100)

    if st.button("▶️ Rodar simulação"):
        resultados = simular_comparacao(n)

        m1, m2 = st.columns(2)
        m1.metric(
            "Manter a escolha",
            f"{resultados['manter'].taxa_sucesso:.2%}",
            help="Probabilidade teórica: 33,33%",
        )
        m2.metric(
            "Trocar a escolha",
            f"{resultados['trocar'].taxa_sucesso:.2%}",
            help="Probabilidade teórica: 66,67%",
        )

        # Gráfico de barras: manter vs trocar
        fig1, ax1 = plt.subplots(figsize=(5, 3.2))
        nomes = ["Manter", "Trocar"]
        taxas = [resultados["manter"].taxa_sucesso, resultados["trocar"].taxa_sucesso]
        cores = ["#9d0208", "#2d6a4f"]
        ax1.bar(nomes, taxas, color=cores)
        ax1.axhline(1 / 3, color="#9d0208", linestyle="--", linewidth=1, alpha=0.6)
        ax1.axhline(2 / 3, color="#2d6a4f", linestyle="--", linewidth=1, alpha=0.6)
        ax1.set_ylim(0, 1)
        ax1.set_ylabel("Taxa de sucesso")
        ax1.set_title(f"Resultado com {n:,} rodadas".replace(",", "."))
        for i, v in enumerate(taxas):
            ax1.text(i, v + 0.02, f"{v:.1%}", ha="center", fontweight="bold")
        st.pyplot(fig1)

        # Gráfico de convergência
        st.subheader("Convergência para a probabilidade teórica")
        xs_m, ys_m = evolucao_convergencia(n, passo=max(1, n // 200), estrategia="manter")
        xs_t, ys_t = evolucao_convergencia(n, passo=max(1, n // 200), estrategia="trocar")

        fig2, ax2 = plt.subplots(figsize=(7, 3.5))
        ax2.plot(xs_m, ys_m, label="Manter", color="#9d0208")
        ax2.plot(xs_t, ys_t, label="Trocar", color="#2d6a4f")
        ax2.axhline(1 / 3, color="#9d0208", linestyle="--", linewidth=1, alpha=0.5)
        ax2.axhline(2 / 3, color="#2d6a4f", linestyle="--", linewidth=1, alpha=0.5)
        ax2.set_xlabel("Número de rodadas")
        ax2.set_ylabel("Taxa de sucesso acumulada")
        ax2.legend()
        st.pyplot(fig2)

# --------------------------------------------------------------------------
# ABA 3 — Explicação do problema
# --------------------------------------------------------------------------

with aba_sobre:
    st.subheader("Como funciona o Penalty Hall")
    st.markdown(
        """
1. Uma das três regiões do gol é sorteada como **favorável** (o goleiro não a defende).
2. Você escolhe uma região para bater, sem saber qual é a favorável — **1/3** de chance de acertar de cara.
3. O goleiro, que conhece a região favorável, **revela uma região desfavorável** entre as que você não escolheu.
4. Você decide **manter** sua escolha inicial ou **trocar** para a única região restante.
5. O resultado é comparado à região favorável: **gol** ou **defesa**.

**Por que trocar é melhor?** A revelação do goleiro não é aleatória: ele nunca revela a
região favorável. Isso faz com que, nos 2/3 dos casos em que a escolha inicial estava
errada, a região restante (após a revelação) seja exatamente a favorável. Por isso:

- Manter → **≈ 33,33%** de chance de gol
- Trocar → **≈ 66,67%** de chance de gol
        """
    )
