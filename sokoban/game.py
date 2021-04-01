import pygame
import sys
from pygame.locals import *
import constants as SOKOBAN
from level import *
from player import *
from scores import *
from player_interface import *
from solver import *
from pyautogui import press, typewrite, hotkey

import _thread
import time


def move(threadName, delay, strategy):
    for step in strategy:
        if step in ['R', 'r']:
            press('right')
        if step in ['L', 'l']:
            press('left')
        if step in ['D', 'd']:
            press('down')
        if step in ['U', 'u']:
            press('up')
        # time.sleep(0.2)


class Game:
    def __init__(self, window):
        self.window = window
        self.load_textures()
        self.player = None
        self.index_level = 1
        self.load_level()
        self.play = True
        self.scores = Scores(self)
        self.player_interface = PlayerInterface(self.player, self.level)

    def load_textures(self):
        self.textures = {
            SOKOBAN.WALL: pygame.image.load('assets/images/wall.png').convert_alpha(),
            SOKOBAN.BOX: pygame.image.load('assets/images/box.png').convert_alpha(),
            SOKOBAN.TARGET: pygame.image.load('assets/images/target.png').convert_alpha(),
            SOKOBAN.TARGET_FILLED: pygame.image.load('assets/images/valid_box.png').convert_alpha(),
            SOKOBAN.PLAYER: pygame.image.load(
                'assets/images/player_sprites.png').convert_alpha()
        }

    def load_level(self):
        self.level = Level(self.index_level)
        self.board = pygame.Surface((self.level.width, self.level.height))
        if self.player:
            self.player.pos = self.level.position_player
            self.player_interface.level = self.level
        else:
            self.player = Player(self.level)

    def start(self):
        while self.play:
            self.process_event(pygame.event.wait())
            self.update_screen()

    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                # Quit game
                self.play = False
            if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z, K_s, K_q, K_d]:
                # Move players
                self.player.move(event.key, self.level, self.player_interface)
                if self.has_win():
                    self.index_level += 1
                    if (self.index_level == 21):
                        self.index_level = 1
                    self.scores.save()
                    self.load_level()
            if event.key == K_r:
                # Restart current level
                self.load_level()
            if event.key == K_l:
                # Cancel last move
                self.level.cancel_last_move(self.player, self.player_interface)
        if event.type == MOUSEBUTTONUP:
            self.player_interface.click(event.pos, self.level, self)
        if event.type == MOUSEMOTION:
            self.player_interface.mouse_pos = event.pos

    def update_screen(self):
        pygame.draw.rect(self.board, SOKOBAN.WHITE, (0, 0, self.level.width *
                                                     SOKOBAN.SPRITESIZE, self.level.height * SOKOBAN.SPRITESIZE))
        pygame.draw.rect(self.window, SOKOBAN.WHITE,
                         (0, 0, SOKOBAN.WINDOW_WIDTH, SOKOBAN.WINDOW_HEIGHT))

        self.level.render(self.board, self.textures)
        self.player.render(self.board, self.textures)

        pox_x_board = (SOKOBAN.WINDOW_WIDTH / 2) - (self.board.get_width() / 2)
        pos_y_board = (SOKOBAN.WINDOW_HEIGHT / 2) - \
            (self.board.get_height() / 2)
        self.window.blit(self.board, (pox_x_board, pos_y_board))

        self.player_interface.render(self.window, self.index_level)

        pygame.display.flip()

    def has_win(self):
        nb_missing_target = 0
        for y in range(len(self.level.structure)):
            for x in range(len(self.level.structure[y])):
                if self.level.structure[y][x] == SOKOBAN.TARGET:
                    nb_missing_target += 1

        return nb_missing_target == 0

    def auto_move(self):
        # strategy = get_move(
        #     self.level.structure[:-1], self.level.position_player, 'dfs')
        # strategy = get_move(
        #     self.level.structure[:-1], self.level.position_player, 'bfs')
        strategy = get_move(
            self.level.structure[:-1], self.level.position_player, 'ucs')
        # strategy = get_move(
        #     self.level.structure[:-1], self.level.position_player, 'astar')
        # with open("assets/sokobanSolver/Solverlevel_" + str(self.index_level) + ".txt", 'w+') as solver_file:
        #     for listitem in strategy:
        #         solver_file.write('%s, ' % listitem)
        if strategy is not None:
            try:
                _thread.start_new_thread(move, ("Thread-1", 2, strategy))
            except:
                print("Error: unable to start thread")


# Define a function for the thread
