from typing import List
import nygame
import pygame
from pygame.event import Event
import pygame.font
from pygame.constants import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP
import pygame.transform
import pygame.key
from pygame.surface import Surface
import pygame.image

from nylcd.lib.lcd import LCDSurface


class TicTacToeDisplay:
    def __init__(self):
        self.bg = pygame.image.load("./demos/data/tictactoe-bg.png")
        self.lcd = LCDSurface(pygame.image.load("./demos/data/tictactoe-lcd.png"), bgcolor=None)
        self.player_x = False
        self.player_o = False
        self.player_wins = False
        self.player_go = False
        self.grid_x = [[False] * 3, [False] * 3, [False] * 3]
        self.grid_o = [[False] * 3, [False] * 3, [False] * 3]
        
    def render_to(self, surf: Surface):
        surf.blit(self.bg, (0, 0))
        self.lcd.segments[0].active = self.player_o
        self.lcd.segments[1].active = self.player_x
        self.lcd.segments[2].active = self.player_wins
        self.lcd.segments[3].active = self.player_go
        self.lcd.segments[4].active = self.grid_o[0][0]
        self.lcd.segments[5].active = self.grid_o[1][0]
        self.lcd.segments[6].active = self.grid_o[2][0]
        self.lcd.segments[7].active = self.grid_x[0][0]
        self.lcd.segments[8].active = self.grid_x[1][0]
        self.lcd.segments[9].active = self.grid_x[2][0]
        self.lcd.segments[10].active = self.grid_o[0][1]
        self.lcd.segments[11].active = self.grid_o[1][1]
        self.lcd.segments[12].active = self.grid_o[2][1]
        self.lcd.segments[13].active = self.grid_x[0][1]
        self.lcd.segments[14].active = self.grid_x[1][1]
        self.lcd.segments[15].active = self.grid_x[2][1]
        self.lcd.segments[16].active = self.grid_o[0][2]
        self.lcd.segments[17].active = self.grid_o[1][2]
        self.lcd.segments[18].active = self.grid_o[2][2]
        self.lcd.segments[19].active = self.grid_x[0][2]
        self.lcd.segments[20].active = self.grid_x[1][2]
        self.lcd.segments[21].active = self.grid_x[2][2]
        self.lcd.render()
        surf.blit(self.lcd.surface, (0, 0))

    def get_size(self):
        return self.lcd.get_size()


class Game(nygame.Game):
    def __init__(self):
        super().__init__(showfps=True, bgcolor=None)
        self.display = TicTacToeDisplay()
        self.size = self.display.get_size()
        self.reset_display()
        self.x = 0
        self.y = 0
        self.player = "x"
        self.winner = None
        self.playfield = [[None] * 3, [None] * 3, [None] * 3]

    def loop(self, events: List[Event]):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_LEFT:
                    self.x = max(0, self.x - 1)
                elif e.key == K_RIGHT:
                    self.x = min(self.x + 1, 2)
                elif e.key == K_UP:
                    self.y = max(0, self.y - 1)
                elif e.key == K_DOWN:
                    self.y = min(self.y + 1, 2)
                elif e.key == K_SPACE:
                    if self.winner:
                        self.reset()
                    else:
                        if self.playfield[self.x][self.y] is None:
                            self.playfield[self.x][self.y] = self.player
                            self.player = "x" if self.player == "o" else "o"
                            
        self.winner = self.check_winner()

        if self.winner is None:
            self.display.player_o = self.player == "o"
            self.display.player_x = self.player == "x"
            self.display.player_go = True
            self.display.player_wins = False
        elif self.winner == "stalemate":
            self.display.player_o = True
            self.display.player_x = True
            self.display.player_go = False
            self.display.player_wins = False
        else:
            self.display.player_o = self.winner == "o"
            self.display.player_x = self.winner == "x"
            self.display.player_go = False
            self.display.player_wins = True
        
        for y in range(3):
            for x in range(3):
                self.display.grid_o[x][y] = self.playfield[x][y] == "o"
                self.display.grid_x[x][y] = self.playfield[x][y] == "x"

        if self.player == "x":
            self.display.grid_x[self.x][self.y] = self.blink
        else:
            self.display.grid_o[self.x][self.y] = self.blink
            
        self.display.render_to(self.surface)

    def reset(self):
        self.x = 0
        self.y = 0
        self.player = "x"
        self.winner = None
        self.playfield = [[None] * 3, [None] * 3, [None] * 3]

    def check_winner(self):
        stalemate = not any(sq is None for row in self.playfield for sq in row)
        if stalemate:
            return "stalemate"

        win_combos = [
            ((0, 0), (0, 1), (0, 2)),
            ((1, 0), (1, 1), (1, 2)),
            ((2, 0), (2, 1), (2, 2)),

            ((0, 0), (1, 0), (2, 0)),
            ((0, 1), (1, 1), (2, 1)),
            ((0, 2), (1, 2), (2, 2)),

            ((0, 0), (1, 1), (2, 2)),
            ((0, 2), (1, 1), (2, 0))
        ]
        for (x1, y1), (x2, y2), (x3, y3) in win_combos:
            combo_player = self.playfield[x1][y1]
            if combo_player is None:
                continue
            if self.playfield[x2][y2] == combo_player and self.playfield[x3][y3] == combo_player:
                return combo_player
        return None

    @property
    def blink(self):
        time_off = 0.5
        time_on = 0.5
        now = nygame.time.get_ticks_sec()
        offset = now % (time_off + time_on)
        is_on = offset >= time_off
        return is_on


def main():
    Game().run()

if __name__ == "__main__":
    main()
