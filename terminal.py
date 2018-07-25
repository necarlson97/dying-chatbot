from text_mode import Engine, start

class Terminal(Engine):

  border = '|'
  cursor = '█'

  blink_time = 1000

  def setup(self):
    self.colors['error'] = 196 # red (also 1 is red)
    # 232-255 on is different colors of gray
    # beyond 255 is reversed
    self.colors['user'] = 7 # white
    self.colors['bg'] = 9 # Specail dark gray bg

    self.buffer = ''

    self.slow_write_speed = 200
    self.to_write = []

    super().setup()

  # EACH CYCLE
  def update(self):
    super().update()

    if self.to_write and self.update_count % self.slow_write_speed == 0:
      self.log(self.to_write[0])
      if self.to_write[0] == 'UP':
        self.buffer = ''
        self.push_up()
        self.to_write.pop(0)
      else:
        self.buffer_write(self.to_write.pop(0))

  def render(self):
    # Write out buffer at bottom of screen
    buffer_user = 'bot' if self.to_write else 'user'
    self.write_to(s=self.buffer, color=self.colors[buffer_user])

    super().render()

    # Draw border
    for r in range(0, len(self.matrix)):
      if self.offset > 0:
        self.stdscr.addch(r, self.offset - 1, self.border)
        self.stdscr.addch(r,self.offset + self.cols, self.border)

    # blink cursor
    if not self.to_write and self.update_count % self.blink_time*2 > self.blink_time:
      self.stdscr.addstr(self.rows-1, self.offset + len(self.buffer), self.cursor, self.colors['system'])

  # HIGH LEVEL / UTILITY
  def key(self, c):
    if self.to_write:
      return

    if c == 10: # Enter
      self.push_up()
      self.buffer = ''
    elif c == 127: # Escape
      self.clear_row()
      self.buffer = self.buffer[:-1]
    elif c > 0:
      self.buffer_write(chr(c))

  def buffer_write(self, ch):
    self.buffer += ch
    self.buffer = self.buffer[:self.cols-1]

  def push_up(self):
     # Write out buffer at bottom of screen
    self.matrix.pop(0)
    self.matrix.append(self.new_row(0))
    self.corrupt_matrix.pop(0)
    self.corrupt_matrix.append(self.corr_row())
    self.color_matrix.pop(0)
    self.color_matrix.append(self.color_row())

if __name__ == '__main__':
  start(Terminal)
