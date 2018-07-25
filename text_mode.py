import random
import curses
import threading

random.seed('a')

class Engine():

  colors = {}
  colors['system'] = 8 # gray

  def __init__(self, stdscr):
    self.stdscr = stdscr

    self.log_file = open('.log.txt', 'w')

    curses.noecho()
    curses.curs_set(0)
    self.stdscr.nodelay(True)

    self.update_count = 0
    self.corr_default = 0

    self.resize(30, 30)

  # LIFECYCLE
  def setup(self):
    for key, val in self.colors.items():
      self.colors[key] = curses.color_pair(val)

    for i in range(0, curses.COLORS):
      try:
        curses.init_pair(i, i, 0)
      except curses.error:
        continue

  def run(self):
    self.running = True
    self.setup()
    while self.running:
      self.update()
      self.render()
    self.cleanup()
  
  def cleanup(self):
    curses.endwin()
    self.log_file.close()

  # EACH CYCLE
  def update(self):
    self.update_count += 1
    c = self.stdscr.getch()
    if c == curses.KEY_EXIT or c == 27:
      self.running = False
    elif c == curses.KEY_RESIZE:
      self.resize()
    self.key(c)

  def render(self):
    for r in range(0, len(self.matrix)):
      for c in range(0, len(self.matrix[r])):
        color = self.color_matrix[r][c]
        if random.random() < self.corrupt_matrix[r][c]:
          letter = random.randint(32, 126)
          self.stdscr.addch(r, c + self.offset, letter)
        else:
          self.stdscr.addstr(r, c + self.offset, self.matrix[r][c], color)

  # HIGH LEVEL / UTILITY
  def key(self, c):
    # Overwrite me
    return

  def log(self, *args, end='\n'):
    s = ', '.join([str(e) for e in args])
    s += end
    self.log_file.write(s)

  def write_to(self, r=-1, c=0, s='', corr=[], colors=[], color=-1):
    if not isinstance(s, str):
      s = str(s)

    if r < 0:
      r += self.rows

    for l in s:
      self.matrix[r][c] = l
      if corr:
        self.corrupt_matrix[r][c] = corr.pop(0)
      if colors:
        self.color_matrix[r][c] = colors.pop(0) 
      elif color > 0:
        self.color_matrix[r][c] = color
      c+=1
      if c >= self.cols: break

  def resize(self, rows=-1, cols=-1):
    max_rows, max_cols = self.stdscr.getmaxyx()
    max_cols -= 1
   
    self.rows = max_rows
    if 0 < rows and rows < max_rows:
      self.rows = rows
    self.cols = max_cols
    if 0 < cols and rows < max_cols:
      self.cols = cols

    self.offset = (max_cols - self.cols) // 2

    # Memory of the screen state (list comprehension creates deep copies)
    self.matrix = self.new_cols(self.new_row)
    self.corrupt_matrix = self.new_cols(self.corr_row)
    self.color_matrix = self.new_cols(self.color_row)
    self.log(f'Resize: {self.rows}, {self.cols}')

  # ROW MANAGEMENT
  def clear_row(self, r=-1):
    if r < 0: r = self.rows + r
    self.matrix[r] = self.new_row(r)
    self.corrupt_matrix[r] = self.corr_row(r)
    self.color_matrix[r] = self.color_row(r)

  def new_row(self, *args):
    return [' ']*self.cols

  def corr_row(self, row=-1, rate=-1, *args):
    if rate < 0:
      rate = self.corr_default
    return [rate]*self.cols

  def color_row(self, row=-1, color=-1, *args):
    if color < 0:
      color = self.colors['system']
    return [color]*self.cols

  def new_cols(self, new_row_funct):
    return [new_row_funct(r) for r in range(self.rows)]

# CREATE & START
def create(EngType):
  def _create(stdscr):
    eng = EngType(stdscr)
    eng.run()
  curses.wrapper(_create)

def start(EngType=Engine, threaded=False):
  if threaded:
    thr = threading.Thread(target=create, args=(EngType,))
    thr.daemon = True
    thr.start()
  else:
    create(EngType)

if __name__ == '__main__':
  start()
