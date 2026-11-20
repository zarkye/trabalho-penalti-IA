RA = 2024014377
NOMES = "Lucas Fagundes e João Biankati"

NUMEROS = [576, 205, 242]

# Linha 1: o RA de um dos dois, so numeros. Linha 2: os nomes da dupla, entre
# as aspas. NUMEROS: os 3 numeros do fuzzy, em cm, [esquerda, direita, teto],
# escolhidos olhando o 1o gol da tela (o mouse mostra o lado e a altura).
#
# Em cima de cada funcao estao o que ela recebe, o que devolve, dicas e a aula
# para consultar. Facam na ordem e rodem py main.py depois de cada uma.

import random

from pecas import ajustar, ida, neuronio, triangulo


# REGUA (tarefa 1)
# Recebe: pontos, uma lista de penaltis. Cada penalti e um par (entradas,
#   defendeu), como ([130, 91], 0): entradas = [lado, altura], em cm, e
#   defendeu = 1 (defesa) ou 0 (gol).
# Devolve: uma lista com um par (menor, maior) para cada coluna das entradas:
#   [(menor lado, maior lado), (menor altura, maior altura)].
# Dica 1: a coluna j e a lista com o entradas[j] de todos os penaltis.
# Dica 2: min() e max() dao o menor e o maior valor de uma lista.
# Consultem: o medir_regua do dados.py da aula de redes neurais (22/10) e a
#   regua da aula de regressao (15/10).
# Exemplo: regua([([100, 50], 0), ([300, 20], 1), ([200, 80], 0)])
#   devolve [(100, 300), (20, 80)].
def regua(pontos):
    r = []

    for j in range(len(pontos[0][0])):
        valores = []
        for penalti in pontos:
            entradas = penalti[0]
            valores.append(entradas[j])

        r.append((min(valores), max(valores)))

    return r


# NORMALIZAR (tarefa 1)
# Recebe: entradas, um penalti [lado, altura]; r, a lista de pares (menor,
#   maior) que a regua devolve.
# Devolve: uma lista nova, do mesmo tamanho, com cada valor na regua:
#   (valor - menor) / (maior - menor).
# Dica 1: o valor da posicao j usa o par r[j].
# Dica 2: nao cortem em 0 e 1: um penalti do teste pode dar menos que 0 ou
#   mais que 1.
# Consultem: o na_regua do dados.py da aula de redes neurais (22/10).
# Exemplo: normalizar([350, 10], [(100, 300), (20, 80)]) devolve
#   [1.25, -0.1666...].
def normalizar(entradas, r):
    resultado = []

    for j in range(len(entradas)):
        menor = r[j][0]
        maior = r[j][1]
        valor = (entradas[j] - menor) / (maior - menor)
        resultado.append(valor)

    return resultado


# MATRIZ (tarefa 1)
# Recebe: chances, as chances de defesa que um modelo deu (de 0 a 1); certos,
#   o que aconteceu (1 = defesa, 0 = gol), na mesma ordem; limiar, o numero a
#   partir do qual o modelo diz "pega" (o main.py usa 0,5).
# Devolve: 4 numeros, nesta ordem: VP, FP, FN, VN.
#   VP: disse pega e foi defesa    FN: disse gol e foi defesa
#   FP: disse pega e foi gol       VN: disse gol e foi gol
# Dica 1: a posicao i das duas listas e o mesmo penalti.
# Dica 2: chance igual ao limiar conta como "pega" (>=).
# Consultem: a matriz do rede.py da aula de redes neurais (22/10).
# Exemplo: matriz([0.9, 0.2, 0.5, 0.4], [1, 1, 0, 0], 0.5) devolve
#   (1, 1, 1, 1).
def matriz(chances, certos, limiar):
    vp = 0
    fp = 0
    fn = 0
    vn = 0

    for i in range(len(chances)):
        chance = chances[i]
        certo = certos[i]

        if chance >= limiar:
            if certo == 1:
                vp += 1
            else:
                fp += 1
        else:
            if certo == 1:
                fn += 1
            else:
                vn += 1

    return vp, fp, fn, vn


