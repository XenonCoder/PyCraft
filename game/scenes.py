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

import time
import pyglet
import os

from collections import deque

from pyglet.gl import *
from pyglet.media import Player
from pyglet.shapes import Rectangle
from pyglet.window import key, mouse
from pyglet.sprite import Sprite
from pyglet.graphics import OrderedGroup

from .blocks import *
from .inventory import *
from .utilities import *
from .graphics import BlockGroup
from .genworld import WorldGenerator
from .world import Model


class AudioEngine:
    """A high level audio engine for easily playing SFX and Music."""

    def __init__(self, channels=5):
        self.sfx_players = deque([Player() for _ in range(channels)], maxlen=channels)
        self.music_player = Player()

    def set_volume(self, percentage):
        """Set the audio volume, as a percentage of 1 to 100.

        :param percentage: int: The volume, as a percentage.
        """
        volume = max(min(1, percentage / 100), 0)
        for player in self.sfx_players:
            player.volume = volume
        self.music_player.volume = volume

    def play(self, source, position=(0, 0, 0)):
        """Play a sound effect on the next available channel

        :param source: A pyglet audio Source
        :param position: Optional spacial position for the sound.
        """
        player = self.sfx_players[0]
        player.position = position
        player.queue(source=source)
        if not player.playing:
            player.play()
        else:
            player.next_source()
        self.sfx_players.rotate()

    def play_music(self, source):
        """Play a music track, or switch to a new one.

        :param source: A pyglet audio Source
        """
        self.music_player.queue(source=source)
        if not self.music_player.playing:
            self.music_player.play()
        else:
            self.music_player.next_source()


class Scene:
    """A base class for all Scenes to inherit from.

    All Scenes must contain an `update` method. In addition,
    you can also define event handlers for any of the events
    dispatched by the `Window`. Any Scene methods that match
    the Window event names will be automatically set when
    changing to the Scene.
    """

    scene_manager = None        # This is assigned when adding the Scene
    audio = AudioEngine()       # All Scenes share the same AudioEngine

    def update(self, dt):
        raise NotImplementedError


class MenuScene(Scene):
    def __init__(self, window):
        self.window = window
        self.batch = pyglet.graphics.Batch()

        # Create a
        title_image = pyglet.resource.image('TerraCraft.png')
        title_image.anchor_x = title_image.width // 2
        title_image.anchor_y = title_image.height + 10
        position = self.window.width // 2, self.window.height
        self.title_graphic = Sprite(img=title_image, x=position[0], y=position[1], batch=self.batch)

        self.start_label = pyglet.text.Label('Select save & press Enter to start', font_size=25,
                                             x=self.window.width // 2, y=self.window.height // 2,
                                             anchor_x='center', anchor_y='center', batch=self.batch)

        # Create labels for three save slots:
        self.save_slot_labels = []
        for save_slot in [1, 2, 3]:
            self.scene_manager.save.save_slot = save_slot
            # indicate if an existing save exists
            if self.scene_manager.save.has_save_game():
                label_text = f"{save_slot}:  load"
            else:
                label_text = f"{save_slot}:  new game"
            y_pos = 190 - 50 * save_slot
            label = pyglet.text.Label(
                label_text, font_size=20, x=40, y=y_pos, batch=self.batch)
            self.save_slot_labels.append(label)

        # Highlight the default save slot
        self.scene_manager.save.save_slot = 1
        self._highlight_save_slot()

    def update(self, dt):
        pass

    def _highlight_save_slot(self):
        # First reset all labels to white
        for label in self.save_slot_labels:
            label.color = 255, 255, 255, 255
        # Highlight the selected slot
        index = self.scene_manager.save.save_slot - 1
        self.save_slot_labels[index].color = 50, 50, 50, 255

    def on_key_press(self, symbol, modifiers):
        """Event handler for the Window.on_key_press event."""
        if symbol == key.ENTER:
            self.scene_manager.change_scene('GameScene')
        elif symbol == key.ESCAPE:
            self.window.set_exclusive_mouse(False)
            return pyglet.event.EVENT_HANDLED

        if symbol in (key._1, key._2, key._3):
            if symbol == key._1:
                self.scene_manager.save.save_slot = 1
            elif symbol == key._2:
                self.scene_manager.save.save_slot = 2
            elif symbol == key._3:
                self.scene_manager.save.save_slot = 3
            self._highlight_save_slot()

    def on_mouse_press(self, x, y, button, modifiers):
        """Event handler for the Window.on_resize event."""
        self.window.set_exclusive_mouse(True)

    def on_resize(self, width, height):
        """Event handler for the Window.on_resize event."""
        # Keep the graphics centered on resize
        self.title_graphic.position = width//2, height
        self.start_label.x = width // 2
        self.start_label.y = height // 2

    def on_draw(self):
        """Event handler for the Window.on_draw event."""
        self.window.clear()
        self.batch.draw()


