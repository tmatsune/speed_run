import pygame as pg
import math, random
false = False
true = True

def get_image(path: str, scale: list, color=None) -> pg.image:
    img: pg.image = pg.image.load(path)
    img = pg.transform.scale(img, (scale[0], scale[1])).convert_alpha()
    if color:
        img = img.set_colorkey(color)
    return img

def load_img(path):
    img = pg.image.load(path)
    return img

def scale_image(img, scale):
    return pg.transform.scale(img, (scale[0], scale[1]))

def color_swap_image(img, old_color, color):
    img = img.copy()  # Create a copy of the image to avoid modifying the original
    img.set_colorkey(old_color)  # Set the color to be swapped as transparent
    pixel_array = pg.PixelArray(img)
    pixel_array.replace(old_color, color)
    img = pixel_array.surface

    return img

def read_f(path):
    f = open(path, 'r')
    dat = f.read()
    f.close()
    return dat

def write_f(path, dat):
    f = open(path, 'w')
    f.write(dat)
    f.close()

def swap_color(img, old_c, new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf

def silhouette(surf, color=(255, 255, 255)):
    mask = pg.mask.from_surface(surf)
    new_surf = swap_color(mask.to_surface(), (255, 255, 255), color)
    new_surf.set_colorkey((0, 0, 0))
    return new_surf

def outline(target, src, pos, color):
    s = silhouette(src, color=color)
    for shift in [[0, 1], [1, 0], [-1, 0], [0, -1]]:
        target.blit(s, (pos[0] + shift[0], pos[1] + shift[1]))

def text_surface(text: str, size: int, italic: bool, rgb: tuple, font='arial', bold=True):
    font = pg.font.SysFont(font, size, bold, italic)
    text_surface = font.render(text, False, rgb)
    return text_surface

def text_surface_1(text: str, size: int, italic: bool, rgb: tuple, font_path=None, bold=True):
    if font_path: font = pg.font.Font(font_path, size) 
    else: font = pg.font.SysFont('arial', size, bold, italic)  
    if bold: font.set_bold(True)
    if italic: font.set_italic(True)
    text_surface = font.render(text, False, rgb)
    return text_surface

def render_text_box(surf, pos: list, size: list[int], color: tuple, hollow: int = 0):
    pg.draw.rect(surf, color, (pos[0], pos[1], size[0], size[1]), hollow)

def distance(a, b):
    return math.sqrt(math.pow(abs(a[0] - b[0]), 2) + math.pow(a[1] - b[1], 2))

def rand_rad_angle(scalar):
    return random.uniform(-math.pi/scalar, math.pi/scalar)

def mask_collision(mask1, a, mask2, b): return mask2.overlap(mask1, (a[0] - b[0], a[1] - b[1]))

def text_3d(text, size, italic, rgb0, rgb1, offset, font_path=None, bold=True):
    text_0 = text_surface_1(text, size, bold, rgb0, font_path=font_path)
    text_1 = text_surface_1(text, size, bold, rgb1, font_path=font_path)
    text_surf = pg.Surface((text_0.get_width() + 10, text_0.get_height() + 10))
    text_surf.set_colorkey((0, 0, 0))
    text_surf.blit(text_0, (0,0))
    text_surf.blit(text_1, (offset[0], offset[1]))
    return text_surf




'''
paralax
 self.display.blit(self.bg_2, (self.bg_2_pos[0], 0))
        self.display.blit(self.bg, (self.bg_pos[0],0))
        self.bg_pos[0] -= 20 
        self.bg_2_pos[0] -= 20
        if self.bg_pos[0] == -WIDTH: self.bg_pos[0] = WIDTH
        if self.bg_2_pos[0] == -WIDTH: self.bg_2_pos[0] = WIDTH


'''