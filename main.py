import pygame as pg
import sys, random, math 
from enum import Enum
from pygame.locals import *
from src.settings import * 
from src.utils import * 
from src.tilemap import Tile_Map, decor_congif_id
from src.entities import Player
from src.asset_manager import *
from src.particles import * 
from src.anim_effect import Anim_Effect
from src.grass_manger import * 

false = False
true = True
NULL = None
inf = float('inf')
n_inf = float('-inf')
WIN_COND = 4

class State(Enum):
    START = 0 
    RUN = 1 
    PAUSE = 2 
    DEAD = 3 
    TRANSIT = 4 
    WIN = 5

light_mask_base = load_img(f'{IMG_PATH}lights/light.png')
light_mask_base_yellow = light_mask_base.copy()
light_mask_base_yellow.fill((255, 240, 1))  # (1, 196, 248)
light_mask_base_yellow.blit(light_mask_base, (0, 0), special_flags=BLEND_RGBA_MULT)

light_mask_base_blue = light_mask_base.copy()
light_mask_base_blue.fill((1, 196, 248))  # (1, 196, 248)
light_mask_base_blue.blit(light_mask_base, (0, 0), special_flags=BLEND_RGBA_MULT)

light_mask_full = pg.transform.scale(light_mask_base, (WIDTH, HEIGHT))
light_mask_full.blit(light_mask_full, (0, 0), special_flags=BLEND_RGBA_ADD)
light_masks = []
light_masks_yellow = []
light_masks_blue = []
for radius in range(1, 250):
    light_masks.append(pg.transform.scale(light_mask_base, (radius, radius)))
for radius in range(1, 150):
    light_masks_yellow.append(pg.transform.scale(light_mask_base_yellow, (radius, radius)))
for radius in range(1, 150):
    light_masks_blue.append(pg.transform.scale(light_mask_base_blue, (radius, radius)))

def glow(surf, pos, radius, color=False):
    if not color: glow_img = light_masks[radius - 1]
    else:
        if color == 'blue': glow_img = light_masks_blue[radius - 1]
        elif color == 'indigo': glow_img = light_masks_yellow[radius - 1]
    surf.blit(glow_img, (pos[0], pos[1]), special_flags=BLEND_RGBA_ADD)

