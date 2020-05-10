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

import noise

from .blocks import *
from .utilities import *


def generate_world(self):
    """Randomly generate a new world and place all the blocks"""
    n = 80  # 1/2 width and height of world
    s = 1  # step size
    y = 0  # initial y height

    for x in range(-n, n + 1, s):
        for z in range(-n, n + 1, s):
            # create a layer stone an DIRT_WITH_GRASS everywhere.
            self.add_block((x, y - 3, z), BEDSTONE, immediate=False)
            if x in (-n, n) or z in (-n, n):
                # create outer walls.
                # Setting values for the Bedrock (depth, and height of the perimeter wall).
                for dy in range(-2, 9):
                    self.add_block((x, y + dy, z), BEDSTONE, immediate=False)

    # generate the hills randomly

    if HILLS_ON:
        lookup_terrain = []
        def add_terrain_map(height, terrains):
            """Add a new entry to the height map lookup table.

            `height` will be the height at this part of the height map.
            and `terrains` contains blocks for each vertical voxels. The last
            one is on top, and the first one is used for all the remaining voxels
            on bottom.
            """
            lookup_terrain.append((height, terrains))

        add_terrain_map(1, [WATER])
        add_terrain_map(1, [WATER])
        add_terrain_map(1, [WATER])
        add_terrain_map(1, [WATER])
        add_terrain_map(1, [WATER])
        add_terrain_map(1, [WATER])
        add_terrain_map(1, [SAND])
        add_terrain_map(1, [SAND])
        add_terrain_map(2, [SAND])
        add_terrain_map(1, [SAND])
        add_terrain_map(1, [SAND])
        add_terrain_map(1, [DIRT_WITH_GRASS])
        add_terrain_map(1, [DIRT_WITH_GRASS])
        add_terrain_map(2, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(2, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(3, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(4, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(4, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(5, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(5, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(6, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(6, [DIRT, DIRT_WITH_GRASS])
        add_terrain_map(7, [DIRT])
        add_terrain_map(8, [DIRT])
        add_terrain_map(9, [DIRT])
        add_terrain_map(10, [DIRT, DIRT_WITH_SNOW])
        add_terrain_map(11, [DIRT, DIRT_WITH_SNOW, SNOW])
        add_terrain_map(12, [DIRT, DIRT_WITH_SNOW, SNOW, SNOW])
        add_terrain_map(13, [DIRT, DIRT_WITH_SNOW, SNOW, SNOW])
        add_terrain_map(14, [DIRT, DIRT_WITH_SNOW, SNOW, SNOW])
        add_terrain_map(15, [DIRT, DIRT_WITH_SNOW, SNOW, SNOW])

        octaves = 4
        freq = 38
        for x in range(-n + 1, n):
            for z in range(-n + 1, n):
                c = noise.snoise2(x/freq, z/freq, octaves=octaves)
                c = int((c + 1) * 0.5 * len(lookup_terrain))
                if c < 0:
                    c = 0
                nb_block, terrains = lookup_terrain[c]
                for i in range(nb_block):
                    block = terrains[-1-i] if i < len(terrains) else terrains[0]
                    self.add_block((x, y+nb_block-2-i, z), block, immediate=False)
    else:
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                self.add_block((x, y - 2, z), DIRT_WITH_GRASS, immediate=False)

    # generate the clouds

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
