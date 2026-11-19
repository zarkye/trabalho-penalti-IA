import math
import random


def triangulo(x, a, pico, b):
    if b <= a:
        return 0.0
    if x <= a:
        return 1.0 if pico <= a else 0.0
    if x >= b:
        return 1.0 if pico >= b else 0.0
    if x <= pico:
        return (x - a) / (pico - a)
    return (b - x) / (b - pico)


def sigmoide(z):
    if z < -500:
        return 0.0
    return 1 / (1 + math.exp(-z))


def neuronio(entradas, pesos):
    soma = pesos[-1]
    for i in range(len(entradas)):
        soma += entradas[i] * pesos[i]
    return sigmoide(soma)


def ajustar(pesos, entradas, culpa, taxa):
    for i in range(len(entradas)):
        pesos[i] -= taxa * culpa * entradas[i]
    pesos[-1] -= taxa * culpa


def ida(rede, entradas):
    escondidos, saida = rede
    h = [neuronio(entradas, pesos) for pesos in escondidos]
    return h, neuronio(h, saida)


def rede_sorteada(escondidos, pontos, semente):
    sorteio = random.Random(semente)
    lista = []
    for _ in range(escondidos):
        (x1, x2), _ = sorteio.choice(pontos)
        angulo = sorteio.uniform(0, 2 * math.pi)
        w1 = 6 * math.cos(angulo)
        w2 = 6 * math.sin(angulo)
        lista.append([w1, w2, -(w1 * x1 + w2 * x2)])
    saida = [sorteio.uniform(-1, 1) for _ in range(escondidos + 1)]
    return lista, saida


def treinar(volta, rede, pontos, taxa, rodadas):
    for _ in range(rodadas):
        for entradas, certo in pontos:
            volta(rede, entradas, certo, taxa)


def dna_aleatorio():
    return [random.uniform(0, 732), random.uniform(0, 732),
            random.uniform(0, 244)]


def selecionar(dnas, notas):
    vencedor = random.randrange(len(dnas))
    for _ in range(2):
        rival = random.randrange(len(dnas))
        if notas[rival] > notas[vencedor]:
            vencedor = rival
    return dnas[vencedor]


def cruzar(pai, mae):
    corte = random.randrange(1, len(pai))
    return pai[:corte] + mae[corte:]


def evoluir(nota, mutar, pontos, tamanho, geracoes, taxa, passo, semente):
    random.seed(semente)
    dnas = [dna_aleatorio() for _ in range(tamanho)]
    historico = []
    for _ in range(geracoes):
        notas = [nota(dna, pontos) for dna in dnas]
        historico.append(max(notas))
        nova = [dnas[notas.index(max(notas))]]
        while len(nova) < tamanho:
            pai = selecionar(dnas, notas)
            mae = selecionar(dnas, notas)
            nova.append(mutar(cruzar(pai, mae), taxa, passo))
        dnas = nova
    notas = [nota(dna, pontos) for dna in dnas]
    historico.append(max(notas))
    return dnas[notas.index(max(notas))], historico
