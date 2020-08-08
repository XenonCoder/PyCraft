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

from .blocks import *
from .utilities import *
from game import utilities
from .noise import Noise
from .world import Sector


class WorldGenerator:
    """Generate a world model"""

    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        """This thread pool will execute one task at a time. Others are stacked,
        waiting for execution."""

        self.callback = None
        """Callback for the result of the executor"""

        self.hills_enabled = True
        """If True the generator uses a procedural generation for the map.
        Else, a flat floor will be generated."""

        self.y = 4
        """Initial y height"""

        self.cloudiness = 0.35
        """The cloudiness can be custom to change the about of clouds generated.
        0 means blue sky, and 1 means white sky."""

        self.y_cloud = self.y + 20
        """y-position of the clouds."""

        self.nb_trees = 6
        """Max number of trees to generate per sectors"""

        self.tree_chunk_size = 32
        """The number of tree will be generated in this chunk size (in block)"""

        self.enclosure = True
        """If true the world is limited to a fixed size, else the world is infinitely
        generated."""

        self.enclosure_size = 80
        """1/2 width (in x and z) of the enclosure"""

        self.enclosure_height = 12
        """Enclosure height, if generated"""

        self.terrain_gen = Noise(frequency=1 / (38 * 256), octaves=4)
        """Raw generator used to create the terrain"""

        self.cloud_gen = Noise(frequency=1 / (20 * 256), octaves=3)
        """Raw generator used to create the clouds"""

        self.gold_gen = Noise(frequency=1 / (64 * 256), octaves=2, persistence=0.1)
        self.iron_gen = Noise(frequency=1 / (32 * 256), octaves=2, persistence=0.1)
        self.coal_gen = Noise(frequency=1 / (16 * 256), octaves=2, persistence=0.1)
        """Raw generator for ore"""

        self.terrain_gen.randomize()
        self.cloud_gen.randomize()

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

    def _iter_xz(self, chunk):
        """Iterate all the xz block positions from a sector"""
        xmin, _, zmin = chunk.min_block
        xmax, _, zmax = chunk.max_block
        for x in range(xmin, xmax):
            for z in range(zmin, zmax):
                yield x, z

    def _iter_xyz(self, chunk):
        """Iterate all the xyz block positions from a sector"""
        xmin, ymin, zmin = chunk.min_block
        xmax, ymax, zmax = chunk.max_block
        for x in range(xmin, xmax):
            for y in range(ymin, ymax):
                for z in range(zmin, zmax):
                    yield x, y, z

    def generate(self, sector):
        """Generate a specific sector of the world and place all the blocks"""

        chunk = Sector(sector)
        """Store the content of this sector"""

        if self.enclosure:
            self._generate_enclosure(chunk)
        if self.hills_enabled:
            self._generate_random_map(chunk)
        else:
            self._generate_floor(chunk)
        if self.cloudiness > 0:
            self._generate_clouds(chunk)
        if self.nb_trees > 0:
            self._generate_trees(chunk)
        if not self.enclosure:
            self._generate_underworld(chunk)

        return chunk

    def _generate_enclosure(self, chunk):
        """Generate an enclosure with unbreakable blocks on the floor and
        and on the side.
        """
        y_pos = self.y - 2
        height = self.enclosure_height
        if not chunk.contains_y_range(y_pos, y_pos + height):
            # Early break, there is no enclosure here
            return

        y_pos = self.y - 2
        half_size = self.enclosure_size
        n = half_size
        for x, z in self._iter_xz(chunk):
            if x < -n or x > n or z < -n or z > n:
                continue
            # create a layer stone an DIRT_WITH_GRASS everywhere.
            pos = (x, y_pos, z)
            chunk.add_block(pos, BEDSTONE)

            # create outer walls.
            # Setting values for the Bedrock (depth, and height of the perimeter wall).
            if x in (-n, n) or z in (-n, n):
                for dy in range(height):
                    pos = (x, y_pos + dy, z)
                    chunk.add_block(pos, BEDSTONE)

    def _generate_floor(self, chunk):
        """Generate a standard floor at a specific height"""
        y_pos = self.y - 2
        if not chunk.contains_y(y_pos):
            # Early break, there is no clouds here
            return
        n = self.enclosure_size
        for x, z in self._iter_xz(chunk):
            if self.enclosure:
                if x <= -n or x >= n or z <= -n or z >= n:
                    continue
            chunk.add_block((x, y_pos, z), DIRT_WITH_GRASS)

    def _get_biome(self, x, z):
        c = self.terrain_gen.noise2(x, z)
        c = int((c + 1) * 0.5 * len(self.lookup_terrain))
        if c < 0:
            c = 0
        nb_block, terrains = self.lookup_terrain[c]
        return nb_block, terrains

    def _generate_random_map(self, chunk):
        n = self.enclosure_size
        y_pos = self.y - 2
        if not chunk.contains_y_range(y_pos, y_pos + 20):
            return
        for x, z in self._iter_xz(chunk):
            if self.enclosure:
                if x <= -n or x >= n or z <= -n or z >= n:
                    continue
            nb_block, terrains = self._get_biome(x, z)
            for i in range(nb_block):
                block = terrains[-1-i] if i < len(terrains) else terrains[0]
                chunk.add_block((x, y_pos + nb_block - i, z), block)

    def _generate_trees(self, chunk):
        """Generate trees in the map

        For now it do not generate trees between 2 sectors, and use rand
        instead of a procedural generation.
        """
        if not chunk.contains_y_range(self.y, self.y + 20):
            return

        def get_biome(x, y, z):
            """Return the biome at a location of the map plus the first empty place."""
            nb_block, terrains = self._get_biome(x, z)
            y = self.y - 2 + nb_block
            block = terrains[-1]
            return block, y

        sector_pos = chunk.position
        # Common root for many chunks
        # So what it is easier to generate trees between 2 chunks
        sector_root_x = (sector_pos[0] * SECTOR_SIZE // self.tree_chunk_size) * self.tree_chunk_size
        sector_root_z = (sector_pos[2] * SECTOR_SIZE // self.tree_chunk_size) * self.tree_chunk_size
        random.seed(sector_root_x + sector_root_z)

        nb_trees = random.randint(0, self.nb_trees)
        n = self.enclosure_size - 3
        y_pos = self.y - 2

        for _ in range(nb_trees):
            x = sector_root_x + 3 + random.randint(0, self.tree_chunk_size - 7)
            z = sector_root_z + 3 + random.randint(0, self.tree_chunk_size - 7)
            if self.enclosure:
                if x < -n + 2 or x > n - 2 or z < -n + 2 or z > n - 2:
                    continue

            biome, start_pos = get_biome(x, y_pos + 1, z)
            if biome not in [DIRT, DIRT_WITH_GRASS, SAND]:
                continue
            if biome == SAND:
                height = random.randint(4, 5)
                self._create_coconut_tree(chunk, x, start_pos, z, height)
            elif start_pos - self.y > 6:
                height = random.randint(3, 5)
                self._create_fir_tree(chunk, x, start_pos, z, height)
            else:
                height = random.randint(3, 7 - (start_pos - y_pos) // 3)
                self._create_default_tree(chunk, x, start_pos, z, height)

    def _create_plus(self, chunk, x, y, z, block):
        chunk.add_block((x, y, z), block)
        chunk.add_block((x - 1, y, z), block)
        chunk.add_block((x + 1, y, z), block)
        chunk.add_block((x, y, z - 1), block)
        chunk.add_block((x, y, z + 1), block)

    def _create_box(self, chunk, x, y, z, block):
        for i in range(9):
            dx, dz = i // 3 - 1, i % 3 - 1
            chunk.add_block((x + dx, y, z + dz), block)

    def _create_default_tree(self, chunk, x, y, z, height):
        if height == 0:
            return
        if height == 1:
            self._create_plus(x, y, z, LEAVES)
            return
        if height == 2:
            chunk.add_block((x, y, z), TREE)
            chunk.add_block((x, y + 1, z), LEAVES)
            return
        y_tree = 0
        root_height = 2 if height >= 4 else 1
        for _ in range(root_height):
            chunk.add_block((x, y + y_tree, z), TREE)
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
            chunk.add_block((x, y, z), TREE)
            chunk.add_block((x, y + 1, z), LEAVES)
            return
        y_tree = 0
        chunk.add_block((x, y + y_tree, z), TREE)
        y_tree += 1
        self._create_box(chunk, x, y + y_tree, z, LEAVES)
        chunk.add_block((x, y + y_tree, z), TREE)
        y_tree += 1
        h_layer = (height - 2) // 2
        for _ in range(h_layer):
            self._create_plus(chunk, x, y + y_tree, z, LEAVES)
            chunk.add_block((x, y + y_tree, z), TREE)
            y_tree += 1
        for _ in range(h_layer):
            chunk.add_block((x, y + y_tree, z), LEAVES)
            y_tree += 1

    def _create_coconut_tree(self, chunk, x, y, z, height):
        y_tree = 0
        for _ in range(height - 1):
            chunk.add_block((x, y + y_tree, z), TREE)
            y_tree += 1
        chunk.add_block((x + 1, y + y_tree, z), LEAVES)
        chunk.add_block((x - 1, y + y_tree, z), LEAVES)
        chunk.add_block((x, y + y_tree, z + 1), LEAVES)
        chunk.add_block((x, y + y_tree, z - 1), LEAVES)
        if height >= 5:
            chunk.add_block((x + 2, y + y_tree, z), LEAVES)
            chunk.add_block((x - 2, y + y_tree, z), LEAVES)
            chunk.add_block((x, y + y_tree, z + 2), LEAVES)
            chunk.add_block((x, y + y_tree, z - 2), LEAVES)
        if height >= 6:
            y_tree -= 1
            chunk.add_block((x + 3, y + y_tree, z), LEAVES)
            chunk.add_block((x - 3, y + y_tree, z), LEAVES)
            chunk.add_block((x, y + y_tree, z + 3), LEAVES)
            chunk.add_block((x, y + y_tree, z - 3), LEAVES)

    def _generate_clouds(self, chunk):
        """Generate clouds at this `self.y_cloud`.
        """
        y_pos = self.y_cloud
        if not chunk.contains_y(y_pos):
            # Early break, there is no clouds here
            return
        for x, z in self._iter_xz(chunk):
            pos = (x, y_pos, z)
            if not chunk.empty(pos):
                continue
            c = self.cloud_gen.noise2(x, z)
            if (c + 1) * 0.5 < self.cloudiness:
                chunk.add_block(pos, CLOUD)

    def _get_stone(self, pos):
        """Returns the expected mineral at a specific location.

        The input location have to be already known as a stone location.
        """
        v = self.gold_gen.noise3(*pos)
        if 0.02 < v < 0.03:
            return GOLD_ORE
        v = self.iron_gen.noise3(*pos)
        if 0.015 < v < 0.03:
            return IRON_ORE
        v = self.coal_gen.noise3(*pos)
        if 0.01 < v < 0.03:
            return COAL_ORE
        return STONE

    def _generate_underworld(self, chunk):
        if chunk.min_block[1] > self.y - 3:
            return
        for x, y, z in self._iter_xyz(chunk):
            if y > self.y - 2:
                continue
            pos = x, y, z
            block = self._get_stone(pos)
            chunk.add_block(pos, block)
