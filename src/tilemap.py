import pygame as pg
import os, sys, json, copy
from enum import Enum
from .settings import *
from .utils import *
false = False
true = True

MAP_PATH = 'src/maps/'

decor_congif = {
    'bush': [16,16],
    'tree': [32,32],
}
decor_congif_id = {
    0: [16, 16],
    1: [32, 32],
}
hitable_tilesets = {'tileset_0', 'tileset_1', 'tileset_2'}

top_left = 0
top_center = 1
top_right = 2
mid_left = 3
mid_center = 4
mid_right = 5
bottom_left = 6
bottom_center = 7
bottom_right = 8

auto_tile_config: dict = {
    ((0, 1), (1, 0)): top_left,
    ((-1, 0), (0, 1), (1, 0)): top_center,
    ((-1, 0), (0, 1)): top_right,
    ((0, -1), (0, 1), (1, 0)): mid_left,
    ((-1, 0), (0, -1), (0, 1), (1, 0)): mid_center,
    ((-1, 0), (0, -1), (0, 1)): mid_right,
    ((0, -1), (1, 0)): bottom_left,
    ((-1, 0), (0, -1), (1, 0)): bottom_center,
    ((-1, 0), (0, -1)): bottom_right,
}

tile_offsets = [
    (1, 0), (-1, 0), (0, 1), (0, -1)
]

SURROUND_POS = [
    [-1, 0],
    [0, 0],
    [1, 0],
    [-1, -1],
    [0, -1],
    [1, -1],
    [-1, 1],
    [0, 1],
    [1, 1],
]
SURROUND_POS = []
for p in [[[x - 2, y - 2] for x in range(5)] for y in range(5)]:
    SURROUND_POS += p

def tuple_to_str(tuple):
    key = f'{tuple[0]},{tuple[1]}'
    return key

def str_to_tuple(str):
    key = str.split(',')
    return (int(key[0]), int(key[1]))

#TILE_PATH = 'src/assets/tiles/'
HIT_TILE_PATH = 'src/assets/tiles/tileset/'
OBJ_TILE_PATH = 'src/assets/tiles/objects/'

'''
    Tile Map: 
        - hash table
            - pos (x,y)
                - layers (-1,0,1) 
                    - tiles [pos, tile_type, tile_name, image_id, pg.image]
'''

