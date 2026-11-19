import os
import sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
if "--foto" in sys.argv:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

LARGURA = 1200
ALTURA = 660
LADO, ALTURA_GOL = 732, 244
ESCALA = 360 / LADO
CELULA = 4

COR_FUNDO = (244, 244, 244)
COR_PAINEL = (255, 255, 255)
COR_TEXTO = (55, 55, 55)
COR_FRACO = (140, 140, 140)
COR_REDE = (226, 226, 226)
COR_TRAVE = (70, 70, 70)
COR_GRAMA = (120, 170, 100)
COR_PEGA = (242, 135, 120)
COR_LINHA = (170, 40, 40)
COR_GOL = (35, 140, 60)
COR_DEFESA = (205, 35, 35)
COR_CINZA = (232, 232, 232)


def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return f"{100 * x:.1f}%".replace(".", ",")


def fonte(tamanho, negrito=False):
    return pygame.font.SysFont("arial", tamanho, bold=negrito)


def paineis():
    caixas = []
    for linha in range(2):
        for coluna in range(3):
            caixas.append(pygame.Rect(9 + coluna * 397, 48 + linha * 306,
                                      388, 300))
    return caixas


def origem(caixa):
    return caixa.x + 14, caixa.y + 40


def para_tela(caixa, lado, altura):
    gx, gy = origem(caixa)
    return (round(gx + lado * ESCALA),
            round(gy + (ALTURA_GOL - altura) * ESCALA))


def para_cm(caixa, x, y):
    gx, gy = origem(caixa)
    lado = (x - gx) / ESCALA
    altura = ALTURA_GOL - (y - gy) / ESCALA
    if 0 <= lado <= LADO and 0 <= altura <= ALTURA_GOL:
        return round(lado), round(altura)
    return None


def grade(chance):
    colunas = round(LADO * ESCALA / CELULA)
    linhas = round(ALTURA_GOL * ESCALA / CELULA)
    valores = []
    for j in range(linhas):
        altura = ALTURA_GOL - (j + 0.5) * CELULA / ESCALA
        valores.append([chance([(i + 0.5) * CELULA / ESCALA, altura])
                        for i in range(colunas)])
    return valores


def misturar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))


def pintura(valores):
    linhas, colunas = len(valores), len(valores[0])
    folha = pygame.Surface((colunas * CELULA, linhas * CELULA))
    for j in range(linhas):
        for i in range(colunas):
            cor = misturar(COR_PAINEL, COR_PEGA, valores[j][i])
            folha.fill(cor, (i * CELULA, j * CELULA, CELULA, CELULA))
    for j in range(linhas):
        for i in range(colunas):
            dentro = valores[j][i] >= 0.5
            if i + 1 < colunas and (valores[j][i + 1] >= 0.5) != dentro:
                folha.fill(COR_LINHA, ((i + 1) * CELULA - 1, j * CELULA, 2,
                                       CELULA))
            if j + 1 < linhas and (valores[j + 1][i] >= 0.5) != dentro:
                folha.fill(COR_LINHA, (i * CELULA, (j + 1) * CELULA - 1,
                                       CELULA, 2))
    return folha


def desenhar_gol(tela, caixa, folha, cinza=False):
    gx, gy = origem(caixa)
    largura = round(LADO * ESCALA)
    altura = round(ALTURA_GOL * ESCALA)
    tela.fill(COR_GRAMA, (gx - 10, gy + altura, largura + 20, 6))
    tela.fill(COR_CINZA if cinza else COR_PAINEL, (gx, gy, largura, altura))
    for x in range(gx + 12, gx + largura, 12):
        pygame.draw.line(tela, COR_REDE, (x, gy), (x, gy + altura - 1))
    for y in range(gy + 12, gy + altura, 12):
        pygame.draw.line(tela, COR_REDE, (gx, y), (gx + largura - 1, y))
    if folha is not None:
        tela.blit(folha, (gx, gy), special_flags=pygame.BLEND_MULT)
    tela.fill(COR_TRAVE, (gx - 5, gy - 5, 5, altura + 5))
    tela.fill(COR_TRAVE, (gx + largura, gy - 5, 5, altura + 5))
    tela.fill(COR_TRAVE, (gx - 5, gy - 5, largura + 10, 5))


