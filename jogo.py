import sys, pygame
import pprint
from pygame.locals import *
import string
import random
from criar_audio import criar_audio
from receber_comando import receber_comando
from playsound import playsound

pygame.init()
pygame.font.init() 
pygame.display.set_caption('Batalha Naval')

clock = pygame.time.Clock()

size = width, height = 740, 740
speed = [0.1, 0.1]
black = 0, 0, 0
white = 255, 255, 255
tam_grade = 20

screen = pygame.display.set_mode(size)

# Sprites

spr_tabuleiro = pygame.image.load("tabuleiro_grande.png")
spr_navio = pygame.image.load("navio.png")
spr_tiro = pygame.image.load("alvo.png")
spr_agua = pygame.image.load("agua.png")
spr_tiro = pygame.image.load("alvo.png")

# Navios

def rot2vect(rot):
    opc = {'n': [0, -1], 's': [0, 1], 'l': [1, 0], 'o': [-1, 0]}
    return opc[rot]

def grade2tab(pos, tab_idx):
    pos_final = [0, 0]
    if tab_idx == 0:
        pos_final = [120+pos[0]*tam_grade, 120+pos[1]*tam_grade]
    if tab_idx == 1:
        pos_final = [120+pos[0]*tam_grade, 440+pos[1]*tam_grade]
    if tab_idx == 2:
        pos_final = [440+pos[0]*tam_grade, 230+pos[1]*tam_grade]
    return pos_final

class navio:
    def __init__(self, pos, rot, tam, tab_idx):
        self.pos = pos
        self.rot = rot
        self.tam = tam
        self.tab_idx = tab_idx
        self.danos = 0
        self.sprites = []
        self.rects = []
        for i in range(0, tam):
            self.sprites.append(pygame.Surface.copy(spr_navio))
            self.rects.append(self.sprites[i].get_rect())
            self.rects[i] = self.rects[i].move(grade2tab([pos[0]+rot2vect(rot)[0]*i, pos[1]+rot2vect(rot)[1]*i], tab_idx))
            if self.rot == 'o' or self.rot == 'l':
                self.sprites[i] = pygame.transform.rotate(self.sprites[i], 90)

def desenha_navio(nav, screen):
    for i in range(0, nav.tam):
        screen.blit(nav.sprites[i], nav.rects[i])

def pos2num(pos):
    print(pos)
    l = string.ascii_lowercase.index(pos[0].lower())
    c = int(pos[1]) -1

    return [l, c]

def converte_posicoes(posicoes, tab):
    l1 = string.ascii_lowercase.index(posicoes[0][0].lower())
    l2 = string.ascii_lowercase.index(posicoes[1][0].lower())
    c1 = int(posicoes[0][1]) -1
    c2 = int(posicoes[1][1]) -2
    direc = ''
    tam = 0
    print(l1, l2, c1, c2)
    if l1 == l2:
        if c1 < c2:
            direc = 'l'
        else:
            direc = 'o'

        tam = abs(c1 - c2)
    else:
        if l1 < l2:
            direc = 's'
        else:
            direc = 'n'

        tam = abs(l1 - l2)

    nav = navio([l1, c1], direc, tam, tab)
    return nav

lista_navios = []
# nav1 = navio([0, 0], 's', 3, 1)
# nav1.danos = [0, 0, 1]
# lista_navios.append(nav1)
# lista_navios.append(navio([2, 5], 'l', 4, 0))
# lista_navios.append(navio([2, 5], 'l', 4, 2))
lista_navios.append(navio([8, 9], 'o', 2, 2))
lista_navios.append(navio([5, 5], 'o', 5, 1))

# Tabuleiros
# Sim, eu sei que uma classe era melhor

tabuleiros = []
tabuleiros_rect = []
tabuleiros_pos_inicial = [[-1000, -1000], [100, 420], [420, 210]]

class agua:
    def __init__(self, pos, tab_idx):
        self.pos = pos
        self.tab_idx = tab_idx
        self.sprite = pygame.Surface.copy(spr_agua)
        self.rect = self.sprite.get_rect()
        self.rect = self.rect.move(grade2tab(pos, tab_idx))

