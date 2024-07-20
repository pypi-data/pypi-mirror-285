from .game import *
from typing import List, Tuple
import pyglet
import random


class Decor:
    """
    Represents a randomly-spawning decoration on a tile.
    """

    def __init__(
        self,
        texture: str,
        chance: float,
        base_offset: Tuple[int, int],
        generation_faces: List[str] = ["top"],
        random_axies: Tuple[Tuple[int, int], Tuple[int, int]] = ((0, 0), (0, 0)),
    ):
        """
        Create a decoration with a texture, spawn chance, base offset, and random offset ranges.
        generation_faces is a list of faces on which the decoration can spawn - it can be any of:
        - "top"
        - "bottom"
        - "left"
        - "right"
        - "top_left"
        - "top_right"
        - "bottom_left"
        - "bottom_right"
        - "all"
        """
        self.texture_id = texture
        self.chance = chance
        self.base_offset = base_offset
        self.random_axies = random_axies
        self.generation_faces = generation_faces

    def generate(self) -> Tuple[pyglet.image.AbstractImage, Tuple[int, int]]:
        """
        Generate a decoration at a random offset within the specified ranges.
        """
        return self.game.assets.get(self.texture_id), (
            self.base_offset[0]
            + random.randint(self.random_axies[0][0], self.random_axies[0][1]),
            self.base_offset[1]
            + random.randint(self.random_axies[1][0], self.random_axies[1][1]),
        )


class Tile:
    """
    Represents a type of tile in a tilemap.
    """

    def __init__(
        self,
        texture: str,
        game: Game,
        name: str | None = None,
        decor: List[Decor] = [],
        solid: bool = True,
        multi_decor: bool = False,
    ):
        self.texture_id = texture
        self.game = game
        game.log(
            f"Loading texture {texture} for tile \"{name if name else 'unnamed'}\".."
        )
        self.texture = game.assets.get(texture)
        self.solid = solid
        self.decor = decor

    def _generate_decor(
        self, nearby_states: List[List[bool]]
    ) -> List[Tuple[pyglet.image.AbstractImage, Tuple[int, int]]]:
        """
        (Internal) Generate decorations for the tile.
        """
        max_percent = 0
        for d in self.decor:
            max_percent += d.chance
        if max_percent < 100:
            max_percent = 100
        random_percent = random.randint(0, max_percent)
        decor = []
        random.shuffle(self.decor)
        for d in self.decor:
            if d.generation_faces != ["all"]:
                # HACK: ew, ugly
                if nearby_states[0][1] and "top" not in d.generation_faces:
                    continue
                if nearby_states[2][1] and "bottom" not in d.generation_faces:
                    continue
                if nearby_states[1][0] and "left" not in d.generation_faces:
                    continue
                if nearby_states[1][2] and "right" not in d.generation_faces:
                    continue
                if nearby_states[0][0] and "top_left" not in d.generation_faces:
                    continue
                if nearby_states[0][2] and "top_right" not in d.generation_faces:
                    continue
                if nearby_states[2][0] and "bottom_left" not in d.generation_faces:
                    continue
                if nearby_states[2][2] and "bottom_right" not in d.generation_faces:
                    continue
            if random_percent <= d.chance:
                decor.append(d.generate())
                if not self.multi_decor:
                    break
            random_percent -= d.chance
        return decor

    def to_textures(self, nearby_states: List[List[bool]]) -> Tuple[
        pyglet.image.AbstractImage,
        List[Tuple[pyglet.image.AbstractImage, Tuple[int, int]]],
    ]:
        """
        Get the texture and randomly-generated decorations for the tile.
        """
        return self.texture, self._generate_decor(nearby_states)

    def __repr__(self) -> str:
        return f"Tile({self.texture_id}, solid={self.solid}, decor={self.decor})"