def desenhar_pontos(tela, caixa, pontos, chances, limiar, apagado=False):
    for k, (entradas, certo) in enumerate(pontos):
        x, y = para_tela(caixa, entradas[0], entradas[1])
        cor = COR_DEFESA if certo else COR_GOL
        if apagado:
            cor = misturar(cor, COR_CINZA, 0.6)
        pygame.draw.circle(tela, cor, (x, y), 3)
        if chances is not None:
            disse = 1 if chances[k] >= limiar else 0
            if disse != certo:
                pygame.draw.circle(tela, (20, 20, 20), (x, y), 5, 1)


def escrever(tela, texto, x, y, f, cor=COR_TEXTO):
    tela.blit(f.render(texto, True, cor), (x, y))


def texto_modelo(m, chute, limiar):
    linhas = []
    if "falta" in m:
        return [(f"falta fazer: {m['falta']}", COR_FRACO, True)]
    if "matriz" in m:
        vp, fp, fn, vn = m["matriz"]
        total = vp + fp + fn + vn
        linhas.append((f"acerta {vp + vn} de {total} ({pct((vp + vn) / total)})",
                       COR_TEXTO, True))
        linhas.append((f"VP {vp}   FP {fp}   FN {fn}   VN {vn}", COR_TEXTO,
                       False))
        precisao = pct(vp / (vp + fp)) if vp + fp else "-"
        recall = pct(vp / (vp + fn)) if vp + fn else "-"
        linhas.append((f"precisão {precisao}    recall {recall}", COR_TEXTO,
                       False))
    else:
        linhas.append(("a tabela sai quando a matriz der ok", COR_FRACO, False))
    if m.get("treino") is None:
        linhas.append(("não treina", COR_FRACO, False))
    else:
        linhas.append((f"treino: {num(m['treino'])} s", COR_FRACO, False))
    if m.get("numeros"):
        n = [round(v) for v in m["numeros"]]
        linhas.append((f"números: {n}", COR_FRACO, False))
    if chute is not None:
        c = m["chance"](list(chute))
        veredito = "pega" if c >= limiar else "gol"
        linhas.append((f"neste chute: {veredito} ({pct(c)} de defesa)",
                       COR_DEFESA if c >= limiar else COR_GOL, True))
    return linhas


