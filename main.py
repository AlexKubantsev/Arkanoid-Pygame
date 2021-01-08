import os
import pygame
import sys
from random import randint


class Score:
    FONT_SIZE = 36
    SCORE_TEXT = "Score:"
    Y_INDENT_COEFF = 0.95
    X_SCORE_COORD = 750
    FONT_SIZE_COEFF = 2

    def __init__(self, window_width, window_height):
        self.score = 0
        self.font = pygame.font.Font(None, Score.FONT_SIZE)
        self.win_width, self.win_height = window_width, window_height
        self.score_text = self.font.render(Score.SCORE_TEXT, True, (0, 255, 0))

    def up_score(self):
        self.score += 1

    def draw(self, surf):
        score = self.font.render(str(self.score), True, (0, 255, 0))
        surf.blit(score, (Score.X_SCORE_COORD, self.win_height * Score.Y_INDENT_COEFF))
        surf.blit(self.score_text,
                  (Score.X_SCORE_COORD - len(Score.SCORE_TEXT) * Score.FONT_SIZE // Score.FONT_SIZE_COEFF,
                   self.win_height * Score.Y_INDENT_COEFF))

    def get_score(self):
        return self.score


class Ball(pygame.sprite.Sprite):
    RADIUS = 10
    SPEED = 5

    def __init__(self, game_window):
        super().__init__(game_window.all_sprites)

        self.radius = Ball.RADIUS
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.speed = Ball.SPEED

    def draw(self, surf):
        pygame.draw.ellipse(surf, (0, 255, 0), self.rect)

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
    WIDTH = 64
    HEIGHT = 32
    INDENT = 10

    def __init__(self, game_window, x=0, y=0):
        super().__init__(game_window.all_sprites)
        self.width = Block.WIDTH
        self.height = Block.HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = GameWindow.load_image("block" + str(randint(1, 6)) + ".png")

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Paddle(pygame.sprite.Sprite):
    WIDTH = 90
    HEIGHT = 7
    SPEED = 10
    Y_INDENT_COEFF = 0.9

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


