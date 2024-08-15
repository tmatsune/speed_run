import os 
from .settings import * 
from .utils import * 

global bg_star_images, star_images
bg_star_images = []
star_images = {}


def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3


def load_background_effects(path):
    global bg_effects_images
    colors = [(0,99,190), ()]

def load_bg_images(path):
    global bg_star_images
    image_list = os.listdir(path)
    image_list.sort()
    for img in image_list:
        bg_star_images.append(get_image(path + f'/{img}',[CELL_SIZE//1.4, CELL_SIZE//1.4]))

def load_stars(path):
    global star_images
    file_list = os.listdir(path)
    img = get_image(path + '/' + '1.png', [CELL_SIZE//2, CELL_SIZE//2])
    for i in range(2):
        color = (178, 240, 250) if random.randint(0,1) == 0 else (220,180,255)
        img = color_swap_image(img, (255, 255, 255), color)
        star_images[i] = img

    #for star in file_list:

    

class Particle:
    def __init__(self) -> None:
        pass