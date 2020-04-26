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

import pyglet

from game.graphics import *
from game.scenemanager import SceneManager


def main():
    # The pyglet.resource module handles efficient loading of assets:
    pyglet.resource.path = ['assets', 'assets/images', 'assets/sounds']
    pyglet.resource.reindex()

    # Create the main game Window, and set it's icon:
    config = Config(alpha_size=ALPHA_SIZE, double_buffer=DOUBLE_BUFFER)
    window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption=TITLE,
                                  resizable=RESIZABLE, fullscreen=FULLSCREEN, vsync=VSYNC)
    window.set_icon(pyglet.resource.image('icon.png'))

    # Create an instance of the SceneManager, and schedule it to update:
    scene_manager = SceneManager(window=window)
    pyglet.clock.schedule_interval(scene_manager.update, 1.0 / TICKS_PER_SEC)

    # Setup some OpenGL settings (from game.graphics):
    setup_opengl()

    # Enabeling Alpha for our Debug Text:
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

    #start the game loop:
    pyglet.app.run()


if __name__ == '__main__':
    main()
