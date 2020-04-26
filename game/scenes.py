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

import random
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
from .genworld import *

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
        self.position = (0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        # Inventory, Managing selected Block and Inventory overlay
        self.inventory = Inventory(0, window)

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

        self.debug_background = Rectangle(0, self.window.height-INFO_LABEL_FONTSIZE - 20, 0, INFO_LABEL_FONTSIZE + 20, color=(45, 45, 45), batch=self.debug_batch, group=self.hud_background_group) 
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
                generate_world(self.model)

            self.initialized = True

        self.model.process_queue()
        sector = sectorize(self.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            # if self.sector is None:
            #     self.model.process_entire_queue()
            self.sector = sector
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
        # fix bug for jumping outside the wall and falling to infinity.
        y = max(-1.25, y)
        self.position = (x, y, z)

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
                    if tuple(op) not in self.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break
        return tuple(p)

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
                    texture = self.model.world[block]
                    if texture != BEDSTONE:
                        self.model.remove_block(block)
                        self.audio.play(self.destroy_sfx)
            else:
                self.inventory.on_mouse_press(x, y, button, modifiers)
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
            self.rotation = (x, y)
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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.inventory.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

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
        self.inventory.resize(width, height)

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

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
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
        self.info_label.text = 'Selected Block = %s : COORDS = [%.2f, %.2f, %.2f] : %d / %d : FPS = [%02d]' % (
            self.inventory.get_selected_block().name, 
            x, y, z, self.model.currently_shown, len(self.model.world),
            pyglet.clock.get_fps())
        
        # Calculating debug label width and updating its background accordingly (width/height ratio for Arial=0.52 so we multiply with 1.52)
        self.debug_background.width =  int(len(self.info_label.text)*INFO_LABEL_FONTSIZE/1.52)
        self.debug_batch.draw()


class Model(object):
    def __init__(self, batch, group):
        self.batch = batch

        self.group = group

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        #self.generate_world = generate_world(self) 
        
        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

    @property
    def currently_shown(self):
        return len(self._shown)

    def hit_test(self, position, vector, max_distance=NODE_SELECTOR):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            checked_position = normalize((x, y, z))
            if checked_position != previous and checked_position in self.world:
                return checked_position, previous
            previous = checked_position
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False if given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, block, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        block : Block object
            An instance of the Block class.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = block
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            neighbor = (x + dx, y + dy, z + dz)
            if neighbor not in self.world:
                continue
            if self.exposed(neighbor):
                if neighbor not in self.shown:
                    self.show_block(neighbor)
            else:
                if neighbor in self.shown:
                    self.hide_block(neighbor)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        block = self.world[position]
        self.shown[position] = block
        if immediate:
            self._show_block(position, block)
        else:
            self._enqueue(self._show_block, position, block)

    def _show_block(self, position, block):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        block : Block instance
            An instance of the Block class

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
                                               ('v3f/static', vertex_data),
                                               ('t2f/static', block.tex_coords))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dy in [0]:  # range(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()


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