import ast
import inspect
import os
import random
import sys
import time
import traceback

sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import dados
import pecas

K = 7
ESCONDIDOS = 4
TAXA = 0.5
RODADAS = 200
TAXA_LOGISTICA = 0.05
RODADAS_LOGISTICA = 200
TAMANHO = 30
GERACOES = 40
TAXA_MUTACAO = 0.3
PASSO = 30
LIMIAR = 0.5
SEMENTE = 1

FUNCOES = ("regua", "normalizar", "matriz", "fuzzy", "nota", "mutar",
           "distancia", "knn", "treinar_logistica", "volta")
PRECISA = {"knn": ("distancia",)}


def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return f"{100 * x:.1f}%".replace(".", ",")


def linha_do_trabalho(erro):
    for quadro in reversed(traceback.extract_tb(erro.__traceback__)):
        if quadro.filename.endswith("trabalho.py"):
            return quadro
    return None


try:
    import trabalho
except SyntaxError as erro:
    print(f"\n  O trabalho.py tem um erro de digitação na linha {erro.lineno}:")
    print(f"    {(erro.text or '').strip()}")
    print(f"  ({erro.msg})\n")
    raise SystemExit(1)
except ModuleNotFoundError as erro:
    print(f"\n  Não achei o {erro.name}.py nesta pasta.\n")
    raise SystemExit(1)
except Exception as erro:
    quadro = linha_do_trabalho(erro)
    if quadro:
        print(f"\n  O trabalho.py deu erro na linha {quadro.lineno}:")
        print(f"    {quadro.line}")
    else:
        print("\n  O trabalho.py deu erro ao abrir:")
    print(f"  ({type(erro).__name__}: {erro})\n")
    raise SystemExit(1)


class NaoBate(Exception):
    pass


def vazia(nome):
    funcao = getattr(trabalho, nome, None)
    if funcao is None:
        return True
    try:
        arvore = ast.parse(inspect.getsource(funcao).strip())
    except (OSError, TypeError, SyntaxError):
        return False
    corpo = arvore.body[0].body
    return all(isinstance(c, ast.Pass) for c in corpo)


def numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def perto(x, y, folga=1e-6):
    return numero(x) and abs(x - y) <= folga


def lista_perto(deu, certo, folga=1e-6):
    return (isinstance(deu, (list, tuple)) and len(deu) == len(certo)
            and all(perto(a, b, folga) for a, b in zip(deu, certo)))


def mostrar_num(x):
    if isinstance(x, float):
        return f"{x:.4f}".rstrip("0").rstrip(".")
    if isinstance(x, (list, tuple)):
        dentro = ", ".join(mostrar_num(v) for v in x)
        return f"[{dentro}]" if isinstance(x, list) else f"({dentro})"
    return repr(x)


def sem_return(deu):
    if deu is None:
        raise NaoBate("não devolveu nada (falta o return).")


def testar_regua(treino):
    exemplo = [([100, 50], 0), ([300, 20], 1), ([200, 80], 0)]
    deu = trabalho.regua(exemplo)
    sem_return(deu)
    certo = [(100, 300), (20, 80)]
    if (not isinstance(deu, (list, tuple)) or len(deu) != 2
            or not all(lista_perto(a, b) for a, b in zip(deu, certo))):
        raise NaoBate(f"com os 3 pênaltis {mostrar_num([e for e, _ in exemplo])}"
                      f" devolveu {mostrar_num(deu)}; o certo é "
                      f"[(100, 300), (20, 80)].")
    return ""


def testar_normalizar(treino):
    r = [(100, 300), (20, 80)]
    for entradas, certo in (([200, 35], [0.5, 0.25]),
                            ([350, 10], [1.25, -1 / 6])):
        deu = trabalho.normalizar(entradas, r)
        sem_return(deu)
        if not lista_perto(deu, certo):
            raise NaoBate(f"normalizar({entradas}, [(100, 300), (20, 80)]) "
                          f"devolveu {mostrar_num(deu)}; o certo é "
                          f"{mostrar_num(certo)}.")
    return ""


