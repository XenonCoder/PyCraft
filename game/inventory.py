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

from pyglet.sprite import Sprite
from pyglet.graphics import OrderedGroup
from pyglet.shapes import Rectangle

from .blocks import *
from .utilities import *


class Inventory(object):

    def __init__(self, selected_block, window, hud_group, hud_background_group):
        """Inventory manages and draws the Inventory, contains full List of Blocks
        """
        self.selected_block = selected_block
        self.window = window
        self.is_inventory_open = False
        self.hud_group = hud_group
        self.hud_background_group = hud_background_group
        self.hud_foreground_group = OrderedGroup(order=3)
        self._hotbar_batch = pyglet.graphics.Batch()
        self._inventory_batch = pyglet.graphics.Batch()

        # Hotbar Background
        self.hotbar_background = Rectangle(0, 0, 100, 100, (90, 101, 117),batch=self._hotbar_batch, group=self.hud_background_group) 
        self.hotbar_background.opacity = 125

        # Inventory Background
        self.inventory_background = Rectangle(0, 0, self.window.width, self.window.height, (90, 101, 117), batch=self._inventory_batch, group=self.hud_background_group)
        self.inventory_background.opacity = 150
        
        self.selection_indicator = Rectangle(0, 0, PREVIEW_SIZE+HIGHLIGHT_PADDING, PREVIEW_SIZE+HIGHLIGHT_PADDING, (0, 0, 0), batch=self._hotbar_batch, group=self.hud_background_group) 
        self.selection_indicator.opacity = 150

        #Last known possition of mouse and hovered item
        self._mouse_x = 0
        self._mouse_y = 0
        self._drag_x = 0
        self._drag_y = 0
        self._is_dragging = False
        self._is_over_hotbar = False
        self._drag_hotbar_slot = 0
        self._draged_item = []
        self._hovered_item = None

        # List of all Blocks in the Game 
        self.block_list = [DIRT, DIRT_WITH_GRASS, SAND, SNOW, COBBLESTONE,
                          BRICK_COBBLESTONE, BRICK, TREE, LEAVES, WOODEN_PLANKS]

        # List of Blockt currently in hotbar
        self._hotbar = self.block_list[:HOTBAR_SIZE]
        self._hotbar_sprites = []
        self._inventory_sprites = []
        
        #Hotbar Size
        size_x, size_y = self._get_hotbar_size()
        self.size_x = size_x
        self.size_y = size_y
        self.hotbar_x = self.window.width/2 - self.size_x/2
        self.hotbar_y = 0
        self.inventory_x = self.window.width/2 - self.size_x/2
        self.inventory_y = 150

    def toggle_inventory(self):
        """Opens/Closes Inventory
        """
        self.window.set_exclusive_mouse(self.is_inventory_open)
        self.is_inventory_open = not self.is_inventory_open
        self._rebuild_inventory_overlay()

    def _rebuild_hotbar(self):
        self._hotbar_sprites = []
        self.hotbar_background.x = self.hotbar_x
        self.hotbar_background.y = self.hotbar_y
        self.hotbar_background.width = self.size_x
        self.hotbar_background.height = self.size_y
        for i in range(HOTBAR_SIZE):
            slot_x = ((self.size_x/HOTBAR_SIZE)*i)+self.hotbar_x
            if len(self._hotbar) <= i:
                empty_slot = Rectangle(slot_x, self.hotbar_y, PREVIEW_SIZE, PREVIEW_SIZE, (200, 200, 200), batch=self._hotbar_batch, group=self.hud_group)
                empty_slot.opacity = 100
                self._hotbar_sprites.append(empty_slot)
            else:
                self._draw_inventory_slot(slot_x, self.hotbar_y, self._hotbar[i].get_block_image(), self._hotbar_batch, self._hotbar_sprites)

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
        return self._hotbar[self.selected_block]

    def select_block(self, new_block):
        """Selects a new Block"""
        self.selected_block = new_block % len(self._hotbar)
        self._rebuild_hotbar()

    def _draw_inventory_slot(self, x, y, img, render_batch, sprite_list):
        """Moves the Selection Indicator and draws it above a specific sprite"""
        x += INVENTORY_MARGIN/2
        y += INVENTORY_MARGIN/2
        for i_x in range(int(PREVIEW_SIZE/16)):
            for i_y in range(int(PREVIEW_SIZE/16)):
                sp = Sprite(img, x=x + i_x*16, y=y + i_y*16, group=self.hud_group, batch=render_batch)
                sprite_list.append(sp)
    
    def _update_hotbar(self):
        for i in range(HOTBAR_SIZE):
            if i == self.selected_block and not self.is_inventory_open:
                slot_x = ((self.size_x/HOTBAR_SIZE)*i)+self.hotbar_x
                self._update_seletion_indicator(slot_x, self.hotbar_y)
            if self._is_dragging:
                slot_x = ((self.size_x/HOTBAR_SIZE)*i)+self.hotbar_x
                if slot_x < self._drag_x and slot_x+(self.size_x/HOTBAR_SIZE) > self._drag_x:
                    if self.hotbar_y < self._drag_y and self.hotbar_y+self.size_y > self._drag_y:
                        self._drag_hotbar_slot = i
                        self._is_over_hotbar = True
                        self._update_seletion_indicator(slot_x , self.hotbar_y)

    def _update_inventory(self):
        line = 0
        colum = 0
        for block in range(len(self.block_list)):
            if block-(line*HOTBAR_SIZE) >= HOTBAR_SIZE:
                line += 1
                colum = 0
            slot_x = ((PREVIEW_SIZE+INVENTORY_MARGIN)*colum)+self.inventory_x
            slot_y = line*self.size_y+self.inventory_y
            colum += 1
            if slot_x < self._mouse_x and slot_x+(self.size_x/HOTBAR_SIZE) > self._mouse_x:
                if slot_y < self._mouse_y and slot_y+self.size_y > self._mouse_y:
                    self._hovered_item = block
                    self._update_seletion_indicator(slot_x, slot_y)

    def _update_seletion_indicator(self, x, y):
        """Updates the Selection Indicator """
        self.selection_indicator.x = x++HIGHLIGHT_PADDING/2
        self.selection_indicator.y = y++HIGHLIGHT_PADDING/2
        pass

    def _rebuild_inventory_overlay(self):
        """Draws inventory overlay, Position can be changed with x and y"""
        line = 0
        colum = 0

        self.inventory_background.width = self.size_x
        self.inventory_background.height = self.window.height - self.size_y
        self.inventory_background.y = self.size_y
        self.inventory_background.x = self.hotbar_x

        #lay out Blocks
        _inventory_sprites = []
        for block in range(len(self.block_list)):
            if block-(line*HOTBAR_SIZE) >= HOTBAR_SIZE:
                line += 1
                colum = 0
            slot_x = ((PREVIEW_SIZE+INVENTORY_MARGIN)*colum)+self.inventory_x
            slot_y = line*self.size_y+self.inventory_y
            self._draw_inventory_slot(slot_x, slot_y, self.block_list[block].get_block_image(), self._inventory_batch, self._inventory_sprites)
            colum += 1

    def _draw_dragged_item(self):
        if self._is_dragging and self.is_inventory_open and self._hovered_item != None:
            self._draged_item = []
            self._draw_inventory_slot(self._drag_x-PREVIEW_SIZE/2, self._drag_y-PREVIEW_SIZE/2, self.block_list[self._hovered_item].get_block_image(), self._inventory_batch, self._draged_item)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.is_inventory_open and self._hovered_item != None:
            self._is_dragging = True
            self._drag_x = x
            self._drag_y = y
            pass

    def _on_drag_stop(self):
        self._is_dragging = False
        if self._is_over_hotbar:
            self._hotbar[self._drag_hotbar_slot] = self.block_list[self._hovered_item]
            self._rebuild_hotbar()
            self._draged_item = []
            self._hovered_item = None
            self._rebuild_hotbar()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def update(self, dt):
        if self.is_inventory_open:
            self._update_inventory()
            if self._drag_x == 0 and self._drag_y == 0 and self._is_dragging:
                self._on_drag_stop()
        self._is_over_hotbar = False
        self.hovered_hotbar_item = 0
        self._update_hotbar()

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
        self._drag_x = 0
        self._drag_y = 0
        self._mouse_x = x
        self._mouse_y = y
        pass

    def draw(self):
        # Draws Inventory
        self._hotbar_batch.draw()

        if self.is_inventory_open:
            self._inventory_batch.draw()

        if self._is_dragging:
            self._draw_dragged_item()

    def resize(self, width, height):
        # Sets background in case window size changed
        size_x, size_y = self._get_hotbar_size()
        self.size_x = size_x
        self.size_y = size_y
        self._rebuild_hotbar()
        self._rebuild_inventory_overlay()