class tiro:
    def __init__(self, pos, tab_idx):
        self.pos = pos
        self.tab_idx = tab_idx
        self.sprite = pygame.Surface.copy(spr_tiro)
        self.rect = self.sprite.get_rect()
        self.rect = self.rect.move(grade2tab(pos, tab_idx))

def desenha_agua(ag, screen):
    screen.blit(ag.sprite, ag.rect)

def desenha_tiro(tr, screen):
    screen.blit(tr.sprite, tr.rect)

lista_aguas = []

for i in range(0, 3):
    tabuleiros.append(pygame.Surface.copy(spr_tabuleiro))
    tabuleiros_rect.append(tabuleiros[i].get_rect())
    tabuleiros_rect[i] = tabuleiros_rect[i].move(tabuleiros_pos_inicial[i])

# Textos e Etrada de Navios

pilha_entrada = []

myfont = pygame.font.SysFont('arial', 30)

estado = "jogo"
navios_inseridos = 0
posicao_inicial = 0
posicoes = ["", ""]

# 0 -> pergunta a posicao, 1 -> tenta coferir a posicao, 2 -> pergunta segunda posicao, 3 -> confirma segunda posicao, 4 -> confere dados
pergunta_estado = 0

textos_perguntas = ["Diga a posicao inicial do", "Diga a posicao final do"]
nomes_navios = ["Submarino (2)", "Contratorpedo (3)", "Navio-tanque (4)", "Porta-avioes (5)"]

def casa_aleatoria():
    letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    casa = letras[random.randint(0, 9)] + str(random.randint(1, 10))
    criar_audio(casa)
    return casa

lista_tiros = []

def navioNaCasa(l , c, tab):
    for nav in lista_navios:
        if nav.tab_idx == tab:
            print("Pos navio: ", str(nav.pos), str(l), str(c), str(nav.tam), nav.rot)
            if nav.rot == 'n':
                if nav.pos[1] <= l and nav.pos[1] +nav.tam -1 >= l and nav.pos[0] == c:
                    return nav
            elif nav.rot == 's':
                if nav.pos[1] <= l and nav.pos[1] +nav.tam -1 >= l and nav.pos[0] == c:
                    return nav
            elif nav.rot == 'l':
                if nav.pos[0] <= c and nav.pos[0] +nav.tam -1 >= c and nav.pos[1] == l:
                    return nav
            else:
                if nav.pos[0] >= c and nav.pos[0] -nav.tam +1 <= c and nav.pos[1] == l:
                    return nav
    return False

def atira(casa, tabuleiro):
    [l, c] = pos2num(casa)

    repetido = False
    
    for tir in lista_tiros:
        if tir.tab_idx == 2:
            if tir.pos == [c, l]:
                repetido = True
                break
    if repetido:
        return False
    else:
        nav = navioNaCasa(l, c, tabuleiro)
        print(nav)

        if nav:
            playsound('audios/explosion.mp3')
            nav.danos += 1
            if nav.danos >= nav.tam:
                lista_navios.remove(nav)
                print("Navio afundado!")
        else:
            playsound('audios/water.mp3')

        print("Tiro Linha: " + str(l) + " Coluna: " + str(c) + " Tabuleiro: " + str(tabuleiro))
        lista_tiros.append(tiro([c, l], tabuleiro))
        return True

def pergunta_posicao(texto):
    fim = False
    if len(pilha_entrada) > 0:
        tecla = pilha_entrada.pop()

        if tecla == "%r":
            fim = True
        elif tecla == "%b":
            texto = texto[:-1]
        else:
            texto += tecla
    
    return [fim, texto]

def confere_posicoes(posicoes, navio_idx):
    return True