def testar_matriz(treino):
    chances = [0.9, 0.2, 0.5, 0.4, 0.7, 0.1]
    certos = [1, 1, 0, 0, 1, 0]
    for limiar, certo in ((0.5, (2, 1, 1, 2)), (0.8, (1, 0, 2, 3))):
        deu = trabalho.matriz(chances, certos, limiar)
        sem_return(deu)
        if not (isinstance(deu, (list, tuple)) and tuple(deu) == certo):
            raise NaoBate(f"com as chances {chances}, os certos {certos} e o "
                          f"limiar {limiar}, devolveu {mostrar_num(deu)}; o "
                          f"certo é {certo} (VP, FP, FN, VN).")
    return ""


def grade():
    return [(lado, altura) for lado in range(0, 733, 61)
            for altura in range(0, 245, 61)]


def acertos_fuzzy(n, pontos):
    certos = 0
    for (lado, altura), certo in pontos:
        disse = 1 if trabalho.fuzzy(lado, altura, n) >= 0.5 else 0
        certos += disse == certo
    return certos


def testar_fuzzy(treino):
    n = list(trabalho.NUMEROS)
    if len(n) != 3 or not all(numero(v) for v in n):
        raise NaoBate("NUMEROS tem que ser uma lista de 3 números: "
                      "[esquerda, direita, teto].")
    if all(v == 0 for v in n):
        raise NaoBate("ponha em NUMEROS (no topo do trabalho.py) os 3 números "
                      "de vocês.")
    valores = []
    for lado, altura in grade():
        deu = trabalho.fuzzy(lado, altura, n)
        sem_return(deu)
        if not numero(deu) or deu < -1e-9 or deu > 1 + 1e-9:
            raise NaoBate(f"fuzzy({lado}, {altura}, NUMEROS) devolveu "
                          f"{mostrar_num(deu)}: tem que ser uma chance, de 0 "
                          f"a 1.")
        valores.append(deu)
    if max(valores) - min(valores) < 1e-9:
        raise NaoBate(f"devolve {mostrar_num(valores[0])} no gol inteiro: as "
                      f"regras não mudam com o lado nem com a altura.")
    if max(valores) < 0.5:
        raise NaoBate("com os NUMEROS de vocês, o fuzzy não diz “pega” em "
                      "nenhum lugar do gol (nenhuma chance chega a 0,5).")
    if min(valores) >= 0.5:
        raise NaoBate("com os NUMEROS de vocês, o fuzzy diz “pega” no gol "
                      "inteiro (nenhuma chance fica abaixo de 0,5).")
    um = [trabalho.fuzzy(lado, altura, [100, 600, 200])
          for lado, altura in grade()]
    outro = [trabalho.fuzzy(lado, altura, [400, 450, 30])
             for lado, altura in grade()]
    if all(perto(a, b, 1e-12) for a, b in zip(um, outro)):
        raise NaoBate("dá o mesmo com qualquer lista n: os números das "
                      "regras têm que vir do n (é o n que o genético muda).")
    return (f"com os NUMEROS de vocês, acerta {acertos_fuzzy(n, treino)} "
            f"de {len(treino)} no treino")


NOTA_PONTOS = [([100, 50], 1), ([200, 50], 0), ([300, 50], 0), ([400, 50], 1),
               ([200, 90], 1)]
NOTA_CHANCES = {100: 0.5, 200: 0.9, 300: 0.2, 400: 0.49}


def testar_nota(treino):
    vistos = []

    def fuzzy_de_teste(lado, altura, n):
        vistos.append(list(n))
        return NOTA_CHANCES[lado]

    original = trabalho.fuzzy
    trabalho.fuzzy = fuzzy_de_teste
    try:
        deu = trabalho.nota([1, 2, 3], NOTA_PONTOS)
    finally:
        trabalho.fuzzy = original
    sem_return(deu)
    if not vistos or any(v != [1, 2, 3] for v in vistos):
        raise NaoBate("a nota tem que chamar o fuzzy com o n que ela recebe.")
    if deu != 3:
        raise NaoBate(f"com um fuzzy de teste que dá as chances 0,5, 0,9, "
                      f"0,2, 0,49 e 0,9 para 5 pênaltis (certos: 1, 0, 0, 1 "
                      f"e 1), devolveu {mostrar_num(deu)}; o certo é 3.")
    if estado_fuzzy_ok(treino):
        return (f"os NUMEROS de vocês acertam "
                f"{trabalho.nota(list(trabalho.NUMEROS), treino)} de "
                f"{len(treino)}")
    return ""


