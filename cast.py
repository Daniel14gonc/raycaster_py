import pygame
from math import cos, sin, pi, atan2
import random
from OpenGL.GL import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (0, 255, 0)
TRANSPARENT = (255, 255, 255)

SKY = (50, 100, 200)
GROUND = (200, 200, 100)

colors = [
    (0, 20, 10),
    (4, 40, 63),
    (0, 91, 82),
    (219, 242, 38),
    (21, 42, 138)
]

wall1 = pygame.image.load('./Textures/wall1.png')
wall2 = pygame.image.load('./Textures/wall2.png')
wall3 = pygame.image.load('./Textures/wall3.png')
wall4 = pygame.image.load('./Textures/wall4.png')
# wall5 = pygame.image.load('./Textures/wall5.png')

walls = {
    "1" : wall2,
    "2" : wall1,
    "3" : wall3,
    "4" : wall4
}

sprite1 = pygame.image.load('./Sprites/dementor.png')
sprite2 = pygame.image.load('./Sprites/dementor2.png')
sprites = [sprite1, sprite2]

enemies = [
    {
        "n": "s1",
        "x": 70,
        "y": 210,
        "sprite": sprite1
    }, 
    {
        "n": "s1",
        "x": 100,
        "y": 210,
        "sprite": sprite2
    }
]



hagrid = pygame.image.load('./Sprites/hagrid.png')
hedwig = pygame.image.load('./Sprites/hedwig.png')

characters = [
    {
        "name": "hagrid",
        "x": 150,
        "y": 150,
        "sprite": hagrid
    },
    {
        "name": "hedwig",
        "x": 300,
        "y": 400,
        "sprite": hedwig
    }
]

pygame.init()
screen = pygame.display.set_mode((1000, 500))



class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        x, y, self.width, self.height = screen.get_rect()
        self.block_size = 50
        self.map = []
        self.player = {
            "x": int(self.block_size + (self.block_size / 2)),
            "y": int(self.block_size + (self.block_size / 2)),
            "fov": int(pi / 3),
            "a": int(pi / 3)
        }
        self.number = 0
        self.clearZ()
        self.dead_enemies = 0
        self.spell = pygame.mixer.Sound("spell.wav")

    def clearZ(self):
        self.zbuffer = [999999 for z in range(0, int(self.width))]

    def point(self, x, y, color = WHITE):
        # No usa aceleracion grafica. Usar pixel o point usado en juego de la vida
        self.screen.set_at((int(x), int(y)), color)

    def block(self, x, y, wall):
        for i in range(x, x + 10):
            for j in range(y, y + 10):
                tx = int((i - x) * 128 / 10)
                ty = int((j - y) * 128 / 10)
                c = wall.get_at((tx, ty))
                self.point(i, j, c)

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def draw_stake(self, x, h, c, tx):
        start_y = int(self.height / 2 - h / 2)
        end_y = int(self.height / 2 + h / 2)
        height = end_y - start_y
        for y in range(start_y, end_y):
            ty = int((y - start_y) * 128 / height)
            color = walls[c].get_at((tx, ty))
            self.point(x, y, color)

    def cast_ray(self, a):
        d = 0
        origin_x = self.player["x"]
        origin_y = self.player["y"]


        while True:
            x = int(origin_x + d * cos(a))
            y = int(origin_y + d * sin(a))

            i = int(x / self.block_size)
            j = int(y / self.block_size)

            if self.map[j][i] != ' ':
                hitx = x - i * self.block_size
                hity = y - j * self.block_size

                if 1 < hitx < self.block_size - 1:
                    maxhit = hitx
                else:
                    maxhit = hity

                tx = int(maxhit * 128 / self.block_size)
                return d, self.map[j][i], tx

            # self.point(x, y)
            d += 5

    def draw_map(self):
        block = 10
        for x in range(0, 100, int(block)):
            for y in range(0, 100, int(block)):
                i = int(x / block)
                j = int(y / block)

                if self.map[j][i] !=  ' ':
                    self.block(x, y, walls[self.map[j][i]])

    def draw_player(self):
        self.point(self.player["x"]/5, self.player["y"]/5)

    def draw_sprite(self, sprite):
        sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])

        distance = ((self.player["x"] - sprite["x"]) ** 2 + (self.player["y"] - sprite["y"]) ** 2) ** 0.5
        if "name" in sprite and sprite["name"] == "hagrid":
            if distance < 90:
                white = (255, 255, 255)
                
                # assigning values to X and Y variable
                X = 1500
                Y = 900
                font = pygame.font.Font('freesansbold.ttf', 16)
                text = font.render('Deshazte de los dementores y rescata a Hedwig', 
                    True, BLACK, WHITE)
                textRect = text.get_rect()
                textRect.center = (X // 2, Y // 2)
                screen.blit(text, textRect)
        if "n" in sprite and sprite["sprite"] == sprite1:
            sprite["sprite"] = sprite2
        elif "n" in sprite and sprite["sprite"] == sprite2: 
            sprite["sprite"] = sprite1

        sprite_size = int(500 / distance * 500 / 10)

        sprite_x = int(500 + (sprite_a - self.player["a"]) * 500 / self.player["fov"] + (sprite_size / 2))
        sprite_y = int(500 / 2 - sprite_size / 2)

        for x in range(sprite_x, sprite_x + sprite_size):
            for y in range(sprite_y, sprite_y + sprite_size):
                tx = int((x - sprite_x) * 128 / sprite_size)
                ty = int((y - sprite_y) * 128 / sprite_size)
                c = sprite["sprite"].get_at((tx, ty))
                if c != TRANSPARENT:
                    if x > 500 and x < 1000:
                        if self.zbuffer[x - 500] >= distance:   
                            self.zbuffer[x - 500] = distance
                            self.point(x, y, c)

    def render(self):
        self.draw_map()
        self.draw_player()
        self.clearZ()

        # density = 100

        # minimap

        """
        for i in range(0, density):
            a = self.player["a"] - self.player["fov"] / 2 + self.player["fov"] * i / density
            d, c, t = self.cast_ray(a)
        """
        # separador
        
        """
        for i in range(0, 500): 
            self.point(499, i)
            self.point(500, i)
            self.point(501, i)
        """

        # draw in 3d
        
        for i in range(0, int(self.width)):
            a = self.player["a"] - self.player["fov"] / 2 + self.player["fov"] * i / (self.width / 2)
            d, c, tx = self.cast_ray(a)
            x = int(self.width / 2) + i
            h = (self.height / (d * cos(a - self.player["a"]))) * self.height / 5

            if self.zbuffer[i] > d:
                self.draw_stake(x, h, c, tx)
                self.zbuffer[i] = d
        
        for enemy in enemies:
            self.draw_sprite(enemy)

        for character in characters:
            self.draw_sprite(character)

    def check_out_bounds(self):
        for i in range(0, int(self.width)):
            a = self.player["a"] - self.player["fov"] / 2 + self.player["fov"] * i / (self.width / 2)
            d, c, tx = self.cast_ray(a)
            if d <= 10:
                return True

        return False

    def shoot(self):
        indexes = []
        cont = 0
        pygame.mixer.Sound.play(self.spell)
        for sprite in enemies:
            sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])

            distance = ((self.player["x"] - sprite["x"]) ** 2 + (self.player["y"] - sprite["y"]) ** 2) ** 0.5

            sprite_size = int(500 / distance * 500 / 10)

            sprite_x = int(500 + (sprite_a - self.player["a"]) * 500 / self.player["fov"] + (sprite_size / 2))
            sprite_y = int(500 / 2 - sprite_size / 2)

            if 500 < sprite_x < 700:
                indexes.append(cont)
            cont += 1
        
        for index in indexes:
            enemies.pop(index)
            self.dead_enemies += 1

