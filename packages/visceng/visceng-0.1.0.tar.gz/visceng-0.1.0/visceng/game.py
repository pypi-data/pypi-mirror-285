import pyglet
from typing import List, Tuple
from pyglet.clock import Clock
import pyglet.clock
from pyglet import shapes
import traceback
import inspect
import os
import importlib.util
import sys
import datetime
import random


def is_colliding(obj1, obj2):
    """
    Check if two objects are colliding. Assumes that the objects have x, y, width, and height attributes. Operates in screen-space.
    """
    return (
        obj1.x < obj2.x + obj2.width
        and obj1.x + obj1.width > obj2.x
        and obj1.y < obj2.y + obj2.height
        and obj1.y + obj1.height > obj2.y
    )


class GameObject:
    """
    A base class for all game objects. Contains methods for drawing, updating, and handling input.
    Can alternatively be used as a mixin for other classes, or as a representation of a point in screen-space.
    """

    def __init__(self, x: int, y: int):
        """
        Initializes the game object with a position in screen-space.
        """
        self.x: int = x
        self.y: int = y
        self.game: Game = None

    def draw(self):
        """
        Draws the game object. Must be overridden by subclasses.
        What to do here:
        - Draw the object using pyglet's drawing functions.
        - Use the object's x, y, width, height, etc. to draw it.
        What **not** to do here:
        - Update the object's position, size, etc.
        - Handle physics, movement
        """
        pass

    def update(self, dt: float):
        """
        Updates the game object. Must be overridden by subclasses.
        What do do here:
        - Update the object's position, size, etc.
        - Handle physics, movement, using the delta time (dt).
        - Handle any other logic.
        What **not** to do here:
        - Draw the object.
        """
        pass

    def post_init(self):
        """
        Runs after the object has its reference to the game set. This method should only be overridden if you need to access the Game object for initialization.
        See: visceng.game.Game.add
        """
        pass

    def on_keypress(self, symbol: int, modifiers: int):
        """
        Called when a key is pressed. Uses pyglet's key constants for symbols.
        """
        pass

    def on_keyrelease(self, symbol: int, modifiers: int):
        """
        Called when a key is released. Uses pyglet's key constants for symbols.
        """
        pass

    def on_mousepress(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when a mouse button is pressed. Uses pyglet's mouse button constants for buttons.
        """
        pass

    def on_mouserelease(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when a mouse button is released. Uses pyglet's mouse button constants for buttons.
        """
        pass

    def on_mousemove(self, x: int, y: int, dx: int, dy: int):
        """
        Called when the mouse is moved.
        """
        pass


class AnchoredObject(GameObject):
    """
    A game object that is anchored relative to a point on the screen. Useful for UI elements and things that need to stay where they are.
    """

    def __init__(self, anchor: str):
        self.anchor = anchor
        self.anchor_coords = None
        self.offset: tuple = (0, 0)
        super().__init__(0, 0)

    def update(self, dt: float):
        self.anchor_coords = self.game.coords.get(self.anchor)
        self.x = self.anchor_coords[1] + self.offset[0]
        self.y = self.anchor_coords[0] + self.offset[1]

    def set_anchor(self, anchor: str):
        self.anchor = anchor


class Text(GameObject):
    """
    A simple screen-space text object. Can be used for debugging or UI elements.
    """

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        font_size: int = 12,
        font_name: str = "Verdana",
        color: tuple = (255, 255, 255, 255),
    ):
        super().__init__(x, y)
        self.text = pyglet.text.Label(
            text,
            x=x,
            y=y,
            font_size=font_size,
            font_name=font_name,
            anchor_x="center",
            anchor_y="center",
            color=color,
        )

    def draw(self):
        self.text.draw()