def estado_fuzzy_ok(treino):
    try:
        testar_fuzzy(treino)
        return True
    except Exception:
        return False


def testar_mutar(treino):
    random.seed(7)
    original = [100.0, 500.0, 150.0]
    deu = trabalho.mutar(list(original), 0, PASSO)
    sem_return(deu)
    if not lista_perto(deu, original):
        raise NaoBate(f"com taxa 0, nada pode mudar: [100, 500, 150] virou "
                      f"{mostrar_num(deu)}.")
    mudou = 0
    for _ in range(300):
        deu = trabalho.mutar(list(original), 1, PASSO)
        if not (isinstance(deu, list) and len(deu) == 3
                and all(numero(v) for v in deu)):
            raise NaoBate(f"tem que devolver o DNA, a lista de 3 números; "
                          f"devolveu {mostrar_num(deu)}.")
        for antes, depois in zip(original, deu):
            if abs(depois - antes) > PASSO + 1e-9:
                raise NaoBate(f"com passo {PASSO}, o {mostrar_num(antes)} "
                              f"virou {mostrar_num(depois)}: andou mais que o "
                              f"passo.")
            mudou += depois != antes
    if mudou < 850:
        raise NaoBate("com taxa 1, todo número tem que andar; em 300 "
                      f"mutações, só {mudou} dos 900 números mudaram.")
    mudou = 0
    for _ in range(300):
        deu = trabalho.mutar(list(original), 0.3, PASSO)
        mudou += sum(a != b for a, b in zip(original, deu))
    if not 200 <= mudou <= 340:
        raise NaoBate(f"com taxa 0,3, uns 30% dos números têm que andar; em "
                      f"300 mutações, {mudou} dos 900 mudaram.")
    return ""


def testar_distancia(treino):
    for a, b, certo in (([100, 50], [130, 10], 70), ([0.2, 0.9], [0.5, 0.4],
                                                     0.8)):
        deu = trabalho.distancia(a, b)
        sem_return(deu)
        if not perto(deu, certo):
            raise NaoBate(f"distancia({a}, {b}) devolveu {mostrar_num(deu)}; "
                          f"o certo é {mostrar_num(certo)}.")
    return ""


KNN_TREINO = [([0.4, 0.5], 1), ([0.9, 0.9], 0), ([0.5, 0.7], 1),
              ([0.2, 0.2], 0), ([0.65, 0.4], 0)]


def testar_knn(treino):
    for k, certo in ((3, 2 / 3), (1, 1.0), (5, 0.4)):
        deu = trabalho.knn([0.5, 0.5], KNN_TREINO, k)
        sem_return(deu)
        if not perto(deu, certo):
            raise NaoBate(f"no exemplo de 5 pênaltis, com k = {k}, devolveu "
                          f"{mostrar_num(deu)}; o certo é "
                          f"{mostrar_num(certo)} (a chance de defesa).")
    return ""


LOG_PONTOS = [([1, 0], 1), ([0, 1], 0)]
LOG_CERTO = {1: [0.25, -0.281088, -0.031088],
             3: [0.670337, -0.724248, -0.053911]}


def testar_logistica(treino):
    for rodadas, certo in LOG_CERTO.items():
        deu = trabalho.treinar_logistica(LOG_PONTOS, 0.5, rodadas)
        sem_return(deu)
        if not lista_perto(deu, certo, 1e-5):
            raise NaoBate(f"com os 2 pontos [([1, 0], 1), ([0, 1], 0)], taxa "
                          f"0,5 e {rodadas} rodada(s), devolveu "
                          f"{mostrar_num(deu)}; o certo é "
                          f"{mostrar_num(certo)}.")
    return ""


