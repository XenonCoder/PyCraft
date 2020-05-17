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
from .utilities import *
from game import utilities


class WorldGenerator:
    """Generate a world model"""

    def __init__(self, model):
        self.model = model

        self.hills_enabled = True
        """If True the generator uses a procedural generation for the map.
        Else, a flat floor will be generated."""

        self.y = 0
        """Initial y height"""

        self.cloudiness = 0.35
        """The cloudiness can be custom to change the about of clouds generated.
        0 means blue sky, and 1 means white sky."""

        self.nb_trees = 3
        """Max number of trees to generate per sectors"""

        self.enclosure = True
        """If true the world is limited to a fixed size, else the world is infinitely
        generated."""

        self.enclosure_size = 80
        """1/2 width (in x and z) of the enclosure"""

        self.enclosure_height = 12
        """Enclosure height, if generated"""

        self.lookup_terrain = []
        def add_terrain_map(height, terrains):
            """Add a new entry to the height map lookup table.
    
            `height` will be the height at this part of the height map.
            and `terrains` contains blocks for each vertical voxels. The last
            one is on top, and the first one is used for all the remaining voxels
            on bottom.
            """
            self.lookup_terrain.append((height, terrains))

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

    def _iter_xz(self, sector):
        """Iter all the xz block position from a sector"""
        sx, _sy, sz = sector
        for x in range(sx * SECTOR_SIZE, (sx + 1) * SECTOR_SIZE):
            for z in range(sz * SECTOR_SIZE, (sz + 1) * SECTOR_SIZE):
                yield x, z

    def generate(self, sector):
        """Generate a specific sector of the world and place all the blocks"""

        self._generate_enclosure(sector)
        if self.hills_enabled:
            self._generate_random_map(sector)
        else:
            self._generate_floor(sector)
        if self.cloudiness > 0:
            self._generate_clouds(sector)
        if self.nb_trees > 0:
            self._generate_trees(sector)

    def _generate_enclosure(self, sector):
        """Generate an enclosure with unbreakable blocks on the floor and
        and on the side.
        """
        y_pos = self.y - 2
        height = self.enclosure_height=12
        half_size = self.enclosure_size
        n = half_size
        for x, z in self._iter_xz(sector):
            if x < -n or x > n or z < -n or z > n:
                continue
            # create a layer stone an DIRT_WITH_GRASS everywhere.
            self.model.add_block((x, y_pos, z), BEDSTONE, immediate=False)

            if self.enclosure:
                # create outer walls.
                # Setting values for the Bedrock (depth, and height of the perimeter wall).
                if x in (-n, n) or z in (-n, n):
                    for dy in range(height):
                        self.model.add_block((x, y_pos + dy, z), BEDSTONE, immediate=False)

    def _generate_floor(self, sector):
        """Generate a standard floor at a specific height"""
        y_pos= self.y - 2
        n = self.enclosure_size
        for x, z in self._iter_xz(sector):
            if self.enclosure:
                if x <= -n or x >= n - 1 or z <= -n or z >= n - 1:
                    continue
            self.model.add_block((x, y_pos, z), DIRT_WITH_GRASS, immediate=False)

    def _generate_random_map(self, sector):
        n = self.enclosure_size
        y_pos = self.y - 2
        octaves = 4
        freq = 38
        for x, z in self._iter_xz(sector):
            if self.enclosure:
                if x <= -n or x >= n - 1 or z <= -n or z >= n - 1:
                    continue
            c = noise.snoise2(x/freq, z/freq, octaves=octaves)
            c = int((c + 1) * 0.5 * len(self.lookup_terrain))
            if c < 0:
                c = 0
            nb_block, terrains = self.lookup_terrain[c]
            for i in range(nb_block):
                block = terrains[-1-i] if i < len(terrains) else terrains[0]
                self.model.add_block((x, y_pos+nb_block-i, z), block, immediate=False)

    def _generate_trees(self, sector):
        """Generate trees in the map

        For now it do not generate trees between 2 sectors, and use rand
        instead of a procedural generation.
        """
        def get_biome(x, y, z):
            """Return the biome at a location of the map plus the first empty place."""
            # This loop could be removed using procedural height map
            while not self.model.empty((x, y, z)):
                y = y + 1
            block = self.model.world[x, y - 1, z]
            return block, y

        random.seed(sector[0] + sector[2])
        nb_trees = random.randint(0, self.nb_trees)
        n = self.enclosure_size - 3
        y_pos = self.y - 2

        for _ in range(nb_trees):
            x = sector[0] * utilities.SECTOR_SIZE + 3 + random.randint(0, utilities.SECTOR_SIZE-7)
            z = sector[2] * utilities.SECTOR_SIZE + 3 + random.randint(0, utilities.SECTOR_SIZE-7)
            if self.enclosure:
                if x < -n + 2 or x > n - 2 or z < -n + 2 or z > n - 2:
                    continue

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

    def _generate_clouds(self, sector):
        """Generate clouds at this `height` and covering this `half_size`
        centered to 0.
        """
        y_pos = self.y + 20
        octaves = 3
        freq = 20
        for x, z in self._iter_xz(sector):
            c = noise.snoise2(x/freq, z/freq, octaves=octaves)
            if (c + 1) * 0.5 < self.cloudiness:
                self.model.add_block((x, y_pos, z), CLOUD, immediate=False)