def abrir(ra, treino, teste, modelos, numeros, limiar, foto=None,
          chute=None):
    pygame.init()
    if foto:
        tela = pygame.Surface((LARGURA, ALTURA))
    else:
        tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(f"Onde bater o pênalti? RA {ra}")
    f_titulo = fonte(20, True)
    f_painel = fonte(16, True)
    f_texto = fonte(14)
    f_negrito = fonte(14, True)
    caixas = paineis()
    preguicoso = modelos[0]
    outros = modelos[1:]
    for m in outros:
        if "chance" in m:
            try:
                m["folha"] = pintura(grade(m["chance"]))
            except Exception as erro:
                m.pop("chance")
                m["falta"] = f"deu erro ao pintar ({type(erro).__name__})"
    modo = 0
    mouse = None
    relogio = pygame.time.Clock()
    while True:
        if not foto:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if evento.key == pygame.K_t:
                        modo = (modo + 1) % 3
                if evento.type == pygame.MOUSEMOTION:
                    mouse = None
                    for caixa in caixas:
                        mouse = mouse or para_cm(caixa, *evento.pos)
                if (evento.type == pygame.MOUSEBUTTONDOWN
                        and evento.button == 1):
                    for caixa in caixas:
                        chute = para_cm(caixa, *evento.pos) or chute
        tela.fill(COR_FUNDO)
        escrever(tela, f"ONDE BATER O PÊNALTI?   RA {ra}", 14, 6, f_titulo)
        if "matriz" in preguicoso:
            vp, fp, fn, vn = preguicoso["matriz"]
            total = vp + fp + fn + vn
            escrever(tela, f"Chutando sempre gol: acerta {vp + vn} de "
                     f"{total} ({pct((vp + vn) / total)})", 14, 28, f_texto)
        dica = ("mouse em cima de um gol: lado e altura em cm   ·   clique: "
                "chutar   ·   T: pontos   ·   ESC: fechar")
        if mouse:
            dica = f"mouse: lado {mouse[0]} cm, altura {mouse[1]} cm"
        escrever(tela, dica, 1186 - f_texto.size(dica)[0], 28, f_texto,
                 COR_FRACO)
        nomes_modo = ("pontos: os 200 do teste", "pontos: os 400 do treino",
                      "pontos: nenhum")
        escrever(tela, nomes_modo[modo], 1186 - f_texto.size(nomes_modo[modo])
                 [0], 8, f_texto, COR_FRACO)
        caixa = caixas[0]
        tela.fill(COR_PAINEL, caixa)
        escrever(tela, "Os pênaltis do treino", caixa.x + 12, caixa.y + 10,
                 f_painel)
        desenhar_gol(tela, caixa, None)
        desenhar_pontos(tela, caixa, treino, None, limiar)
        defesas = sum(y for e, y in treino)
        y = caixa.y + 174
        textos = [(f"{len(treino)} pênaltis: {defesas} defesas e "
                   f"{len(treino) - defesas} gols", COR_TEXTO, True),
                  ("verde: gol   ·   vermelho: defesa", COR_TEXTO, False),
                  ("nos outros gols, o pintado: o modelo diz", COR_FRACO,
                   False),
                  ("que o goleiro pega; contorno preto: errou", COR_FRACO,
                   False),
                  (f"NUMEROS de vocês: {numeros}", COR_FRACO, False)]
        if chute is not None:
            textos.append((f"o chute: lado {chute[0]} cm, altura {chute[1]} cm",
                           COR_TEXTO, True))
        for texto, cor, negrito in textos:
            escrever(tela, texto, caixa.x + 14, y,
                     f_negrito if negrito else f_texto, cor)
            y += 19
        if chute is not None:
            pygame.draw.circle(tela, (255, 255, 255),
                               para_tela(caixa, *chute), 6)
            pygame.draw.circle(tela, (0, 0, 0), para_tela(caixa, *chute), 6, 1)
        for caixa, m in zip(caixas[1:], outros):
            tela.fill(COR_PAINEL, caixa)
            escrever(tela, m["nome"], caixa.x + 12, caixa.y + 10, f_painel)
            desenhar_gol(tela, caixa, m.get("folha"), cinza="falta" in m)
            if modo == 0:
                desenhar_pontos(tela, caixa, teste, m.get("chances"), limiar,
                                apagado="falta" in m)
            elif modo == 1:
                desenhar_pontos(tela, caixa, treino, None, limiar,
                                apagado="falta" in m)
            y = caixa.y + 174
            for texto, cor, negrito in texto_modelo(m, chute, limiar):
                escrever(tela, texto, caixa.x + 14, y,
                         f_negrito if negrito else f_texto, cor)
                y += 19
            if chute is not None:
                pygame.draw.circle(tela, (255, 255, 255),
                                   para_tela(caixa, *chute), 6)
                pygame.draw.circle(tela, (0, 0, 0), para_tela(caixa, *chute),
                                   6, 1)
        if foto:
            pygame.image.save(tela, foto)
            pygame.quit()
            return
        pygame.display.flip()
        relogio.tick(30)