VOLTA_REDE = ([[0.5, -1.0, 0.2], [1.5, 0.5, -0.3]], [1.0, -2.0, 0.1])
VOLTA_CERTO = [0.524446, -0.934812, 0.281485, 1.452291, 0.372777, -0.459029,
               1.133443, -1.782667, 0.442723]


def testar_volta(treino):
    rede = ([list(p) for p in VOLTA_REDE[0]], list(VOLTA_REDE[1]))
    deu = trabalho.volta(rede, [0.3, 0.8], 1, 0.5)
    pesos = [w for p in rede[0] for w in p] + list(rede[1])
    if not lista_perto(pesos, VOLTA_CERTO, 1e-5):
        raise NaoBate("na rede de exemplo (2 escondidos), um pênalti de "
                      "defesa em [0.3, 0.8] e taxa 0,5: os pesos ficaram "
                      f"{mostrar_num([round(w, 4) for w in pesos])}; o "
                      f"certo é {mostrar_num([round(w, 4) for w in VOLTA_CERTO])}"
                      ".")
    return ""


TESTES = {"regua": testar_regua, "normalizar": testar_normalizar,
          "matriz": testar_matriz, "fuzzy": testar_fuzzy, "nota": testar_nota,
          "mutar": testar_mutar, "distancia": testar_distancia,
          "knn": testar_knn, "treinar_logistica": testar_logistica,
          "volta": testar_volta}


def conferir(treino):
    estado = {}
    print("  AS FUNÇÕES")
    for nome in FUNCOES:
        if vazia(nome):
            estado[nome] = "falta"
            print(f"    {nome}: falta fazer")
            continue
        faltam = [p for p in PRECISA.get(nome, ()) if estado.get(p) != "ok"]
        if faltam:
            estado[nome] = "espera"
            print(f"    {nome}: escrita; confiro quando "
                  f"{' e '.join(faltam)} der ok")
            continue
        try:
            detalhe = TESTES[nome](treino)
            estado[nome] = "ok"
            print(f"    {nome}: ok" + (f" ({detalhe})" if detalhe else ""))
        except NaoBate as erro:
            estado[nome] = "erro"
            print(f"    {nome}: não bate. {erro}")
        except Exception as erro:
            estado[nome] = "erro"
            quadro = linha_do_trabalho(erro)
            onde = (f"na linha {quadro.lineno} ({quadro.line.strip()})"
                    if quadro else "")
            print(f"    {nome}: deu erro {onde}: {type(erro).__name__}: "
                  f"{erro}")
    return estado


def faltando(estado, nomes):
    lista = [n for n in nomes if estado.get(n) != "ok"]
    if len(lista) == 1:
        return lista[0]
    return ", ".join(lista[:-1]) + " e " + lista[-1]


def descrever(erro):
    quadro = linha_do_trabalho(erro)
    onde = f"linha {quadro.lineno}: " if quadro else ""
    return f"{onde}{type(erro).__name__}: {erro}"


