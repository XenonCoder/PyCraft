#!/bin/python3

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

import random
import time
import pyglet
import os

from collections import deque

from pyglet.gl import *
from pyglet.media import Player
from pyglet.window import key, mouse
from pyglet.sprite import Sprite
from pyglet.graphics import OrderedGroup

from .blocks import *
from .inventory import *
from .utilities import *
from .graphics import BlockGroup
from .genworld import *
from .vertexRectangle import *


class Inventory(object):

    def __init__(self, selectedBlock, window):
        """A class for Inventory
        """
        self.selectedBlock = selectedBlock
        self.window = window

        # List of all Blocks in the Game 
        self.blockList = [DIRT, DIRT_WITH_GRASS, SAND, SNOW, COBBLESTONE,
                          BRICK_COBBLESTONE, BRICK, TREE, LEAVES, WOODEN_PLANKS]

        self.tempInventory = pyglet.text.Label('', font_name='Arial', font_size=INFO_LABEL_FONTSIZE,
                                    x=10, y=INFO_LABEL_FONTSIZE+10, anchor_x='left',
                                    anchor_y='top', color=(0, 0, 0, 255))

    def getSelectedBlock(self):
        return self.blockList[self.selectedBlock]

    def selectBlock(self, newBlock):
        self.selectedBlock = newBlock % len(self.blockList)

    def draw(self):
        # Draws Inventory
        self.tempInventory.text = self.getSelectedBlock().name
        self.tempInventory.draw()
        pass

    def resize(self, width, height):
        # Rezizises Inventory
        pass