class Tilemap(WorldObject):
    """
    Renders a tilemap in world-space. Inherits from WorldObject, but does not cull by default - you can change this by setting cull_threshold to any positive value.
    Note: there is no class for screen-space tilemaps because there is realistically no need for it. If, for some horrible reason, you need screen-space tilemaps, you should create a stationary Viewport and add a Tilemap to it.
    """

    def __init__(
        self,
        x: int,
        y: int,
        tiles: List[Tile],
        map: List[List[int]],
        tile_size: int = 16,
        scale: float = 3.0,
    ):
        super().__init__(x, y, cull_threshold=-1)
        self.tile_size = tile_size
        self.scale = scale
        self.tiles = tiles
        self.map = map
        self.height = len(map) * tile_size * scale
        self.width = len(map[0]) * tile_size * scale
        self.t_height = len(map)
        self.t_width = len(map[0])
        self.batch = pyglet.graphics.Batch()
        self.sprites = []

    def post_init(self):
        """
        Creates sprites post-initialization (for game logging)
        """
        self._create_sprites()

    def is_solid(self, x: int, y: int) -> bool:
        """
        Check if a tile coordinate is solid.
        """
        try:
            return self.map[y][x] != -1 and self.tiles[self.map[y][x]].solid
        except IndexError:
            return False

    def _create_sprites(self):
        """
        (Internal) Create sprites for each tile with scaling and add them to the batch.
        """
        self.game.log(
            f"Generating sprites for {len(self.map)}x{len(self.map[0])} tilemap."
        )
        for y, row in enumerate(self.map):
            for x, tile_index in enumerate(row):
                if tile_index != -1:
                    nearby_states = [
                        [
                            self.is_solid(x, y - 1),
                            self.is_solid(x, y),
                            self.is_solid(x, y + 1),
                        ],
                        [self.is_solid(x - 1, y), True, self.is_solid(x + 1, y)],
                        [
                            self.is_solid(x - 1, y - 1),
                            self.is_solid(x - 1, y),
                            self.is_solid(x - 1, y + 1),
                        ],
                    ]
                    textures = self.tiles[tile_index].to_textures(nearby_states)
                    img = textures[0]
                    decor = textures[1]
                    sprite = pyglet.sprite.Sprite(
                        img,
                        x=self.x + (x * self.tile_size * self.scale),
                        y=self.y + (y * self.tile_size * self.scale),
                        batch=self.batch,
                    )
                    sprite.scale = self.scale
                    for d in decor:
                        dec = pyglet.sprite.Sprite(
                            d[0],
                            x=self.x + (x * self.tile_size * self.scale) + d[1][0],
                            y=self.y + (y * self.tile_size * self.scale) + d[1][1],
                            batch=self.batch,
                        )
                        dec.scale = self.scale
                    self.sprites.append(sprite)

    def draw(self):
        """Draw the tilemap using the batch, considering dynamic base screen positions."""
        for y, row in enumerate(self.map):
            for x, tile_index in enumerate(row):
                index = y * self.t_width + x
                if 0 <= index < len(self.sprites) and self.sprites[index] is not None:
                    new_x = self.x + (x * self.tile_size * self.scale)
                    new_y = self.y + (y * self.tile_size * self.scale)
                    self.sprites[index].x = new_x
                    self.sprites[index].y = new_y
        self.batch.draw()

    def world_to_tile(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert world coordinates to tile coordinates.
        """
        return int(x // (self.tile_size * self.scale)), int(
            y // (self.tile_size * self.scale)
        )

    def collides(self, x: int, y: int) -> bool:
        """
        Check if a world coordinate collides with a solid tile.
        """
        tx, ty = self.world_to_tile(x, y)
        if 0 <= ty < len(self.map) and 0 <= tx < len(self.map[0]):
            return self.map[ty][tx] != -1
        return False

    def get_tile(self, x: int, y: int) -> int:
        """
        Get the tile index at a world coordinate.
        """
        tx, ty = self.world_to_tile(x, y)
        return self.map[ty][tx]

    def set_tile(self, x: int, y: int, tile: int):
        """
        Set the tile at a world coordinate, and update sprite.
        """
        tx, ty = self.world_to_tile(x, y)
        self.map[ty][tx] = tile
        self._update_sprite(tx, ty, tile)

    def get_tile_at(self, tx: int, ty: int) -> int:
        """
        Get the tile index at a tile coordinate.
        """
        return self.map[ty][tx]

    def set_tile_at(self, tx: int, ty: int, tile: int):
        """
        Set the tile at a tile coordinate, and update sprite.
        """
        self.map[ty][tx] = tile
        self._update_sprite(tx, ty, tile)

    def _update_sprite(self, tx: int, ty: int, tile: int):
        """
        (Internal) Update the sprite for a specific tile.
        """
        index = ty * self.t_width + tx
        if 0 <= index < len(self.sprites):
            if tile == -1:
                if self.sprites[index] is not None:
                    self.sprites[index].delete()
                self.sprites[index] = None
            else:
                if self.sprites[index] is not None:
                    self.sprites[index].image = self.tiles[tile]
                    self.sprites[index].scale = self.scale
                else:
                    sprite = pyglet.sprite.Sprite(
                        self.tiles[tile],
                        x=self.x + (tx * self.tile_size * self.scale),
                        y=self.y + (ty * self.tile_size * self.scale),
                        batch=self.batch,
                    )
                    sprite.scale = self.scale
                    self.sprites[index] = sprite

    def get_tile_center(self, x: int, y: int) -> Tuple[int, int]:
        """
        Get the center coordinates of the tile at a world coordinate.
        """
        tx, ty = self.world_to_tile(x, y)
        return (tx + 0.5) * self.tile_size * self.scale, (
            ty + 0.5
        ) * self.tile_size * self.scale