class App:
    def __init__(self) -> None:
        pg.init()
        self.screen: pg.display = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.dt: float = 0
        self.clock: pg.time = pg.time.Clock()

        self.fonts = {
            'pixel_0': 'src/assets/fonts/pixel_0.ttf',
            '0': 'src/assets/fonts/0.ttf',
            'pixel_2': 'data/assets/fonts/pixel_2.ttf',
        }
        # ------ GAME VARIABLES
        self.screenshake = 0 
        self.total_time = 0 
        self.mouse_pos = [0, 0]
        self.left_clicked = false 
        self.right_clicked = false 
        self.inputs = [false, false, false, false]
        self.bg = get_image(f'{IMG_PATH}bg/bg.png', [WIDTH, HEIGHT])
        self.bg_2 = self.bg.copy()
        self.bg_pos = [0,0]
        self.bg_2_pos = [WIDTH,0]

        # -------- GAME SETTINGS 
        self.offset = [0,0]
        self.edges = [inf, n_inf, inf, n_inf]  # x, -x, y, -y

        # ------- GAME MAIN DATA 
        self.state = State.START
        self.level = 0
        self.transition = [350, 1, 8, 'closing']

        # -------- PARTICLES 
        self.particles = []
        self.circles = []
        self.circle_particles = []
        self.sparks = []
        self.orbs = []
        self.bg_effects = []
        self.paints = []

        # -------- DATA INIT
        self.grass_manager = Grass_Manager(self)
        self.asset_manager = Asset_Manager()
        self.tile_map = Tile_Map(self, self.grass_manager)
        self.player = None
        self.load_map(self.level)
        self.test_init_func()
        load_stars(PARTS_PATH+'stars')
        load_bg_images(IMG_PATH+'bg/star')
        self.tree_animations = [Anim_Effect(load_img(f'{TILESET_PATH}decor/' + str(i) + '.png'), [
                                            [152, 107, 255], [202, 159, 255], [222, 189, 255]], motion_scale=0.5) for i in range(2)]


    def load_map(self, map_name):
        self.player = Player(self, [50,100], [CELL_SIZE, CELL_SIZE], 'player', True)
        self.tile_map.load_map(map_name)
        self.edges = [inf, n_inf, inf, n_inf]

        # -------- MAP DATA -------- #
        for pos in self.tile_map.tile_map:
            x = pos[0] * CELL_SIZE
            y = pos[1] * CELL_SIZE
            if x < self.edges[0]:
                self.edges[0] = x
            if x > self.edges[1]:
                self.edges[1] = x + CELL_SIZE
            if y < self.edges[2]:
                self.edges[2] = y + CELL_SIZE*2
            if y > self.edges[3]:
                self.edges[3] = y + CELL_SIZE*1

    def render(self):

        # ----- SCREEN SETUP ----- #
        self.display.fill((12, 10, 22))
        light_surf = self.display.copy()
        light_surf.fill((125, 125, 125))

        # ----- UPDATE ----- #
        self.total_time += 1
        self.mouse_pos = pg.mouse.get_pos()

        # ------- SCROLL OFFSET ------- #
        self.offset[0] += ( ( self.player.pos[0] - WIDTH // 2 )  - self.offset[0]) / 12
        self.offset[1] += ( ( self.player.pos[1] - HEIGHT // 2 )  - self.offset[1]) / 12
        if self.offset[0] < self.edges[0]:
            self.offset[0] = self.edges[0]
        if self.offset[0] + WIDTH > self.edges[1]:
            self.offset[0] = self.edges[1] - WIDTH
            
        if self.offset[1] < self.edges[2]:
            self.offset[1] = self.edges[2]
        if self.offset[1] + HEIGHT > self.edges[3]:
            self.offset[1] = self.edges[3] - HEIGHT

        # --------- BACKGROUND EFFECTS --------- #
        # [pos, vel, image_id, rate]
        for i, eff in enumerate(self.bg_effects):
            img = bg_star_images[int(eff[2])]
            eff[2] += eff[3]
            if eff[2] >= len(bg_star_images): eff[2] = 0 
            self.display.blit(img, ((eff[0][0] - self.offset[0]) % WIDTH, (eff[0][1] - self.offset[1]) % HEIGHT))

        # --------- MAIN RENDER ACTIONS ---------- #

        layers, objects = self.tile_map.get_visible_tiles(self.display, self.offset)
        for n, layer in layers.items():
            for tile in layer:
                real_pos = [tile[0][0] * CELL_SIZE, tile[0][1] * CELL_SIZE]
                img = tile[4]
                if tile[2] == 'decor':
                    self.tree_animations[1].render(self.display, (real_pos[0] - self.offset[0], real_pos[1] - self.offset[1]-16), m_clock=self.total_time / 100, seed=251228987)
                elif tile[2] == 'tileset_2' and tile[3] < 3:
                    tile[5].render(self.display, int(math.sin(tile[0][1] / 100 + self.total_time / 20) * 30) / 10,self.offset)
                    self.display.blit(img, (real_pos[0] - self.offset[0], real_pos[1] - self.offset[1]))
                else:
                    self.display.blit(img, (real_pos[0] - self.offset[0], real_pos[1] - self.offset[1]))
        for obj in objects:
            pos = obj[0]
            img = obj[4]
            real_pos = [pos[0] * CELL_SIZE, pos[1] * CELL_SIZE]
            self.display.blit(img, (real_pos[0] - self.offset[0], real_pos[1] - self.offset[1]))
            if mask_collision(obj[5], real_pos, self.player.mask, self.player.pos.copy()):
                if obj[2] == 'target':
                    if self.state == State.RUN:
                        self.level += 1
                        if self.level == WIN_COND:
                            self.change_state(State.WIN)
                        else:
                            self.change_state(State.TRANSIT)
                else:
                    self.player.hit()

        # ----- PLAYER 
        if self.game_on(): self.player.update(self.dt)
        self.player.render(self.display, self.offset)
        glow(light_surf, (self.player.pos[0] - self.offset[0] - 200//2, self.player.pos[1] - self.offset[1] - 200//2), 200, false)
        if self.player.pos[1] > self.edges[3]:
            self.player.dead = true 
            self.player.hit()
        if self.player.dead:
            self.change_state(State.DEAD)
        # ------------- PARTICLES ------------ #

        # -------- ORBS
        # [pos, vel, radius, color]
        for i, p in enumerate(self.orbs):
            p[0][0] += p[1][0]
            p[0][1] += p[1][1]
            color = (170,240, 250) if p[3] == 'blue' else (255, 240, 2)
            pg.draw.circle(self.display, color,
                        (int(p[0][0] - self.offset[0]) % WIDTH, int(p[0][1] - self.offset[1]) % HEIGHT), p[2])
            radius = 60
            radius2 = 20
            glow(light_surf, (int(p[0][0] - self.offset[0] - radius//2) % WIDTH, int(p[0][1] - self.offset[1] - radius//2) % HEIGHT), radius, p[3])
            glow(light_surf, (int(p[0][0] - self.offset[0] - radius2//2) % WIDTH, int(p[0][1] - self.offset[1] - radius2//2) % HEIGHT), radius2, p[3])
        
            if self.state == State.START or self.state == State.WIN:
                if p[0][0] + radius >= WIDTH or p[0][0] - radius <= 0:
                    p[1][0] *= -1
                if p[0][1] + radius >= HEIGHT or p[0][1] - radius <= 0:
                    p[1][1] *= -1
        # ------- SPARKS
        # [ pos, angle, speed, width, width_decay, speed_decay, length, length_decay, col ]
        for i, spark, in enumerate(sorted(self.sparks, reverse=true)):
            spark[0][0] += math.cos(spark[1]) * spark[2]
            spark[0][1] += math.sin(spark[1]) * spark[2]
            spark[3] -= spark[4] # sub width by decay 
            spark[2] *= spark[5] # decrase speed by speed decay 
            spark[6] *= spark[7] # decrease lenght by mult of lngth decay 

            if spark[3] <= 0:
                self.sparks.remove(spark)
                continue
            points = [
                (spark[0][0] + math.cos(spark[1]) * spark[6], spark[0][1] + math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] + math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] + math.pi / 2) * spark[3]),
                (spark[0][0] - math.cos(spark[1]) * spark[6], spark[0][1] - math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] - math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] - math.pi / 2) * spark[3]),
            ]
            points = [(p[0] - self.offset[0], p[1] - self.offset[1]) for p in points]
            color = spark[8] if spark[8] else (247, 237, 186)
            pg.draw.polygon(self.display, color, points)

        # ------- PAINT
        if self.left_clicked:
            if self.player.paint > -10:
                if self.player.paint > 80:
                    self.add_paint(4, 3)
                    self.player.paint -= 1
                elif self.player.paint > 50:
                    self.add_paint(3, 3)
                    self.player.paint -= 1
                elif self.player.paint > 0:
                    self.add_paint(2, 2)
                    self.player.paint = max(0, self.player.paint - 1)
                else:
                    self.add_paint(1, .6)
        else:
            self.player.paint = min(100, self.player.paint + 1)

        # [ pos, angle, speed, width, width_decay, speed_decay, length, length_decay, col ]
        for i, spark, in enumerate(sorted(self.paints, reverse=true)):
            spark[0][0] += math.cos(spark[1]) * spark[2]
            spark[0][1] += math.sin(spark[1]) * spark[2]
            spark[3] -= spark[4] # sub width by decay 
            spark[2] *= spark[5] # decrase speed by speed decay 
            spark[6] *= spark[7] # decrease lenght by mult of lngth decay 

            if spark[1] > -math.pi/2 and spark[1] < 1.2:
                spark[1] += .1
            elif (spark[1] < -math.pi/2 and spark[1] > -4) or (spark[1] > 1.9):
                spark[1] -= .1
            color = (247, 237, 186) if not spark[8] else spark[8]

            if self.tile_map.tile_collide(spark[0].copy()):
                for i in range(3):
                    color = color
                    particle = ['paint', spark[0].copy(), [random.random() * 6 - 3, random.random() * 6 - 3], color, random.randrange(2, 3), random.uniform(.02, .06), 0]
                    self.circle_particles.append(particle)
                self.paints.remove(spark)
                continue

            if spark[3] <= 0:
                self.paints.remove(spark)
                continue
            points = [
                (spark[0][0] + math.cos(spark[1]) * spark[6]*.5, spark[0][1] + math.sin(spark[1]) * spark[6]*.5),
                (spark[0][0] + math.cos(spark[1] + math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] + math.pi / 2) * spark[3]),
                (spark[0][0] - math.cos(spark[1]) * spark[6], spark[0][1] - math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] - math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] - math.pi / 2) * spark[3]),
            ]
            points = [(p[0] - self.offset[0], p[1] - self.offset[1]) for p in points]
            pg.draw.polygon(self.display, color, points)

        # ------ CIRCLE_PARTICLES
        # [ type, pos, vel, color, size, decay, dur ]
        for p in self.circle_particles.copy():
            if p[0] == 'paint' or p[0] == 'fire_ball' or p[0] == 'blood':
                p[1][0] += p[2][0]
                if self.tile_map.tile_collide(p[1]):
                    p[1][0] -= p[2][0]
                    p[2][0] *= -0.7
                p[1][1] += p[2][1]
                if self.tile_map.tile_collide((p[1][0], p[1][1])):
                    p[1][1] -= p[2][1]
                    p[2][1] *= -0.7
                p[2][1] += .2  # gravity

            if p[0] == 'fire':
                p[1][0] += p[2][0]
                p[1][1] += p[2][1]

                if p[6] < 0.2:
                    p[4] += p[5]
                if p[6] < 0.4:
                    p[3] = (245, 237, 186)
                elif p[6] < 0.6:
                    p[3] = (228, 148, 58)
                elif p[6] < 0.9:
                    p[3] = (157, 48, 59)
                elif p[6] < 0.14:
                    p[3] = (62, 33, 55)
                else:
                    p[3] = (31, 14, 28)

                p[6] += p[5]

            if p[0] == 'fire_ball':
                particle = ['fire', p[1].copy(), [random.random() - .5, random.randrange(-4, -1)],
                            (10, 0, 0), random.randrange(6, 8), random.uniform(.12, .18), 0]
                self.circle_particles.append(particle)

            p[4] -= p[5]

            if p[4] < 1:
                self.circle_particles.remove(p)
            else:
                pg.draw.circle(
                    self.display, p[3], (p[1][0] - self.offset[0], p[1][1] - self.offset[1]), p[4])
                
        # -------- CIRCLES
        # [pos, speed, radius, width, decay, speed_decay, color ]
        for circle in self.circles.copy():
            pg.draw.circle(self.display, circle[6],
                           (circle[0][0] - self.offset[0], circle[0][1] - self.offset[1]), int(circle[2]), int(circle[3]))
            circle[2] += circle[1]
            circle[1] *= circle[5]
            circle[3] -= circle[4]
            if circle[3] < 1:
                self.circles.remove(circle)

        # ---------- UI ---------- #

        tutorial_text_0 = text_surface_1(f'LEVEL: {self.level}', 16, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
        tutorial_text_1 = text_surface_1(f'LEVEL: {self.level}', 16, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
        self.display.blit(tutorial_text_0, (10, 10))
        self.display.blit(tutorial_text_1, (10, 12))

        # ------------------ STATE HANDLER ------------------- # 
        if self.state == State.RUN:
            if self.player.dead:
                self.state = State.DEAD
            if self.level == 0:
                if self.player.pos[0] < 150:
                    text = text_surface_1(f"use mouse and right CliCk to fire paint", 8, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
                    text_1 = text_surface_1(f"use mouse and right CliCk to fire paint", 8, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
                    self.display.blit(text, (SCREEN_CENTER[0]-text.get_width()//2, SCREEN_CENTER[1]))
                    self.display.blit(text_1, (SCREEN_CENTER[0]-(text.get_width()//2)+2, SCREEN_CENTER[1]))
                elif self.player.pos[0] < 300:
                    text = text_surface_1(f"Reach Target to advanCe to next round", 8, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
                    text_1 = text_surface_1(f"Reach Target to advanCe to next round", 8, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
                    self.display.blit(text, (SCREEN_CENTER[0]-text.get_width()//2, SCREEN_CENTER[1]))
                    self.display.blit(text_1, (SCREEN_CENTER[0]-(text.get_width()//2)+2, SCREEN_CENTER[1]))

            pg.draw.rect(self.display, WHITE, (WIDTH-20, 10, 14, 42), 2)
            perc = self.player.paint / 100
            color = (14, 226, 50)
            if perc < .35:
                color = (220, 14, 60)
            elif perc < .60:
                color = (240, 230, 0)
            pg.draw.rect(self.display, color, (WIDTH-18, 12, 10, 38 * perc))

        elif self.state == State.TRANSIT:

            player_center = self.player.center()
            pg.draw.circle(self.display, BLACK, (player_center[0] - self.offset[0],
                        player_center[1] - self.offset[1]), int(self.transition[0]), self.transition[1])

            if self.transition[3] == 'closing':
                if self.transition[1] < self.transition[0]:
                    self.transition[1] += self.transition[2]
                    if self.transition[1] >= self.transition[0]:
                        self.reset(self.level)

                        self.offset[0] = (
                            (self.player.pos[0] - WIDTH // 2) - self.offset[0]) / 12
                        self.offset[1] = (
                            (self.player.pos[1] - HEIGHT // 2) - self.offset[1]) / 12

                        if self.offset[0] < self.edges[0]:
                            self.offset[0] = self.edges[0]
                        if self.offset[0] + WIDTH > self.edges[1]:
                            self.offset[0] = self.edges[1] - WIDTH

                        if self.offset[1] < self.edges[2]:
                            self.offset[1] = self.edges[2]
                        if self.offset[1] + HEIGHT > self.edges[3]:
                            self.offset[1] = self.edges[3] - HEIGHT
                        self.transition = [350, 1, 4, 'closing']
                        self.change_state(State.RUN)
                        
                        
                        #self.data.transition[3] = 'opening'
            #else:
            #    self.data.transition[1] -= self.data.transition[2]
            #    if self.data.transition[1] < 0:
            #        self.data.transition = [350, 1, 4, 'closing']
            #        self.data.e_handler.change_state(State.GAME_ON)

        elif self.state == State.DEAD:
            tutorial_text_0 = text_surface_1(f'GAME OVER', 28, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
            tutorial_text_1 = text_surface_1(f'GAME OVER', 28, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
            text_surf = pg.Surface((tutorial_text_0.get_width() + 4, tutorial_text_0.get_height()+10))
            text_surf.set_colorkey((0, 0, 0))
            text_surf.blit(tutorial_text_0, (0,0))
            text_surf.blit(tutorial_text_1, (0, 4))
            self.display.blit(text_surf, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()))

            reset_text = text_surface_1(f"press 'r' to reset game", 10, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
            reset_text_1 = text_surface_1(f"press 'r' to reset game", 10, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
            reset_text_flash = text_surface_1(f"press 'r' to reset game", 10, false, (255, 255, 255), font_path=self.fonts['pixel_0'])
            self.display.blit(reset_text, (SCREEN_CENTER[0]-reset_text.get_width()//2, SCREEN_CENTER[1]))
            self.display.blit(reset_text_1, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
            if math.sin(self.total_time) > 0:
                self.display.blit(reset_text_flash, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))

        elif self.state == State.PAUSE:
            pass
        elif self.state == State.START:
            pg.draw.rect(self.display, (0, 30, 80), (0, 0, WIDTH, HEIGHT))
            tutorial_text_0 = text_surface_1(f'PAINT RUN', 28, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
            tutorial_text_1 = text_surface_1(f'PAINT RUN', 28, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
            text_surf = pg.Surface((tutorial_text_0.get_width() + 4, tutorial_text_0.get_height()+10))
            text_surf.set_colorkey((0, 0, 0))
            text_surf.blit(tutorial_text_0, (0,0))
            text_surf.blit(tutorial_text_1, (0, 4))
            self.display.blit(text_surf, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()))

            reset_text = text_surface_1(f"press 's' to start", 10, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
            reset_text_1 = text_surface_1(f"press 's' to start", 10, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
            reset_text_flash = text_surface_1(f"press 's' to start", 10, false, (255, 255, 255), font_path=self.fonts['pixel_0'])
            self.display.blit(reset_text, (SCREEN_CENTER[0]-reset_text.get_width()//2, SCREEN_CENTER[1]))
            self.display.blit(reset_text_1, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
            if math.sin(self.total_time) > .2:
                self.display.blit(reset_text_flash, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
        elif self.state == State.WIN:
            pg.draw.rect(self.display, (0, 30, 80),(0, 0, WIDTH, HEIGHT))
            tutorial_text_0 = text_surface_1(f'YOU WIN!', 28, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
            tutorial_text_1 = text_surface_1(f'YOU WIN!', 28, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
            text_surf = pg.Surface((tutorial_text_0.get_width() + 4, tutorial_text_0.get_height()+10))
            text_surf.set_colorkey((0, 0, 0))
            text_surf.blit(tutorial_text_0, (0,0))
            text_surf.blit(tutorial_text_1, (0, 4))
            self.display.blit(text_surf, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()))

            reset_text = text_surface_1(f"press 'r' to reset game", 10, false, (178, 100, 255), font_path=self.fonts['pixel_0'])
            reset_text_1 = text_surface_1(f"press 'r' to reset game", 10, false, (100, 205, 255), font_path=self.fonts['pixel_0'])
            reset_text_flash = text_surface_1(f"press 'r' to reset game", 10, false, (255, 255, 255), font_path=self.fonts['pixel_0'])
            self.display.blit(reset_text, (SCREEN_CENTER[0]-reset_text.get_width()//2, SCREEN_CENTER[1]))
            self.display.blit(reset_text_1, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
            if math.sin(self.total_time) > .2:
                self.display.blit(reset_text_flash, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
        else:
            assert 0, f'ERROR STATE NOT FOUND {self.state}'

        # ---------- DISPLAY SCREENS ---------- #

        screenshake_offset = [0, 0]
        if self.screenshake > 0:
            self.screenshake -= 1
            screenshake_offset[0] = random.randrange(-8, 8)
            screenshake_offset[1] = random.randrange(-8, 8)
        disp_x = screenshake_offset[0]
        disp_y = screenshake_offset[1]

        self.display.blit(light_surf, (0, 0), special_flags=BLEND_RGBA_MULT)
        self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (disp_x, disp_y))

        pg.display.flip()
        pg.display.update()

    # ------------------- GAME FUNCS -------------------- #
    def game_on(self):
        return self.state == State.RUN
    
    def change_state(self, state):
        if self.state != state:
            self.state = state

    def test_init_func(self):
        for i in range(22):
            self.orbs.append([[random.randrange(10, WIDTH), random.randrange(10,HEIGHT)],
                              [random.uniform(-.6, .6), random.uniform(-.6, .6)],
                              1,
                              random.choice(['blue', 'indigo']),
                              inf
                              ])

        for i in range(18):
            self.bg_effects.append(
                [
                    [random.randrange(0,WIDTH), random.randrange(HEIGHT//4, HEIGHT-HEIGHT//4)],
                    [random.uniform(.6,1.2),1],
                    random.choice([0,len(bg_star_images)-1]),
                    random.uniform(.1, .3)
                ]
                )

    def add_paint(self, amount, scalar):
        # [ pos, angle, speed, width, width_decay, speed_decay, length, length_decay, col ]
        ang = math.atan2(self.mouse_pos[1]//2 - self.player.center()[1]-self.offset[1], self.mouse_pos[0]//2 - self.player.center()[0]+self.offset[0])
        for i in range(amount):
            # offset = random.uniform(-math.pi/6, math.pi/6)
            paint = [self.player.center(), 
                     ang, 
                     random.randrange(8, 11),
                     random.randrange(3, 5), 
                     .2,  # .2
                     0.9,
                     random.randrange(10, 12), 
                     0.90,
                     random.choice([(37, 255, 60), (37, 120, 250), (255, 37, 80), (250, 250, 50), (150, 50, 250)])]
            self.paints.append(paint)
        player_ang = math.atan2((self.player.center()[1]-self.offset[1]) - self.mouse_pos[1]//2, (self.player.center()[0]-self.offset[0]) - self.mouse_pos[0]//2)
        self.player.apply_force([math.cos(player_ang)*scalar,math.sin(player_ang)*scalar])

    def reset(self, level):
        self.level = level
        self.load_map(self.level)
        self.player.dead = false
        self.change_state(State.RUN)

    def update(self):
        self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps()}')
        self.dt = self.clock.tick(FPS)
        self.dt /= 1000

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_1:
                    pg.quit()
                    sys.exit()
                if e.key == pg.K_a:
                    self.inputs[0] = True
                if e.key == pg.K_d:
                    self.inputs[1] = True
                if e.key == pg.K_w:
                    self.inputs[2] = True
                    self.player.jump()
                if e.key == pg.K_s:
                   self.reset(3)
                if e.key == pg.K_p:
                    if self.state == State.PAUSE:
                        self.state = State.RUN
                    else:
                        self.state = State.PAUSE
                if e.key == pg.K_r:
                    self.reset(0)

            if e.type == pg.KEYUP:
                if e.key == pg.K_a:
                    self.inputs[0] = False
                if e.key == pg.K_d:
                    self.inputs[1] = False
                if e.key == pg.K_w:
                    self.inputs[2] = False

            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.left_clicked = True
                if e.button == 3:
                    self.right_clicked = True
            if e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.left_clicked = False
                if e.button == 3:
                    self.right_clicked = False


    def run(self):
        while True:
            self.check_inputs()
            self.render()
            self.update()


if __name__ == '__main__':
    
    app = App()
    app.run()
