
# import os
# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

class Graphics:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.width - 10, self.height - 10))
        pygame.display.set_caption("PAC-MAN")
        
    def put_pixel(self, image: pygame.Surface, x: int, y: int, 
                  color: tuple[int, int, int]) -> None:
        image.set_at((x, y), color)
        
    def draw_rectangle(self, image, x, y, width, height, color) -> None:
        for dy in range(height):
            for dx in range(width):
                self.put_pixel(image, x + dx, y + dy, color)

    def run(self):
        try:
            running = True
            while running:
                self.draw_rectangle(self.screen, 500, 500, 100, 100, (200, 200, 200))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                self.clock.tick(60)
            pygame.quit()
        except KeyboardInterrupt:
            print("\nGame interrupted by the Player")
            pygame.quit()


if __name__ == "__main__":
    g = Graphics()
    g.run()
