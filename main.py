import pygame as pg
import sys, random, math 
from pygame.locals import *
from src.settings import * 
from src.utils import * 
from src.tilemap import Tile_Map, decor_congif_id
from src.entities import Player
from src.asset_manager import *
from src.particles import * 

false = False
true = True
NULL = None
inf = float('inf')
n_inf = float('-inf')

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
    if not color:
        glow_img = light_masks[radius - 1]
    else:
        if color == 'blue':
            glow_img = light_masks_blue[radius - 1]
        elif color == 'indigo':
            glow_img = light_masks_yellow[radius - 1]
    surf.blit(glow_img, (pos[0], pos[1]), special_flags=BLEND_RGBA_ADD)

class App:
    def __init__(self) -> None:
        pg.init()
        self.screen: pg.display = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.dt: float = 0
        self.clock: pg.time = pg.time.Clock()
        # ------ GAME VARIABLES
        self.screenshake = 0 
        self.total_time = 0 
        self.mouse_pos = [0, 0]
        self.left_clicked = false 
        self.right_clicked = false 
        self.inputs = [false, false, false, false]
        self.bg = get_image(f'{IMG_PATH}bg.png', [WIDTH, HEIGHT])
        self.bg_2 = self.bg.copy()
        self.bg_pos = [0,0]
        self.bg_2_pos = [WIDTH,0]

        # -------- GAME SETTINGS 
        self.offset = [0,0]
        self.edges = [inf, n_inf, inf, n_inf]  # x, -x, y, -y

        # -------- PARTICLES 
        self.particles = []
        self.circles = []
        self.circle_particles = []
        self.sparks = []
        self.orbs = []
        self.bg_effects = []

        # -------- DATA INIT
        self.asset_manager = Asset_Manager()
        self.tile_map = Tile_Map(self)
        self.player = None
        self.load_map(1)
        self.test_init_func()
        load_stars(PARTS_PATH+'stars')

    def load_map(self, map_name):
        self.player = Player(self, [100,100], [CELL_SIZE, CELL_SIZE], 'player', True)
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
                self.edges[2] = y 
            if y > self.edges[3]:
                self.edges[3] = y + CELL_SIZE*2

    def render(self):

        # ----- SCREEN SETUP ----- #
        self.display.fill((12, 10, 18))
        light_surf = self.display.copy()
        light_surf.fill((125, 125, 125))

    
        self.total_time += 1

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
        # [pos, vel, type]
        for i, eff in enumerate(self.bg_effects):
            #eff[0][0] += eff[1][0]
            #eff[0][1] += eff[1][1]

            sine_offset = math.sin(eff[0][0] * 0.04) * .8  # Adjust 0.05 and 10 for frequency and amplitude
            eff[0][1] += 1

            img = star_images[eff[2]]
            self.display.blit(
                img, ((eff[0][0] - self.offset[0]) % WIDTH, (eff[0][1] - self.offset[1]) % HEIGHT))
            #glow(light_surf, (int(eff[0][0] - self.offset[0] - 20//2) % WIDTH, int(eff[0][1] - self.offset[1] - 20//2) % HEIGHT),20, 'blue')

        # --------- MAIN RENDER ACTIONS ---------- #

        layers = self.tile_map.get_visible_tiles(self.offset)
        for n, layer in layers.items():
            for tile in layer:
                real_pos = [tile[0][0] * CELL_SIZE, tile[0][1] * CELL_SIZE]
                img = tile[4]
                if tile[2] == 'decor':
                    img = scale_image(tile[4], decor_congif_id[tile[3]])

                self.display.blit(img, (real_pos[0] - self.offset[0], real_pos[1] - self.offset[1]))
    
        
        self.player.update(self.dt)
        self.player.render(self.display, self.offset)

        # ------------- PARTICLES ------------ #

        # [pos, vel, radius, color, dur]
        for i, p in enumerate(sorted(self.orbs, reverse=true)):
            p[0][0] += p[1][0]
            p[0][1] += p[1][1]
            color = (170,240, 250) if p[3] == 'blue' else (255, 240, 2)
            pg.draw.circle(self.display, color,
                           (int(p[0][0] - self.offset[0]) % WIDTH, int(p[0][1] - self.offset[1]) % HEIGHT), p[2])
            radius = 60
            radius2 = 20
            glow(light_surf, (int(p[0][0] - self.offset[0] - radius//2) % WIDTH, int(p[0][1] - self.offset[1] - radius//2) % HEIGHT), radius, p[3])
            glow(light_surf, (int(p[0][0] - self.offset[0] - radius2//2) % WIDTH, int(p[0][1] - self.offset[1] - radius2//2) % HEIGHT), radius2, p[3])
            if p[4] < 1:
                self.orbs.pop()
        
        # ---- NOTE TEST 
        glow(light_surf, (self.player.pos[0] - self.offset[0] - 200//2, self.player.pos[1] - self.offset[1] - 200//2), 200, false)
        
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

    def test_init_func(self):
        for i in range(22):
            self.orbs.append([[random.randrange(10, WIDTH), random.randrange(10,HEIGHT)],
                              [random.uniform(-.6, .6), random.uniform(-.6, .6)],
                              1,
                              random.choice(['blue', 'indigo']),
                              inf
                              ])

        for i in range(10):
            self.bg_effects.append(
                [
                    [i * random.randrange(14,18), random.randrange(50,160)],
                    [random.uniform(.6,1.2),1],
                    random.choice([0,1])
                ]
                )

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
                    pass

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
