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

from .config import *


def cube_vertices(x, y, z, n):
    """Return the vertices of the Block at position x, y, z with size 2*n.
    :param x: int or float of the Block's x position
    :param y: int or float of the Block's y position
    :param z: int or float of the Block's z position
    :param n: float representing the size of the Block
    :return: tuple of len 72 containing vertex data for a Block
    """
    return (x-n, y+n, z-n,  x-n, y+n, z+n,  x+n, y+n, z+n,  x+n, y+n, z-n,  # top
            x-n, y-n, z-n,  x+n, y-n, z-n,  x+n, y-n, z+n,  x-n, y-n, z+n,  # bottom
            x-n, y-n, z-n,  x-n, y-n, z+n,  x-n, y+n, z+n,  x-n, y+n, z-n,  # left
            x+n, y-n, z+n,  x+n, y-n, z-n,  x+n, y+n, z-n,  x+n, y+n, z+n,  # right
            x-n, y-n, z+n,  x+n, y-n, z+n,  x+n, y+n, z+n,  x-n, y+n, z+n,  # front
            x+n, y-n, z-n,  x-n, y-n, z-n,  x-n, y+n, z-n,  x+n, y+n, z-n)  # back


def normalize(position):
    """Accepts `position` of arbitrary precision clamps it.

    :param position: tuple of len 3
    :return: tuple of ints of len 3, representing a block position
    """
    x, y, z = position
    return int(round(x)), int(round(y)), int(round(z))


def sectorize(position):
    """Returns a tuple representing the sector for the given `position`

    :param position: tuple of len 3
    :return: tuple of len 3 representing the sector
    """
    x, y, z = position
    return int(x) // SECTOR_SIZE, int(y) // SECTOR_SIZE, int(z) // SECTOR_SIZE
