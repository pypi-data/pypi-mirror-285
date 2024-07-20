from .game import *


class Button(ClickableRect):
    """
    A simple flat button with text.
    """

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: Tuple[int, int, int, int],
        text: str,
        font_size: int = 20,
        text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        font: str = None,
        callback: callable = None,
    ):
        super().__init__(x, y, w, h, color)
        self.text = Text(
            x + w // 2,
            y + h // 2,
            text,
            font_size=font_size,
            font_name=font,
            color=text_color,
        )
        self.callback = callback

    def draw(self):
        """
        Draw the button and the text.
        """
        super().draw()
        self.text.draw()

    def onclick(self, x, y):
        """
        Calls the callback function if it is set.
        """
        if self.callback:
            self.callback()


class SpriteButton(Sprite):
    """
    A simple button that uses a sprite instead. Has optional text rendering.
    """

    def __init__(
        self,
        x,
        y,
        sprite: str,
        render_text: bool = True,
        text: str = "Change me!",
        font_size: int = 20,
        font: str = "Verdana",
        text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        scale: float = 3.0,
        callback: callable = None,
    ):
        super().__init__(sprite, x, y, scale=scale)
        self.callback = callback
        self.render_text = render_text
        self.text, self.font_size, self.font, self.text_color = (
            text,
            font_size,
            font,
            text_color,
        )

    def post_init(self):
        super().post_init()
        if self.render_text:
            self.text = Text(
                self.x + self.sprite.width * 1.5,
                self.y + self.sprite.height * 1.5,
                self.text,
                font_size=self.font_size,
                font_name=self.font,
                color=self.text_color,
            )

    def draw(self):
        super().draw()
        if hasattr(self, "text"):
            self.text.draw()

    def on_mousepress(self, x: int, y: int, button: int, modifiers: int):
        if self.contains(x, y):
            self.game.log("Button clicked!")
            if self.callback:
                self.callback()
