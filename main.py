import os
import pygame
import sys
from random import randint
import datetime as dt


class Bonus:
    BONUS_SHOWING_TIME = 5
    N_BLOCKS_FOR_GET_INCR_PLATFORM = 20

    def __init__(self, window_sizes, paddle, ball, blocks):
        self.win_width, self.win_height = window_sizes
        self.start_bonus_showing_time = None
        self.paddle = paddle
        self.ball = ball
        self.n_blocks, self.m_blocks = GameWindow.N_BLOCKS, GameWindow.M_BLOCKS
        self.blocks = blocks

    def is_bonus_can_get(self, n):
        is_blocks_crashed = self.n_blocks * \
            self.m_blocks - len(self.blocks) > 0
        is_n_blocks_crashed = (
            self.n_blocks * self.m_blocks - len(self.blocks)) % n == 0
        return is_blocks_crashed and is_n_blocks_crashed

    def try_get_incr_platform(self):
        current_time = dt.datetime.now()
        if self.start_bonus_showing_time is None \
                and self.is_bonus_can_get(self.N_BLOCKS_FOR_GET_INCR_PLATFORM)\
                and self.ball.get_lifes() >= Ball.STANDART_LIFES:
            self.paddle.increase_width()
            self.paddle.set_color(0, 0, 0)
            self.ball.set_color(0, 0, 0)
            self.paddle.gradient_effect()
            self.ball.gradient_effect()
            self.start_bonus_showing_time = current_time

        elif self.start_bonus_showing_time is not None and \
                (current_time -
                 self.start_bonus_showing_time).seconds <= self.BONUS_SHOWING_TIME \
                and self.ball.get_lifes() >= Ball.STANDART_LIFES:
            self.paddle.gradient_effect()
            self.ball.gradient_effect()
        elif self.ball.get_lifes() < Ball.STANDART_LIFES:
            self.paddle.set_color(*Paddle.STANDART_COLOR)
            self.ball.set_color(*Ball.STANDART_COLOR)
            self.paddle.set_width(Paddle.WIDTH)
            self.start_bonus_showing_time = None
        else:
            self.paddle.set_color(*Paddle.STANDART_COLOR)
            self.ball.set_color(*Ball.STANDART_COLOR)
            self.start_bonus_showing_time = None

    def try_get_life(self):
        current_time = dt.datetime.now()
        if self.start_bonus_showing_time is None \
                and self.is_bonus_can_get(self.n_blocks * self.m_blocks//2):
            self.ball.increase_lifes()
            self.paddle.set_color(0, 0, 0)
            self.ball.set_color(0, 0, 0)
            self.paddle.gradient_effect()
            self.ball.gradient_effect()
            self.start_bonus_showing_time = current_time

        elif self.start_bonus_showing_time is not None and \
                (current_time -
                 self.start_bonus_showing_time).seconds <= self.BONUS_SHOWING_TIME:
            self.paddle.gradient_effect()
            self.ball.gradient_effect()
        elif self.ball.get_lifes() < Ball.STANDART_LIFES:
            self.paddle.set_color(*Paddle.STANDART_COLOR)
            self.ball.set_color(*Ball.STANDART_COLOR)
            self.paddle.set_width(Paddle.WIDTH)
            self.start_bonus_showing_time = None
        else:
            self.paddle.set_color(*Paddle.STANDART_COLOR)
            self.ball.set_color(*Ball.STANDART_COLOR)
            self.start_bonus_showing_time = None


class Score:
    FONT_SIZE = 36
    SCORE_TEMPLATE = "Score: {}"
    Y_INDENT_COEFF = 0.95
    X_INDENT_PIXELS = 50
    FONT_SIZE_COEFF = 5
    STANDART_COLOR = (0, 255, 0)

    def __init__(self, window_sizes):
        self.score = 0
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        self.win_width, self.win_height = window_sizes

    def up_score(self):
        self.score += 1

    def draw(self, surf):
        score_string = self.SCORE_TEMPLATE.format(str(self.score))
        score_text = self.font.render(score_string, True, self.STANDART_COLOR)
        surf.blit(score_text,
                  (self.win_width - self.X_INDENT_PIXELS -
                   len(score_string) *
                   self.FONT_SIZE // self.FONT_SIZE_COEFF,
                   self.win_height * self.Y_INDENT_COEFF))

    def get_score(self):
        return self.score


class Ball(pygame.sprite.Sprite):
    RADIUS = 7
    SPEED = 5
    STANDART_COLOR = (0, 255, 0)
    STANDART_LIFES = 5
    FONT_SIZE = 36
    LIVES_TEMPLATE = "Lives left: {}"
    Y_INDENT_COEFF = 0.95
    COLLISION_EPSILON = 10

    def __init__(self, window_sizes, all_sprites):
        super().__init__(all_sprites)
        self.win_width, self.win_height = window_sizes
        self.radius = self.RADIUS
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.speed = self.SPEED
        self.color = self.STANDART_COLOR
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        self.lifes = self.STANDART_LIFES
        self.is_ball_static = True
        self.x_direction = self.y_direction = 1

    def invert_x_direction(self):
        self.x_direction = -self.x_direction

    def invert_y_direction(self):
        self.y_direction = -self.y_direction

    def get_x_direction(self):
        return self.x_direction

    def get_y_direction(self):
        return self.y_direction

    def set_static(self, state):
        self.is_ball_static = state

    def centering(self, paddle_x, paddle_y, paddle_width, paddle_height):

        centering_x = paddle_x + (paddle_width -
                                  self.get_radius())//2
        centering_y = paddle_y -\
            self.get_radius() * 2
        self.set_pos(centering_x, centering_y)
        self.set_static(True)

    def static_state(self):
        return self.is_ball_static

    def draw(self, surf):
        pygame.draw.ellipse(surf, self.color, self.rect)

    def decrease_lifes(self):
        self.lifes -= 1

    def increase_lifes(self):
        self.lifes += 1

    def draw_lifes(self, surf):
        lifes_count_text = self.font.render(
            self.LIVES_TEMPLATE.format(str(self.lifes)),
            True,
            (0, 255, 0))
        surf.blit(lifes_count_text, (0, self.win_height * self.Y_INDENT_COEFF))

    def gradient_effect(self):
        self.color = (randint(50, 255), randint(50, 255), randint(50, 255))

    def get_lifes(self):
        return self.lifes

    def set_color(self, r, g, b):
        self.color = (r, g, b)

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_pos(self):
        return self.rect.x, self.rect.y

    def get_radius(self):
        return self.radius

    def update(self):
        self.rect.x += self.x_direction * self.speed
        self.rect.y += self.y_direction * self.speed

    def collision_detector(self, rect):

        if self.get_x_direction() > 0:
            dx = self.rect.right - rect.left
        else:
            dx = rect.right - self.rect.left
        if self.get_y_direction() > 0:
            dy = self.rect.bottom - rect.top
        else:
            dy = rect.bottom - self.rect.top
        if abs(dx - dy) < self.COLLISION_EPSILON:
            self.invert_x_direction()
            self.invert_y_direction()
        elif dx > dy:
            self.invert_y_direction()
        elif dx < dy:
            self.invert_x_direction()


class Block(pygame.sprite.Sprite):
    WIDTH = 64
    HEIGHT = 32
    INDENT = 5

    def __init__(self, all_sprites, x=0, y=0):
        super().__init__(all_sprites)
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = GameWindow.load_image(
            "block" + str(randint(1, 5)) + ".png")
        self.block_crashed_sound = pygame.mixer.Sound("data/block_crashed.mp3")

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def play_crashed_effect(self, is_game_volumes_on):
        if is_game_volumes_on:
            self.block_crashed_sound.play()


class ConcreteBlock(Block):
    def __init__(self, all_sprites, hardness=1, x=0, y=0):
        super().__init__(all_sprites)
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = GameWindow.load_image(
            "block" + str(randint(1, 5)) + ".png")
        self.block_crashed_sound = pygame.mixer.Sound("data/block_crashed.mp3")
        self.block_hit_sound = pygame.mixer.Sound("data/rock_hit.mp3")
        self.hardness = hardness

    def play_crashed_effect(self, is_game_volumes_on):
        if is_game_volumes_on and self.hardness > 0:
            self.block_hit_sound.play()
        elif is_game_volumes_on:
            self.block_crashed_sound.play()

    def block_hitted(self):
        self.image = GameWindow.load_image("block_hitted.png")
        self.decrease_hardness()

    def decrease_hardness(self):
        self.hardness -= 1

    def get_hardness(self):
        return self.hardness


class IronBlock(Block):
    def __init__(self, all_sprites, x=0, y=0):
        super().__init__(all_sprites)
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = GameWindow.load_image("iron_block.png")
        self.block_crashed_sound = pygame.mixer.Sound("data/metal_hit.wav")


class Paddle(pygame.sprite.Sprite):
    WIDTH = 90
    HEIGHT = 7
    SPEED = 10
    Y_INDENT_COEFF = 0.9
    BONUS_WIDTH_INCREASE = 30
    STANDART_COLOR = (192, 192, 192)

    def __init__(self, window_sizes, all_sprites):
        super().__init__(all_sprites)
        self.win_width, self.win_height = window_sizes
        self.width, self.height = self.WIDTH, self.HEIGHT
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.speed = self.SPEED
        self.color = self.STANDART_COLOR
        self.paddle_touch_sound = pygame.mixer.Sound(
            "data/paddle_touch_sound.wav")
        self.direction = 1

    def play_touch_effect(self, is_game_volumes_on):
        if is_game_volumes_on:
            self.paddle_touch_sound.play()

    def move(self):
        if self.direction < 0 and self.rect.x > 0:
            self.rect.x += self.direction * self.speed
        elif self.direction > 0 and self.rect.x < self.win_width - self.width:
            self.rect.x += self.direction * self.speed

    def set_direction(self, val):
        self.direction = val

    def get_direction(self):
        return self.direction

    def increase_width(self):
        self.width += self.BONUS_WIDTH_INCREASE
        self.rect.w = self.width
        x, y = self.get_pos()
        if x + self.width > self.win_width:
            self.set_pos(self.win_width - self.width, y)

    def centering(self):
        centering_paddle_x = (self.win_width - self.get_width())//2
        centering_paddle_y = self.win_height * self.Y_INDENT_COEFF
        self.set_pos(centering_paddle_x, centering_paddle_y)

    def gradient_effect(self):
        self.color = (randint(50, 255), randint(50, 255), randint(50, 255))

    def set_width(self, width):
        self.rect.w = width
        self.width = width

    def set_color(self, r, g, b):
        self.color = (r, g, b)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

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
    N_BLOCKS = 8
    M_BLOCKS = 18
    IRON_BLOCKS_COORDS = [(0, 0),
                          (0, N_BLOCKS - 1),
                          (M_BLOCKS - 1, N_BLOCKS - 1),
                          (M_BLOCKS - 1, 0),
                          (M_BLOCKS//2 - 1, N_BLOCKS // 2 - 1),
                          (M_BLOCKS // 2, N_BLOCKS // 2 - 1),
                          (M_BLOCKS//2 + 1, N_BLOCKS//2 - 1),
                          (M_BLOCKS//2 - 1, N_BLOCKS - 1),
                          (M_BLOCKS//2, N_BLOCKS - 1),
                          (M_BLOCKS//2 + 1, N_BLOCKS - 1)
                          ]
    CONCRETE_BLOCK_FREQ = 10

    LOSE = 0
    WIN = 1

    def __init__(self, width, height, screen):
        self.width = width
        self.height = height
        self.opened_menu = None
        self.screen = screen
        self.lose_sound = pygame.mixer.Sound("data/lose_sound.mp3")
        self.win_sound = pygame.mixer.Sound("data/win_sound.wav")
        self.game_background = self.load_image("game_background.jpg")

    def ui_initial(self):
        self.is_game_volumes_on = self.opened_menu.game_volumes_state()
        self.pause = False
        self.score = Score(self.get_window_size())
        self.bonus = Bonus(self.get_window_size(),
                           self.paddle, self.ball, self.blocks)
        self.is_key_downed = False
        self.clock = pygame.time.Clock()
        self.pause_menu = PauseMenu(
            self.width, self.height,
            self.screen, self,
            self.opened_menu.volume_control)
        self.set_menu(self.pause_menu)

    def game_objects_initial(self):
        self.all_sprites = pygame.sprite.Group()
        self.paddle = Paddle(self.get_window_size(), self.all_sprites)
        self.paddle.centering()

        self.ball = Ball(self.get_window_size(), self.all_sprites)
        self.ball.centering(
            *self.paddle.get_pos(),
            self.paddle.get_width(), self.paddle.get_height())

    def bonus_get_handler(self):
        self.bonus.try_get_incr_platform()
        self.bonus.try_get_life()

    def start_game(self):
        self.game_objects_initial()
        self.blocks_placement()
        self.ui_initial()

        self.running = True

        while self.running:
            self.events_handler()
            if not self.pause:
                self.opened_menu.close_menu()
                if self.is_key_downed:
                    self.paddle.move()
                    self.ball.set_static(False)
                self.update_game_loop()
                self.win_lost_detector()
                block_hit_index = self.ball.rect.collidelist(
                    list(map(lambda x: x.rect, self.blocks)))
                self.blocks_collision_handler(block_hit_index)
                self.collision_handler()

            else:
                self.pause_menu.draw()

    def update_game_loop(self):
        self.is_game_volumes_on = self.opened_menu.game_volumes_state()
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_background,
                         self.game_background.get_rect())
        self.score.draw(self.screen)
        self.ball.draw_lifes(self.screen)
        if not self.ball.static_state():
            self.ball.update()
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.blocks_draw()
        self.bonus_get_handler()
        pygame.display.update()
        pygame.display.flip()
        self.clock.tick(GameWindow.FPS)

    def play_game_end_effect(self, state):
        if self.is_game_volumes_on:
            if state == self.WIN:
                self.win_sound.play()
            else:
                self.lose_sound.play()

    def get_window_size(self):
        return self.width, self.height

    def win_lost_detector(self):
        if not self.blocks:
            self.play_game_end_effect(self.WIN)
            self.game_end()
            Menu(self.width, self.height, self.screen,
                 self, self.score.get_score(), self.WIN,
                 self.opened_menu.volume_control).draw()
        ball_y = self.ball.get_pos()[1]
        paddle_y = self.paddle.get_pos()[1]
        if ball_y > paddle_y + self.paddle.get_height():
            self.ball.decrease_lifes()

            if self.ball.get_lifes() <= 0:
                self.play_game_end_effect(self.LOSE)
                self.game_end()
                Menu(self.width, self.height, self.screen,
                     self, self.score.get_score(), self.LOSE,
                     self.opened_menu.volume_control).draw()
            else:
                self.paddle.set_width(Paddle.WIDTH)
                self.paddle.centering()
                self.ball.centering(
                    *self.paddle.get_pos(), self.paddle.get_width(),
                    self.paddle.get_height())

    def collision_handler(self):
        if self.ball.rect.colliderect(self.paddle.rect)\
                and self.ball.get_y_direction() > 0:
            self.paddle.play_touch_effect(self.is_game_volumes_on)
            self.ball.collision_detector(self.paddle.rect)

        up_collision_line = self.ball.rect.clipline(0, 0, self.width, 0)
        right_collision_line = self.ball.rect.clipline(
            self.width, 0, self.width, self.height)
        left_collision_line = self.ball.rect.clipline(0, 0, 0, self.height)

        if right_collision_line:
            self.ball.invert_x_direction()
        if left_collision_line:
            self.ball.invert_x_direction()
        if up_collision_line:
            self.ball.invert_y_direction()

    def blocks_placement(self):
        self.blocks = []
        for i in range(self.M_BLOCKS):
            for j in range(self.N_BLOCKS):
                if (i, j) in self.IRON_BLOCKS_COORDS:
                    self.blocks.append(IronBlock(
                        self.all_sprites, i * (Block.WIDTH + Block.INDENT),
                        j * (Block.HEIGHT + Block.INDENT)))
                elif i * j % self.CONCRETE_BLOCK_FREQ == 0:
                    self.blocks.append(ConcreteBlock(
                        self.all_sprites, x=i * (Block.WIDTH + Block.INDENT),
                        y=j * (Block.HEIGHT + Block.INDENT)))

                else:
                    self.blocks.append(Block(
                        self.all_sprites, i * (Block.WIDTH + Block.INDENT),
                        j * (Block.HEIGHT + Block.INDENT)))

    def blocks_draw(self):
        for block in self.blocks:
            block.draw(self.screen)

    def pause_handler(self):
        self.pause = not self.pause

    def blocks_collision_handler(self, index):
        if index != -1:
            block = self.blocks[index]
            if (type(block) == Block) or \
                    (type(block) == ConcreteBlock
                        and block.get_hardness() == 0):
                self.score.up_score()
                del self.blocks[index]
                block.play_crashed_effect(self.is_game_volumes_on)
                self.ball.collision_detector(block.rect)
            elif type(block) == ConcreteBlock:
                block.play_crashed_effect(self.is_game_volumes_on)
                block.block_hitted()
                self.ball.collision_detector(block.rect)
            else:
                block.play_crashed_effect(self.is_game_volumes_on)
                self.ball.collision_detector(block.rect)

    def events_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.is_key_downed = True
                    self.paddle.set_direction(1)
                    self.ball.set_static(False)
                elif event.key == pygame.K_LEFT:
                    self.is_key_downed = True
                    self.paddle.set_direction(-1)
                    self.ball.set_static(False)
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


class VolumeControl:
    VOLUME_IMG_WIDTH = 64
    VOLUME_IMG_HEIGHT = 64

    def __init__(self, game_window, screen, up_btn_h):
        self.screen = screen
        self.width, self.height = game_window.get_window_size()
        self.clicks = 0
        self.mute_img = game_window.load_image("mute.png")
        self.unmute_img = game_window.load_image("unmute.png")
        self.volume_control_img_rect = pygame.Rect((self.width -
                                                    self.VOLUME_IMG_WIDTH)//2,
                                                   self.height//2 -
                                                   up_btn_h -
                                                   self.VOLUME_IMG_HEIGHT,
                                                   self.VOLUME_IMG_WIDTH,
                                                   self.VOLUME_IMG_HEIGHT)

    def draw(self):
        if self.clicks % 2 == 0:
            self.screen.blit(self.mute_img, self.volume_control_img_rect)
        else:
            self.screen.blit(self.unmute_img, self.volume_control_img_rect)

    def click_handler(self):
        self.clicks += 1
        self.clicks = self.clicks % 2

    def is_volume_on(self):
        return self.clicks % 2 == 0

    def is_point_in(self, x, y):
        return self.volume_control_img_rect.collidepoint(x, y)


class Menu:
    FONT_SIZE = 36
    TEMPLATE = "You {} with score: {}"
    Y_INDENT_COEFF = 0.95
    FONT_PX_COEFF = 3
    START_BUTTON = 0
    QUIT_BUTTON = 1
    MUTE_UNMUTE_BUTTON = 2

    def __init__(self, width, height, screen,
                 game_window, score=None, end_state=None, volume_control=None):
        self.font = pygame.font.Font(None, Score.FONT_SIZE)
        self.end_state = end_state
        self.score = score
        self.width = width
        self.height = height
        self.screen = screen
        self.game_window = game_window
        self.background_font = GameWindow.load_image("menu_background.jpg")
        self.start_btn_font = GameWindow.load_image("play_button.png")
        self.start_btn_rect = pygame.Rect((self.width -
                                           self.start_btn_font.get_width())//2,
                                          (self.height -
                                           self.start_btn_font.get_height())//2,
                                          *self.start_btn_font.get_size())
        self.quit_btn_font = GameWindow.load_image("quit_button.png")
        self.quit_btn_rect = pygame.Rect((self.width -
                                          self.quit_btn_font.get_width())//2,
                                         (self.height +
                                          self.quit_btn_font.get_height())//2,
                                         *self.quit_btn_font.get_size())
        self.btn_select_sound = pygame.mixer.Sound(
            "data/menu_selection_click.wav")
        self.selected_btn = None
        if volume_control is None:
            self.volume_control = VolumeControl(
                self.game_window, self.screen,
                self.start_btn_font.get_height())
        else:
            self.volume_control = volume_control

    def draw(self):
        self.running = True
        self.game_window.set_menu(self)
        while self.running:
            self.events_handler()
            self.update_menu_loop()

    def update_menu_loop(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_font,
                         self.background_font.get_rect())
        self.volume_control.draw()
        self.screen.blit(self.start_btn_font,
                         self.start_btn_rect)
        self.screen.blit(self.quit_btn_font, self.quit_btn_rect)
        if self.score is not None and self.end_state is not None:
            self.game_score_draw()
        pygame.display.update()
        pygame.display.flip()

    def game_volumes_state(self):
        return self.volume_control.is_volume_on()

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
                start_btn_selected = self.start_btn_rect.collidepoint(
                    *event.pos)
                quit_btn_selected = self.quit_btn_rect.collidepoint(*event.pos)
                mute_unmute_btn_selected = self.volume_control.is_point_in(
                    *event.pos)
                if start_btn_selected and \
                        self.selected_btn != self.START_BUTTON:
                    self.selected_btn = self.START_BUTTON
                    self.play_btn_selected_effect()
                if quit_btn_selected and self.selected_btn != self.QUIT_BUTTON:
                    self.selected_btn = self.QUIT_BUTTON
                    self.play_btn_selected_effect()
                if mute_unmute_btn_selected and \
                        self.selected_btn != self.MUTE_UNMUTE_BUTTON:
                    self.selected_btn = self.MUTE_UNMUTE_BUTTON
                    self.play_btn_selected_effect()
                if not start_btn_selected and \
                    not quit_btn_selected and \
                        not mute_unmute_btn_selected:
                    self.selected_btn = None
            if event.type == pygame.MOUSEBUTTONUP:
                if self.start_btn_rect.collidepoint(*event.pos):
                    self.game_window.start_game()
                elif self.quit_btn_rect.collidepoint(*event.pos):
                    self.close_menu()
                    sys.exit(0)
                elif self.volume_control.is_point_in(*event.pos):
                    self.volume_control.click_handler()

    def play_btn_selected_effect(self):
        if self.volume_control.is_volume_on():
            self.btn_select_sound.play()

    def game_score_draw(self):
        text_state = "win" if self.end_state == GameWindow.WIN else "lose"
        end_text = self.font.render(
            Menu.TEMPLATE.format(text_state, str(self.score)), True,
            (0, 255, 0))
        self.screen.blit(end_text,
                         (0,
                          self.height * Menu.Y_INDENT_COEFF))


class PauseMenu(Menu):
    def __init__(self, width, height, screen, game_window,
                 volume_control, score=None, end_state=None):
        self.font = pygame.font.Font(None, Score.FONT_SIZE)
        self.end_state = end_state
        self.score = score
        self.width = width
        self.height = height
        self.screen = screen
        self.game_window = game_window
        self.background_font = GameWindow.load_image("game_background.jpg")
        self.start_btn_font = GameWindow.load_image("play_button.png")
        self.start_btn_rect = pygame.Rect((self.width -
                                           self.start_btn_font.get_width())//2,
                                          (self.height -
                                           self.start_btn_font.get_height())//2,
                                          *self.start_btn_font.get_size())
        self.quit_btn_font = GameWindow.load_image("quit_button.png")
        self.quit_btn_rect = pygame.Rect((self.width -
                                          self.quit_btn_font.get_width())//2,
                                         (self.height +
                                          self.quit_btn_font.get_height())//2,
                                         *self.quit_btn_font.get_size())
        self.btn_select_sound = pygame.mixer.Sound(
            "data/menu_selection_click.wav")
        self.selected_btn = None
        self.volume_control = volume_control

    def events_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_menu()
                sys.exit(0)
            if event.type == pygame.MOUSEMOTION:
                start_btn_selected = self.start_btn_rect.collidepoint(
                    *event.pos)
                quit_btn_selected = self.quit_btn_rect.collidepoint(*event.pos)
                mute_unmute_btn_selected = self.volume_control.is_point_in(
                    *event.pos)
                if start_btn_selected and \
                        self.selected_btn != self.START_BUTTON:
                    self.selected_btn = self.START_BUTTON
                    self.play_btn_selected_effect()
                if quit_btn_selected and self.selected_btn != self.QUIT_BUTTON:
                    self.selected_btn = self.QUIT_BUTTON
                    self.play_btn_selected_effect()
                if mute_unmute_btn_selected and \
                        self.selected_btn != self.MUTE_UNMUTE_BUTTON:
                    self.selected_btn = self.MUTE_UNMUTE_BUTTON
                    self.play_btn_selected_effect()
                if not start_btn_selected and \
                    not quit_btn_selected and \
                        not mute_unmute_btn_selected:
                    self.selected_btn = None
            if event.type == pygame.MOUSEBUTTONUP:
                if self.start_btn_rect.collidepoint(*event.pos):
                    self.game_window.pause_handler()
                    self.screen.fill((0, 0, 0))
                    self.running = False
                elif self.quit_btn_rect.collidepoint(*event.pos):
                    self.close_menu()
                    sys.exit(0)
                elif self.volume_control.is_point_in(*event.pos):
                    self.volume_control.click_handler()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_window.pause_handler()
                self.screen.fill((0, 0, 0))
                self.running = False


def main():
    pygame.init()
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)
    game_wnd = GameWindow(width, height, screen)
    Menu(width, height, screen, game_wnd).draw()


if __name__ == "__main__":
    main()