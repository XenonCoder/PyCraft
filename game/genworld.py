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
import random
import noise

from .blocks import *
from .utilities import *
from .graphics import BlockGroup
from wheel.pep425tags import calculate_macosx_platform_tag

def generate_world(self):
    """Randomly generate a new world and place all the blocks"""
    n = 80  # 1/2 width and height of world
    s = 1  # step size
    y = 0  # initial y height

    for x in range(-n, n + 1, s):
        for z in range(-n, n + 1, s):
            # create a layer stone an DIRT_WITH_GRASS everywhere.
            self.add_block((x, y - 2, z), DIRT_WITH_GRASS, immediate=True)
            self.add_block((x, y - 3, z), BEDSTONE, immediate=False)
            if x in (-n, n) or z in (-n, n):
                # create outer walls.
                # Setting values for the Bedrock (depth, and height of the perimeter wall).
                for dy in range(-2, 9):
                    self.add_block((x, y + dy, z), BEDSTONE, immediate=False)

    # generate the hills randomly

    if not HILLS_ON:
        return

    o = n - 10
    for _ in range(120):
        a = random.randint(-o, o)  # x position of the hill
        b = random.randint(-o, o)  # z position of the hill
        c = -1  # base of the hill
        h = random.randint(1, 6)  # height of the hill
        s = random.randint(4, 8)  # 2 * s is the side length of the hill
        d = 1  # how quickly to taper off the hills
        block = random.choice([DIRT_WITH_GRASS, SNOW, SAND])
        for y in range(c, c + h):
            for x in range(a - s, a + s + 1):
                for z in range(b - s, b + s + 1):
                    if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                        continue
                    if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:  # 6 = flat map
                        continue
                    self.add_block((x, y, z), block, immediate=False)
            s -= d  # decrement side length so hills taper off

    cloudiness = 0.35  # between 0 (blue sky) and 1 (white sky)
    sky_n = 100  # 1/2 width and height of sky
    cloud_y = y + 20  # height of the sky
    octaves = 3
    freq = 20
    nb = sky_n * 2 + 1
    for x in range(0, nb):
        for z in range(0, nb):
            c = noise.snoise2(x/freq, z/freq, octaves=octaves)
            if (c + 1) * 0.5 < cloudiness:
                self.add_block((x-sky_n, cloud_y, z-sky_n), CLOUD, immediate=False)
