import sys
from enum import Enum
from src.tilemap import *
from src.settings import *
from src.utils import *

false = False
true = True

class Click(Enum):
    NONE = 0
    JUST_PRESSED = 1
    PRESSED = 2
    JUST_RELEASED = 3

class Mouse:
    def __init__(self, app) -> None:
        self.app = app
        self.left_click = Click.NONE
        self.right_click = Click.NONE
        self.pos = [0, 0]
        self.tile_pos = [0, 0]
        self.mouse_rect = pg.Rect(0, 0, 5, 5)

    def update(self):
        self.tile_pos = [self.pos[0] // CELL_SIZE, self.pos[1] // CELL_SIZE]
        self.handle_click()
        self.mouse_rect = pg.Rect(self.pos[0], self.pos[1], 5, 5)

    def handle_click(self):
        # ---- LEFT CLICK ---- #
        if self.app.left_clicked and self.left_click == Click.JUST_PRESSED:
            self.left_click = Click.PRESSED
        if self.app.left_clicked and self.left_click == Click.NONE:
            self.left_click = Click.JUST_PRESSED
        if not self.app.left_clicked:
            if (self.left_click == Click.PRESSED or self.left_click == Click.JUST_PRESSED):
                self.left_click = Click.JUST_RELEASED
            elif self.left_click == Click.JUST_RELEASED:
                self.left_click = Click.NONE
        # ---- RIGHT CLICK ---- #
        if self.app.right_clicked and self.right_click == Click.JUST_PRESSED:
            self.right_click = Click.PRESSED
        if self.app.right_clicked and self.right_click == Click.NONE:
            self.right_click = Click.JUST_PRESSED
        if not self.app.right_clicked:
            if (self.right_click == Click.PRESSED or self.right_click == Click.JUST_PRESSED):
                self.right_click = Click.JUST_RELEASED
            elif self.right_click == Click.JUST_RELEASED:
                self.right_click = Click.NONE

    def render(self, surf):
        pg.draw.rect(surf, RED, (self.pos[0], self.pos[1], 3, 3))

    def rect(self) -> pg.Rect:
        return self.mouse_rect


class Tile_Editor:
    def __init__(self) -> None:
        pg.init()
        self.screen: pg.display = pg.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.dt: float = 0
        self.clock: pg.time = pg.time.Clock()
        self.inputs = [False, False, False, False]
        self.left_clicked = False
        self.right_clicked = False
        self.offset = [0, 0]

        # ----- TILE MODES ----- #
        self.hitable = True
        self.is_object = True
        self.save_map_window = False
        self.layer = 0                  # mutiple layers, for every layer, have one or more tiles
        self.can_place_tile = False
        self.load_map_mode = true
        # ---------------------- #
        self.tile_index = 0
        self.tile_img_index = 0
        self.curr_map_id = -1

        self.mouse = Mouse(self)
        self.level_editor = Level_Editor(self)
        self.curr_tile = None

        pg.mouse.set_visible(False)

    def render(self):

        self.display.fill((0, 0, 0))

        # ----- MOUSE ---- #
        mouse_pos = pg.mouse.get_pos()
        self.mouse.pos = [mouse_pos[0]//2, mouse_pos[1]//2]

        self.mouse.update()
        mouse_rect = self.mouse.rect()

        # --------- CURR TILE --------- #
        if self.tile_index > 0:
            self.tile_index %= len(self.level_editor.tile_data)

        if self.can_place_tile:
            self.curr_tile = self.level_editor.tile_data[self.tile_index]
            tile_type = self.curr_tile[0]
            tile_name = self.curr_tile[1]

            tile_type_text = text_surface(f'type: {tile_type}', 10, False, WHITE)
            self.display.blit(tile_type_text, [WIDTH - tile_type_text.get_width() - 10, 10])

            tile_name_text = text_surface(f'type: {tile_name}', 10, False, WHITE)
            self.display.blit(tile_name_text, [WIDTH - tile_name_text.get_width() - 10, 30])

            tile_id_text = text_surface(f'type: {self.tile_img_index}', 10, False, WHITE)
            self.display.blit(tile_id_text, [WIDTH - tile_id_text.get_width() - 10, 50])

            tile_images = self.curr_tile[2]
            self.tile_img_index %= len(tile_images) if len(tile_images) > 1 else 1

            img_offset = [0, 0]
            if self.tile_img_index > -1 and self.tile_img_index < len(tile_images):
                img = get_image(tile_images[self.tile_img_index], [CELL_SIZE, CELL_SIZE])
                if tile_name == 'decor':
                    img_id_png = tile_images[self.tile_img_index].split('/')
                    img_id = img_id_png[-1].split('.')[0]
                    
                    if img_id == '1':
                        img = get_image(tile_images[self.tile_img_index], decor_congif_id[int(img_id)])
                elif tile_name == 'buildings':
                    img = get_image(tile_images[self.tile_img_index], [CELL_SIZE*1, CELL_SIZE*4])
                
                if tile_name == 'tileset_2':
                    img = color_swap_image(get_image(tile_images[self.tile_img_index], [
                                           CELL_SIZE, CELL_SIZE]), (255,255,255),(0, 250, 0))

                self.display.blit(img, (
                    (self.mouse.tile_pos[0] * CELL_SIZE) - img_offset[0],
                    (self.mouse.tile_pos[1] * CELL_SIZE) - img_offset[1])
                )
                pg.draw.rect(self.display, WHITE, (
                    self.mouse.tile_pos[0] * CELL_SIZE, self.mouse.tile_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # --------- MAIN RENDER ACTIONS ---------- #

        if self.save_map_window:
            self.level_editor.tile_editor_display(self.display, mouse_rect)

        self.offset[0] += (self.inputs[1] - self.inputs[0]) * CELL_SIZE
        self.offset[1] += (self.inputs[3] - self.inputs[2]) * CELL_SIZE
        self.level_editor.render(self.display, self.offset)

        # --------- ADDING/REMOVING TILES --------- #

        if self.can_place_tile:
            tile_pos = [(self.mouse.pos[0] + self.offset[0]) // CELL_SIZE,
                        (self.mouse.pos[1] + self.offset[1]) // CELL_SIZE]
            if self.mouse.right_click == Click.JUST_PRESSED:
                self.level_editor.remove_tile(tile_pos, self.layer)
            if self.mouse.left_click == Click.JUST_PRESSED or self.mouse.left_click == Click.PRESSED:
                self.curr_tile[2].sort()
                img = get_image(self.curr_tile[2][self.tile_img_index], [CELL_SIZE, CELL_SIZE])
                self.level_editor.add_tile(tile_pos, [self.curr_tile[0], self.curr_tile[1], self.tile_img_index, img, self.curr_tile[2][self.tile_img_index]], self.layer, )

        # ------------ RENDER TEXT ------------- #

        layer_text = text_surface(f'layer: {self.layer}', 10, False, WHITE)
        self.display.blit(layer_text, [10, 10])

        hitable = self.hitable
        hitable_text = text_surface(
            f'hitable: { "True" if hitable else "False" }', 10, False, WHITE)
        self.display.blit(hitable_text, [10, 30])

        is_object = self.is_object
        object_text = text_surface(
            f'is object: { "True" if is_object else "False" }', 10, False, WHITE)
        self.display.blit(object_text, [10, 50])

        can_place_tile = self.can_place_tile
        object_text = text_surface(
            f'tile mode: { "Tile Mode" if can_place_tile else "Observe Mode" }', 10, False, WHITE)
        self.display.blit(object_text, [10, 70])

        # ------------ BLIT DISPLAYS ------------- #

        self.mouse.render(self.display)
        self.screen.blit(pg.transform.scale(
            self.display, self.screen.get_size()), (0, 0))
        pg.display.flip()
        pg.display.update()

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
                if pg.K_0 <= e.key <= pg.K_9:
                    number_pressed = e.key - pg.K_0
                    if self.load_map_mode:
                        self.level_editor.tile_map.load_map(number_pressed)
                    else:
                        self.curr_map_id = number_pressed

                if e.key == pg.K_a:
                    self.tile_index -= 1
                if e.key == pg.K_d:
                    self.tile_index += 1
                if e.key == pg.K_w:
                    self.tile_img_index += 1
                if e.key == pg.K_s:
                    self.tile_img_index -= 1
                if e.key == pg.K_e:
                    self.layer += 1
                if e.key == pg.K_q:
                    self.layer -= 1

                if e.key == pg.K_v:
                    self.hitable = not self.hitable
                if e.key == pg.K_b:
                    self.is_object = not self.is_object
                if e.key == pg.K_m:
                    self.level_editor.save_map()
                if e.key == pg.K_n:
                    self.level_editor.save_edited_map(self.curr_map_id)
                if e.key == pg.K_c:
                    self.can_place_tile = not self.can_place_tile

                if e.key == pg.K_f:
                    if self.curr_tile:
                        tile_pos = [(self.mouse.pos[0] + self.offset[0]) // CELL_SIZE,
                                    (self.mouse.pos[1] + self.offset[1]) // CELL_SIZE]
                        self.level_editor.auto_tile(
                            tile_pos, self.curr_tile[2], self.layer)
                        
                if e.key == pg.K_LEFT:
                    self.inputs[0] = True
                if e.key == pg.K_RIGHT:
                    self.inputs[1] = True
                if e.key == pg.K_UP:
                    self.inputs[2] = True
                if e.key == pg.K_DOWN:
                    self.inputs[3] = True

            if e.type == pg.KEYUP:
                if e.key == pg.K_LEFT:
                    self.inputs[0] = False
                if e.key == pg.K_RIGHT:
                    self.inputs[1] = False
                if e.key == pg.K_UP:
                    self.inputs[2] = False
                if e.key == pg.K_DOWN:
                    self.inputs[3] = False

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
    app = Tile_Editor()
    app.run()
