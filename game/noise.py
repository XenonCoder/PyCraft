#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

from libs import perlin


class Noise(perlin.SimplexNoise):
    """Configure a coherent noise generator.

    - `frequency`: Frequency of the noise according to the input values (default: 1.0).
                   A frequency of 1 means that input between 0..1 will cover the period
                   of the permutation table. After that the pattern is repeated.
    - `octaves`: Amount of passes to generate a multi-frequencial noise (default: 1).
    - `lacunarity`: If `octaves` is used, coefficient used to multiply the frequency
                    between two consecutive octaves (default is 2.0).
    - `persistence`: If `octaves` is used, coefficient used to multipy the amplitude
                     between two consecutive octaves (default is 0.5, divide by 2).
    """

    def __init__(self, frequency=1.0, octaves=1, lacunarity=2.0, persistence=0.5):
        super()
        self.frequency = frequency
        octaves = int(octaves)
        assert octaves >= 1
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

    def noise2(self, x, y):
        """Generate a noise 2D.
        """
        coef = self.period * self.frequency
        x = x * coef
        y = y * coef
        if self.octaves == 1:
            return super().noise2(x, y)
        else:
            frequency = 1.0
            amplitude = 1.0
            value = 0
            maximun = 0
            for _ in range(self.octaves):
                value += super().noise2(x * frequency, y * frequency) * amplitude
                maximun += amplitude;
                frequency *= self.lacunarity
                amplitude *= self.persistence
            return value / maximun

    def noise3(self, x, y, z):
        """Generate a noise 3D.
        """
        coef = self.period * self.frequency
        x = x * coef
        y = y * coef
        z = z * coef
        if self.octaves == 1:
            return super().noise3(x, y, z)
        else:
            frequency = 1.0
            amplitude = 1.0
            value = 0
            maximun = 0
            for _ in range(self.octaves):
                value += super().noise3(x * frequency,
                                        y * frequency,
                                        z * frequency) * amplitude
                maximun += amplitude;
                frequency *= self.lacunarity
                amplitude *= self.persistence
            return value / maximun
