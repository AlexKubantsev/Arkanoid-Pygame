import os
import pygame_menu
import pygame
import sys
from random import randint


class Ball(pygame.sprite.Sprite):
    RADIUS = 10
    SPEED = 5

    def __init__(self, game_window):
        super().__init__(game_window.all_sprites)

        self.radius = Ball.RADIUS
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.speed = Ball.SPEED

    def draw(self, surf):
        pygame.draw.ellipse(surf, (255, 0, 0), self.rect)

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_pos(self):
        return self.rect.x, self.rect.y

    def get_radius(self):
        return self.radius

    def update(self, direction_x, direction_y):
        self.rect.x += direction_x * self.speed
        self.rect.y += direction_y * self.speed


class Block(pygame.sprite.Sprite):
    WIDTH = 60
    HEIGHT = 30
    INDENT = 10

    def __init__(self, game_window, x=0, y=0):
        super().__init__(game_window.all_sprites)
        self.width = Block.WIDTH
        self.height = Block.HEIGHT

        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, surf):
        pygame.draw.rect(surf, (255, 0, 0), self.rect)


class Paddle(pygame.sprite.Sprite):
    WIDTH = 90
    HEIGHT = 7
    SPEED = 10

    def __init__(self, game_window):
        super().__init__(game_window.all_sprites)
        self.width, self.height = Paddle.WIDTH, Paddle.HEIGHT
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.speed = Paddle.SPEED
        self.win_width, self.win_height = game_window.get_window_size()

    def move_paddle(self, direction):
        if direction < 0 and self.rect.x > 0:
            self.rect.x += direction * self.speed
        elif direction > 0 and self.rect.x < self.win_width - self.width:
            self.rect.x += direction * self.speed

    def draw(self, surf):
        pygame.draw.rect(surf, (255, 0, 0), self.rect)

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_pos(self):
        return self.rect.x, self.rect.y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


class EndGameWindow:
    def __init__(self, game_window):
        game_window.screen.fill((0, 0, 0))
        game_window.running = False


class GameWindow:
    FPS = 60
    N_BLOCKS = 5
    M_BLOCKS = 11

    def __init__(self, width, height, screen):
        self.width = width
        self.height = height
        self.opened_menu = None
        self.screen = screen

    def start_game(self):
        self.opened_menu.clear()
        self.all_sprites = pygame.sprite.Group()
        self.running = True
        self.clock = pygame.time.Clock()
        self.paddle = Paddle(self)
        self.paddle.set_pos(self.width // 2, 0.9 * self.height)
        self.is_key_downed = False
        self.paddle_direction = 1
        self.ball = Ball(self)
        self.ball.set_pos(self.paddle.rect.x, self.paddle.rect.y - self.ball.radius * 2)

        self.ball_x_direction = self.ball_y_direction = 1
        # block = Block(self)
        self.blocks_placement()
        while self.running:
            self.event_handler()
            if self.is_key_downed:
                self.paddle.move_paddle(self.paddle_direction)
            self.screen.fill((0, 0, 0))
            self.ball.update(self.ball_x_direction, self.ball_y_direction)
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self.win_lost_detector()
            block_hit_index = self.ball.rect.collidelist(list(map(lambda x: x.rect, self.blocks)))
            self.blocks_collision_handler(block_hit_index)
            self.blocks_draw()
            self.collision_handler()

            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(GameWindow.FPS)

    def get_window_size(self):
        return self.width, self.height

    def win_lost_detector(self):
        if not self.blocks:
            EndGameWindow(self)
        if self.ball.rect.y > self.paddle.rect.y + self.paddle.rect.h:
            EndGameWindow(self)

    def collision_handler(self):
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball_y_direction > 0:
            self.collision_detector(self.paddle.rect)
        x, y = self.ball.get_pos()
        r = self.ball.get_radius()
        if x + r >= self.width:
            self.ball_x_direction = -self.ball_x_direction
        if y + r >= self.height:
            self.ball_y_direction = -self.ball_x_direction
        if x - r <= 0:
            self.ball_x_direction = -self.ball_x_direction
        if y - r <= 0:
            self.ball_y_direction = -self.ball_y_direction

    def blocks_placement(self):
        self.blocks = [
            Block(self, i * (Block.WIDTH + Block.INDENT), j * (Block.HEIGHT + Block.INDENT)) for j in
            range(GameWindow.N_BLOCKS) for i in range(GameWindow.M_BLOCKS)]

    def blocks_draw(self):
        for block in self.blocks:
            block.draw(self.screen)

    def blocks_collision_handler(self, index):
        if index != -1:
            block_rect = self.blocks.pop(index).rect
            self.collision_detector(block_rect)

    def collision_detector(self, rect):
        if self.ball_x_direction < 0:
            dx = self.ball.rect.right - rect.left
        else:
            dx = rect.right - self.ball.rect.left
        if self.ball_y_direction < 0:
            dy = self.ball.rect.bottom - rect.top
        else:
            dy = rect.bottom - self.ball.rect.top

        if abs(dx - dy) < 10:
            self.ball_x_direction, self.ball_y_direction = -self.ball_x_direction, -self.ball_y_direction
        elif dx > dy:
            self.ball_y_direction = -self.ball_y_direction
        elif dx < dy:
            self.ball_x_direction = -self.ball_x_direction

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                self.is_key_downed = True
                if event.key == pygame.K_RIGHT:
                    self.paddle_direction = 1
                elif event.key == pygame.K_LEFT:
                    self.paddle_direction = -1
            if event.type == pygame.KEYUP:
                self.is_key_downed = False

    def set_menu(self, menu):
        self.opened_menu = menu

    @staticmethod
    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image


class Menu:
    def __init__(self, width, height, screen, game_window):
        menu = pygame_menu.Menu(height, width, "Arkanoid",
                                theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.EXIT
                                )
        game_window.set_menu(menu)
        menu.add_button("Play", game_window.start_game)
        menu.mainloop(screen)


def main():
    pygame.init()
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    game_wnd = GameWindow(width, height, screen)
    Menu(width, height, screen, game_wnd)


if __name__ == "__main__":
    main()
