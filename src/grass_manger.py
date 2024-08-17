import pygame as pg 
import os, math, random
from copy import deepcopy
from .settings import IMG_PATH, CELL_SIZE, COLS, ROWS, WHITE, SKY_BLUE
from .utils import get_image, distance

true=True
false=False

global grass_images
grass_images = []

# when player is close to grass, check grass tile_map to see which tiles are to be bent and by how much 

def load_grass_images(path):
    imgs = os.listdir(path)
    imgs.sort()
    for img in imgs:
        grass_images.append(get_image(f'{path}/{img}', [CELL_SIZE//2, CELL_SIZE//2]))

class Grass_Manager:
    def __init__(self, app) -> None:
        self.app = app  
        self.grass_tiles = {}
        self.grass_cache = {}
        load_grass_images(IMG_PATH + 'grass')
    
    def render(self, surf, offset=[0,0]):
        pass
    def apply_force(self):
        pass

class Grass_Tile:
    def __init__(self, grass_manager, pos) -> None:
        self.grass_manager = grass_manager
        self.blades = [] # [id, image_id, angle]
        self.pos = pos.copy()
        self.real_pos = [self.pos[0]*CELL_SIZE, self.pos[1]*CELL_SIZE]
        self.hit_by_player = false
        for i in range(6):
            self.blades.append( [i, random.randint(0, len(grass_images)-1), 180])

    def render(self, surf, rot, offset=[0,0]):
        p_pos = self.grass_manager.app.player.center()

        for blade in self.blades:
            #blade[2] = 180 + rot*4
            
            pivot = ((self.pos[0])*CELL_SIZE, (self.pos[1])*CELL_SIZE)
            rot_offset = pg.math.Vector2(0, 6)
            img = grass_images[blade[1]]
            flipped_image = pg.transform.flip(img, false, true)
            rotated_image = pg.transform.rotozoom(flipped_image, -blade[2], 1)
            rotated_offset = rot_offset.rotate(blade[2])
            rect = rotated_image.get_rect(center=pivot+rotated_offset)
            surf.blit(rotated_image, ((rect.x - offset[0]) + blade[0]*2, (rect.y - offset[1]) + 17))
            
            blade_pos = [pivot[0] + blade[0]*2 + 1, pivot[1]+18]
            dist_from_player = distance(p_pos, blade_pos)
            
            if dist_from_player < 16:
                blade[2] = 180 + ((24 - dist_from_player) * 2) if p_pos[0] < blade_pos[0] else 180 - ((24 - dist_from_player) * 2)
            elif blade[2] != 180:
                if blade[2] < 180: blade[2] += 1
                else: blade[2] -= 1
                if 180 - abs(blade[2]) < 1: blade[2] = 180
            #pg.draw.circle(surf, WHITE, (blade_pos[0] - offset[0], blade_pos[1] - offset[1]), 1)

    def update(self, wind_time):
        pass

''' ---- rotate around axis --- #
self.angle += 6
pivot = self.center()
offset = pg.math.Vector2(CELL_SIZE//8, CELL_SIZE//2)
flipped_image = pg.transform.flip(img, false, true)
rotated_image = pg.transform.rotozoom(flipped_image, -self.angle, 1)
rotated_offset = offset.rotate(self.angle)
rect = rotated_image.get_rect(center=pivot+rotated_offset)
surf.blit(rotated_image, rect)
'''
