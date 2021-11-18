import pygame
from math import sin, cos, atan2, inf, sqrt, pi, hypot
from pygame import gfxdraw
from random import choice, randint, random
from itertools import combinations
import parameters
import numpy as np

from display_size import displayHeight, displayWidth



def clamp(val, low=None, high=None):
    # Return value no lower than low and no higher than high
    minimum = -inf if low is None else low
    maximum = inf if high is None else high
    return max(min(val, maximum), minimum)


def dist(x1, y1, x2, y2, less_than=None, greater_than=None):
    # Use less_than or greater_than avoid using costly square root function
    if less_than is not None:
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) < less_than ** 2
    if greater_than is not None:
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) > greater_than ** 2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# # def overlapping_particle(x, y, r):
# #        # Returns an overlapping particle from particles or None if not touching any
# #        for particle in particles:
# #            if dist(x, y, particle.x, particle.y, less_than=r + particle.r):
# #                return particle
           

def draw_circle(surface, x, y, radius, color):
    # Draw anti-aliased circle
    gfxdraw.aacircle(surface, int(x), int(y), radius, color)
    gfxdraw.filled_circle(surface, int(x), int(y), radius, color)


def particle_bounce_velocities(p1, p2):
    # Change particle velocities to make them bounce
    # Based off github.com/xnx/collision/blob/master/collision.py lines 148-156
    from parameters import COLLISION_DAMPING, DO_DAMPING
    m1, m2 = p1.r ** 2, p2.r ** 2
    big_m = m1 + m2
    r1, r2 = np.array((p1.x, p1.y)), np.array((p2.x, p2.y))
    d = np.linalg.norm(r1 - r2) ** 2
    v1, v2 = np.array((p1.vx, p1.vy)), np.array((p2.vx, p2.vy))
    u1 = v1 - 2 * m2 / big_m * np.dot(v1 - v2, r1 - r2) / d * (r1 - r2)
    u2 = v2 - 2 * m1 / big_m * np.dot(v2 - v1, r2 - r1) / d * (r2 - r1)
    p1.vx, p1.vy = u1 * (COLLISION_DAMPING if DO_DAMPING else 1)
    p2.vx, p2.vy = u2 * (COLLISION_DAMPING if DO_DAMPING else 1)


def particle_bounce_positions(p1, p2):
    # Push particles away so they don't overlap
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    angle = atan2(dy, dx)
    center_x = p1.x + 0.5*dx
    center_y = p1.y + 0.5*dy
    radius = (p1.r + p2.r) / 2
    p1.x = center_x - (cos(angle) * radius)
    p1.y = center_y - (sin(angle) * radius)
    p2.x = center_x + (cos(angle) * radius)
    p2.y = center_y + (sin(angle) * radius)
    

