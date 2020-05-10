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
import random
from .blocks import *


class WorldGenerator:
    """Generate a world model"""

    def __init__(self, model):
        self.model = model

        self.hills_enabled = True
        """If True the generator uses a procedural generation for the map.
        Else, a flat floor will be generated."""

        self.cloudiness = 0.35
        """The cloudiness can be custom to change the about of clouds generated.
        0 means blue sky, and 1 means white sky."""

        self.nb_trees = 200
        """Number of trees to generate"""

    def generate(self):
        """Randomly generate a new world and place all the blocks"""
        n = 80  # 1/2 width and height of world
        y = 0  # initial y height

        self._generate_enclosure(y_pos=y - 2, height=12, half_size=n)
        if self.hills_enabled:
            self._generate_random_map(y_pos=y - 2, half_size=n)
        else:
            self._generate_floor(y_pos=y - 2, half_size=n)
        if self.nb_trees > 0:
            self._generate_trees(y_pos=y - 2, half_size=n - 3)
        if self.cloudiness > 0:
            self._generate_clouds(y_pos=y + 20, half_size=n + 20)

    def _generate_enclosure(self, y_pos, height, half_size):
        """Generate an enclosure with unbreakable blocks on the floor and
        and on the side.
        """
        n = half_size
        for x in range(-n, n + 1):
            for z in range(-n, n + 1):
                # create a layer stone an DIRT_WITH_GRASS everywhere.
                self.model.add_block((x, y_pos, z), BEDSTONE, immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    # Setting values for the Bedrock (depth, and height of the perimeter wall).
                    for dy in range(height):
                        self.model.add_block((x, y_pos + dy, z), BEDSTONE, immediate=False)

    def _generate_floor(self, y_pos, half_size):
        """Generate a standard floor at a specific height"""
        for x in range(-half_size + 1, half_size):
            for z in range(-half_size + 1, half_size):
                self.model.add_block((x, y_pos, z), DIRT_WITH_GRASS, immediate=False)

    def _generate_random_map(self, y_pos, half_size):
        n = half_size
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
                    self.model.add_block((x, y_pos+nb_block-i, z), block, immediate=False)

    def _generate_trees(self, y_pos, half_size):
        def get_biome(x, y, z):
            """Return the biome at a location of the map plus the first empty place."""
            # This loop could be removed using procedural height map
            while not self.model.empty((x, y, z)):
                y = y + 1
            block = self.model.world[x, y - 1, z]
            return block, y

        for _ in range(self.nb_trees):
            x = random.randint(-half_size, half_size)
            z = random.randint(-half_size, half_size)
            biome, start_pos = get_biome(x, y_pos + 1, z)
            if biome not in [DIRT, DIRT_WITH_GRASS, SAND]:
                continue
            if biome == SAND:
                height = random.randint(4, 5)
                self._create_coconut_tree(x, start_pos, z, height)
            elif start_pos > 6:
                height = random.randint(3, 5)
                self._create_fir_tree(x, start_pos, z, height)
            else:
                height = random.randint(3, 7 - (start_pos - y_pos) // 3)
                self._create_default_tree(x, start_pos, z, height)

    def _create_plus(self, x, y, z, block):
        self.model.add_block((x, y, z), block, immediate=False)
        self.model.add_block((x - 1, y, z), block, immediate=False)
        self.model.add_block((x + 1, y, z), block, immediate=False)
        self.model.add_block((x, y, z - 1), block, immediate=False)
        self.model.add_block((x, y, z + 1), block, immediate=False)

    def _create_box(self, x, y, z, block):
        for i in range(9):
            dx, dz = i // 3 - 1, i % 3 - 1
            self.model.add_block((x + dx, y, z + dz), block, immediate=False)

    def _create_default_tree(self, x, y, z, height):
        if height == 0:
            return
        if height == 1:
            self._create_plus(x, y, z, LEAVES)
            return
        if height == 2:
            self.model.add_block((x, y, z), TREE, immediate=False)
            self.model.add_block((x, y + 1, z), LEAVES, immediate=False)
            return
        y_tree = 0
        root_height = 2 if height >= 4 else 1
        for _ in range(root_height):
            self.model.add_block((x, y + y_tree, z), TREE, immediate=False)
            y_tree += 1
        self._create_plus(x, y + y_tree, z, LEAVES)
        y_tree += 1
        for _ in range(height - 4):
            self._create_box(x, y + y_tree, z, LEAVES)
            y_tree += 1
        self._create_plus(x, y + y_tree, z, LEAVES)

    def _create_fir_tree(self, x, y, z, height):
        if height == 0:
            return
        if height == 1:
            self._create_plus(x, y, z, LEAVES)
            return
        if height == 2:
            self.model.add_block((x, y, z), TREE, immediate=False)
            self.model.add_block((x, y + 1, z), LEAVES, immediate=False)
            return
        y_tree = 0
        self.model.add_block((x, y + y_tree, z), TREE, immediate=False)
        y_tree += 1
        self._create_box(x, y + y_tree, z, LEAVES)
        self.model.add_block((x, y + y_tree, z), TREE, immediate=False)
        y_tree += 1
        h_layer = (height - 2) // 2
        for _ in range(h_layer):
            self._create_plus(x, y + y_tree, z, LEAVES)
            self.model.add_block((x, y + y_tree, z), TREE, immediate=False)
            y_tree += 1
        for _ in range(h_layer):
            self.model.add_block((x, y + y_tree, z), LEAVES, immediate=False)
            y_tree += 1

    def _create_coconut_tree(self, x, y, z, height):
        y_tree = 0
        for _ in range(height - 1):
            self.model.add_block((x, y + y_tree, z), TREE, immediate=False)
            y_tree += 1
        self.model.add_block((x + 1, y + y_tree, z), LEAVES, immediate=False)
        self.model.add_block((x - 1, y + y_tree, z), LEAVES, immediate=False)
        self.model.add_block((x, y + y_tree, z + 1), LEAVES, immediate=False)
        self.model.add_block((x, y + y_tree, z - 1), LEAVES, immediate=False)
        if height >= 5:
            self.model.add_block((x + 2, y + y_tree, z), LEAVES, immediate=False)
            self.model.add_block((x - 2, y + y_tree, z), LEAVES, immediate=False)
            self.model.add_block((x, y + y_tree, z + 2), LEAVES, immediate=False)
            self.model.add_block((x, y + y_tree, z - 2), LEAVES, immediate=False)
        if height >= 6:
            y_tree -= 1
            self.model.add_block((x + 3, y + y_tree, z), LEAVES, immediate=False)
            self.model.add_block((x - 3, y + y_tree, z), LEAVES, immediate=False)
            self.model.add_block((x, y + y_tree, z + 3), LEAVES, immediate=False)
            self.model.add_block((x, y + y_tree, z - 3), LEAVES, immediate=False)

    def _generate_clouds(self, y_pos, half_size):
        """Generate clouds at this `height` and covering this `half_size`
        centered to 0.
        """
        octaves = 3
        freq = 20
        nb = half_size * 2 + 1
        for x in range(0, nb):
            for z in range(0, nb):
                c = noise.snoise2(x/freq, z/freq, octaves=octaves)
                if (c + 1) * 0.5 < self.cloudiness:
                    self.model.add_block((x-half_size, y_pos, z-half_size), CLOUD, immediate=False)