def montar_modelos(estado, treino, teste):
    modelos = []
    ok = lambda *nomes: all(estado.get(n) == "ok" for n in nomes)
    r = None
    aviso = ", sem a régua"
    na_regua = lambda e: list(e)
    if ok("regua", "normalizar"):
        try:
            r = trabalho.regua(treino)
            na_regua = lambda e: trabalho.normalizar(e, r)
            aviso = ""
        except Exception as erro:
            print(f"  A régua do treino deu erro ({descrever(erro)}).")
            r = None
    treino_r = [(na_regua(e), y) for e, y in treino]
    modelos.append({"nome": "sempre gol", "curto": "sempre gol",
                    "chance": lambda e: 0.0, "treino": None})

    def fuzzy_maos():
        n = list(trabalho.NUMEROS)
        return {"nome": "fuzzy, números de vocês", "curto": "fuzzy (vocês)",
                "treino": None, "numeros": n,
                "chance": lambda e: trabalho.fuzzy(e[0], e[1], n)}

    def fuzzy_genetico():
        inicio = time.perf_counter()
        melhor, historico = pecas.evoluir(trabalho.nota, trabalho.mutar,
                                          treino, TAMANHO, GERACOES,
                                          TAXA_MUTACAO, PASSO, SEMENTE)
        gasto = time.perf_counter() - inicio
        melhor = list(melhor)
        return {"nome": "fuzzy, números do genético",
                "curto": "fuzzy (genético)", "treino": gasto,
                "numeros": melhor, "historico": historico,
                "chance": lambda e: trabalho.fuzzy(e[0], e[1], melhor)}

    def knn():
        nome = f"KNN{aviso}" if aviso else f"KNN (k = {K})"
        return {"nome": nome, "curto": "KNN", "treino": None,
                "chance": lambda e: trabalho.knn(na_regua(e), treino_r, K)}

    def logistica():
        inicio = time.perf_counter()
        pesos = list(trabalho.treinar_logistica(treino_r, TAXA_LOGISTICA,
                                                RODADAS_LOGISTICA))
        gasto = time.perf_counter() - inicio
        nome = f"logística{aviso}" if aviso else "regressão logística"
        return {"nome": nome, "curto": "logística", "treino": gasto,
                "chance": lambda e: pecas.neuronio(na_regua(e), pesos)}

    def rede():
        inicio = time.perf_counter()
        pesos = pecas.rede_sorteada(ESCONDIDOS, treino_r, SEMENTE)
        pecas.treinar(trabalho.volta, pesos, treino_r, TAXA, RODADAS)
        gasto = time.perf_counter() - inicio
        nome = (f"rede{aviso}" if aviso
                else f"rede neural ({ESCONDIDOS} escondidos)")
        return {"nome": nome, "curto": "rede", "treino": gasto,
                "chance": lambda e: pecas.ida(pesos, na_regua(e))[1]}

    def rede_crua():
        pesos = pecas.rede_sorteada(ESCONDIDOS, treino, SEMENTE)
        pecas.treinar(trabalho.volta, pesos, treino, TAXA, RODADAS)
        return {"nome": "rede neural sem a régua", "curto": "rede crua",
                "treino": None, "so_tabela": True,
                "chance": lambda e: pecas.ida(pesos, e)[1]}

    lista = [("fuzzy, números de vocês", ["fuzzy"], fuzzy_maos),
             ("fuzzy, números do genético", ["fuzzy", "nota", "mutar"],
              fuzzy_genetico),
             (f"KNN (k = {K})", ["distancia", "knn"], knn),
             ("regressão logística", ["treinar_logistica"], logistica),
             (f"rede neural ({ESCONDIDOS} escondidos)", ["volta"], rede)]
    if r is not None:
        lista.append(("rede neural sem a régua", ["volta"], rede_crua))
    for nome, precisa, fazer in lista:
        if not ok(*precisa):
            if not nome.endswith("sem a régua"):
                modelos.append({"nome": nome,
                                "falta": faltando(estado, precisa)})
            continue
        try:
            modelos.append(fazer())
        except Exception as erro:
            modelos.append({"nome": nome,
                            "falta": f"deu erro ({descrever(erro)})"})
    return modelos


def medir(modelos, teste, estado):
    certos = [y for e, y in teste]
    for m in modelos:
        if "chance" not in m:
            continue
        try:
            inicio = time.perf_counter()
            m["chances"] = [m["chance"](e) for e, y in teste]
            m["responder"] = time.perf_counter() - inicio
            if estado.get("matriz") == "ok":
                m["matriz"] = tuple(trabalho.matriz(m["chances"], certos,
                                                    LIMIAR))
        except Exception as erro:
            m.pop("chance")
            m["falta"] = f"deu erro no teste ({descrever(erro)})"


def linha_tabela(m):
    nome = m["nome"]
    if "falta" in m:
        return f"  {nome:<30}falta: {m['falta']}"
    if "matriz" not in m:
        return f"  {nome:<30}(a matriz ainda não deu ok)"
    vp, fp, fn, vn = m["matriz"]
    total = vp + fp + fn + vn
    acerta = f"{vp + vn} ({pct((vp + vn) / total)})"
    precisao = pct(vp / (vp + fp)) if vp + fp else "-"
    recall = pct(vp / (vp + fn)) if vp + fn else "-"
    treino = "-" if m.get("treino") is None else f"{num(m['treino'])} s"
    return (f"  {nome:<30}{acerta:<13}{vp:>3}{fp:>4}{fn:>4}{vn:>5}"
            f"{precisao:>8}{recall:>8}{treino:>7}")


