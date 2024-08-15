import pygame as pg
import os
import json
from .utils import read_f, get_image
from .settings import CELL_SIZE, ANIM_PATH

class Animation_Data:
    def __init__(self, path, type) -> None:
        self.type = type
        self.animations_data = {}
        self.animations = {}
        for anim in os.listdir(path):
            self.animations_data[anim] = {'images': [], 'config': None}
            full_path = f'{path}/{anim}/'
            for img in os.listdir(path + '/' + anim):
                if img.split('.')[-1] == 'png':
                    self.animations_data[anim]['images'].append(
                        get_image(full_path+img, [CELL_SIZE, CELL_SIZE]))
                else:
                    f = open(full_path + img, 'r')
                    config = json.loads(f.read())
                    f.close()
                    self.animations_data[anim]['config'] = config
        self.create_animations()

    def create_animations(self):
        for type, data in self.animations_data.items():
            images = data['images']
            config = data['config']
            self.animations[type] = Animation(type, images, config)

    def print_data(self):
        for k, j in self.animations.items():
            print(k)
            images = j['images']
            config = j['config']
            print('\t config')
            print('\t\t', config)
            print('\t images')
            for img in images:
                print('\t\t', img)

class Animation:
    def __init__(self, state, images, config) -> None:
        self.state = state
        self.images = images.copy()
        self.config = config
        self.time = 0
        self.frame = 0

    def update(self, dt):
        if len(self.images) > 1:
            self.frame %= len(self.images) - 1
            self.time += 1
            if self.time > self.config['frames'][self.frame]:
                self.frame += 1
                self.time = 0
        else:
            self.frame = 0

    def image(self):
        return self.images[self.frame]

    def copy(self):
        return Animation(self.state, self.images, self.config)

class Asset_Manager:
    def __init__(self) -> None:
        self.animations = {}
        self.get_animations()
    def get_animations(self):
        for anim_type in os.listdir(ANIM_PATH):
            anims = os.listdir(ANIM_PATH + anim_type)
            if anims:
                self.animations[anim_type] = Animation_Data(ANIM_PATH + anim_type, anim_type)

    def get_anim_data(self, type):
        if type in self.animations:
            return self.animations[type]
        assert 0, 'type not found, invalid type'
