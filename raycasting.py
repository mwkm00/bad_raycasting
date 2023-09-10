import pygame as pg
import numpy
import random

WIDTH = 800
HEIGHT = 800
WIDTH_TRUE = 1600
FPS = 60
RES = (WIDTH_TRUE, HEIGHT)

display = pg.display.set_mode(RES)
clock = pg.time.Clock()

running = True

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 10
        self.rays = []
        self.distances = []
        for x in range(90):
            self.rays.append(Raycast(self.x, self.y, numpy.radians(x)))

    def move(self):
        cos_a = numpy.cos(self.angle+45)
        sin_a = numpy.sin(self.angle+45)
        dx, dy = 0, 0
        speed_sin = self.speed * sin_a
        speed_cos = self.speed * cos_a

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            dx += -speed_sin
            dy += speed_cos

        if self.x + dx < 800 and self.x + dx > 0:
            self.x += dx
        if self.y + dy < 800 and self.y + dy > 0:
            self.y += dy
        
        if keys[pg.K_LEFT]:
            self.angle -= 0.02
        if keys[pg.K_RIGHT]:
            self.angle += 0.02
        self.angle %= numpy.pi*2

    def update(self):
        self.move()
        for ray in self.rays:
            ray.x = self.x
            ray.y = self.y
            ray.update(ray.angle+self.angle)
            
    def look(self, walls):
        for ray in self.rays:
            closest = None
            record = 999999999
            for wall in walls:
                pt = ray.cast(wall)
                if pt:
                    a = numpy.array((pt[0], pt[1]))
                    b = numpy.array((self.x, self.y))
                    d = numpy.linalg.norm((a-b))
                    if d < record:
                        record = d
                        closest = pt
            if closest:
                pg.draw.line(display, "white", (self.x, self.y), (closest[0], closest[1]))
                distance = (self.x-closest[0])*(self.x-closest[0]) + (self.y-closest[1])*(self.y-closest[1])
                self.distances.append(numpy.sqrt(distance))

    def draw(self):
        pg.draw.circle(display, "green", (self.x, self.y), 8)
        for i, d in enumerate(self.distances):
            c = int(((d/1132)*255))
            h = int((d/2000)*HEIGHT)
            pg.draw.rect(display, pg.Color(255-c,255-c,255-c), 
                         pg.Rect((WIDTH+i*(WIDTH//88),h),(WIDTH//90,HEIGHT-h*1.5)))

        #pg.draw.line(display, "yellow", (self.x, self.y), (self.x + WIDTH * numpy.cos(self.angle+45), 
            #self.y + WIDTH * numpy.sin(self.angle+45)))

class Obstacle:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.start_pos = (start_x, start_y)
        self.end_pos = (end_x, end_y)
    def draw(self):
        pg.draw.line(display, "red", self.start_pos, self.end_pos)

class Raycast:
    def __init__(self, x ,y, angle):
        self.x = x
        self.y = y
        self.pos = [x,y]
        self.angle = angle
        self.dir = [numpy.cos(self.angle),numpy.sin(self.angle)]

    def look_at(self, x, y):
        self.dir[0] = x - self.x
        self.dir[1] = y - self.y
        self.dir = self.dir / numpy.linalg.norm(self.dir)

    def update(self, angle):
        self.dir = [numpy.cos(angle),numpy.sin(angle)]

    def cast(self, wall):
        x1 = wall.start_x
        y1 = wall.start_y
        x2 = wall.end_x
        y2 = wall.end_y

        x3 = self.x
        y3 = self.y
        x4 = self.x + self.dir[0]
        y4 = self.y + self.dir[1]

        den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)

        if den == 0:
            return False
        
        t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4))/den
        u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3))/den

        if (t > 0 and t < 1 and u > 0):
            point = [0,0]
            point[0] = x1 + t*(x2 - x1)
            point[1] = y1 + t*(y2 - y1)
            return point
        else:
            return False

player = Player(WIDTH//2, HEIGHT//2)


obstacles = [Obstacle(random.randint(0,800),random.randint(0,800),random.randint(0,800),random.randint(0,800)) for x in range(5)]
#obstacles = [Obstacle(250,250,250,350), Obstacle(250,350,350,350), Obstacle(350,350,350,250), Obstacle(350,250,250,250)]
obstacles.append(Obstacle(0,0,0,800))
obstacles.append(Obstacle(0,0,800,0))
obstacles.append(Obstacle(800,800,800,0))
obstacles.append(Obstacle(800,799,0,799))
while running:
    display.fill((0,0,0))
    clock.tick(FPS)
    player.draw()
    player.update()
    player.distances = []
    player.look(obstacles)
    for o in obstacles:
        o.draw()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    pg.display.flip()
    