class GameWindow:
    FPS = 60
    N_BLOCKS = 6
    M_BLOCKS = 10
    COLLISION_EPSILON = 10
    LOSE = 0
    WIN = 1

    def __init__(self, width, height, screen):
        self.width = width
        self.height = height
        self.opened_menu = None
        self.screen = screen
        self.block_crashed_sound = pygame.mixer.Sound("data/block_crashed.mp3")
        self.paddle_touch_sound = pygame.mixer.Sound("data/paddle_touch_sound.wav")
        self.lose_sound = pygame.mixer.Sound("data/lose_sound.mp3")
        self.win_sound = pygame.mixer.Sound("data/win_sound.wav")
        self.game_background = self.load_image("game_background.png")

    def start_game(self):
        self.pause = False
        self.score = Score(self.width, self.height)
        self.all_sprites = pygame.sprite.Group()
        self.running = True
        self.clock = pygame.time.Clock()
        self.paddle = Paddle(self)
        self.paddle.set_pos(self.width // 2, Paddle.Y_INDENT_COEFF * self.height)
        self.is_key_downed = False
        self.paddle_direction = 1
        self.ball = Ball(self)
        self.ball.set_pos(self.paddle.rect.x, self.paddle.rect.y - self.ball.radius * 2)
        self.ball_x_direction = self.ball_y_direction = 1
        self.blocks_placement()
        while self.running:
            self.event_handler()
            if not self.pause:
                self.opened_menu.close_menu()
                if self.is_key_downed:
                    self.paddle.move_paddle(self.paddle_direction)
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.game_background, self.game_background.get_rect())
                self.score.draw(self.screen)
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
            else:
                pause_menu = PauseMenu(self.width, self.height, self.screen, self)

    def play_block_crashed_effect(self):
        self.block_crashed_sound.play()

    def play_game_end_effect(self, state):
        if state == self.WIN:
            self.win_sound.play()
        else:
            self.lose_sound.play()

    def play_paddle_touch_effect(self):
        self.paddle_touch_sound.play()

    def get_window_size(self):
        return self.width, self.height

    def win_lost_detector(self):
        if not self.blocks:
            self.play_game_end_effect(self.WIN)
            self.game_end()
            Menu(self.width, self.height, self.screen, self, self.score.get_score(), self.WIN).draw()
        if self.ball.rect.y > self.paddle.rect.y + self.paddle.rect.h:
            self.play_game_end_effect(self.LOSE)
            self.game_end()
            Menu(self.width, self.height, self.screen, self, self.score.get_score(), self.LOSE).draw()

    def collision_handler(self):
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball_y_direction > 0:
            self.play_paddle_touch_effect()
            self.collision_detector(self.paddle.rect)
        x, y = self.ball.get_pos()
        r = self.ball.get_radius()
        if x + r >= self.width:
            self.ball_x_direction = -self.ball_x_direction
        if x - r <= 0:
            self.ball_x_direction = -self.ball_x_direction
        if y - r <= 0:
            self.ball_y_direction = -self.ball_y_direction

    def blocks_placement(self):
        self.blocks = [
            Block(self, i * (Block.WIDTH + Block.INDENT), j * (Block.HEIGHT + Block.INDENT)) for j in
            range(0, GameWindow.N_BLOCKS) for i in range(1, GameWindow.M_BLOCKS)]

    def blocks_draw(self):
        for block in self.blocks:
            block.draw(self.screen)

    def pause_handler(self):
        self.pause = not self.pause

    def blocks_collision_handler(self, index):
        if index != -1:
            self.play_block_crashed_effect()
            self.score.up_score()
            block_rect = self.blocks.pop(index).rect
            self.collision_detector(block_rect)

    def collision_detector(self, rect):
        if self.ball_x_direction > 0:
            dx = self.ball.rect.right - rect.left
        else:
            dx = rect.right - self.ball.rect.left
        if self.ball_y_direction > 0:
            dy = self.ball.rect.bottom - rect.top
        else:
            dy = rect.bottom - self.ball.rect.top
        if abs(dx - dy) < GameWindow.COLLISION_EPSILON:
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
                if event.key == pygame.K_RIGHT:
                    self.is_key_downed = True
                    self.paddle_direction = 1
                elif event.key == pygame.K_LEFT:
                    self.is_key_downed = True
                    self.paddle_direction = -1
                elif event.key == pygame.K_ESCAPE:
                    self.pause_handler()
            if event.type == pygame.KEYUP:
                self.is_key_downed = False

    def set_menu(self, menu):
        self.opened_menu = menu

    def game_end(self):
        self.screen.fill((0, 0, 0))
        self.running = False

    @staticmethod
    def load_image(name, colorkey=None):
        fullname = os.path.join("data", name)
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
    FONT_SIZE = 36
    TEMPLATE = "You {} With score:"
    Y_INDENT_COEFF = 0.95
    FONT_PX_COEFF = 3

    def __init__(self, width, height, screen, game_window, score=None, end_state=None):
        self.font = pygame.font.Font(None, Score.FONT_SIZE)
        self.end_state = end_state
        self.score = score
        self.width = width
        self.height = height
        self.screen = screen
        self.game_window = game_window
        self.game_window.set_menu(self)
        self.background_font = GameWindow.load_image("menu_background.png")
        self.start_btn_font = GameWindow.load_image("play_button.png")
        self.start_btn_rect = pygame.Rect((self.width - self.start_btn_font.get_width()) // 2,
                                          (self.height - self.start_btn_font.get_height()) // 2,
                                          *self.start_btn_font.get_size())
        self.quit_btn_font = GameWindow.load_image("quit_button.png")
        self.quit_btn_rect = pygame.Rect((self.width - self.quit_btn_font.get_width()) // 2,
                                         (self.height + self.quit_btn_font.get_height()) // 2,
                                         *self.quit_btn_font.get_size())
        self.btn_select_sound = pygame.mixer.Sound("data/menu_selection_click.wav")
        self.selected_btn = None
        self.draw()

    def draw(self):
        self.running = True
        while self.running:
            self.screen.fill((0, 0, 0))
            self.events_handler()
            self.screen.blit(self.background_font, self.background_font.get_rect())
            self.screen.blit(self.start_btn_font,
                             self.start_btn_rect)
            self.screen.blit(self.quit_btn_font, self.quit_btn_rect)
            if self.score is not None and self.end_state is not None:
                self.game_score_draw()
            pygame.display.update()
            pygame.display.flip()

    def close_menu(self):
        self.screen.fill((0, 0, 0))
        self.end_state = None
        self.score = None
        self.running = False

    def events_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_menu()
                sys.exit(0)
            if event.type == pygame.MOUSEMOTION:
                start_btn_selected = self.start_btn_rect.collidepoint(*event.pos)
                quit_btn_selected = self.quit_btn_rect.collidepoint(*event.pos)
                # 0 - start button select 1 - quit button select
                if start_btn_selected and self.selected_btn != 0:
                    self.selected_btn = 0
                    self.play_btn_selected_effect()
                if quit_btn_selected and self.selected_btn != 1:
                    self.selected_btn = 1
                    self.play_btn_selected_effect()
                if not start_btn_selected and not quit_btn_selected:
                    self.selected_btn = None
            if event.type == pygame.MOUSEBUTTONUP:
                if self.start_btn_rect.collidepoint(*event.pos):
                    self.game_window.start_game()
                elif self.quit_btn_rect.collidepoint(*event.pos):
                    self.close_menu()
                    sys.exit(0)

    def play_btn_selected_effect(self):
        self.btn_select_sound.play()

    def game_score_draw(self):
        score = self.font.render(str(self.score), True, (0, 255, 0))
        text_state = "win" if self.end_state == GameWindow.WIN else "lose"
        end_text = self.font.render(Menu.TEMPLATE.format(text_state), True, (0, 255, 0))
        self.screen.blit(end_text,
                         (0,
                          self.height * Menu.Y_INDENT_COEFF))
        self.screen.blit(score, (
            len(str(end_text)) * Menu.FONT_SIZE // Menu.FONT_PX_COEFF, self.height * Score.Y_INDENT_COEFF))


class PauseMenu(Menu):
    def __init__(self, width, height, screen, game_window, score=None, end_state=None):
        self.font = pygame.font.Font(None, Score.FONT_SIZE)
        self.end_state = end_state
        self.score = score
        self.width = width
        self.height = height
        self.screen = screen
        self.game_window = game_window
        self.game_window.set_menu(self)
        self.background_font = GameWindow.load_image("game_background.png")
        self.start_btn_font = GameWindow.load_image("play_button.png")
        self.start_btn_rect = pygame.Rect((self.width - self.start_btn_font.get_width()) // 2,
                                          (self.height - self.start_btn_font.get_height()) // 2,
                                          *self.start_btn_font.get_size())
        self.quit_btn_font = GameWindow.load_image("quit_button.png")
        self.quit_btn_rect = pygame.Rect((self.width - self.quit_btn_font.get_width()) // 2,
                                         (self.height + self.quit_btn_font.get_height()) // 2,
                                         *self.quit_btn_font.get_size())
        self.btn_select_sound = pygame.mixer.Sound("data/menu_selection_click.wav")
        self.selected_btn = None
        self.draw()

    def events_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_menu()
                sys.exit(0)
            if event.type == pygame.MOUSEMOTION:
                start_btn_selected = self.start_btn_rect.collidepoint(*event.pos)
                quit_btn_selected = self.quit_btn_rect.collidepoint(*event.pos)
                # 0 - start button select 1 - quit button select
                if start_btn_selected and self.selected_btn != 0:
                    self.selected_btn = 0
                    self.play_btn_selected_effect()
                if quit_btn_selected and self.selected_btn != 1:
                    self.selected_btn = 1
                    self.play_btn_selected_effect()
                if not start_btn_selected and not quit_btn_selected:
                    self.selected_btn = None

            if event.type == pygame.MOUSEBUTTONUP:
                if self.start_btn_rect.collidepoint(*event.pos):
                    self.game_window.pause_handler()
                    self.screen.fill((0, 0, 0))
                    self.running = False
                elif self.quit_btn_rect.collidepoint(*event.pos):
                    self.close_menu()
                    sys.exit(0)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_window.pause_handler()
                self.screen.fill((0, 0, 0))
                self.running = False


def main():
    pygame.init()
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    game_wnd = GameWindow(width, height, screen)
    Menu(width, height, screen, game_wnd)


if __name__ == "__main__":
    main()