r = Raycaster(screen)
r.load_map('map.txt')

north, south = pygame.K_UP, pygame.K_DOWN
east, west = pygame.K_RIGHT, pygame.K_LEFT

change = 0
horizontal_direction = 1
vertical_direction = 1
clock = pygame.time.Clock()
running = True

pygame.mixer.music.load('potter.wav')
pygame.mixer.music.play(-1)

while running:
    screen.fill(BLACK)
    screen.fill(SKY, (r.width, 0, r.width, r.height / 2))
    screen.fill(GROUND, (r.width, r.height / 2, r.width, r.height))

    r.render()

    pygame.display.flip()
    clock.tick()
    # print(clock.get_fps())
    
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False

        if (event.type == pygame.KEYDOWN):

            if event.key == pygame.K_a:
                r.player["a"] -= pi / 10
            if event.key == pygame.K_d:
                r.player["a"] += pi / 10
            
            if event.key == pygame.K_SPACE:
                r.shoot()

            angle = r.player["a"] % (2 * pi)

            if (change == 0 or change == 2) and (angle < pi / 10 or angle > 5 * pi / 3):
                temp1, temp2 = east, west
                east, west = north, south
                north, south = temp1, temp2
                change = 1
                horizontal_direction = -1
                vertical_direction = 1

            elif change == 1 and pi/3 <= angle and angle <= 9 * pi / 10:
                temp1, temp2 = east, west
                east, west = north, south
                north, south = temp1, temp2
                change = 0
                horitzontal_direction = 1
                vertical_direction = 1

            elif (change == 0 or change == 2) and (angle >= 9 * pi / 10 and angle <= 4 * pi / 3):
                temp1, temp2 = east, west
                east, west = north, south
                north, south = temp1, temp2
                change = 1
                horizontal_direction = 1
                vertical_direction = -1

            elif (change == 0 or change == 1) and 4 * pi / 3 <= angle <= 5 * pi / 3:
                temp1, temp2 = east, west
                east, west = north, south
                north, south = temp1, temp2
                change = 2
                horizontal_direction = -1
                vertical_direction = -1

            if event.key == east:
                r.player["x"] -= 10 * horizontal_direction
                if r.check_out_bounds():
                    r.player["x"] += 10 * horizontal_direction
            if event.key == west:
                r.player["x"] += 10 * horizontal_direction
                if r.check_out_bounds():
                    r.player["x"] -= 10 * horizontal_direction
            if event.key == north:
                r.player["y"] += 10 * vertical_direction
                if r.check_out_bounds():
                    r.player["y"] -= 10 * vertical_direction
            if event.key == south:
                r.player["y"] -= 10 * vertical_direction
                if r.check_out_bounds():
                    r.player["y"] += 10 * vertical_direction