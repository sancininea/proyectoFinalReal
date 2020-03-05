##################################################################################################
#
# Importar bibliotecas, pygame es la que permite hacer el juego, Neat es la que permite crear la
# secuencia de aprendizaje reforzado
#
##################################################################################################
import pygame
import neat
import time
import os
import random

# posición de la ventana
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (512,25)

# Se requiere inicializar los métodos de uso del tipo de letra desde aquí
pygame.font.init()

# Constantes con el tamaño de ventana a utilizar
WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

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
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # Método jump, modifica la velocidad y altura haciendo que el pájaro "suba" en pantalla
    def jump(self):
        self.vel = -10.5
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
    VEL = 5

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
def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Generation: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

##################################################################################################
#
# Proceso principal
#
# Crea los objetos, inicia la ventana y controla el proceso del juego
#
##################################################################################################
def main(genomes, config): # Vamos a definir esta como la fitness-function de la red NEAT
    
    # Contador del número de generaciones
    global GEN
    GEN +=1
    
    # Objetos de almacenamiento de NEAT
    nets = []
    ge = []
    birds = []

    # Este ciclo tiene un _ porque genomes es un objeto con una tupla, un número y el objeto
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)

    # Crea los objetos a dibujar en la ventana e inicia la ventana que contiene las imágenes
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    # Variables
    clock = pygame.time.Clock()
    score = 0

    # Ciclo principal
    run = True
    while run:
        # Regula la velocidad del pájaro
        clock.tick(30)
        # Termina la aplicación si el usuario lo desea
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        # Revisa cual es el tubo "activo" en caso de haber 2, es decir, contra cual verá si choca el pájaro
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1 
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        # Variables de apoyo para manejo del arreglo de tubos
        add_pipe = False
        rem = []

        # Tubos
        for pipe in pipes:
            # Pájaros
            for x, bird in enumerate(birds):
                # Revisa si hubo un choque, a quienes chocan les reduce el valor de entrenamiento y los "mata" en el juego
                if pipe.collide(bird):
                    ge[x].fitness -=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                # Si el pájaro pasa un tubo, añade un tubo nuevo
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # Añade el tubo a la lista de "Remover" si el pájaro ya lo pasó
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            # Movimiento del tubo sobre la pantalla
            pipe.move()

        # Añade un nuevo tubo si el pájaro ya pasó el anterior y aumenta su valor de entrenamiento por haber pasado un tubo
        if add_pipe:
            score +=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        # Quita los tubos que ya pasamos
        for r in rem:
            pipes.remove(r)

        # Revisa si el pájaro choca con el suelo, a quienes chocan les reduce el valor de entrenamiento y los "mata" en el juego
        for x, bird in enumerate(birds):
            if bird.y +  bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # Mueve el piso para dar el efecto de vuelo
        base.move()
        
        # Dibuja todo en la ventana
        draw_window(win, birds, pipes, base, score, GEN)
    
# Inicializa el proceso NEAT
def run(config_path):
    #Configuración
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                               neat.DefaultSpeciesSet, neat.DefaultStagnation,
                               config_path)
    # Variable de población (population)
    p = neat.Population(config)

    # Envía datos a la consola para ver el desarrollo del proceso
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)

# Inicia el proceso si se llama desde Main
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)