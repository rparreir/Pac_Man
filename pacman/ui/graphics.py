"""Graphics layer of the game: window, images, text and keyboard.

This is the only module in the project that imports pygame. Every method of
``Graphics`` uses only pygame functions that have a MiniLibX (MLX)
equivalent:

    Graphics        pygame                        MLX
    --------------  ----------------------------  ---------------------------
    __init__        init, display.Info,           mlx_init,
                    display.set_mode,             mlx_get_screen_size,
                    display.set_caption           mlx_new_window
    put_pixel       Surface.set_at                write to mlx_get_data_addr
    draw_rectangle  put_pixel in a loop           mlx_pixel_put in a loop
    load_image      image.load                    mlx_png_file_to_image
    put_image       Surface.blit                  mlx_put_image_to_window
    put_string      font.Font, Font.render        mlx_string_put
    key_input       event.get (QUIT, KEYDOWN)     mlx_hook
    next_frame      display.flip, Clock.tick      mlx_loop (one frame)
"""
import pygame
from pathlib import Path
import sys

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


class GraphicsError(Exception):
    """Raised when the window cannot open or an image cannot be loaded."""


class Graphics:
    """Game window and drawing operations, in the style of the MLX.

    Attributes:
        screen: The window surface where everything is drawn.
        font: The font used by put_string.
        clock: The clock that keeps the game at ~60 FPS.
        w: Screen width in pixels.
        h: Screen height in pixels.
    """

    def __init__(self) -> None:
        """Start pygame and open a window almost as large as the screen."""
        pygame.init()
        pygame.display.set_caption("PAC-MAN")
        info = pygame.display.Info()
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.w, self.h = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.w - 10, self.h - 10))

    def put_pixel(self, image: pygame.Surface, x: int, y: int,
                  color: tuple[int, int, int]) -> None:
        """Paint one pixel of an image.

        Args:
            image: The image (or the screen) to paint on.
            x: Pixel column; 0 is the left edge.
            y: Pixel row; 0 is the top edge.
            color: RGB color, each value from 0 to 255.
        """
        image.set_at((x, y), color)

    def draw_rectangle(self, image: pygame.Surface, x: int,
                       y: int, width: int, height: int,
                       color: tuple[int, int, int]) -> None:
        """Draw a filled rectangle, pixel by pixel.

        Args:
            image: The image (or the screen) to draw on.
            x: Column of the top-left corner.
            y: Row of the top-left corner.
            width: Width in pixels.
            height: Height in pixels.
            color: RGB color, each value from 0 to 255.
        """
        for dy in range(height):
            for dx in range(width):
                self.put_pixel(image, x + dx, y + dy, color)

    def load_image(self, path: str) -> pygame.Surface:
        """Load a PNG image, keeping its transparency.

        Args:
            path: Path to the image file (use ASSETS_DIR / ...).

        Returns:
            The loaded image, ready to draw.

        Raises:
            GraphicsError: If the file is missing or is not a valid image.
        """
        try:
            loaded_image = pygame.image.load(path).convert_alpha()
            return loaded_image
        except (OSError, pygame.error) as exc:
            raise GraphicsError(f"Cannot load image '{path}': {exc}")


    def put_image(self, image: pygame.Surface, x: int, y: int) -> None:
        """Draw an image on the window.

        Args:
            image: The image to draw.
            x: Column of the top-left corner.
            y: Row of the top-left corner.
        """
        self.screen.blit(image, (x, y))

    def put_string(self, x: int, y: int, color: tuple[int, int, int],
                   text: str) -> None:
        """Write text on the window.

        Args:
            x: Column of the top-left corner.
            y: Row of the top-left corner.
            color: RGB color, each value from 0 to 255.
            text: The text to write.
        """
        text_image = self.font.render(text, True, color)
        self.screen.blit(text_image, (x, y))

    # testes para features futuros, para apagar
    def _load_test_assets(self) -> None:
        # fantasmas
        self.blinky = self.load_image(ASSETS_DIR / "ghosts" / "blinky.png")  # type: ignore[arg-type]  # noqa: E501
        self.pinky = self.load_image(ASSETS_DIR / "ghosts" / "pinky.png")  # type: ignore[arg-type]  # noqa: E501
        self.inky = self.load_image(ASSETS_DIR / "ghosts" / "inky.png")  # type: ignore[arg-type]  # noqa: E501
        self.clyde = self.load_image(ASSETS_DIR / "ghosts" / "clyde.png")  # type: ignore[arg-type]  # noqa: E501
        self.blue_ghost = self.load_image(ASSETS_DIR / "ghosts" / "blue_ghost.png")  # type: ignore[arg-type]  # noqa: E501
        # outros
        self.dot = self.load_image(ASSETS_DIR / "other" / "dot.png")  # type: ignore[arg-type]  # noqa: E501
        self.apple = self.load_image(ASSETS_DIR / "other" / "apple.png")  # type: ignore[arg-type]  # noqa: E501
        self.strawberry = self.load_image(ASSETS_DIR / "other" / "strawberry.png")  # type: ignore[arg-type]  # noqa: E501
        # pacman (3 frames por direção)
        self.pac_right_1 = self.load_image(ASSETS_DIR / "pacman-right" / "1.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_right_2 = self.load_image(ASSETS_DIR / "pacman-right" / "2.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_right_3 = self.load_image(ASSETS_DIR / "pacman-right" / "3.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_left_1 = self.load_image(ASSETS_DIR / "pacman-left" / "1.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_left_2 = self.load_image(ASSETS_DIR / "pacman-left" / "2.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_left_3 = self.load_image(ASSETS_DIR / "pacman-left" / "3.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_up_1 = self.load_image(ASSETS_DIR / "pacman-up" / "1.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_up_2 = self.load_image(ASSETS_DIR / "pacman-up" / "2.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_up_3 = self.load_image(ASSETS_DIR / "pacman-up" / "3.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_down_1 = self.load_image(ASSETS_DIR / "pacman-down" / "1.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_down_2 = self.load_image(ASSETS_DIR / "pacman-down" / "2.png")  # type: ignore[arg-type]  # noqa: E501
        self.pac_down_3 = self.load_image(ASSETS_DIR / "pacman-down" / "3.png")  # type: ignore[arg-type]  # noqa: E501

    # testes para features futuros, para apagar
    def _draw_test_assets(self) -> None:
        """TEMPORÁRIO: desenha os assets, uma pasta por linha."""
        # linha 1: fantasmas
        self.put_image(self.blinky, 100, 100)
        self.put_image(self.pinky, 140, 100)
        self.put_image(self.inky, 180, 100)
        self.put_image(self.clyde, 220, 100)
        self.put_image(self.blue_ghost, 260, 100)
        # linha 2: outros
        self.put_image(self.dot, 100, 140)
        self.put_image(self.apple, 140, 140)
        self.put_image(self.strawberry, 180, 140)
        # linha 3: pacman para a direita
        self.put_image(self.pac_right_1, 100, 180)
        self.put_image(self.pac_right_2, 140, 180)
        self.put_image(self.pac_right_3, 180, 180)
        # linha 4: pacman para a esquerda
        self.put_image(self.pac_left_1, 100, 220)
        self.put_image(self.pac_left_2, 140, 220)
        self.put_image(self.pac_left_3, 180, 220)
        # linha 5: pacman para cima
        self.put_image(self.pac_up_1, 100, 260)
        self.put_image(self.pac_up_2, 140, 260)
        self.put_image(self.pac_up_3, 180, 260)
        # linha 6: pacman para baixo
        self.put_image(self.pac_down_1, 100, 300)
        self.put_image(self.pac_down_2, 140, 300)
        self.put_image(self.pac_down_3, 180, 300)

    def key_input(self) -> list[str]:
        """Read this frame's events and return the keys as words.

        Arrows and WASD give "up", "down", "left" and "right"; P gives
        "pause"; Esc and the window close button give "quit". Call it once
        per frame, because it empties pygame's event queue.

        Returns:
            The words for the keys pressed since the last frame, in order.
        """
        key_list: list = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                key_list.append("quit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    key_list.append("quit")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    key_list.append("up")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    key_list.append("down")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    key_list.append("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    key_list.append("right")
                elif event.key == pygame.K_p:
                    key_list.append("pause")

        return key_list

    def next_frame(self) -> None:
        """Show what was drawn and wait for the next frame (~60 FPS)."""
        pygame.display.flip()
        self.clock.tick(60)

    def run(self) -> None:
        """TEMPORARY: demo to test the window by hand."""
        try:
            running = True
            self._load_test_assets()

            while running:
                self._draw_test_assets()
                (self.screen, 500, 500, 20, 20, (200, 200, 200))
                self.put_string(200, 200, (100, 100, 100), "TEST")
                for key in self.key_input():
                    if key == "quit":
                        running = False
                    else:
                        print(key)
                self.next_frame()
            pygame.quit()
        except KeyboardInterrupt:
            print("\nGame interrupted by the Player")
            pygame.quit()
        except GraphicsError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            pygame.quit()
            sys.exit(1)


if __name__ == "__main__":
    g = Graphics()
    g.run()