class Particle:
    def __init__(self, r, angle=None, vel_mult=1, x=None, y=None):
        a = 2 * pi * random() if angle is None else angle  # Angles are clockwise from 3 o'clock
        self.vx, self.vy = (cos(a)*vel_mult, sin(a)*vel_mult)
        self.dir = pygame.math.Vector2((self.vx, self.vy)).normalize()
        #self.velocity = 0
        self.color = (85, 239, 196)
        self.r = r  # Radius
        self.x, self.y = x, y
        #self.x, self.y = 300, 400
        if self.x is None or self.y is None:
            self.calculate_pos()
        

    def calculate_pos(self):
        # Find a position where we won't overlap with any other particles
        while True:
            self.x, self.y = randint(self.r, displayWidth - self.r), randint(self.r, displayHeight - self.r)
            #if overlapping_particle(self.x, self.y, self.r) is None:  # If valid spot
                #break
            break

    def damping(self, amount):
        # Slow down the particle gradually
        self.vx *= amount
        self.vy *= amount

    def gravity(self, amount):
        self.vx += amount

    def wall_collisions(self, damping_amount):
        # Velocity
        collided = False
        if not self.r < self.x < displayWidth - self.r:
            self.vx *= damping_amount
            collided = True
        if not self.r < self.y < displayHeight - self.r:
            self.vy *= damping_amount
            collided = True
            

        # Position
        if collided:
            # Get out of wall
            self.x = clamp(self.x, low=self.r, high=displayWidth - self.r)
            self.y = clamp(self.y, low=self.r, high=displayHeight - self.r)
            
            
    def user_wall_collisions(self, x, y, x1, x2, y1, y2, damping_amount):
        # Velocity
        collided = False
        radius = parameters.NEW_GENERATION_RADIUS
        rleft, rtop, width, height = x1, y1, x2-x1, y2-y1
        rright, rbottom = rleft + width/2, rtop + height/2
        self.color = (85, 239, 196)
        
        # bounding box of the circle
        cleft, ctop     = x-radius, y-radius
        cright, cbottom = x+radius, y+radius
        
        if rright < cleft or rleft > cright or rbottom < ctop or rtop > cbottom:
            return False  # no collision possible
    
        # check whether any point of rectangle is inside circle's radius
        for xs in (rleft, rleft+width):
            for ys in (rtop, rtop+height):
                # compare distance between circle's center point and each point of
                # the rectangle with the circle's radius
                if hypot(xs-x, ys-y) <= radius:
                    return True  # collision detected
    
        # check if center of circle is inside rectangle
        if rleft <= x <= rright and rtop <= y <= rbottom:
            self.color = (255, 255, 255)
            #self.vx *= damping_amount
            #collided = True
            return True  # overlaid
    
        return False  # no collision detected
        
        
        # if not self.r < self.x < x1 - self.r:
        #     self.vx *= damping_amount
        #     collided = True
        # if not self.r < self.y < y1 - self.r:
        #     self.vy *= damping_amount
        #     collided = True
            

        # # # Position
        # if collided:
        #     # Get out of wall
        #     self.x = clamp(self.x, low=self.r, high=x1 - self.r)
        #     self.y = clamp(self.y, low=self.r, high=y1 - self.r)
        
    def thickness_lines(self, x, y, x1, x2, y1, y2, width, damping_amount):
        r = sqrt((x2-x1) ** 2 + (y2-y1) **2)
        deltax = width * (y1-y2) / r
        deltay = width * (x2-x1) / r
        x3 = x1 + deltax
        y3 = y1 + deltay
        x4 = x2 + deltax
        y4 = y2 + deltay
        
        x5 = x1 - deltax
        y5 = y1 - deltay
        x6 = x2 - deltax
        y6 = y2 - deltay
        
        self.line_collision(x, y, x3, x4, y3, y4, damping_amount)
        self.line_collision(x, y, x5, x6, y5, y6, damping_amount)
    
    
    def line_collision(self, x, y, x1, x2, y1, y2, damping_amount):
        collided = False
        #radius = parameters.NEW_GENERATION_RADIUS
        #self.color = (85, 239, 196)
        x1 -= x
        y1 -= y
        x2 -= x
        y2 -= y
        
        normal = (-(y2 - y1), (x2 - x1))
        
        a = (x2 - x1) ** 2 + (y2 - y1) ** 2
        b = 2*(x1 * (x2 - x1) + y1 * (y2 - y1))
        c = x1 ** 2 + y1 ** 2 - self.r ** 2
        disc = b ** 2 - 4*a*c
        if disc <= 0:
            self.color = (85, 239, 196)
        else:
            sqrtdisc = sqrt(disc)
            t1 = (-b + sqrtdisc)/(2*a)
            t2 = (-b - sqrtdisc)/(2*a)
            if (t1 > 0 and t1 < 1) or (t2 > 0 and t2 < 1):
                #bself.color = (255, 255, 255)
                
                new_direc = self.dir.reflect(normal).normalize()
            
                self.vx = new_direc[0] #* damping_amount
                self.vy = new_direc[1] #* damping_amount
                
                #self.vx *= damping_amount
                #self.vy *= damping_amount
            # else:
            #     self.color = (85, 239, 196)
        
        # if collided:
        #     if x1 < x2 and y1 < y2:
        #         self.x = clamp(self.x, low=x1, high=x2 - self.r)
        #         self.y = clamp(self.y, low=y1, high=y2 - self.r)
        #     if x1 > x2 and y1 < y2:
        #         self.x = clamp(self.x, low=x2, high=x1 - self.r)
        #         self.y = clamp(self.y, low=y1, high=y2 - self.r)
        #     if x1 < x2 and y1 > y2:
        #         self.x = clamp(self.x, low=x1, high=x2 - self.r)
        #         self.y = clamp(self.y, low=y2, high=y1 - self.r)
        #     if x1 > x2 and y1 > y2:
        #         self.x = clamp(self.x, low=x2, high=x1 - self.r)
        #         self.y = clamp(self.y, low=y2, high=y1 - self.r)
            

    def move(self, speed):
        self.dir = pygame.math.Vector2((self.vx, self.vy)).normalize()
        self.x += self.vx * speed
        self.y += self.vy * speed

    def draw(self, surface):
        draw_circle(surface, self.x, self.y, self.r, self.color)

    def apply_force_towards(self, x, y, strength=1):
        # May be used in later implementations with attractions
        dx = x - self.x
        dy = y - self.y
        self.vx += dx * 0.00001 * strength
        self.vy += dy * 0.00001 * strength
        

