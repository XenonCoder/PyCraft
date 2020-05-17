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

import concurrent.futures
import random
import noise

from .blocks import *
from .utilities import *
from game import utilities


class Chunk:
    """A chunk of the world, with some helpers"""

    def __init__(self, sector):
        self.blocks = {}

        self.sector = sector
        assert sector[1] == 0
        """For now a chunk is infinite vertically"""

    def empty(self, pos):
        return pos not in self.blocks

    def __setitem__(self, pos, value):
        self.blocks[pos] = value

    def __getitem__(self, pos):
        return self.blocks[pos]


class WorldGenerator:
    """Generate a world model"""

    def __init__(self, model):
        self.model = model

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        """This thread pool will execute one task at a time. Others are stacked,
        waiting for execution."""

        self.callback = None
        """Callback for the result of the executor"""

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

    def set_callback(self, callback):
        """Set a callback called when a new sector is computed"""
        self.callback = callback

    def request_sector(self, sector):
        """Compute the content of a sector asynchronously and return the result to a
        callback already specified to this generator.
        """
        def send_result(future):
            chunk = future.result()
            self.callback(chunk)
        future = self.executor.submit(self.generate, sector)
        future.add_done_callback(send_result)

    def _iter_xz(self, sector):
        """Iter all the xz block position from a sector"""
        sx, _sy, sz = sector
        for x in range(sx * SECTOR_SIZE, (sx + 1) * SECTOR_SIZE):
            for z in range(sz * SECTOR_SIZE, (sz + 1) * SECTOR_SIZE):
                yield x, z

    def generate(self, sector):
        """Generate a specific sector of the world and place all the blocks"""

        chunk = Chunk(sector)
        """Store the content of this sector"""

        self._generate_enclosure(chunk)
        if self.hills_enabled:
            self._generate_random_map(chunk)
        else:
            self._generate_floor(chunk)
        if self.cloudiness > 0:
            self._generate_clouds(chunk)
        if self.nb_trees > 0:
            self._generate_trees(chunk)

        return chunk

    def _generate_enclosure(self, chunk):
        """Generate an enclosure with unbreakable blocks on the floor and
        and on the side.
        """
        y_pos = self.y - 2
        height = self.enclosure_height
        half_size = self.enclosure_size
        n = half_size
        for x, z in self._iter_xz(chunk.sector):
            if x < -n or x > n or z < -n or z > n:
                continue
            # create a layer stone an DIRT_WITH_GRASS everywhere.
            chunk[(x, y_pos, z)] = BEDSTONE

            if self.enclosure:
                # create outer walls.
                # Setting values for the Bedrock (depth, and height of the perimeter wall).
                if x in (-n, n) or z in (-n, n):
                    for dy in range(height):
                        chunk[(x, y_pos + dy, z)] = BEDSTONE

    def _generate_floor(self, chunk):
        """Generate a standard floor at a specific height"""
        y_pos= self.y - 2
        n = self.enclosure_size
        for x, z in self._iter_xz(chunk.sector):
            if self.enclosure:
                if x <= -n or x >= n - 1 or z <= -n or z >= n - 1:
                    continue
            chunk[(x, y_pos, z)] = DIRT_WITH_GRASS

    def _generate_random_map(self, chunk):
        n = self.enclosure_size
        y_pos = self.y - 2
        octaves = 4
        freq = 38
        for x, z in self._iter_xz(chunk.sector):
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
                chunk[(x, y_pos+nb_block-i, z)] = block

    def _generate_trees(self, chunk):
        """Generate trees in the map

        For now it do not generate trees between 2 sectors, and use rand
        instead of a procedural generation.
        """
        def get_biome(chunk, x, y, z):
            """Return the biome at a location of the map plus the first empty place."""
            # This loop could be removed using procedural height map
            while not chunk.empty((x, y, z)):
                y = y + 1
            block = chunk[x, y - 1, z]
            return block, y

        sector = chunk.sector
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

            biome, start_pos = get_biome(chunk, x, y_pos + 1, z)
            if biome not in [DIRT, DIRT_WITH_GRASS, SAND]:
                continue
            if biome == SAND:
                height = random.randint(4, 5)
                self._create_coconut_tree(chunk, x, start_pos, z, height)
            elif start_pos > 6:
                height = random.randint(3, 5)
                self._create_fir_tree(chunk, x, start_pos, z, height)
            else:
                height = random.randint(3, 7 - (start_pos - y_pos) // 3)
                self._create_default_tree(chunk, x, start_pos, z, height)

    def _create_plus(self, chunk, x, y, z, block):
        chunk[(x, y, z)] = block
        chunk[(x - 1, y, z)] = block
        chunk[(x + 1, y, z)] = block
        chunk[(x, y, z - 1)] = block
        chunk[(x, y, z + 1)] = block

    def _create_box(self, chunk, x, y, z, block):
        for i in range(9):
            dx, dz = i // 3 - 1, i % 3 - 1
            chunk[(x + dx, y, z + dz)] = block

    def _create_default_tree(self, chunk, x, y, z, height):
        if height == 0:
            return
        if height == 1:
            self._create_plus(x, y, z, LEAVES)
            return
        if height == 2:
            chunk[(x, y, z)] = TREE
            chunk[(x, y + 1, z)] = LEAVES
            return
        y_tree = 0
        root_height = 2 if height >= 4 else 1
        for _ in range(root_height):
            chunk[(x, y + y_tree, z)] = TREE
            y_tree += 1
        self._create_plus(chunk, x, y + y_tree, z, LEAVES)
        y_tree += 1
        for _ in range(height - 4):
            self._create_box(chunk, x, y + y_tree, z, LEAVES)
            y_tree += 1
        self._create_plus(chunk, x, y + y_tree, z, LEAVES)

    def _create_fir_tree(self, chunk, x, y, z, height):
        if height == 0:
            return
        if height == 1:
            self._create_plus(chunk, x, y, z, LEAVES)
            return
        if height == 2:
            chunk[(x, y, z)] = TREE
            chunk[(x, y + 1, z)] = LEAVES
            return
        y_tree = 0
        chunk[(x, y + y_tree, z)] = TREE
        y_tree += 1
        self._create_box(chunk, x, y + y_tree, z, LEAVES)
        chunk[(x, y + y_tree, z)] = TREE
        y_tree += 1
        h_layer = (height - 2) // 2
        for _ in range(h_layer):
            self._create_plus(chunk, x, y + y_tree, z, LEAVES)
            chunk[(x, y + y_tree, z)] = TREE
            y_tree += 1
        for _ in range(h_layer):
            chunk[(x, y + y_tree, z)] = LEAVES
            y_tree += 1

    def _create_coconut_tree(self, chunk, x, y, z, height):
        y_tree = 0
        for _ in range(height - 1):
            chunk[(x, y + y_tree, z)] = TREE
            y_tree += 1
        chunk[(x + 1, y + y_tree, z)] = LEAVES
        chunk[(x - 1, y + y_tree, z)] = LEAVES
        chunk[(x, y + y_tree, z + 1)] = LEAVES
        chunk[(x, y + y_tree, z - 1)] = LEAVES
        if height >= 5:
            chunk[(x + 2, y + y_tree, z)] = LEAVES
            chunk[(x - 2, y + y_tree, z)] = LEAVES
            chunk[(x, y + y_tree, z + 2)] = LEAVES
            chunk[(x, y + y_tree, z - 2)] = LEAVES
        if height >= 6:
            y_tree -= 1
            chunk[(x + 3, y + y_tree, z)] = LEAVES
            chunk[(x - 3, y + y_tree, z)] = LEAVES
            chunk[(x, y + y_tree, z + 3)] = LEAVES
            chunk[(x, y + y_tree, z - 3)] = LEAVES

    def _generate_clouds(self, chunk):
        """Generate clouds at this `height` and covering this `half_size`
        centered to 0.
        """
        y_pos = self.y + 20
        octaves = 3
        freq = 20
        for x, z in self._iter_xz(chunk.sector):
            c = noise.snoise2(x/freq, z/freq, octaves=octaves)
            if (c + 1) * 0.5 < self.cloudiness:
                chunk[(x, y_pos, z)] = CLOUD
