import csv
import math
import random
import sys

LADO = 732
ALTURA = 244
TOTAL = 600
TREINO = 400


def goleiro(ra):
    sorteio = random.Random(ra)
    return (sorteio.uniform(290, 440), sorteio.uniform(45, 80),
            sorteio.uniform(160, 210), sorteio.uniform(95, 120)), sorteio


def gerar(ra):
    (cx, cy, rx, ry), sorteio = goleiro(ra)
    penaltis = []
    for _ in range(TOTAL):
        mira = sorteio.random()
        if mira < 0.33:
            lado = sorteio.gauss(100, 75)
        elif mira < 0.66:
            lado = sorteio.gauss(632, 75)
        else:
            lado = sorteio.gauss(366, 110)
        lado = min(max(lado, 15), LADO - 15)
        if sorteio.random() < 0.55:
            altura = abs(sorteio.gauss(30, 45))
        else:
            altura = sorteio.uniform(20, 230)
        altura = min(max(altura, 10), ALTURA - 10)
        d = ((lado - cx) / rx) ** 2 + ((altura - cy) / ry) ** 2
        chance = 0.93 / (1 + math.exp(5 * (d - 1)))
        defendeu = 1 if sorteio.random() < chance else 0
        penaltis.append(([round(lado), round(altura)], defendeu))
    return penaltis


def carregar(ra):
    penaltis = gerar(ra)
    return penaltis[:TREINO], penaltis[TREINO:]


def gravar_csv(ra):
    nome = f"penaltis_{ra}.csv"
    with open(nome, "w", encoding="utf-8", newline="") as arquivo:
        saida = csv.writer(arquivo, delimiter=";")
        saida.writerow(["lado_cm", "altura_cm", "defendeu", "parte"])
        for i, ((lado, altura), defendeu) in enumerate(gerar(ra)):
            saida.writerow([lado, altura, defendeu,
                            "treino" if i < TREINO else "teste"])
    print(f"Gravei {nome}: {TOTAL} penaltis ({TREINO} de treino).")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Use: py dados.py RA   (o RA so com numeros)")
    else:
        gravar_csv(int(sys.argv[1]))