class Tile_Map:
    def __init__(self, app) -> None:
        self.app = app
        self.tile_map = {}
        self.unhitable_tiles = {}
        self.enemies = []
        self.background_objects = []
        self.all_layers = []

    def render(self, surf, offset):
        for c in range(int(0 + offset[0] // CELL_SIZE) - 1, int((COLS*CELL_SIZE + offset[0]) // CELL_SIZE) + 2):
            for r in range(int(0 + offset[1] // CELL_SIZE) - 1, int((ROWS*CELL_SIZE + offset[1]) // CELL_SIZE) + 2):
                pos = (c, r)
                if pos in self.tile_map:
                    for layer, data in self.tile_map[pos].items():
                        surf.blit(data[3], ((int(pos[0]) * CELL_SIZE) - offset[0], (int(pos[1]) * CELL_SIZE) - offset[1]))

    def get_visible_tiles(self, offset):
        layers = {l: [] for l in self.all_layers}
        for c in range(int(0 + offset[0] // CELL_SIZE) - 1, int((COLS*CELL_SIZE + offset[0]) // CELL_SIZE) + 2):
            for r in range(int(0 + offset[1] // CELL_SIZE) - 1, int((ROWS*CELL_SIZE + offset[1]) // CELL_SIZE) + 2):
                pos = (c, r)
                if pos in self.tile_map:
                    for layer, data in self.tile_map[pos].items():
                        tile_data = [pos] + data
                        layers[layer].append(tile_data)
        return layers

    def load_map(self, map):
        res_data = {}
        unhitable_tiles = {}
        enemies = []
        all_layers: set = set()

        path = f'{MAP_PATH}{map}.json'
        fl = open(path, 'r')
        map_data = json.load(fl)
        fl.close()

        for k, layers in map_data['tile_map'].items():
            key = str_to_tuple(k)
            res_data[key] = {}
            unhitable_tiles[key] = {}
            for layer, tile in layers.items():
                if tile[0] == 'objects':
                    print('object: ', tile)
                else:
                    if tile[1] == 'decor':
                        if tile[2] == 2:
                            tile[3] = get_image(tile[3], [CELL_SIZE*1.5, CELL_SIZE*1.5])
                        else:
                            tile[3] = get_image(tile[3], [CELL_SIZE, CELL_SIZE])
                    else:
                        tile[3] = get_image(tile[3], [CELL_SIZE, CELL_SIZE])
                    res_data[key][layer] = tile
            for layer in res_data[key]:
                all_layers.add(layer)
            if len(res_data[key]) == 0:
                del res_data[key]
            if len(unhitable_tiles[key]) == 0:
                del unhitable_tiles[key]

        self.tile_map = res_data  # map_data['tile_map']
        self.unhitable_tiles = unhitable_tiles

        sorted_layer_list = list(all_layers)
        sorted_layer_list.sort()
        self.all_layers = sorted_layer_list

        self.enemies = enemies

    def get_surrounding_tiles(self, pos):
        tiles = []
        pos = [pos[0] // CELL_SIZE, pos[1] // CELL_SIZE]
        for offset in SURROUND_POS:
            key = (pos[0] + offset[0], pos[1] + offset[1])
            if key in self.tile_map:
                for layer in self.tile_map[key]:
                    if self.tile_map[key][layer][1] != 'decor' and self.tile_map[key][layer][1][:2] != 'bg':
                        tiles.append(
                            pg.Rect(key[0] * CELL_SIZE, key[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        return tiles

    def get_nearby_rects(self, pos):
        p = [pos[0] // CELL_SIZE, pos[1] // CELL_SIZE]
        tiles = []
        for offset in SURROUND_POS:
            key = (p[0] + offset[0], p[1] + offset[1])
            if key in self.tile_map:
                tiles.append(
                    pg.Rect(key[0] * CELL_SIZE, key[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        return tiles

    def tile_collide(self, pos):
        tile_pos = (int(pos[0] // CELL_SIZE), int(pos[1] // CELL_SIZE))
        if tile_pos in self.tile_map:
            for layer, tile in self.tile_map[tile_pos].items():
                if tile[1] in hitable_tilesets:
                    return True
        return False


# ------------------------- LEVEL EDITOR ------------------------- #

class Level_Editor:
    def __init__(self, app) -> None:
        self.app = app
        self.tile_data = []
        self.tile_map = Tile_Map(self)
        self.layers = set()
        self.get_tile_data()

    def render(self, surf, offset):
        for c in range(int(0 + offset[0] // CELL_SIZE) - 1, int((COLS*CELL_SIZE + offset[0]) // CELL_SIZE) + 2):
            for r in range(int(0 + offset[1] // CELL_SIZE) - 1, int((ROWS*CELL_SIZE + offset[1]) // CELL_SIZE) + 2):
                pos = (c, r)
                if pos in self.tile_map.tile_map:
                    for layer, data in self.tile_map.tile_map[pos].items():
                        img = data[3]
                        #img = get_image(data[3], [CELL_SIZE, CELL_SIZE])
                        if data[1] == 'decor':
                            img = scale_image(data[3], decor_congif_id[data[2]])
                        surf.blit(img, ((int(pos[0]) * CELL_SIZE) - offset[0], (int(pos[1]) * CELL_SIZE) - offset[1]))

    # --------- CREATING TILE MAP FUNCS -------- #

    def save_map(self):
        new_tile_map = {}
        layers_found = set()

        for pos, layers in self.tile_map.tile_map.items():
            layers_copy = {}
            for k,tile in layers.items():
                layers_copy[k] = [tile[0], tile[1], tile[2], f'src/assets/tiles/{tile[0]}/{tile[1]}/{tile[2]}.png']

            new_tile_map[tuple_to_str(pos)] = layers_copy
            for layer in layers:
                layers_found.add(layer)
                
        layers = []
        for l in layers_found:
            layers.append(l)

        ln = len(os.listdir(MAP_PATH))
        path = f'{MAP_PATH}/{ln}.json'
        fl = open(path, 'w')
        json.dump({
            'all_layers': layers,
            'tile_map': new_tile_map
        }, fl)
        fl.close()
        for k, val in new_tile_map.items():
            print(val)

    def save_edited_map(self, num):
        new_tile_map = {}
        layers_found = set()

        for pos, layers in self.tile_map.tile_map.items():
            new_tile_map[tuple_to_str(pos)] = layers
            for layer in layers:
                layers_found.add(layer)

        layers = []
        for l in layers_found:
            layers.append(l)

        path = f'{MAP_PATH}/{num}.json'
        fl = open(path, 'w')
        json.dump({
            'all_layers': layers,
            'tile_map': new_tile_map
        }, fl)
        fl.close()

    def save_to_json(self):
        pass

    def json_to_dict(self):
        pass

    # -------- TILE EDITOR FUNCS ------- #
    def add_tile(self, pos, tile_data, layer):
        key = tuple(pos)
        if layer not in self.layers:
            self.layers.add(layer)
        if key not in self.tile_map.tile_map:
            self.tile_map.tile_map[key] = {}
            self.tile_map.tile_map[key][layer] = tile_data
        self.tile_map.tile_map[key][layer] = tile_data

    def remove_tile(self, pos, layer):
        key = tuple(pos)
        if key in self.tile_map.tile_map:
            if layer in self.tile_map.tile_map[key]:
                del self.tile_map.tile_map[key][layer]
                if len(self.tile_map.tile_map[key]) == 0:
                    del self.tile_map.tile_map[key]

    def auto_tile(self, starting_pos, tileset_imgs, layer):
        v = set()
        key = tuple(starting_pos)
        if key not in self.tile_map.tile_map:
            print('pos not in tile map')
            return
        if layer not in self.tile_map.tile_map[key]:
            print('pos in tile map, but incorrect layer')
            return

        def dfs(pos, v: set):
            if pos in v:
                return
            v.add(pos)
            nearby_tiles = []
            neighbors = []
            for offset in tile_offsets:
                search_pos = (pos[0] + offset[0], pos[1] + offset[1])
                if search_pos in self.tile_map.tile_map and layer in self.tile_map.tile_map[search_pos]:
                    nearby_tiles.append(offset)
                    neighbors.append(search_pos)
            auto_tile_key = tuple(sorted(nearby_tiles))
            if auto_tile_key in auto_tile_config:
                tile_imgs = sorted(tileset_imgs)
                self.tile_map.tile_map[pos][layer][3] = get_image(tile_imgs[auto_tile_config[auto_tile_key]], [CELL_SIZE,CELL_SIZE])
                self.tile_map.tile_map[pos][layer][2] = auto_tile_config[auto_tile_key]
            for n in neighbors:
                dfs(n, v)
        dfs(key, v)

    def tile_editor_display(self, surf, mouse_rect):
        pg.draw.rect(surf, (180, 180, 180), (0, 0, 200, HEIGHT))

    # -------- GET DATA --------- #
    def get_tile_data(self):
        tile_types = os.listdir(TILE_PATH)
        for i in range(len(tile_types)):
            tile_type = tile_types[i]
            tile_names = os.listdir(TILE_PATH + tile_type)
            for j in range(len(tile_names)):
                tile_name = tile_names[j]
                full_tile_name_path = f'{TILE_PATH}{tile_type}/{tile_name}'
                images = []
                for tile_id in os.listdir(full_tile_name_path):
                    if tile_id.split('.')[-1] == 'png':
                        full_tile_img_path = f'{full_tile_name_path}/{tile_id}'
                        images.append(full_tile_img_path)
                self.tile_data.append([tile_type, tile_name, images])
