from input_recog import Recog
from terminal import Terminal, start

class Bot(Terminal):

  def setup(self):
    self.colors['bot'] = 172 # orange
    self.recog = Recog()
    self.corr_default = 0 #.1

    super().setup()

    self.soft_reboot()

  def key(self, c):
    buff = self.buffer
    super().key(c)
    if c == 10: # Enter
      self.to_write = [s for s in self.recog.respond(buff)]
      self.to_write.append('UP')
    

  def soft_reboot(self):
    self.write_to(s='REBOOT', color=self.colors['system'])

    for r in range(self.rows):
      self.push_up()

  def correct_memory():
    self.corr_default /= 100
    self.soft_reboot()

if __name__ == '__main__':
  start(Bot)