def tabela(modelos, teste):
    defesas = sum(y for e, y in teste)
    linhas = [f"  O TESTE: {len(teste)} pênaltis que nenhum modelo viu "
              f"({defesas} defesas e {len(teste) - defesas} gols)",
              "",
              f"  {'modelo':<30}{'acerta':<13} VP  FP  FN   VN"
              f"  precis.  recall treino"]
    linhas += [linha_tabela(m) for m in modelos]
    extra = []
    for m in modelos:
        if m.get("numeros") and m["nome"].endswith("genético"):
            extra.append(f"  Os números do genético: "
                         f"{[round(v) for v in m['numeros']]} (os de vocês: "
                         f"{list(trabalho.NUMEROS)}).")
    respostas = [m for m in modelos
                 if "responder" in m and not m.get("so_tabela")
                 and m["nome"] != "sempre gol"]
    if respostas:
        tempos = "; ".join(f"{m['curto']} {num(m['responder'], 2)} s"
                           for m in respostas)
        extra.append(f"  Tempo para responder os {len(teste)} do teste:")
        extra.append(f"    {tempos}.")
    return linhas + ([""] + extra if extra else [])


def gravar(texto):
    with open("resultados.txt", "w", encoding="utf-8") as arquivo:
        arquivo.write(texto + "\n")


def main():
    foto = None
    if "--foto" in sys.argv:
        foto = sys.argv[sys.argv.index("--foto") + 1]
    chute = None
    if "--chute" in sys.argv:
        lado, altura = sys.argv[sys.argv.index("--chute") + 1].split(",")
        chute = (int(lado), int(altura))
    sem_tela = "--sem-tela" in sys.argv
    ra = getattr(trabalho, "RA", 0)
    if not isinstance(ra, int) or ra <= 0:
        print("\n  Ponha o RA de um dos dois na linha 1 do trabalho.py "
              "(só números) e rode de novo.\n")
        raise SystemExit(1)
    treino, teste = dados.carregar(ra)
    defesas = sum(y for e, y in treino)
    cabeca = [f"  TRABALHO IA B2: ONDE BATER O PÊNALTI?   RA {ra}   "
              f"{getattr(trabalho, 'NOMES', '')}",
              f"  {len(treino)} pênaltis de treino ({defesas} defesas e "
              f"{len(treino) - defesas} gols) e {len(teste)} de teste.",
              f"  O 1º do treino: lado {treino[0][0][0]} cm, altura "
              f"{treino[0][0][1]} cm, "
              f"{'defesa' if treino[0][1] else 'gol'}.", ""]
    print("\n" + "\n".join(cabeca))
    estado = conferir(treino)
    print()
    modelos = montar_modelos(estado, treino, teste)
    medir(modelos, teste, estado)
    linhas = tabela(modelos, teste)
    if estado.get("matriz") != "ok":
        linhas.append("  A tabela completa sai quando a matriz der ok.")
    print("\n".join(linhas) + "\n")
    feitas = sum(1 for v in estado.values() if v == "ok")
    resumo = [f"  Funções em ok: {feitas} de {len(FUNCOES)}."]
    sem_ok = [n for n in FUNCOES if estado[n] != "ok"]
    if sem_ok:
        resumo.append("  Sem ok: " + ", ".join(sem_ok) + ".")
    gravar("\n".join(cabeca + linhas + [""] + resumo))
    print("  Gravei o resultados.txt.")
    if sem_tela:
        return
    import tela
    print("  Abrindo a tela (ESC fecha)...\n")
    tela.abrir(ra, treino, teste, [m for m in modelos
                                   if not m.get("so_tabela")],
               list(trabalho.NUMEROS), LIMIAR, foto, chute)


if __name__ == "__main__":
    main()
