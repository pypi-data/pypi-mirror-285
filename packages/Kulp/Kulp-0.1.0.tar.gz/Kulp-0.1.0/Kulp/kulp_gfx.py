import pygame as pg


class Rectangle:
    def __init__(self, x, y, width, height, color=pg.color.Color(255, 255, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def collides(self, other) -> bool:
        """

        :type other: Rectangle
        """
        return self._get().colliderect(other._get())

    def _get(self):
        return pg.Rect(self.x, self.y, self.width, self.height)