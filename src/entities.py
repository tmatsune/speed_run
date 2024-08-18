import pygame as pg 
import math, random
from .entity import Entity 
from .utils import silhouette, get_image
from .settings import CELL_SIZE, IMG_PATH

false = False
true = True

FORCE_SCALAR_DECAY = .2
MAX_JUMPS = 2
HURT_TIME = 1

class Player(Entity):
    def __init__(self, app, pos, size, type, animated=False) -> None:
        super().__init__(app, pos, size, type, animated)
        # ---- CONST ---- #
        self.speed = 3.4
        self.image_base_dimensions = [CELL_SIZE, CELL_SIZE]

        self.mask = pg.mask.from_surface(self.anim.image())
        
        # ---- VARS ---- # 

        # -- LIST 
        self.vel = [0, 0]
        self.scale = [1, 1]
        
        # -- VAR
        self.air_time = 0
        self.force_scalar = 1 
        self.flip = false 
        self.jumps = MAX_JUMPS
        self.squish_velocity = 0
        self.angle = 0 
        self.paint = 100
        self.hurt_timer = HURT_TIME
        self.dead = false 
        self.gun_img = get_image(IMG_PATH + 'objs/gun.png', [8,8])

    def update(self, dt):
        super().update(dt)

        self.inputs = [false, false, false, false]#self.app.inputs.copy()

        if self.inputs[0]:
            self.flip = true
        elif self.inputs[1]:
            self.flip = false

        speed_x = (self.inputs[1] - self.inputs[0])
        if self.force_scalar != 1 and not self.just_hit:
            if self.flip: 
                if speed_x == 0: speed_x = -1
                else: speed_x = -1.1
            else: 
                if speed_x == 0: speed_x = 1
                else: speed_x = 1.1
        elif self.force_scalar != 1:
            self.just_hit = false
            speed_x = 1.2 if self.flip else -1.2

        #self.apply_force([speed_x * self.speed * self.force_scalar, 0])
        self.add_friction()
        self.vel[1] = min(10, self.vel[1]+1)

        if self.force_scalar > 1:
            self.force_scalar -= FORCE_SCALAR_DECAY
        elif self.force_scalar < 1:
            self.force_scalar = 1

        hitable_rects = self.app.tile_map.get_surrounding_tiles(self.pos)
        collisions = self.movement(self.vel, hitable_rects)
        self.squash_effect(collisions)
        self.state_handler(collisions)

        if collisions['down']:
            self.vel[1] = 0
            self.air_time = 0
            self.jumps = MAX_JUMPS
        else:
            self.air_time += 1

    def render(self, surf, offset=[0,0]):
        offset = offset.copy()
        if self.anim.config['offset']:
            offset[0] += self.anim.config['offset'][0]
            offset[1] += self.anim.config['offset'][1]
        img = self.anim.image()
        if self.scale != [1,1]:
            img = pg.transform.scale(img, (int(self.scale[0] * self.image_base_dimensions[0]), int(self.scale[1] * self.image_base_dimensions[1])))
            x_diff = (CELL_SIZE - img.get_width()) // 2         
            y_diff = (CELL_SIZE - img.get_height()) 
            offset[0] -= x_diff
            offset[1] -= y_diff 
            
        if self.flip:
            img = pg.transform.flip(img, self.flip, false)

        if not self.dead:
            surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
            gun_pos = self.center()
            ang = math.atan2(self.app.mouse_pos[0]//2 - self.center()[0]+offset[0], self.app.mouse_pos[1]//2 - self.center()[1]+offset[1])
            gun_img = pg.transform.rotate(self.gun_img, math.degrees(ang)-90)
            surf.blit(gun_img, (gun_pos[0] - offset[0] - 4, gun_pos[1] - offset[1] - 4))

        self.mask = pg.mask.from_surface(img)
        if self.state == 'hurt':
            if math.sin(self.data.total_time) > 0:
                sil = silhouette(img)
                surf.blit(sil, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def hit(self):
        if not self.dead:
            self.dead = true   

            for i in range(30):
                color = random.choice([(37, 255, 60), (37, 120, 250), (255, 37, 80), (250, 250, 50), (150, 50, 250)])
                particle = ['paint', self.center(), [random.random() * 6 - 3, random.random() * 6 - 3], color, random.randrange(2, 3), random.uniform(.02, .06), 0]
                self.app.circle_particles.append(particle)
            self.app.circles.append([self.center(), 6, 1, 6, 0.15, 0.9, (247, 237, 186)])
            for i in range(30):
                ang = random.uniform(-math.pi, math.pi)
                spark = [self.center(), ang, random.randrange(7, 10), random.randrange(4, 6), random.uniform(.20, .24), 0.9, random.randrange(14, 18), random.uniform(.92, .98), 
                         random.choice([(37, 255, 60), (37, 120, 250), (255, 37, 80), (250, 250, 50), (150, 50, 250)])]
                self.app.sparks.append(spark)
            '''
            for i in range(18):
                angle = random.uniform(-3.14, 3.14)
                speed = random.randrange(1, 2)
                particle = ['fire_ball', self.center(), [math.cos(angle) * speed, math.sin(angle) * speed], (245, 237, 186), random.randrange(2, 3), .04, 0]
                self.app.circle_particles.append(particle)
            for i in range(30):
                pos = self.center()
                fire = ['fire', [pos[0] + random.randrange(-2,2), pos[1] + random.randrange(10,20)], [random.uniform(-.5,.5), random.uniform(-1.2, -.5)], (10, 0, 0), random.randrange(3, 6), random.uniform(.12, .16), 0]
                self.app.circle_particles.append(fire)
            '''

    def add_friction(self):
        if self.vel[0] > 0:
            self.vel[0] -= .4
        elif self.vel[0] < 0:
            self.vel[0] += .4
        if abs(self.vel[0]) < .5:
            self.vel[0] = 0 
    
    def apply_force(self, force):
        self.vel[0] += force[0]
        self.vel[1] += force[1]
        if self.vel[0] > 4: self.vel[0] = min(4, self.vel[0])
        if self.vel[0] < -4: self.vel[0] = max(-4, self.vel[0])
        
        if self.vel[1] < -4: self.vel[1] = max(-4, self.vel[1])

    def jump(self):
        if self.jumps > 0:
            self.jumps -= 1 
            self.vel[1] = -12
        for i in range(2):
            ang = (5*math.pi)/4 if i < 1 else (7*math.pi)/4
            pos = [self.pos[0]+2, self.pos[1]+12] if i == 0 else [self.pos[0]+14, self.pos[1]+12]
            spark = [
                     pos, # pos
                     ang,          # angle
                     2,            # speed 
                     2,            # width 
                     0.3,          # width decay 
                     0.6,          # speed_decay 
                     6,            # length
                     0.88,         # length decay 
                     None
                    ]
            self.app.sparks.append(spark)
        for i in range(2):
            ang = (4*math.pi)/3 if i < 1 else (5*math.pi)/3
            pos = [self.pos[0]+5, self.pos[1] + 8] if i == 0 else [self.pos[0]+11, self.pos[1]+8]
            spark = [
                pos,  # pos
                ang,          # angle
                2,            # speed
                2,            # width
                0.3,          # width decay
                0.6,          # speed_decay
                6,            # length
                0.88,         # length decay
                None
            ]
            self.app.sparks.append(spark)

    def state_handler(self, collisions):
        if self.state == 'idle':
            if self.vel[0] != 0:
                if not collisions['down']: self.change_state('jump')
                else: self.change_state('run')
            elif not collisions['down']:
                self.change_state('jump')
        elif self.state == 'run':
            if self.vel[0] == 0:
                self.change_state('idle')
            elif not collisions['down']:
                self.change_state('jump')
        elif self.state == 'jump':
            if collisions['down']:
                self.change_state('idle')

    def squash_effect(self, collisions):
        self.scale[1] += self.squish_velocity               # increase y scale
        self.scale[1] = max(0.3, min(self.scale[1], 1.5))   # get max y scale
        self.scale[0] = 2 - self.scale[1]                   # get x scale, larger y scale, smaller x scale 

        if self.scale[1] > 1:                               # get scale back to 1
            self.squish_velocity -= 0.026
        elif self.scale[1] < 1:
            self.squish_velocity += 0.026

        if self.squish_velocity > 0:                        # get squish vel back to 0 
            self.squish_velocity -= 0.016
        if self.squish_velocity < 0:
            self.squish_velocity += 0.016

        if self.squish_velocity != 0:               
            if (abs(self.squish_velocity) < 0.06) and (abs(self.scale[1] - 1) < 0.06):
                self.scale[1] = 1
                self.squish_velocity = 0

        if collisions['down']:
            if self.vel[1] > 6:
                self.squish_velocity = -0.14
    