class GameScene(Scene):
    def __init__(self, window):
        self.window = window

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()
        # Debug Batch gets rendered with all debug infos
        self.debug_batch = pyglet.graphics.Batch()

        # pyglet Groups manages setting/unsetting OpenGL state.
        self.block_group = BlockGroup(
            self.window, pyglet.resource.texture('textures.png'), order=0)
        self.hud_background_group = OrderedGroup(order=1)
        self.hud_group = OrderedGroup(order=2)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # When flying gravity has no effect and speed is increased.
        self.flying = FLYING

        # Determine if player is running. If false, then player is walking.
        self.running = RUNNING

        # Wether or not all gui elements are drawn.
        self.toggleGui = TOGGLE_GUI

        # Wether or not the fps counter and player coordinates are drawn.
        self.toggleLabel = TOGGLE_INFO_LABEL

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (SECTOR_SIZE // 2, 6, SECTOR_SIZE // 2)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # True if the location of the camera have changed between an update
        self.frustum_updated = False

        # Velocity in the y (upward) direction.
        self.dy = 0

        # Inventory, Managing selected Block and Inventory overlay
        self.inventory = Inventory(0, window, self.hud_group, self. hud_background_group)

        # Convenience list of num keys.
        self.num_keys = [key._1, key._2, key._3, key._4, key._5,
                         key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model(batch=self.batch, group=self.block_group)

        # The crosshairs at the center of the screen.
        self.reticle = self.batch.add(4, GL_LINES, self.hud_group, 'v2i', ('c3B', [0]*12))

        # The highlight around focused block.
        indices = [0, 1, 1, 2, 2, 3, 3, 0, 4, 7, 7, 6, 6, 5, 5, 4, 0, 4, 1, 7, 2, 6, 3, 5]
        self.highlight = self.batch.add_indexed(24, GL_LINES, self.block_group, indices,
                                                'v3f/dynamic', ('c3B', [0]*72))

        # The label that is displayed in the top left of the canvas (also its background).
        # The Background gets initialized with 0 width, we update its width in draw
        self.info_label = pyglet.text.Label('', font_name='Arial', font_size=INFO_LABEL_FONTSIZE,
                                            x=10, y=self.window.height - 10, anchor_x='left',
                                            anchor_y='top', color=(255, 255, 255, 255), batch=self.debug_batch, group=self.hud_group)

        self.debug_background = Rectangle(0,
                self.window.height-INFO_LABEL_FONTSIZE - 20, 0,
                INFO_LABEL_FONTSIZE + 20, color=(45, 45, 45),
                batch=self.debug_batch, group=self.hud_background_group)
        self.debug_background.opacity = 150

        # Boolean whether to display loading screen.
        self.initialized = False

        # Some environmental SFX to preload:
        self.jump_sfx = pyglet.resource.media('jump.wav', streaming=False)
        self.destroy_sfx = pyglet.resource.media('dirt.wav', streaming=False)

        self.on_resize(*self.window.get_size())

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        self.window.set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return dx, dy, dz

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        elif self.flying and not self.dy == 0:
            dx = 0.0
            dy = self.dy
            dz = 0.0
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def init_player_on_summit(self):
        """Make sure the sector containing the actor is loaded and the player is on top of it.
        """
        generator = self.model.generator
        x, y, z = self.position
        free_height = 0
        limit = 100
        while free_height < PLAYER_HEIGHT and limit:
            pos = x , y, z
            sector_position = sectorize(pos)
            if sector_position not in self.model.sectors:
                sector = generator.generate(sector_position)
                self.model.register_sector(sector)
            if self.model.empty(pos):
                free_height += 1
            else:
                free_height = 0
            y = y + 1
            limit -= 1

        position = x, y - PLAYER_HEIGHT + 1, z
        if self.position != position:
            self.position = position
            self.frustum_updated = True

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        if not self.initialized:
            self.set_exclusive_mouse(True)

            has_save = False
            if self.scene_manager.save.has_save_game():
                # Returns False if unable to load the save
                has_save = self.scene_manager.save.load_world(self.model)

            if not has_save:
                generator = WorldGenerator()
                generator.y = self.position[1]
                generator.hills_enabled = HILLS_ON
                self.model.generator = generator
                self.init_player_on_summit()

            self.initialized = True

        self.model.process_queue()

        if self.frustum_updated:
            sector = sectorize(self.position)
            self.update_shown_sectors(self.position, self.rotation)
            self.sector = sector
            self.frustum_updated = False

        m = 8
        dt = min(dt, 0.2)
        self.inventory.update(dt)
        for _ in range(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = FLYING_SPEED if self.flying else RUNNING_SPEED if self.running else WALKING_SPEED
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)

        position = (x, y, z)
        if self.position != position:
            self.position = position
            self.frustum_updated = True

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall DIRT_WITH_GRASS. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in range(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in range(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if self.model.empty(tuple(op), must_be_loaded=True):
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break

        generator = self.model.generator
        if generator is None:
            # colliding with the virtual floor
            # to avoid to fall infinitely.
            p[1] = max(-1.25, p[1])
        else:
            if generator.enclosure:
                # Force the player inside the enclosure
                s = generator.enclosure_size
                if p[0] < -s:
                    p[0] = -s
                elif p[0] > s:
                    p[0] = s
                if p[2] < -s:
                    p[2] = -s
                elif p[2] > s:
                    p[2] = s

        return tuple(p)

    def update_shown_sectors(self, position, rotation):
        """Update shown sectors according to the actual frustum.

        A sector is a contiguous x, y sub-region of world. Sectors are
        used to speed up world rendering.
        """
        sector = sectorize(position)
        if self.sector == sector:
            # The following computation is based on the actual sector
            # So if there is no changes on the sector, it have to display
            # The exact same thing
            return

        sectors_to_show = []
        pad = int(FOG_END) // SECTOR_SIZE
        for dx in range(-pad, pad + 1):
            for dy in range(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    # Manathan distance
                    dist = abs(dx) + abs(dy) + abs(dz)
                    if dist > pad + pad // 2:
                        # Skip sectors outside of the sphere of radius pad+1
                        continue
                    x, y, z = sector
                    sectors_to_show.append((dist, x + dx, y + dy, z + dz))

        # Sort by distance to the player in order to
        # displayed closest sectors first
        sectors_to_show = sorted(sectors_to_show)
        sectors_to_show = [s[1:] for s in sectors_to_show]
        self.model.show_only_sectors(sectors_to_show)

    def on_mouse_press(self, x, y, button, modifiers):
        """Event handler for the Window.on_mouse_press event.

        Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if self.exclusive:
            if not self.inventory.is_inventory_open:
                vector = self.get_sight_vector()
                block, previous = self.model.hit_test(self.position, vector)
                if button == mouse.RIGHT or (button == mouse.LEFT and modifiers & key.MOD_CTRL):
                    # ON OSX, control + left click = right click.
                    if previous:
                        self.model.add_block(previous, self.inventory.get_selected_block())
                elif button == pyglet.window.mouse.LEFT and block:
                    texture = self.model.get_block(block)
                    if texture != BEDSTONE:
                        self.model.remove_block(block)
                        self.audio.play(self.destroy_sfx)
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """Event handler for the Window.on_mouse_motion event.

        Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive and not self.inventory.is_inventory_open:
            x, y = self.rotation
            x, y = x + dx * LOOK_SPEED_X, y + dy * LOOK_SPEED_Y
            y = max(-90, min(90, y))
            rotation = (x, y)
            if self.rotation != rotation:
                self.rotation = rotation
                self.frustum_updated = True
        elif self.inventory.is_inventory_open:
            self.inventory.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        """Event handler for the Window.on_key_press event.

        Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.W and not self.inventory.is_inventory_open:
            self.strafe[0] -= 1
        elif symbol == key.S and not self.inventory.is_inventory_open:
            self.strafe[0] += 1
        elif symbol == key.A and not self.inventory.is_inventory_open:
            self.strafe[1] -= 1
        elif symbol == key.D and not self.inventory.is_inventory_open:
            self.strafe[1] += 1
        elif symbol == key.I:
            self.inventory.toggle_inventory()
        elif symbol == key.SPACE and not self.inventory.is_inventory_open:
            if self.flying:
                # Reduces vertical flying speed
                # 0.1 positive value that allows vertical flight up.
                self.dy = 0.1 * JUMP_SPEED
            elif self.dy == 0:
                self.dy = JUMP_SPEED
                self.audio.play(self.jump_sfx)
        elif symbol == key.LCTRL and not self.inventory.is_inventory_open:
            self.running = True
        elif symbol == key.LSHIFT and not self.inventory.is_inventory_open:
            if self.flying:
                # Reduces vertical flying speed
                # -0.1 negative value that allows vertical flight down.
                self.dy = -0.1 * JUMP_SPEED
            elif self.dy == 0:
                self.dy = JUMP_SPEED
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
            return pyglet.event.EVENT_HANDLED
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol == key.F1:
            self.scene_manager.change_scene("HelpScene")
        elif symbol == key.F2:
            self.toggleGui = not self.toggleGui
        elif symbol == key.F3:
            self.toggleLabel = not self.toggleLabel
        elif symbol == key.F5:
            self.scene_manager.save.save_world(self.model)
        elif symbol == key.F12:
            self._takeScreenshot()
        elif symbol in self.num_keys:
            self.inventory.select_block(symbol - self.num_keys[0])
        elif symbol == key.ENTER:
            self.scene_manager.change_scene('MenuScene')

    def _takeScreenshot(self):
        if not os.path.exists('screenshots/'):
            os.mkdir("screenshots")
        shot_number = 0
        while os.path.exists('screenshots/screenshot - {}.png'.format(shot_number)):
            shot_number += 1
        pyglet.image.get_buffer_manager().get_color_buffer().save('screenshots/screenshot - {}.png'.format(shot_number))

    def on_key_release(self, symbol, modifiers):
        """Event handler for the Window.on_key_release event.

        Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1
        elif symbol == key.SPACE:
            self.dy = 0
        elif symbol == key.LCTRL:
            self.running = False
        elif symbol == key.LSHIFT:
            self.dy = 0
        elif symbol == key.P:
            breakpoint()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.inventory.is_inventory_open:
            self.inventory.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        else:
            self.on_mouse_motion(x, y, dx ,dy)

    def on_resize(self, width, height):
        """Event handler for the Window.on_resize event.

         Called when the window is resized to a new `width` and `height`.
        """

        # Reset the info label, debug Background and reticle positions.
        self.debug_background.y = height-INFO_LABEL_FONTSIZE - 20
        self.info_label.y = height - 10
        x, y = width // 2, height // 2
        n = 10
        self.reticle.vertices[:] = (x - n, y, x + n, y, x, y - n, x, y + n)

    def on_draw(self):
        """Event handler for the Window.on_draw event.

        Called by pyglet to draw the canvas.
        """
        self.window.clear()
        # Set the current position/rotation before drawing
        self.block_group.position = self.position
        self.block_group.rotation = self.rotation
        # Draw everything in the batch
        self.batch.draw()

        # Optionally draw some things
        if self.toggleGui:
            self.draw_focused_block()
            self.inventory.draw()
            if self.toggleLabel:
                self.draw_label()

    def get_focus_block(self):
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        return block

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        block = self.get_focus_block()
        if block:
            x, y, z = block
            self.highlight.vertices[:] = cube_vertices(x, y, z, 0.51)
        else:
            # Make invisible by setting all vertices to 0
            self.highlight.vertices[:] = [0] * 72

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x, y, z = self.position
        elements = []
        elements.append("FPS = [%02d]" % pyglet.clock.get_fps())
        elements.append("COORDS = [%.2f, %.2f, %.2f]" % (x, y, z))
        elements.append("SECTORS = %d [+%d]" % (len(self.model.sectors), len(self.model.requested)))
        elements.append("BLOCKS = %d" % self.model.count_blocks())
        self.info_label.text = ' : '.join(elements)
        # Calculating debug label width and updating its background accordingly (width/height ratio for Arial=0.52 so we multiply with 1.52)
        self.debug_background.width =  int(len(self.info_label.text)*INFO_LABEL_FONTSIZE/1.52)

        self.debug_batch.draw()


class HelpScene(Scene):
    def __init__(self, window):
        self.window = window
        self.batch = pyglet.graphics.Batch()

        self.labels = []
        self.text_strings = ["  GAME OPTIONS",
                             "* Left click mouse to destroy block",
                             "* Right click mouse to create block",
                             "* Press keys 1 through 0 to choose block type",
                             "* Press F2 key to hide block selection",
                             "* Press F3 key to hide debug stats"]

        self.return_label = pyglet.text.Label("Press any key to return to game", font_size=25,
                                              x=self.window.width // 2, y=20, anchor_x='center',
                                              color=(0, 50, 50, 255), batch=self.batch)

        self.spacing = 60
        y_position = self.window.height - self.spacing

        for string in self.text_strings:
            self.labels.append(pyglet.text.Label(string, font_size=22, x=40, y=y_position,
                                                 color=(0, 50, 50, 255), batch=self.batch))
            y_position -= self.spacing

        self.on_resize(*self.window.get_size())

    def on_resize(self, width, height):
        y_position = height - self.spacing
        for label in self.labels:
            label.y = y_position
            y_position -= self.spacing

    def update(self, dt):
        pass

    def on_key_press(self, symbol, modifiers):
        self.scene_manager.change_scene("GameScene")
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        self.window.clear()
        self.batch.draw()