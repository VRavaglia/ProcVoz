import sys, pygame
import pprint
from pygame.locals import *

pygame.init()
pygame.font.init() 
pygame.display.set_caption('Batalha Naval')

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
        self.danos = []
        self.danos_spr = []
        self.sprites = []
        self.rects = []
        for i in range(0, tam):
            self.danos.append(0)
            self.sprites.append(pygame.Surface.copy(spr_navio))
            self.danos_spr.append(pygame.Surface.copy(spr_tiro))
            self.rects.append(self.sprites[i].get_rect())
            self.rects[i] = self.rects[i].move(grade2tab([pos[0]+rot2vect(rot)[0]*i, pos[1]+rot2vect(rot)[1]*i], tab_idx))
            if self.rot == 'o' or self.rot == 'l':
                self.sprites[i] = pygame.transform.rotate(self.sprites[i], 90)

def desenha_navio(nav, screen):
    for i in range(0, nav.tam):
        screen.blit(nav.sprites[i], nav.rects[i])
        if nav.danos[i] > 0:
            screen.blit(nav.danos_spr[i], nav.rects[i])

lista_navios = []
nav1 = navio([0, 0], 's', 3, 1)
nav1.danos = [0, 0, 1]
lista_navios.append(nav1)
lista_navios.append(navio([2, 5], 'l', 4, 0))
lista_navios.append(navio([5, 5], 'o', 5, 2))

# Tabuleiros
# Sim, eu sei que uma classe era melhor

tabuleiros = []
tabuleiros_rect = []
tabuleiros_pos_inicial = [[100, 100], [100, 420], [420, 210]]

class agua:
    def __init__(self, pos, tab_idx):
        self.pos = pos
        self.tab_idx = tab_idx
        self.sprite = pygame.Surface.copy(spr_agua)
        self.rect = self.sprite.get_rect()
        self.rect = self.rect.move(grade2tab(pos, tab_idx))

def desenha_agua(ag, screen):
    screen.blit(ag.sprite, ag.rect)


lista_aguas = []

for i in range(0, 3):
    tabuleiros.append(pygame.Surface.copy(spr_tabuleiro))
    tabuleiros_rect.append(tabuleiros[i].get_rect())
    tabuleiros_rect[i] = tabuleiros_rect[i].move(tabuleiros_pos_inicial[i])

# Textos e Etrada de Navios

myfont = pygame.font.SysFont('Open Sans', 30)

estado = "entrada"
navios_inseridos = 0
posicao_inicial = 0
posicoes = ["A1", "A2"]

# 0 -> pergunta a posicao, 1 -> tenta coferir a posicao, 2 -> pergunta segunda posicao, 3 -> confirma segunda posicao, 4 -> confere dados
pergunta_estado = 0

textos_perguntas = ["Diga a posicao inicial do", "Diga a posicao final do"]
nomes_navios = ["Submarino (2)", "Contratorpedo (3)", "Navio-tanque (4)", "Porta-avioes (5)"]



def pergunta_posicao():
    return input ("Insira a posicao: ")

def confere_posicoes(posicoes, navio_idx):
    return True

def estado_entrada(posicao_inicial, navios_inseridos, pergunta_estado, posicoes):

    texto = textos_perguntas[posicao_inicial] + " " + nomes_navios[navios_inseridos]
    pergunta = myfont.render(texto, False, (0, 0, 0))
    confirmacao = myfont.render("A posicao inserida esta correta? (s/n)", False, (0, 0, 0))
    
    screen.blit(pergunta,(50,370))
    screen.blit(myfont.render("Estado: " + str(pergunta_estado), False, (0, 0, 0)),(50,670))

    if pergunta_estado == 1 or pergunta_estado == 3:
        if pergunta_estado == 2:
            pos = posicoes[1]
        else:
            pos = posicoes[0]

        posicao_texto = myfont.render(pos, False, (0, 0, 0))
        
        screen.blit(confirmacao,(50,570))
        screen.blit(posicao_texto,(50,470))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key==K_s:
                    pergunta_estado = pergunta_estado + 1

            if event.type == pygame.KEYDOWN:
                if event.key==K_n:
                    pergunta_estado = pergunta_estado - 1
                
    elif pergunta_estado == 0 or pergunta_estado == 2:
        if pergunta_estado == 2:
            posicao_inicial = 1
            posicoes[1] = pergunta_posicao()
        else:
            posicao_inicial = 0
            posicoes[0] = pergunta_posicao()
        
        pergunta_estado = pergunta_estado + 1

    elif pergunta_estado == 4:
        pos_corretas = confere_posicoes(posicoes, navios_inseridos)

        pergunta_estado = 0

        if pos_corretas:
            navios_inseridos = navios_inseridos + 1
    
    return [posicao_inicial, navios_inseridos, pergunta_estado, posicoes]

def estado_jogo():
    for i in range(0, 3):
        screen.blit(tabuleiros[i], tabuleiros_rect[i])

    for nav in lista_navios:
        desenha_navio(nav, screen)

    for ag in lista_aguas:
        desenha_agua(ag, screen)

while 1:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(white)

    if estado == "entrada":
        [posicao_inicial, navios_inseridos, pergunta_estado, posicoes] = estado_entrada(posicao_inicial, navios_inseridos, pergunta_estado, posicoes)
    elif estado == "jogo":
        estado_jogo()

    pygame.display.flip()