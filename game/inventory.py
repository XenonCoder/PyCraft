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

    def __init__(self, selected_block, window):
        """Inventory manages and draws the Inventory, contains full List of Blocks
        """
        self.selected_block = selected_block
        self.window = window

        self.is_inventory_open = False

        # Background for our Hotbar
        self.hotbar_background = VertexRectangle(0, 0, 100, 100, (90, 101, 117, 125))
        self.selectionIndicator = VertexRectangle(0, 0, PREVIEW_SIZE, PREVIEW_SIZE, (0, 0, 0, 80))

        #Last known possition of mouse and hovered item
        self.mouse_x = 0
        self.mouse_y = 0
        self.drag_x = 0
        self.drag_y = 0
        self.hovered_item = None
        self.is_draggign = False
        self.is_over_hotbar = False
        self.drag_hotbar_slot = 0

        # List of all Blocks in the Game 
        self.block_list = [DIRT, DIRT_WITH_GRASS, SAND, SNOW, COBBLESTONE,
                          BRICK_COBBLESTONE, BRICK, TREE, LEAVES, WOODEN_PLANKS]

        # List of Blockt currently in hotbar
        self.hotbar = self.block_list[:HOTBAR_SIZE]

    def toggle_inventory(self):
        """Opens/Closes Inventory
        """
        self.window.set_exclusive_mouse(self.is_inventory_open)
        self.is_inventory_open = not self.is_inventory_open

    def _get_hotbar_size(self):
        """Returns width and height of hotbar
        values are returned in tupel (width, height)
        """
        width = 0
        height = PREVIEW_SIZE + INVENTORY_MARGIN
        for i in range(HOTBAR_SIZE):
            width += PREVIEW_SIZE + INVENTORY_MARGIN
        return (width, height)

    def get_selected_block(self):
        """Returns currently selected hotbar Block"""
        return self.hotbar[self.selected_block]

    def select_block(self, newBlock):
        """Selects a new Block"""
        self.selected_block = newBlock % len(self.hotbar)

    def _draw_inventory_slot(self, x, y, texture):
        """Moves the Selection Indicator and draws it above a specific texture"""
        x += INVENTORY_MARGIN/2
        y += INVENTORY_MARGIN/2
        for i_x in range(int(PREVIEW_SIZE/16)):
            for i_y in range(int(PREVIEW_SIZE/16)):
                texture.blit(x + i_x*16, y + i_y*16)

    def _draw_seletion_indicator(self, x, y):
        """Draws the Selection Indicator """
        self.selectionIndicator.move_absolute(x+INVENTORY_MARGIN/2, y+INVENTORY_MARGIN/2)
        self.selectionIndicator.draw()
        pass

    def _draw_hotbar(self, x, y):
        """Draws the Hotbar"""
        size_x, size_y = self._get_hotbar_size()

        # Sets background in case window size changed
        self.hotbar_background.size_absolute((size_x, size_y))
        self.hotbar_background.draw()

        # Draws each slot in Hotbar
        for i in range(HOTBAR_SIZE):
            slot_x = ((size_x/HOTBAR_SIZE)*i)+x
            if len(self.hotbar) <= i:
                VertexRectangle(slot_x, y, PREVIEW_SIZE, PREVIEW_SIZE, (200, 200, 200, 100))
            else:
                self._draw_inventory_slot(slot_x, y, self.hotbar[i].get_block_texture())
            if i == self.selected_block and not self.is_inventory_open:
                self._draw_seletion_indicator(slot_x, y)
            if self.is_draggign:
                if slot_x < self.drag_x and slot_x+(size_x/HOTBAR_SIZE) > self.drag_x:
                    if y < self.drag_y and y+size_y > self.drag_y:
                        self.drag_hotbar_slot = i
                        self.is_over_hotbar = True
                        self._draw_seletion_indicator(slot_x , y)

    def _draw_inventory_overlay(self, x, y):
        # Draws background
        VertexRectangle(0, 0, self.window.width, self.window.height, (90, 101, 117, 125, 80)).draw()

        block_count = len(self.block_list)
        size_x, size_y = self._get_hotbar_size()
        line = 0
        colum = 0

        #lays out Blocks
        for block in range(len(self.block_list)):
            if block-(line*HOTBAR_SIZE) >= HOTBAR_SIZE:
                line += 1
                colum = 0
            slot_x = ((PREVIEW_SIZE+INVENTORY_MARGIN)*colum)+x
            slot_y = line*size_y+y
            self._draw_inventory_slot(slot_x, slot_y, self.block_list[block].get_block_texture())
            if slot_x < self.mouse_x and slot_x+(size_x/HOTBAR_SIZE) > self.mouse_x:
                if slot_y < self.mouse_y and slot_y+size_y > self.mouse_y:
                    self.hovered_item = block
                    self._draw_seletion_indicator(slot_x, slot_y)
            colum += 1

    def _draw_dragged_item(self):
        if self.is_draggign and self.is_inventory_open and self.hovered_item != None:
            self._draw_inventory_slot(self.drag_x-PREVIEW_SIZE/2, self.drag_y-PREVIEW_SIZE/2, self.block_list[self.hovered_item].get_block_texture())

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.is_inventory_open and self.hovered_item != None:
            self.is_draggign = True
            self.drag_x = x
            self.drag_y = y
            pass

    def _on_drag_stop(self):
        self.is_draggign = False
        if self.is_over_hotbar:
            self.hotbar[self.drag_hotbar_slot] = self.block_list[self.hovered_item]
            self.hovered_item = None

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def update(self, dt):
        if self.drag_x == 0 and self.drag_y == 0 and self.is_draggign:
            self._on_drag_stop()
        self.is_over_hotbar = False
        self.hovered_hotbar_item = 0

    def on_mouse_motion(self, x, y, dx, dy):
        """Event handler for the Window.on_mouse_motion event.
        Gets only called when inventory is open!

        Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        self.drag_x = 0
        self.drag_y = 0
        self.mouse_x = x
        self.mouse_y = y
        pass

    def draw(self):
        # Draws Inventory
        if self.is_inventory_open:
            self._draw_inventory_overlay(0, 100)
        self._draw_hotbar(0, 0)
        self._draw_dragged_item()

    def resize(self, width, height):
        # Rezizises Inventory
        pass


