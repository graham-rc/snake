#!/usr/bin/env python
import curses
from curses import wrapper
import time
import threading
from enum import Enum


class ScreenInterface:
    def __init__(self, curses_scr: curses.window, height: int = 0, width: int = 0):
        self.screen = curses_scr
        self.running = True
        self.refresh_rate = 0.1
        if height != 0 and width != 0:
            self.window = curses.newwin(height, width, 4, 4)
        else:
            self.window = self.screen

    def refresh_all(self):
        # while self.running:
        self.window.refresh()
        self.screen.refresh()
        time.sleep(self.refresh_rate)

    def puts(self, s: str):
        self.window.addstr(s)


class Direction(Enum):
    NONE = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    def get_vector(self):
        if self == Direction.NONE:
            return {'x': 0, 'y': 0}
        elif self == Direction.UP:
            return {'x': 0, 'y': -1}
        elif self == Direction.RIGHT:
            return {'x': 1, 'y': 0}
        elif self == Direction.DOWN:
            return {'x': 0, 'y': 1}
        elif self == Direction.LEFT:
            return {'x': -1, 'y': 0}


class Snake(threading.Thread):
    def __init__(self, screen: ScreenInterface):
        super().__init__()
        self.screen = screen
        self.h, self.w = screen.window.getmaxyx()
        self.h -= 2
        self.w -= 2
        self.running = True
        self.pause = False
        self.direction = Direction.NONE
        self.pos = {"x": 0, "y": 0}
        self.snake_len = 5
        self.snake = [(0, 0)]
        threading.Thread(target=self.get_input, daemon=True, name="input").start()

    def get_input(self):
        while self.running:
            key = self.screen.screen.getch()
            if key == curses.KEY_UP and self.direction != Direction.DOWN:
                self.direction = Direction.UP
            elif key == curses.KEY_DOWN and self.direction != Direction.UP:
                self.direction = Direction.DOWN
            elif key == curses.KEY_RIGHT and self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT
            elif key == curses.KEY_LEFT and self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            elif chr(key) == 'q':
                self.running = False
            elif chr(key) == 'p':
                self.pause = not self.pause

    def delete_snake_tail(self):
        while len(self.snake) > self.snake_len:
            self.screen.window.addstr(1 + self.snake[0][0], 1 + self.snake[0][1], " ")
            del self.snake[0]

    def run(self):
        self.screen.window.box()
        issues = ''
        while self.running:
            if self.pause:
                while self.pause:
                    time.sleep(0.05)
            # Move 1 square and refresh.
            try:
                if issues != '':
                    self.screen.screen.addstr(0, 0, f"Fault: {issues}")
                    issues = ''
                else:
                    self.screen.screen.addstr(0, 0, f'{self.pos["x"]}, {self.pos["y"]}')
                self.screen.window.addstr(self.pos["y"] + 1, self.pos["x"] + 1, 'X')
                self.delete_snake_tail()
                vector = self.direction.get_vector()
                self.pos["x"] = (self.pos["x"] + vector['x']) % self.w
                self.pos["y"] = (self.pos["y"] + vector['y']) % self.h
                self.snake.append((self.pos["y"], self.pos["x"]))
                self.screen.refresh_all()
            except Exception as e:
                issues += repr(e)
            time.sleep(0.25)


def main(std_scr):
    snake = Snake(ScreenInterface(std_scr, 11, 17))
    snake.start()
    snake.join()


if __name__ == "__main__":
    wrapper(main)