class AnchoredText(AnchoredObject):
    """
    Anchored text object, optimal for UI.
    """

    def __init__(
        self,
        anchor: str,
        text: str,
        font_size: int = 12,
        font_name: str = "Verdana",
        color: tuple = (255, 255, 255, 255),
    ):
        super().__init__(anchor)
        self.anchor = anchor
        self.text_str = text
        self.font_size = font_size
        self.font_name = font_name
        self.color = color

    def post_init(self):
        anchor_x, anchor_y = self.game.coords.anchors_for(self.anchor)
        self.text = pyglet.text.Label(
            self.text_str,
            x=0,
            y=0,
            font_size=self.font_size,
            font_name=self.font_name,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=self.color,
        )
        self.offset = (
            (0, -(self.text.content_height // 2))
            if "top" in self.anchor or "bottom" in self.anchor
            else (0, 0)
        )

    def update(self, dt: float):
        super().update(dt)
        self.text.x = self.x
        self.text.y = self.y
        self.text.text = self.text_str
        self.text.font_name = self.font_name
        self.text.font_size = self.font_size
        self.text.color = self.color

    def draw(self):
        self.text.draw()


class AnchoredSprite(AnchoredObject):
    """
    Anchored sprite object. Useful for UI elements - for interactivity, see `visceng.ui.SpriteButton`.
    """

    def __init__(self, anchor: str, image_id: str, scale: float = 1.0):
        super().__init__(anchor)
        self.anchor = anchor
        self.image_id = image_id
        self.scale = scale
        self.sprite = None

    def post_init(self):
        self.sprite = pyglet.sprite.Sprite(
            self.game.assets.get(self.image_id), x=self.x, y=self.y
        )
        self.sprite.scale = self.scale
        self.offset = (
            (0, -(self.sprite.height // 2))
            if "top" in self.anchor or "bottom" in self.anchor
            else (0, 0)
        )

    def update(self, dt: float):
        super().update(dt)
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = self.scale

    def draw(self):
        self.sprite.draw()


class FPSCounter(AnchoredText):
    """
    An anchored FPS counter that is placed in the bottom left corner of the screen. Added to scenes by default, but can be disabled.
    """

    def __init__(self):
        super().__init__("bottom_left", "FPS: 0")
        self.fps = 0
        self.EPSILON = 1e-6
        self.current_window = []

    def update(self, dt: float):
        self.fps = round((dt + self.EPSILON) ** -1)
        self.current_window.append(self.fps)
        if len(self.current_window) > 128:
            self.current_window.pop(0)
        self.fps = round(sum(self.current_window) / len(self.current_window))
        self.text.text = f"FPS: {self.fps}"

    def draw(self):
        self.text.draw()


class Viewport:
    """
    Represents a viewport in a Scene. WorldObjects can be added to the viewport instead of the game directly, and are drawn in world-space relative to the viewport.
    Objects that are too far off-screen are culled based on a threshold, with draws (but not updates!) skipped.
    """

    def __init__(self, use_debug_movement: bool = False):
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.use_debug_movement = use_debug_movement
        self.move_speed = 500
        self.game: "Game" = None
        self.preshake_location = (0, 0)
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_callback = None
        self.shake_calledback = False
        self._last_shake_move = (0, 0)

    def shake(
        self,
        intensity: int,
        duration: float,
        restore_original_position: bool = True,
        callback: callable = None,
    ):
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_callback = callback
        self.shake_calledback = False
        self.preshake_location = (self.x, self.y)

    def update(self, dt: float):
        if self.shake_duration > 0:
            self.shake_duration -= dt
            move_x = random.randint(-self.shake_intensity, self.shake_intensity)
            move_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.x += move_x - self._last_shake_move[0]
            self.y += move_y - self._last_shake_move[1]
            self._last_shake_move = (move_x, move_y)
        elif not self.shake_calledback:
            self.x, self.y = self.preshake_location
            if self.shake_callback:
                self.shake_callback()
            self.shake_calledback = True
        if self.use_debug_movement:
            if pyglet.window.key.LEFT in self.game.keys:
                self.x -= self.move_speed * dt
            if pyglet.window.key.RIGHT in self.game.keys:
                self.x += self.move_speed * dt
            if pyglet.window.key.UP in self.game.keys:
                self.y += self.move_speed * dt
            if pyglet.window.key.DOWN in self.game.keys:
                self.y -= self.move_speed * dt

    def update_size(self, width: int, height: int):
        self.game.log(f"Updating viewport to {width}x{height}")
        self.width = width
        self.height = height
        if self.use_debug_movement:
            self.x += 1
            self.y -= 1

    def update_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x <= self.width and 0 <= y <= self.height

    def contains_threshold(self, x: int, y: int, threshold: int) -> bool:
        return (
            x < -threshold
            or x > self.width + threshold
            or y < -threshold
            or y > self.height + threshold
        )

    def should_draw(self, obj: "WorldObject") -> bool:
        if obj.cull_threshold == -1:
            return True
        return not self.contains_threshold(obj.x, obj.y, obj.cull_threshold)

    def get_screen_pos(self, x: int, y: int) -> tuple:
        return x - self.x, y - self.y

    def add(self, obj: GameObject):
        self.game.add(obj, viewport=self)


class WorldObject(GameObject):
    """
    A game object that exists in world-space. Must be added to a Viewport to be drawn correctly.
    If the cull threshold is set to -1, the object will not be culled.
    """

    def __init__(self, x: int, y: int, cull_threshold: int = 150):
        """
        Initializes the world object with a position in world-space and a cull threshold.
        Note: the world position of a WorldObject is seperate from its screen position. If you're trying to move the object, use obj.wx and obj.wy instead of obj.x and obj.y - which are the screen-space positions and are updated by the viewport.
        """
        self.wx = x
        self.wy = y
        self.x = x
        self.y = y
        self.viewport: Viewport = None
        self.cull_threshold: int = cull_threshold

    def update(self, dt: float):
        self.x, self.y = self.viewport.get_screen_pos(self.wx, self.wy)


class WorldText(WorldObject):
    """
    A world-space text object. Useful for pop-up text (damage numbers, etc.) or anything else that needs to exist in world-space.
    """

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        cull_threshold: int = 150,
        font_size: int = 12,
        font_name: str = "Verdana",
    ):
        super().__init__(x, y, cull_threshold)
        self.text = pyglet.text.Label(
            text,
            x=x,
            y=y,
            font_size=font_size,
            font_name=font_name,
            anchor_x="center",
            anchor_y="center",
        )

    def draw(self):
        self.text.x = self.x
        self.text.y = self.y
        self.text.draw()


class BasicRect(GameObject):
    """
    A simple screen-space rectangle object. Useful for debugging or UI elements.
    """

    def __init__(self, x: int, y: int, width: int, height: int, color: tuple):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.color = color
        self.rectangle = shapes.Rectangle(x, y, width, height, color=color)

    def draw(self):
        self.rectangle.draw()

    def update(self, dt: float):
        # Update the rectangle's position if x or y have changed
        self.rectangle.color = self.color
        if self.rectangle.x != self.x or self.rectangle.y != self.y:
            self.rectangle.x = self.x
            self.rectangle.y = self.y

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
        self.rectangle.x = x
        self.rectangle.y = y

    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height
        self.rectangle.width = width
        self.rectangle.height = height

    def set_color(self, color: tuple):
        self.color = color
        self.rectangle.color = color

    def contains(self, x: int, y: int) -> bool:
        return (
            self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
        )


class AssetManager:
    """
    A simple asset loader/manager that loads assets from a directory and stores them for later use.
    """

    def __init__(self, use_texture_filter: bool = False):
        self.textures = {}
        self.audio = {}
        self.all = {}
        self.use_filter = use_texture_filter
        if not self.use_filter:
            pyglet.image.Texture.default_min_filter = pyglet.image.GL_NEAREST
            pyglet.image.Texture.default_mag_filter = pyglet.image.GL_NEAREST

    def from_dir(self, path: str) -> dict:
        res_textures = {}
        res_audio = {}
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".png"):
                    name = (
                        os.path.relpath(os.path.join(root, file), path)
                        .split(".")[0]
                        .replace("\\", "/")
                    )
                    res_textures[name] = pyglet.image.load(os.path.join(root, file))
                elif (
                    file.endswith(".wav")
                    or file.endswith(".mp3")
                    or file.endswith(".flac")
                    or file.endswith(".ogg")
                ):
                    name = (
                        os.path.relpath(os.path.join(root, file), path)
                        .split(".")[0]
                        .replace("\\", "/")
                    )
                    res_audio[name] = pyglet.media.load(
                        os.path.join(root, file), streaming=False
                    )
        self.textures.update(res_textures)
        self.audio.update(res_audio)
        self.all.update(res_textures)
        self.all.update(res_audio)
        return self.all

    def add(self, id: str, path: str) -> dict:
        if path.endswith(".png"):
            self.textures[id] = pyglet.image.load(path)
            self.all[id] = self.textures[id]
        elif (
            path.endswith(".wav")
            or path.endswith(".mp3")
            or path.endswith(".flac")
            or path.endswith(".ogg")
        ):
            self.audio[id] = pyglet.media.load(path, streaming=False)
            self.all[id] = self.audio[id]
        return self.all

    def get(self, id: str) -> pyglet.image.AbstractImage | pyglet.media.Source:
        if id in self.textures:
            return self.textures[id]
        elif id in self.audio:
            return self.audio[id]
        else:
            raise KeyError(f"Asset {id} not found.")


class Sprite(GameObject):
    """
    A simple screen-space sprite object that draws a texture by its ID.
    """

    def __init__(self, image_id: str, x: int, y: int, scale: float = 1.0):
        super().__init__(x, y)
        self.image_id = image_id
        self.scale = scale
        self.width: int = -1
        self.height: int = -1
        try:
            self.sprite = pyglet.sprite.Sprite(self.game.assets.get(image_id), x=x, y=y)
            self.orig_width = self.sprite.width
            self.orig_height = self.sprite.height
        except AttributeError:
            self.sprite = None  # wait for self.game to be set

    def post_init(self):
        if not self.sprite:
            self.sprite = pyglet.sprite.Sprite(
                self.game.assets.get(self.image_id), x=self.x, y=self.y
            )
            self.orig_width = self.sprite.width
            self.orig_height = self.sprite.height

    def draw(self):
        if self.sprite:
            self.sprite.draw()

    def update(self, dt: float):
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = self.scale
        self.width = self.sprite.width
        self.height = self.sprite.height

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y

    def set_scale(self, scale: float):
        self.scale = scale
        self.sprite.scale = scale

    def contains(
        self, x: int, y: int, accurate: bool = True, alpha_threshold: float = 0.0
    ) -> bool:
        is_within_bounds = (
            self.sprite.x <= x <= self.sprite.x + self.sprite.width
            and self.sprite.y <= y <= self.sprite.y + self.sprite.height
        )
        if not accurate or not is_within_bounds:
            return is_within_bounds
        try:
            pixel_alpha = (
                self.sprite.image.get_region(x - self.sprite.x, y - self.sprite.y, 1, 1)
                .get_image_data()
                .get_data()[3]
            )
        except IndexError:
            return False
        return is_within_bounds and pixel_alpha > alpha_threshold


class SpriteBackground(Sprite):
    """
    A sprite that is scaled to fit the window, avoiding letterboxing. Ideal for menu backgrounds or non-parallaxing backgrounds that avoid world-space.
    """

    def __init__(self, image_id: str):
        super().__init__(image_id, 0, 0)

    def update(self, dt: float):
        image_aspect_ratio = self.orig_width / self.orig_height
        window_aspect_ratio = self.game.width / self.game.height

        # Calculate scale factors for both width and height
        scale_factor_width = self.game.width / self.orig_width
        scale_factor_height = self.game.height / self.orig_height

        # Choose the smaller scale factor to fit the image without letterboxing
        if image_aspect_ratio > window_aspect_ratio:
            scale_factor = scale_factor_height
        else:
            scale_factor = scale_factor_width

        self.sprite.scale = scale_factor

        # Center the image
        self.x = (self.game.width - self.orig_width * scale_factor) / 2
        self.y = (self.game.height - self.orig_height * scale_factor) / 2

        self.sprite.x = self.x
        self.sprite.y = self.y


class WorldSprite(Sprite, WorldObject):
    """
    A sprite that exists in world-space. Must be added to a Viewport to be drawn correctly.
    """

    def __init__(
        self,
        image_id: str,
        x: int,
        y: int,
        scale: float = 1.0,
        cull_threshold: int = 150,
    ):
        Sprite.__init__(self, image_id, x, y, scale)
        WorldObject.__init__(self, x, y, cull_threshold)

    def draw(self):
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.draw()

    def update(self, dt: float):
        super().update(dt)
        self.sprite.scale = self.scale

    def set_position(self, x: int, y: int):
        super().set_position(x, y)
        self.sprite.x = self.x
        self.sprite.y = self.y

    def set_scale(self, scale: float):
        super().set_scale(scale)
        self.sprite.scale = scale


class AnimatedSprite(GameObject):
    """
    An animated screen-space sprite that draws a series of textures by their base ID and a following frame number.
    """

    def __init__(
        self,
        x: int,
        y: int,
        base_id: str,
        scale: float = 1.0,
        loop: bool = True,
        animation_fps: int = 15,
        start_at_zero: bool = False,
    ):
        """
        base_id: str - The base ID of the texture, without the frame number.
        frames: int - The number of frames in the animation.
        x: int - The x position of the sprite.
        y: int - The y position of the sprite.
        scale: float - The scale of the sprite.
        loop: bool - Whether the animation should loop. If this is False, the AnimatedSprite will remove itself from rendering after the animation has played once.
        animation_fps: int - The number of frames per second of the animation.
        """
        super().__init__(x, y)
        self.base_id = base_id
        self.scale = scale
        self.current_frame = 0 if start_at_zero else 1
        self.start_at_zero = start_at_zero
        self.sprite = None
        self.loop = loop
        self.animation_fps = animation_fps
        self.animation_timer = 0

    def _get_animation_length(self):
        """
        (Internal) Get the number of frames in the animation.
        """
        frames = self.current_frame
        while True:
            if f"{self.base_id}_{frames}" in self.game.assets.textures:
                frames += 1
            else:
                break
        self.game.log("Found animation with " + str(frames) + " frames.")
        return frames

    def post_init(self):
        self.frames = self._get_animation_length()
        self.sprite = pyglet.sprite.Sprite(
            self.game.assets.get(f"{self.base_id}_{self.current_frame}"),
            x=self.x,
            y=self.y,
        )

    def draw(self):
        self.sprite.draw()

    def update(self, dt: float):
        self.animation_timer += dt
        if self.animation_timer >= 1 / self.animation_fps:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= self.frames:
                if self.loop:
                    self.current_frame = 0 if self.start_at_zero else 1
                else:
                    self.game.destroy(self)
                    return
            self.sprite.image = self.game.assets.get(
                f"{self.base_id}_{self.current_frame}"
            )
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = self.scale


class WorldAnimatedSprite(WorldObject):
    """
    An animated sprite that exists in world-space. Must be added to a Viewport to be drawn correctly.
    """

    def __init__(
        self,
        x: int,
        y: int,
        base_id: str,
        scale: float = 1.0,
        loop: bool = True,
        animation_fps: int = 15,
        start_at_zero: bool = False,
        cull_threshold: int = 150,
    ):
        WorldObject.__init__(self, x, y, cull_threshold)
        self.base_id = base_id
        self.scale = scale
        self.current_frame = 0 if start_at_zero else 1
        self.start_at_zero = start_at_zero
        self.sprite = None
        self.loop = loop
        self.animation_fps = animation_fps
        self.animation_timer = 0

    def _get_animation_length(self):
        """
        (Internal) Get the number of frames in the animation.
        """
        frames = self.current_frame
        while True:
            if f"{self.base_id}_{frames}" in self.game.assets.textures:
                frames += 1
            else:
                break
        self.game.log("Found animation with " + str(frames) + " frames.")
        return frames

    def post_init(self):
        self.frames = self._get_animation_length()
        self.sprite = pyglet.sprite.Sprite(
            self.game.assets.get(f"{self.base_id}_{self.current_frame}"),
            x=self.x,
            y=self.y,
        )

    def draw(self):
        self.sprite.draw()

    def update(self, dt: float):
        super().update(dt)
        self.animation_timer += dt
        if self.animation_timer >= 1 / self.animation_fps:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= self.frames:
                if self.loop:
                    self.current_frame = 0 if self.start_at_zero else 1
                else:
                    self.game.destroy(self)
                    return
            self.sprite.image = self.game.assets.get(
                f"{self.base_id}_{self.current_frame}"
            )
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = self.scale


class AnchoredAnimatedSprite(AnchoredObject):
    """
    An anchored animated sprite object. Useful for background animated elements.
    """

    def __init__(
        self,
        anchor: str,
        base_id: str,
        scale: float = 1.0,
        loop: bool = True,
        animation_fps: int = 15,
        start_at_zero: bool = False,
    ):
        super().__init__(anchor)
        self.base_id = base_id
        self.scale = scale
        self.current_frame = 0 if start_at_zero else 1
        self.start_at_zero = start_at_zero
        self.sprite = None
        self.loop = loop
        self.animation_fps = animation_fps
        self.animation_timer = 0

    def _get_animation_length(self):
        """
        (Internal) Get the number of frames in the animation.
        """
        frames = self.current_frame
        while True:
            if f"{self.base_id}_{frames}" in self.game.assets.textures:
                frames += 1
            else:
                break
        self.game.log("Found animation with " + str(frames) + " frames.")
        return frames

    def post_init(self):
        self.frames = self._get_animation_length()
        self.sprite = pyglet.sprite.Sprite(
            self.game.assets.get(f"{self.base_id}_{self.current_frame}"), x=self.x, y=self.y
        )

    def draw(self):
        self.sprite.draw()

    def update(self, dt: float):
        self.animation_timer += dt
        if self.animation_timer >= 1 / self.animation_fps:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= self.frames:
                if self.loop:
                    self.current_frame = 0 if self.start_at_zero else 1
                else:
                    self.game.destroy(self)
                    return
            self.sprite.image = self.game.assets.get(
                f"{self.base_id}_{self.current_frame}"
            )
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = self.scale


class ClickableRect(BasicRect):
    """
    A clickable rectangle object. Override the onclick method to handle clicks.
    """

    def onclick(self, x: int, y: int):
        self.game.log("Override me!")

    def on_mousepress(self, x: int, y: int, button: int, modifiers: int):
        if self.contains(x, y):
            self.onclick(x, y)


class CoordAnchors:
    """
    A class that stores the anchor points for the screen. You probably don't have to touch this.
    """

    def __init__(self, h: int, w: int):
        self.height = h
        self.width = w

    def anchors_for(self, anchor: str) -> Tuple[str, str]:
        """
        anchor_x : str
            Anchor point of the X coordinate: one of "left", "center" or "right".
        anchor_y : str
            Anchor point of the Y coordinate: one of "bottom", "baseline", "center" or "top".
        """

        return {
            "center": ("center", "center"),
            "top_left": ("left", "top"),
            "top_right": ("right", "top"),
            "bottom_left": ("left", "bottom"),
            "bottom_right": ("right", "bottom"),
            "top_center": ("center", "center"),
            "bottom_center": ("center", "bottom"),
            "left_center": ("left", "center"),
            "right_center": ("right", "center"),
        }[anchor]

    def update(self, h: int, w: int):
        self.height = h
        self.width = w

    def get(self, name: str):
        return getattr(self, name)()

    def center(self):
        return self.width // 2, self.height // 2

    def top_left(self):
        return 0, self.height

    def top_right(self):
        return self.width, self.height

    def bottom_left(self):
        return 0, 0

    def bottom_right(self):
        return self.width, 0

    def top_center(self):
        return self.width, self.height // 2

    def bottom_center(self):
        return self.width // 2, 0

    def left_center(self):
        return 0, self.height // 2

    def right_center(self):
        return self.width, self.height // 2


class Scene:
    """
    A base class for all scenes. Contains methods for setting up and tearing down scenes, as well as loading and unloading scenes.
    """

    def __init__(self, game: "Game"):
        """
        (__init__) Sets a reference to the game object for the scene to use. You don't need to touch this.
        """
        self.game = game

    def setup(self):
        """Set up the scene with specific game objects and configurations."""
        pass

    def post_setup(self):
        """Run after the scene has been set up."""
        pass

    def teardown(self):
        """Clean up the scene, removing all game objects and configurations."""
        self.game.clear_scene()

    def load(self):
        """Load the scene by first clearing the current scene, then setting up the new scene."""
        self.teardown()
        self.game.pre_load()
        self.setup()


class SceneManager:
    """
    A simple scene manager that loads scenes from a directory and stores them for later use. You don't need to touch this.
    """

    def __init__(self):
        self.scenes = {}

    def _load_file(self, file_path: str):
        module_name = os.path.basename(file_path).split(".")[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def load(self, dir: str):
        for file in os.listdir(dir):
            if file.endswith(".py"):
                module = self._load_file(os.path.join(dir, file))
                unique_name = module.__name__
                self.scenes[unique_name] = {
                    "scene": module.SCENE,
                    "start": module.START,
                }
        return self.scenes

    def get_start(self):
        for unique_name in self.scenes:
            if self.scenes[unique_name]["start"]:
                return self.scenes[unique_name]["scene"]

    def get(self, name: str):
        return self.scenes[name]["scene"]


class Game:
    """
    The main game class. Handles the game loop, input, and rendering.
    """

    def __init__(
        self,
        resizable: bool = True,
        width: int = 800,
        height: int = 600,
        title: str = "Game",
        fps_limit: int = 99999,
        fps_counter: bool = True,
        asset_dir: str = "assets",
        scene_dir: str = "scenes",
        loader: callable = None,
        log_dir: str = "logs",
        vsync: bool = False,
    ):
        """
        Initializes the game object.
        """
        self.window = pyglet.window.Window(width, height, title, resizable=resizable)
        self.window.push_handlers(
            self.on_close,
            self.on_key_press,
            self.on_key_release,
            self.on_mouse_press,
            self.on_mouse_release,
        )
        self.window.set_vsync(vsync)
        self.objects: List[dict] = []
        self.viewports: List[Viewport] = []
        self.clock = Clock()
        self.fps_limit = fps_limit
        self.running = False
        self.height = height
        self.width = width
        self.coords = CoordAnchors(width, height)
        self.assets = AssetManager()
        self.assets.from_dir(asset_dir)
        self.keys: List[int] = []
        self.fps_counter = fps_counter
        self.loader = loader
        self.timescale = 1.0
        self.log_dir = log_dir
        self.current_scene = None
        os.makedirs(log_dir, exist_ok=True)
        self.log_f = open(
            os.path.join(log_dir, f"visceng-{self._unix_time()}.log"), "w"
        )
        self._last_resolution = (width, height)
        if loader:
            self.log("WARN: Loaders are not yet supported. Sorry!")
        self.scenes = SceneManager()
        self.scenes.load(scene_dir)
        self.start_scene = self.scenes.get_start()
        self.load_scene(self.start_scene)
        self.called_scene_init = False

    def _unix_time(self) -> int:
        """
        (Internal) Get the current time in seconds since the Unix epoch.
        """
        return (
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).total_seconds()

    def pre_load(self):
        """
        Function that runs before loading a scene. Can be overridden to add custom behavior.
        """
        if self.fps_counter:
            self.add(FPSCounter(), "_fps_counter")

    def post_load(self):
        """
        Function that runs after loading a scene. Can be overridden to add custom behavior.
        """
        pass

    def load_scene(self, scene: Scene | str):
        """
        Load a scene by its class or name. If a string is passed, the scene will be fetched from the scene manager.
        """
        self.current_scene = None
        self.called_scene_init = False
        if isinstance(scene, str):
            self.log(f"Searching for scene {scene}...")
            try:
                scene = self.scenes.get(scene)
            except:
                self.log(
                    f"Scene {scene} not found. Available scenes: {', '.join(self.scenes.scenes.keys())}"
                )
                return
        self.log(f"Loading scene {scene.__qualname__}")
        self.current_scene = scene(self)  # TODO: loading screen
        self.current_scene.load()
        self.post_load()
        self.log(f"Scene {scene.__qualname__} loaded.")

    def do_for_every_enabled(self, func, skip_viewports: bool = False):
        """
        (Internal) Runs a function for every enabled object in the game.
        """
        for obj in self.objects:
            if obj["enabled"]:
                if skip_viewports and obj["viewport"]:
                    continue
                func(obj["object"])

    def on_update(self, dt: float):
        """
        Update function that runs every frame. Calls the update method on every enabled object, then calls the on_draw method.
        """
        dt *= self.timescale  # HACK: this should be done in the clock
        if not self.called_scene_init and self.current_scene:
            self.current_scene.post_setup()
            self.called_scene_init = True
        self.width = self.window.width
        self.height = self.window.height
        if self._last_resolution != (self.width, self.height):
            self._last_resolution = (self.width, self.height)
            self.log(f"Resolution changed to {self.width}x{self.height}")
            self.coords.update(self.width, self.height)
            for viewport in self.viewports:
                viewport.update_size(self.width, self.height)
        self.coords.update(self.width, self.height)
        self.do_for_every_enabled(lambda obj: obj.update(dt))
        for viewport in self.viewports:
            viewport.update(dt)
        self.on_draw()

    def on_draw(self):
        """
        Draw function that runs every frame. Calls the draw method on every enabled object. Skips viewports, and lets them handle their own drawing (see `Viewport`).
        """
        self.window.clear()
        for viewport in self.viewports:
            for obj in self.objects:
                if obj["viewport"] == viewport:
                    if viewport.should_draw(obj["object"]):
                        obj["object"].draw()
        self.do_for_every_enabled(lambda obj: obj.draw(), skip_viewports=True)

    def run(self) -> int:
        """
        Run the game loop. Returns 0 if the game exits normally, 1 if an exception is raised - exit codes are passed directly back to the shell.
        """
        if self.fps_counter:
            self.add(FPSCounter(), "_fps_counter")
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick()
                self.on_update(dt)
                self.window.dispatch_events()
                self.window.flip()
            return 0
        except:
            traceback.print_exc()
            self.log("Fatal error!")
            self.log(traceback.format_exc())
            return 1

    def add(self, obj: GameObject, id: str = None, viewport: Viewport = None) -> str:
        """
        Add an object to the game. Optionally, set an ID for the object, and add it to a viewport.
        Returns the ID of the object - if no ID is set, the ID will be a unique integer in string form.
        """
        id = id or str(len(self.objects))
        self.objects.append(
            {"object": obj, "enabled": True, "id": id, "viewport": viewport}
        )
        obj.game = self  # set reference to avoid extra params
        if viewport:
            obj.viewport = viewport
        obj.post_init()
        return id

    def add_viewport(self, viewport: Viewport):
        """
        Adds a Viewport to the game. Viewports are used to render world-space objects, and have their own culling system - see `visceng.game.Viewport`.
        """
        self.viewports.append(viewport)
        viewport.game = self
        viewport.update_size(self.width, self.height)

    def get(self, id: str) -> GameObject:
        """
        Gets a GameObject by its assigned ID. Raises a ValueError if the object is not found.
        """
        for obj in self.objects:
            if obj["id"] == id:
                return obj["object"]
        raise ValueError(f"Object with id {id} not found.")

    def enable(self, id: str) -> GameObject:
        """
        Enables a GameObject by its assigned ID. Returns the object.
        Disabled objects are not updated or drawn.
        """
        for obj in self.objects:
            if obj["id"] == id:
                obj["enabled"] = True
                return obj["object"]

    def disable(self, id: str) -> GameObject:
        """
        Disables a GameObject by its assigned ID. Returns the object.
        Disabled objects are not updated or drawn.
        """
        for obj in self.objects:
            if obj["id"] == id:
                obj["enabled"] = False
                return obj["object"]

    def destroy(self, id: str) -> GameObject:
        """
        Destroys and removes a GameObject from a scene by its assigned ID. Returns the object.
        """
        for obj in self.objects:
            if obj["id"] == id:
                self.objects.remove(obj)
                return obj["object"]

    def on_key_press(self, symbol: int, modifiers: int):
        """
        (Internal) Called when a key is pressed. Calls the on_keypress method on every enabled object.
        """
        if symbol not in self.keys:
            self.keys.append(symbol)
        self.do_for_every_enabled(lambda obj: obj.on_keypress(symbol, modifiers))

    def on_key_release(self, symbol: int, modifiers: int):
        """
        (Internal) Called when a key is released. Calls the on_keyrelease method on every enabled object.
        """
        try:
            self.keys.remove(symbol)
        except ValueError:
            pass
        self.do_for_every_enabled(lambda obj: obj.on_keyrelease(symbol, modifiers))

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        (Internal) Called when a mouse button is pressed. Calls the on_mousepress method on every enabled object.
        """
        self.do_for_every_enabled(
            lambda obj: obj.on_mousepress(x, y, button, modifiers)
        )

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """
        (Internal) Called when a mouse button is released. Calls the on_mouserelease method on every enabled object.
        """
        self.do_for_every_enabled(
            lambda obj: obj.on_mouserelease(x, y, button, modifiers)
        )

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """
        (Internal) Called when the mouse is moved. Calls the on_mousemove method on every enabled object.
        """
        self.do_for_every_enabled(lambda obj: obj.on_mousemove(x, y, dx, dy))

    def _log(self, *args):
        """
        (Internal) Log a message to the console with a timestamp.
        """
        print(
            f"{datetime.datetime.now().strftime('%m/%d/%Y %H:%M')} > {' '.join(map(str, args))}"
        )
        self.log_f.write(
            f"{datetime.datetime.now().strftime('%m/%d/%Y %H:%M')} > {' '.join(map(str, args))}\n"
        )

    def log(self, *args):
        """
        Logs a message to the console with a timestamp and the calling class and line number.
        Generally, you'll want to call this from within a GameObject by using `self.game.log()`.
        """
        stack = traceback.extract_stack()
        caller_frame = next(
            (
                frame
                for frame in reversed(stack[:-1])
                if frame.filename != __file__ or frame.name != "log"
            ),
            None,
        )
        if caller_frame:
            caller_locals = inspect.currentframe().f_back.f_locals
            if "self" in caller_locals:
                caller_class = caller_locals["self"].__class__.__name__
            else:
                caller_class = "Unknown"
            caller_len = len(f"{caller_class}@{caller_frame.lineno}")
            self._log(
                f"{caller_class}@{caller_frame.lineno}{' ' * (12-caller_len)} >", *args
            )
        else:
            self._log("Unknown >", *args)

    def on_close(self):
        """
        Runs when the window is closed. Stops the game loop. Can be overridden to add custom behavior.
        """
        self.running = False

    def clear_scene(self):
        """
        Clears the current scene by removing all objects and viewports, resetting any possibly changed variables to their default state.
        Note: If you're changing the game's variables, you should override this method and reset them to their default state.
        """
        self.current_scene = None
        self.called_scene_init = False
        self.timescale = 1.0
        self.objects.clear()
        self.viewports.clear()
        self.clock = Clock()
        self.log("Scene cleared and reset to default state.")

    def remove(self, obj: GameObject):
        """
        Removes an object from the game.
        """
        for obj in self.objects:
            if obj["object"] == obj:
                self.objects.remove(obj)
