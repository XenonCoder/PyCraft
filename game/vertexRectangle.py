#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
 ________                                        ______                       ______     __
|        \                                      /      \                     /      \   |  \ 
 \$$$$$$$$______    ______    ______   ______  |  $$$$$$\  ______   ______  |  $$$$$$\ _| $$_
   | $$  /      \  /      \  /      \ |      \ | $$   \$$ /      \ |      \ | $$_  \$$|   $$ \ 
   | $$ |  $$$$$$\|  $$$$$$\|  $$$$$$\ \$$$$$$\| $$      |  $$$$$$\ \$$$$$$\| $$ \     \$$$$$$
   | $$ | $$    $$| $$   \$$| $$   \$$/      $$| $$   __ | $$   \$$/      $$| $$$$      | $$ __
   | $$ | $$$$$$$$| $$      | $$     |  $$$$$$$| $$__/  \| $$     |  $$$$$$$| $$        | $$|  \ 
   | $$  \$$     \| $$      | $$      \$$    $$ \$$    $$| $$      \$$    $$| $$         \$$  $$
    \$$   \$$$$$$$ \$$       \$$       \$$$$$$$  \$$$$$$  \$$       \$$$$$$$ \$$          \$$$$


Copyright (C) 2013 Michael Fogleman
Copyright (C) 2018/2019 Stefano Peris <xenonlab.develop@gmail.com>

Github repository: <https://github.com/XenonLab-Studio/TerraCraft>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pyglet import graphics, gl


class VertexRectangle:
    """VertextRectangle which can be Drawn on Screen,

    I saw this first by nbroderick-code https://gist.github.com/codehearts/69162414fff28b29e984fde8b3905dde
    and changed some details to fit our needs
    """


    def __init__(self, x, y, width, height, color):
        """Create new Rectangle at the given Spot and with the given dimensions, 
        Colors are given in RGBA (r, g, b, a)

        for example: (45, 171, 196, 100) would be an blueish transparent color
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        r = color[0]
        g = color[1]
        b = color[2]
        a = color[3]
        self.vertex_list = graphics.vertex_list(4, 'v2f', 'c4B')
        self.vertex_list.vertices = (x, y,
                                   x + width, y,
                                   x + width, y + height,
                                   x, y + height)
        self.vertex_list.colors = (r, g, b, a,
                                   r, g, b, a,
                                   r, g, b, a,
                                   r, g, b, a)
        self.draw_mode = gl.GL_QUADS

    def draw(self):
        self.vertex_list.draw(self.draw_mode)

    def move_relative(self, dx, dy):
        self.__init__(self.x+dx, self.y+dy, self.width, self.height, self.color)

    def move_absolute(self, x, y):
        self.__init__(x, y, self.width, self.height, self.color)

    def width_absolute(self, w):
        self.__init__(self.x, self.y , w, self.height,
                      self.color)

    def height_absolute(self, h):
        self.__init__(self.x, self.y , self.width, h,
                self.color)

    def size_absolute(self, size):
        self.__init__(self.x, self.y , size[0], size[1],
            self.color)

    def width_relative(self, dw):
        self.__init__(self.x, self.y, self.width + dw, self.height,
                      self.color)