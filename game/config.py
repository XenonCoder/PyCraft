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


import math


# Window settings
TITLE = 'TerraCraft'
WIDTH = 800
HEIGHT = 600
VSYNC = True
ALPHA_SIZE = True
DOUBLE_BUFFER = 8
FULLSCREEN = False
RESIZABLE = True
INFO_LABEL_FONTSIZE = 12
TOGGLE_GUI = True
TOGGLE_INFO_LABEL = True

# FPS
TICKS_PER_SEC = 60

# Player
PLAYER_HEIGHT = 2
RUNNING = False
FLYING = False

# Inventory
HOTBAR_SIZE = 5
INVENTORY_MARGIN = 16
HIGHLIGHT_PADDING = 8
PREVIEW_SIZE = 90

# Look speed
LOOK_SPEED_X = 0.15
LOOK_SPEED_Y = 0.15

# Fog range
FOG_START = 20.0
FOG_END = 60.0

# Size of sectors used to ease block loading.
SECTOR_SIZE = 16

# Speed
WALKING_SPEED = 3
RUNNING_SPEED = 6
FLYING_SPEED = 10

# Node selector (block selector)
NODE_SELECTOR = 8

# Gravity
GRAVITY = 20.0

# Jump
MAX_JUMP_HEIGHT = 1.0   # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2

JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)

# Terminal velocity
TERMINAL_VELOCITY = 50

# Generate Hills?
HILLS_ON = True
