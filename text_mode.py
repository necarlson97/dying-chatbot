
import time
import random
import curses
import threading
import os
import string

random.seed('a')

class Engine():

  border = '#'

  cursor = '█'

  blink_time = 4000

  def new_row(self, *args):
    return [' ']*self.cols

  def corr_row(self, row=-1, rate=.0001, *args):
    return [rate]*self.cols

  def new_cols(self, new_row_funct):
    return [new_row_funct(r) for r in range(self.rows)]

  def __init__(self, stdscr):
    self.stdscr = stdscr

    self.log_file = open('.log.txt', 'w')
    
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
      curses.init_pair(i, i, 0)
    stdscr.bkgd(' ', curses.color_pair(1))

      
    
    curses.noecho()
    curses.curs_set(0)
    self.stdscr.nodelay(True)

    self.buffer = ''
    self.update_count = 0

    # Screen size of the Exidy Sorcerer (reversed?)
    self.resize(64, 30)

  def log(self, *args):
    s = ', '.join([str(e) for e in args])
    s += '\n'
    self.log_file.write(s)

  def resize(self, rows=-1, cols=-1):
    self.rows, self.cols = self.stdscr.getmaxyx()
    self.rows -= 1
    self.cols -= 1
    if 0 < rows and rows < self.rows:
      self.rows = rows
    if 0 < cols and rows < self.cols:
      self.cols = cols

    # Memory of the screen state (list comprehension creates deep copies)
    self.matrix = self.new_cols(self.new_row)
    self.corrupt_matrix = self.new_cols(self.corr_row)
    self.log({self.rows}, {self.cols})

  def run(self):
    self.running = True
    while self.running:
      self.update()
      self.render()
    self.cleanup()
  
  def cleanup(self):
    curses.endwin()
    self.log_file.close()

  def update(self):
    self.update_count += 1
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
      self.buffer = self.buffer[:self.cols-1]

  def render(self):
    self.write_to(self.rows-1, 0, self.buffer)
    if self.update_count % self.blink_time*2 > self.blink_time:
      self.write_to(self.rows-1, len(self.buffer), self.cursor)
    else:
      self.write_to(self.rows-1, len(self.buffer), ' ')
    for r in range(0, len(self.matrix)):
      for c in range(0, len(self.matrix[r])):
        if random.random() < self.corrupt_matrix[r][c]:
          letter = random.choice(string.printable)
          self.stdscr.addch(r, c, letter)
        else:
          color = random.randint(0, curses.COLORS)
          self.stdscr.addstr(r, c, self.matrix[r][c], curses.color_pair(color))

  def write_to(self, r=0, c=0, s=''):
    if not isinstance(s, str):
      s = str(s)
    for l in s:
      self.matrix[r][c] = l
      c+=1
      if c >= self.cols: break

  def from_bottom(self, s):
    self.log(s)
    self.clear_row()
    self.write_to(self.rows-1, 0, s)
    self.matrix.pop(0)
    self.matrix.append(self.new_row(0))
    self.corrupt_matrix.pop(0)
    self.corrupt_matrix.append(self.corr_row())

  def clear_row(self, r=-1):
    if r < 0: r = self.rows + r
    self.matrix[r] = self.new_row(r)

    
def create(stdscr):
  eng = Engine(stdscr)
  eng.run()

if __name__ == '__main__':
  curses.wrapper(create)
  
def start():
  eng = curses.wrapper(create)

  thr = threading.Thread(target=eng.run)
  thr.daemon = True
  thr.start()

  return eng
