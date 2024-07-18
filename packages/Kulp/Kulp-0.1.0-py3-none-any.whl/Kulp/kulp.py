import logging
from typing import Tuple

import pygame as pg
from pygame.locals import *

from Kulp.kulp_gfx import Rectangle


class Color:
    RED: pg.color.Color = pg.color.Color(255, 0, 0)
    YELLOW: pg.color.Color = pg.color.Color("yellow")
    GREEN: pg.color.Color = pg.color.Color(0, 255, 0)
    BLUE: pg.color.Color = pg.color.Color(0, 0, 255)
    BLACK: pg.color.Color = pg.color.Color(0, 0, 0)
    WHITE: pg.color.Color = pg.color.Color(255, 255, 255)


class Key:
    SPACE = pg.K_SPACE
    LEFT_ALT = pg.K_LALT
    RIGHT_ALT = pg.K_RALT
    LEFT_CONTROL = pg.K_LCTRL
    RIGHT_CONTROL = pg.K_RCTRL
    LEFT_SHIFT = pg.K_LSHIFT
    RIGHT_SHIFT = pg.K_RSHIFT
    BACKSPACE = pg.K_BACKSPACE
    RETURN = pg.K_RETURN
    ESCAPE = pg.K_ESCAPE
    TAB = pg.K_TAB
    RIGHT_ARROW = pg.K_RIGHT
    LEFT_ARROW = pg.K_LEFT
    UP_ARROW = pg.K_UP
    DOWN_ARROW = pg.K_DOWN

    @staticmethod
    def char(c: str):
        try:
            return globals()[f"K_{c.lower()}"]
    
        except Exception as e:
            logging.log(logging.CRITICAL, "Could not find key.")
            quit(0)


class GameWindow:
    def __init__(self, title: str, size: Tuple[int, int], background_color=Color.BLACK, fps: int = 60):
        self._window = pg.display.set_mode(size)
        pg.display.set_caption(title)
        self.fps = fps
        self.bg = background_color

        self._update = None
        self._key = None

    def on_update(self, func):
        def wrap():
            self._update = func

        wrap()

    def on_key(self, func):
        def wrap():
            self._key = func

        wrap()

    def draw_rect(self, rect: Rectangle):
        pg.draw.rect(self._window, rect.color, rect._get())

    def start(self):
        running: bool = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit(0)

                elif event.type == pg.KEYDOWN:
                    if self._key:
                        self._key(event.key)

            self._window.fill(self.bg)
            if self._update:
                self._update()

            pg.display.flip()
            pg.time.Clock().tick(self.fps)