# FUZZY (tarefa 2): as regras sao de voces
# Recebe: lado e altura do chute, em cm; n, uma lista [esquerda, direita,
#   teto] (o main.py manda o NUMEROS; o genetico manda outras listas).
# Devolve: a chance de defesa, um numero de 0 a 1.
# Dica 1: com o triangulo, calculem quanto o chute e "meio" (entre esquerda e
#   direita) e quanto e "baixo" (abaixo do teto), de 0 a 1. Com o pico numa
#   ponta, o triangulo vira rampa.
# Dica 2: a forca de uma regra com E e o min das partes; o NAO e 1 menos o
#   valor. Pelo menos uma regra diz defende (saida 1) e uma diz gol (saida 0).
# Dica 3: a chance e a media das saidas pesada pela forca de cada regra: a
#   soma de forca x saida, dividida pela soma das forcas. Se a soma das forcas
#   der 0, nao da para dividir: devolvam 0.
# Dica 4: usem os numeros do n, nunca o NUMEROS direto.
# Consultem: o triangulo e a lista REGRAS do fuzzy.py da aula de fuzzy (24/09).
# Exemplo: forcas 0,75 (defende), 0,25 e 0,25 (gol) dao
#   (0,75 x 1 + 0,25 x 0 + 0,25 x 0) / (0,75 + 0,25 + 0,25) = 0,6.
def fuzzy(lado, altura, n):
    esquerda = n[0]
    direita = n[1]
    teto = n[2]

    meio = triangulo(lado, 0, (esquerda + direita) / 2, 732)
    baixo = triangulo(altura, 0, 0, teto)

    nao_meio = 1 - meio
    nao_baixo = 1 - baixo

    regras = []
    regras.append((min(meio, baixo), 1))
    regras.append((min(meio, nao_baixo), 0))
    regras.append((min(nao_meio, baixo), 0))
    regras.append((min(nao_meio, nao_baixo), 1))

    soma_forcas = 0
    soma_ponderada = 0

    for regra in regras:
        forca = regra[0]
        saida = regra[1]
        soma_forcas += forca
        soma_ponderada += forca * saida

    if soma_forcas == 0:
        return 0

    return soma_ponderada / soma_forcas


# NOTA (tarefa 3): a nota de um DNA no genetico
# Recebe: n, uma lista [esquerda, direita, teto] (o DNA); pontos, a lista de
#   penaltis ([lado, altura], defendeu).
# Devolve: quantos penaltis o fuzzy, com os numeros n, acerta.
# Dica 1: o fuzzy diz "pega" com chance de 0,5 para cima. Acertar e dizer pega
#   num penalti que foi defesa (1), ou gol num que foi gol (0).
# Dica 2: chamem o fuzzy de voces com o n em cada penalti.
# Consultem: o acertos do knn.py da aula de KNN (08/10): o jeito de contar e
#   o mesmo.
# Exemplo: se o fuzzy da 0,9, 0,2 e 0,5 em tres penaltis que foram defesa,
#   defesa e gol, a nota e 1 (so acerta o 1o).
def nota(n, pontos):
    certos = 0

    for penalti in pontos:
        entradas = penalti[0]
        certo = penalti[1]

        lado = entradas[0]
        altura = entradas[1]
        chance = fuzzy(lado, altura, n)

        if chance >= 0.5:
            disse = 1
        else:
            disse = 0

        if disse == certo:
            certos += 1

    return certos


# MUTAR (tarefa 3): a mutacao do genetico
# Recebe: dna, uma lista de 3 numeros; taxa, a chance de cada numero mudar
#   (0,3 = 30%); passo, o maximo que ele anda, em cm (o main.py usa 30).
# Devolve: o dna, com os numeros que mudaram.
# Dica 1: para cada posicao, sorteiem se ela muda: random.random() da um
#   numero de 0 a 1.
# Dica 2: quem muda anda um valor sorteado entre -passo e +passo:
#   random.uniform(a, b) da um numero qualquer de a ate b.
# Consultem: o mutar do genetico.py da aula de algoritmos geneticos (01/10).
#   La o gene era 0 ou 1 e trocava; aqui ele anda um pouco.
def mutar(dna, taxa, passo):
    novo = []

    for numero in dna:
        if random.random() < taxa:
            numero = numero + random.uniform(-passo, passo)
        novo.append(numero)

    return novo


# DISTANCIA (tarefa 4)
# Recebe: a e b, duas listas de numeros do mesmo tamanho, como [100, 50].
# Devolve: um numero: a soma das diferencas sem sinal, posicao a posicao.
# Dica: abs() tira o sinal: abs(-40) da 40.
# Consultem: a distancia do knn.py da aula de KNN (08/10).
# Exemplo: distancia([100, 50], [130, 10]) devolve 30 + 40 = 70.
def distancia(a, b):
    total = 0

    for i in range(len(a)):
        diferenca = abs(a[i] - b[i])
        total += diferenca

    return total


