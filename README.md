# Penalty Hall ⚽

Adaptação do **Problema de Monty Hall** para o contexto de cobranças de pênalti
no futebol, desenvolvida para a disciplina de Modelagem Linear para
Aprendizado de Máquina (Ciência da Computação).

## Estrutura do projeto

```
├── __init__.py
├── logic.py        
├── simulation.py    
│── app.py           
├── requirements.txt
└── README.md
```

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

A interface abre no navegador com três abas:

- **Jogar** - cobre pênaltis rodada a rodada, escolhendo manter ou trocar.
- **Simulação** - roda milhares de partidas instantaneamente e compara as
  estratégias com gráficos.
- **Como funciona** - explica o raciocínio matemático por trás do problema.

## Rodando só a simulação (sem interface)

```bash
python -m penalty_hall.simulation
```

Imprime no terminal o resultado de 10.000 rodadas para cada estratégia.
