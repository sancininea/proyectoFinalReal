##################################################################################################
#
# Importar bibliotecas, pygame es la que permite hacer el juego
#
##################################################################################################
import pygame
import time
import os
import random
from pygame.locals import * 

# posición de la ventana
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (512,25)

# Se requiere inicializar los métodos de uso del tipo de letra desde aquí
pygame.font.init()

# Constantes con el tamaño de ventana a utilizar
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Constantes con las imagenes de cada objeto a usar en el juego
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load("img\\bird1.png")), pygame.transform.scale2x(pygame.image.load("img\\bird2.png")), pygame.transform.scale2x(pygame.image.load("img\\bird3.png"))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load("img\\pipe.png"))
BASE_IMG = pygame.transform.scale2x(pygame.image.load("img\\base.png"))
BG_IMG = pygame.transform.scale2x(pygame.image.load("img\\bg.png"))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

##################################################################################################
#
# Clase Bird
#
# Esta clase contiene las atributos y métodos para controlar al pájaro
#
##################################################################################################
class Bird:
    # Constantes que indican las imagenes a usar, la rotación, velocidad y tiempo de animación del aleteo
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    # Método de inicio del objeto, asigna los valores de posición, imágen y velocidad
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = -1
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # Método jump, modifica la velocidad y altura haciendo que el pájaro "suba" en pantalla
    def jump(self):
        self.vel = -9.5
        self.tick_count = 0
        self.height = self.y
    
    # Método move
    def move(self):
        self.tick_count +=1

        d = self.vel * self.tick_count + 1.5 * self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d <0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
            else:
                if self.tilt > -90:
                    self.tilt -= self.ROT_VEL

    # Método draw dibuja al pájaro, dependiendo del tiempo cambia de un dibujo a otro para dar el efecto de aleteo
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # Método mask este sirve para devolver el valor de la superficie, este se usa para saber si el dibujo colisiona con otro
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

##################################################################################################
#
# Clase Pipe
#
# Esta clase contiene las atributos y métodos para controlar los tubos
#
##################################################################################################
class Pipe:
    # Constantes de velocidad y distancia entre tubos
    GAP = 200
    VEL = 4

    # Inicio de objeto
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        
        # El tubo de arriba requiere que la imagen quede volteada, por eso se hace flip
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    # Define el tamaño del tubo de arriba con un valor al azar y el de abajo con la posición del de arriba y el "GAP"
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # Movimiento del tubo
    def move(self):
        self.x -= self.VEL

    # Dibuja el tubo
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Revisa si el pájaro chocó con el tubo
    def collide(self, bird):
        # Las máscaras son la colección de pixeles que contiene el dibujo (quitando los transparentes)
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Estos son los cuadros que contiene la imagen
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Este método compara dos matrices para ver si tiene puntos que chocan
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # Si colisionan los dibujos reales entones regresa verdadero
        if t_point or b_point:
            return True
        
        return False

##################################################################################################
#
# Clase Base
#
# Esta clase contiene las atributos y métodos para controlar el movimiento del suelo
#
##################################################################################################
class Base:
    # Constantes que manejan la velocidad y la imagen del suelo
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    # Inicio de la clase
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # Movimiento del suelo
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Dibujo del suelo
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

##################################################################################################
#
# Proceso de dibujo
#
# Dibuja los objetos en la posición indicada sobre la pantalla definida
#
##################################################################################################
def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)
    bird.draw(win)
    pygame.display.update()

##################################################################################################
#
# Proceso principal
#
# Crea los objetos, inicia la ventana y controla el proceso del juego
#
##################################################################################################
def main():
    
    # Crea los objetos a dibujar en la ventana
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    # Variables
    clock = pygame.time.Clock()
    score = 0

    pygame.time.wait(1000)

    # Ciclo principal
    run = True
    while run:
        # Regula la velocidad del pájaro
        clock.tick(30)
        # Termina la aplicación si el usuario lo desea o si el pájaro toca un tubo, el suelo o el cielo
        # Hace que el pájaro salte con el click del mouse, la barra espaciadora o la flechita hacia arriba
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONUP or (event.type == KEYUP and
                event.key in (K_UP, K_RETURN, K_SPACE)):
                bird.jump()
        
        bird.move()

        # Variables de apoyo para manejo del arreglo de tubos
        add_pipe = False
        rem = []

        # Tubos
        for pipe in pipes:
            # Pájaros
            if pipe.collide(bird):
                run = False
            # Si el pájaro pasa un tubo, añade un tubo nuevo
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            # Añade el tubo a la lista de "Remover" si el pájaro ya lo pasó
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            # Movimiento del tubo sobre la pantalla
            pipe.move()

        # Añade un nuevo tubo si el pájaro ya pasó el anterior
        if add_pipe:
            score +=1
            pipes.append(Pipe(600))

        # Quita los tubos que ya pasamos
        for r in rem:
            pipes.remove(r)

        # Revisa si el pájaro choca con el suelo
        if bird.y +  bird.img.get_height() >= 730 or bird.y < 0:
            run = False

        # Mueve el piso para dar el efecto de vuelo
        base.move()
        
        # Dibuja todo en la ventana
        draw_window(win, bird, pipes, base, score)
    

# Inicia el proceso si se llama desde Main
if __name__ == "__main__":
    main()