# KNN (tarefa 4)
# Recebe: entradas, um penalti [lado, altura]; treino, a lista de penaltis
#   ([lado, altura], defendeu); k, quantos vizinhos olhar (o main.py usa 7).
# Devolve: a chance de defesa, de 0 a 1: entre os k penaltis do treino mais
#   perto das entradas, a fracao que foi defesa.
# Dica 1: usem a distancia de voces para medir as entradas contra cada
#   penalti do treino.
# Dica 2: o .sort() de uma lista de pares ordena pelo 1o valor do par.
# Dica 3: a fracao e quantas defesas ha entre os k, dividido por k.
# Consultem: o vizinhos e o adivinhar do knn.py da aula de KNN (08/10). La a
#   resposta era o numero mais votado; aqui e a fracao de defesas.
# Exemplo: com k = 3, se os 3 mais perto foram defesa, gol e defesa, devolve
#   2 / 3 = 0.666...
def knn(entradas, treino, k):
    vizinhos = []

    for penalti in treino:
        pontos = penalti[0]
        certo = penalti[1]
        d = distancia(entradas, pontos)
        vizinhos.append((d, certo))

    vizinhos.sort()
    vizinhos = vizinhos[:k]

    if len(vizinhos) == 0:
        return 0

    defesas = 0
    for vizinho in vizinhos:
        certo = vizinho[1]
        defesas += certo

    return defesas / k


# TREINAR_LOGISTICA (tarefa 5): a regressao logistica, um neuronio so
# Recebe: pontos, a lista de penaltis ([lado, altura], defendeu); taxa, o
#   tamanho do passo (o main.py usa 0,05); rodadas, quantas vezes passar por
#   todos os pontos (o main.py usa 200).
# Devolve: os 3 pesos: [peso do lado, peso da altura, vies].
# Dica 1: comecem com os pesos [0, 0, 0].
# Dica 2: em cada rodada, para cada ponto: a chance com o neuronio, a culpa
#   (chance - certo) e o ajustar. Os dois vem prontos do pecas.py.
# Consultem: o treinar e a volta do rede.py da aula de redes neurais (22/10):
#   aqui so tem um neuronio, como a saida da rede.
# Exemplo: treinar_logistica([([1, 0], 1), ([0, 1], 0)], 0.5, 1) devolve
#   [0.25, -0.2811..., -0.0311...].
def treinar_logistica(pontos, taxa, rodadas):
    pesos = [0, 0, 0]

    for rodada in range(rodadas):
        for penalti in pontos:
            entradas = penalti[0]
            certo = penalti[1]

            chance = neuronio(entradas, pesos)
            culpa = chance - certo
            ajustar(pesos, entradas, culpa, taxa)

    return pesos


# VOLTA (tarefa 6): o treino da rede neural, um penalti de cada vez
# Recebe: rede, o par (escondidos, saida): escondidos e a lista com os pesos
#   de cada neuronio escondido, e saida, os pesos do neuronio de saida;
#   entradas, um penalti [lado, altura]; certo, 1 (defesa) ou 0 (gol); taxa,
#   o tamanho do passo.
# Devolve: nada. Ela muda os pesos dentro da rede.
# Dica 1: a ida(rede, entradas) devolve o h (a saida de cada escondido) e a
#   chance.
# Dica 2: o erro e chance - certo. A culpa do escondido j e
#   erro x peso j da saida x h[j] x (1 - h[j]), e o ajustar dele usa essa culpa.
# Dica 3: ajustem a saida por ultimo, com o h como entradas e o erro como
#   culpa: a culpa dos escondidos usa o peso antigo da saida.
# Consultem: a volta do rede.py da aula de redes neurais (22/10).
def volta(rede, entradas, certo, taxa):
    escondidos = rede[0]
    saida = rede[1]

    h = ida(rede, entradas)[0]
    chance = ida(rede, entradas)[1]
    erro = chance - certo

    pesos_saida_antigos = list(saida)
    culpas_escondidos = []

    for j in range(len(escondidos)):
        culpa = (erro * pesos_saida_antigos[j] * h[j]
                 * (1 - h[j]))
        culpas_escondidos.append(culpa)

    ajustar(saida, h, erro, taxa)

    for j in range(len(escondidos)):
        ajustar(escondidos[j], entradas, culpas_escondidos[j], taxa)