def estado_entrada(posicao_inicial, navios_inseridos, pergunta_estado, posicoes, pilha_entrada):

    texto = textos_perguntas[posicao_inicial] + " " + nomes_navios[navios_inseridos]
    pergunta = myfont.render(texto, False, (0, 0, 0))
    confirmacao = myfont.render("A posicao inserida esta correta? (s/n)", False, (0, 0, 0))
    
    screen.blit(pergunta,(50,370))
    posicao_texto = myfont.render("Posicao inicial/final: " + str(posicoes[0]) + "/"+ str(posicoes[1]), False, (0, 0, 0))
    screen.blit(posicao_texto,(50,470))
    screen.blit(myfont.render("Estado: " + str(pergunta_estado), False, (0, 0, 0)),(50,670))

    if pergunta_estado == 1 or pergunta_estado == 3:
          
        screen.blit(confirmacao,(50,570))
        if len(pilha_entrada) > 0:
            tecla = pilha_entrada.pop()
            if tecla == "s":
                pergunta_estado += 1
            elif tecla == "n":
                pergunta_estado -= 1
                
    elif pergunta_estado == 0 or pergunta_estado == 2:
        fim_pergunta = False
        idx = round(pergunta_estado/2)
        posicao_inicial = idx

        [fim_pergunta, posicoes[idx]] = pergunta_posicao(posicoes[idx])

        if fim_pergunta:
            pergunta_estado += 1

    elif pergunta_estado == 4:
        pos_corretas = confere_posicoes(posicoes, navios_inseridos)

        pergunta_estado = 0

        if pos_corretas:
            navios_inseridos += 1
    
    return [posicao_inicial, navios_inseridos, pergunta_estado, posicoes]

def estado_jogo(jogador, texto_casa, pilha_entrada):
    for i in range(0, 3):
        screen.blit(tabuleiros[i], tabuleiros_rect[i])

    for nav in lista_navios:
        desenha_navio(nav, screen)

    for ag in lista_aguas:
        desenha_agua(ag, screen)

    for tr in lista_tiros:
        desenha_tiro(tr, screen)    

    jogador_txt = "Jogador"
    
    if jogador:
        [fim_pergunta, texto_casa] = pergunta_posicao(texto_casa)       
        
        if fim_pergunta:
            
            voz = receber_comando()
            print("voz: ")
            print(voz)
            texto_casa = voz[0] + voz[1]
            if atira(texto_casa, 2):
                jogador = False
            else:
                print("Tiro repetido")
         
        screen.blit(myfont.render("Aperte ENTER para dizer qual casa quer atirar.", False, (0, 0, 0)) ,(50,50))  
            
    else:
        jogador_txt = "Computador"
        jogador = True
        atira(casa_aleatoria(), 1)        

    screen.blit(myfont.render("Jogador", False, (0, 0, 0)) ,(155,380))
    screen.blit(myfont.render("Computador", False, (0, 0, 0)), (450, 170))

    return [jogador, texto_casa, pilha_entrada]

roda = True
jogador = True
texto_casa = ""

while roda:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            roda = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pilha_entrada.append("%r")
                elif event.key == pygame.K_BACKSPACE:
                    pilha_entrada.append("%b")
                else:
                    pilha_entrada.append(event.unicode)

    screen.fill(white)

    if estado == "entrada":
        navios_antes = navios_inseridos
        [posicao_inicial, navios_inseridos, pergunta_estado, posicoes] = estado_entrada(posicao_inicial, navios_inseridos, pergunta_estado, posicoes, pilha_entrada)
        if navios_inseridos > navios_antes:
            nav = converte_posicoes(posicoes, 1)
            lista_navios.append(nav)
            posicoes = ["", ""]

        if navios_inseridos > 1:
            estado = "jogo"

    elif estado == "jogo":
        [jogador, texto_casa, pilha_entrada] = estado_jogo(jogador, texto_casa, pilha_entrada)
        nNavP = 0
        nNavC = 0

        for nav in lista_navios:
            if nav.tab_idx == 1:
                nNavP += 1
            elif nav.tab_idx == 2:
                nNavC += 1

        if nNavP == 0:
            estado = "fimC"
        elif nNavC == 0:
            estado = "fimP"      
    
    elif estado == "fimC":
        screen.blit(myfont.render("Computador Ganhou", False, (0, 0, 0)) ,(50,10))
    elif estado == "fimP":
        screen.blit(myfont.render("Jogador Ganhou", False, (0, 0, 0)) ,(50,10))

    pygame.display.flip()

pygame.quit()
sys.exit()