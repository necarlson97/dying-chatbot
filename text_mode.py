
import time
import random
import curses
import threading

random.seed('a')

class Engine():

  running = True

  stdscr = None # the curses 'screen' or 'window'
  border = '#'

  # Default: Screen size of the Exidy Sorcerer
  # overwritten by actual current size of terminal
  rows = 30
  cols = 64

  buffer = ''

  def new_row(self, r):
    return [' ']*self.cols

  def __init__(self, stdscr):
    self.stdscr = stdscr
    
    curses.start_color()
    curses.noecho()
    curses.curs_set(0)
    self.stdscr.nodelay(True)

    self.resize()
    self.matrix = [self.new_row(r) for r in range(self.rows)]
    

  def resize(self):
    self.rows, self.cols = self.stdscr.getmaxyx()
    self.rows -= 1
    self.cols -= 1
    # Memory of the screen state (list comprehension creates deep copies)
    self.matrix = [self.new_row(r) for r in range(self.rows)]
    self.from_bottom(f'{self.rows}, {self.cols}')

  def run(self):
    while self.running:
      self.update()
    curses.endwin()

  def update(self):
    c = self.stdscr.getch()
    if c == curses.KEY_EXIT or c == 27:
      self.running = False
    elif c == curses.KEY_RESIZE:
      self.resize()
    elif c == curses.KEY_ENTER or c == 10:
      self.from_bottom(self.buffer)
      self.buffer = ''
    elif c == curses.KEY_DC or c == 127:
      self.clear_row()
      self.buffer = self.buffer[:-1]
    elif c > 0:
      self.buffer += chr(c)
      self.buffer = self.buffer[:self.cols]
    self.render()

  def render(self):
    self.write_to(self.rows-1, 0, self.buffer)
    self.write_to(self.rows-1, 0, self.buffer)
    for r in range(0, len(self.matrix)):
      for c in range(0, len(self.matrix[r])):
        self.stdscr.addch(r, c, self.matrix[r][c])

  def write_to(self, r=0, c=0, s=''):
    for l in s:
      self.matrix[r][c] = l
      c+=1
      if c >= self.cols: break

  def from_bottom(self, s):
    self.write_to(self.rows-1, 0, s)
    self.matrix.pop(0)
    self.matrix.append(self.new_row(0))

  def clear_row(self, r=-1):
    if r < 0: r = self.rows + r
    self.matrix[r] = self.new_row(r)


if __name__ == '__main__':
  eng = curses.wrapper(create)
  eng.run()

    
def create(stdscr):
  return Engine(stdscr)

  
def start():
  eng = curses.wrapper(create)

  thr = threading.Thread(target=eng.run)
  thr.daemon = True
  thr.start()

  return eng
