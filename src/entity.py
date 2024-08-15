import pygame as pg
from .utils import *
from .settings import CELL_SIZE

false = False
true = True

class Entity:
    def __init__(self, app, pos, size, type, animated=False) -> None:
        self.app = app
        self.pos = pos.copy()
        self.size = size.copy()
        self.type = type
        self.state = 'idle'
        self.angle = 0
        self.centered = False
        self.animated = animated
        self.tile_pos = [0, 0]
        if animated:
            self.animation_data = app.asset_manager.get_anim_data(type)
            self.anim = self.animation_data.animations[self.state].copy()

    def rect(self):
        if self.centered:
            return pg.Rect(self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2, self.size[0], self.size[1])
        else:
            return pg.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def center(self):
        return [self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2]

    def change_state(self, state):
        if self.state != state:
            self.state = state
            self.anim = self.animation_data.animations[state].copy()

    def render(self, surf, offset=[0, 0]):
        offset = offset.copy()
        if self.anim.config['offset']:
            offset[0] += self.anim.config['offset'][0]
            offset[1] += self.anim.config['offset'][1]
        img = self.anim.image()
        if self.anim.config['outline']:
            outline(surf, self.anim.image(), ((self.pos[0] - offset[0]) // 1, (self.pos[1] - offset[1]) // 1), self.anim.config['outline'])
        surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def update(self, dt):
        if self.animated:
            self.anim.update(dt)

    def get_tile_hits(self, rect, tiles):
        hits = []
        for tile in tiles:
            if rect.colliderect(tile):
                hits.append(tile)
        return hits

    def movement(self, vel, tiles):
        self.pos[0] += vel[0]
        hitable_tiles = self.get_tile_hits(self.rect(), tiles)
        curr_rect = self.rect()
        directions = {'left': False, 'right': False, 'up': False, 'down': False}

        for tile in hitable_tiles:
            if vel[0] > 0:
                curr_rect.right = tile.left
                self.pos[0] = curr_rect.left
                directions['right'] = True
            elif vel[0] < 0:
                curr_rect.left = tile.right
                self.pos[0] = curr_rect.left
                directions['left'] = True

        self.pos[1] += vel[1]
        hitable_tiles = self.get_tile_hits(self.rect(), tiles)
        curr_rect = self.rect()
        for tile in hitable_tiles:
            if vel[1] > 0:
                curr_rect.bottom = tile.top
                self.pos[1] = curr_rect.y
                directions['down'] = True
            if vel[1] < 0:
                curr_rect.top = tile.bottom
                self.pos[1] = curr_rect.y
                directions['up'] = True
        return directions
