import pygame as pg 
from enum import Enum
from .settings import CELL_SIZE, RED

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
        pg.draw.rect(surf, RED, (self.pos[0], self.pos[1], 5, 5))

    def rect(self) -> pg.Rect:
        return self.mouse_rect