class Wall:

    def __init__(self, x1, y1, x2, y2, width):
        self.x1 = x1
        self.y1 = y1 #displayHeight - y1
        self.x2 = x2
        self.y2 = y2 #displayHeight - y2
        self.width = width


    def draw(self, surface):
        pygame.draw.line(surface, (50,120,100), (self.x1, self.y1), (self.x2, self.y2), self.width)
        
        

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simple Wall Fluid Sim")
        width = displayWidth
        height = displayHeight
        self.screen = pygame.display.set_mode((width, height))
        self.myfont = pygame.font.SysFont("monospace", 16)
        
        
        self.clock = pygame.time.Clock()
        self.ticks = 60           
        self.exit = False
        
        self.walls = []
        self.line_width = 5#2.5
        
        #self.set_walls()
        
        self.particles = []
        self.new_generation()
        
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        self.press = False
        
        self.wall_list = []
        
    # def set_walls(self):
    #     self.walls.append(Wall(0, -100, 1, displayHeight+100))
    #     self.walls.append(Wall(-100, 0, displayWidth+100, 1))
    #     self.walls.append(Wall(displayWidth, -100, displayWidth-1, displayHeight+100))
    #     self.walls.append(Wall(-100, displayHeight, displayWidth+100, displayHeight-1))
        
    
    def add_particle(self, angle=None, vel_mult=1, x=None, y=None, r=None):
        self.particles.append(Particle(angle=angle, vel_mult=vel_mult, x=x, y=y, r=r))
        
    
    def new_generation(self):
        for _ in range(parameters.NEW_GENERATION_NUM_PARTICLES):
            self.particles.append(Particle(r = parameters.NEW_GENERATION_RADIUS))
            
        
    def render(self):    
        #self.screen.fill((127, 225, 212))
        self.screen.fill((0,0,0))
            
        for i in self.walls:
            i.draw(self.screen)
            #print(i.x1, i.x2, i.y1, i.y2)
            #print("break")
        
        for particle in self.particles:
            particle.draw(self.screen)
            # stext = self.myfont.render(str(particle.dir), 1, (255,255,255))
            # self.screen.blit(stext, (500, 10))
              
    
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        speedtext = self.myfont.render(str(self.mouse_x) + " and " + str(self.mouse_y), 1, (255,255,255))
        self.screen.blit(speedtext, (7, 10))
        
        
        pygame.display.flip()

    def add_wall_coord(self):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        if len(self.wall_list) == 0:
            self.wall_list.append(self.mouse_x)
            self.wall_list.append(self.mouse_y)
        if len(self.wall_list) == 2 and self.mouse_x not in self.wall_list and self.mouse_y not in self.wall_list:
            self.wall_list.append(self.mouse_x)
            self.wall_list.append(self.mouse_y)
            self.walls.append(Wall(self.wall_list[0], self.wall_list[1],
                              self.wall_list[2], self.wall_list[3], int(2*self.line_width)))
            self.wall_list = []
        

    def run(self):
        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit = True
                        
            if event.type == pygame.MOUSEBUTTONUP:
                self.add_wall_coord()
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE:
                        self.wall_list = []
                        
            keys = pygame.key.get_pressed()
            if keys[pygame.K_g]:
                parameters.GRAVITY = 0.025 if parameters.GRAVITY == 0 else 0
                parameters.DO_DAMPING = parameters.GRAVITY != 0
                        
            for particle in self.particles:
                particle.damping(parameters.DAMPING if parameters.DO_DAMPING else 1)
                particle.gravity(parameters.GRAVITY)
                particle.wall_collisions(-parameters.WALL_DAMPING if parameters.DO_DAMPING else -1)
                particle.move(parameters.SPEED_MULTIPLIER)
                for wall in self.walls:
                    #particle.user_wall_collisions(particle.x, particle.y, wall.x1, wall.x2, wall.y1, wall.y2, -parameters.WALL_DAMPING if parameters.DO_DAMPING else -1)
                    #particle.line_collision(particle.x, particle.y, wall.x1, wall.x2, wall.y1, wall.y2, self.line_width, -parameters.WALL_DAMPING if parameters.DO_DAMPING else -1)
                    particle.thickness_lines(particle.x, particle.y, wall.x1, wall.x2, wall.y1, wall.y2, self.line_width, -parameters.WALL_DAMPING if parameters.DO_DAMPING else -1)
                    
            # Test inter-particle collisions
            pairs = combinations(range(len(self.particles)), 2)  # All combinations of particles
            for i, j in pairs:
                p1, p2 = self.particles[i], self.particles[j]
                if dist(p1.x, p1.y, p2.x, p2.y, less_than=p1.r + p2.r):  # If they are touching
                    particle_bounce_velocities(p1, p2)
                    particle_bounce_positions(p1, p2)
                    
                
            self.render()
            
            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()