class Player_Template:
  """Player template: Generic player class invoked by Team using "TYPE" method"""

  def __init__(self, name, board_name, start_pos, moves, value, number=1):
    self.name = name
    self.board_name = board_name
    self.start_pos = start_pos
    self.curr_pos = start_pos
    self.moves = moves
    self.value = value
    self.number = number
    self.image = None

  def __str__(self):
    return 'Player_Template of name: {}, board_name: {}, ' \
           'start_pos: {}, curr_pos: {}, moves: {}, ' \
           'value: {}, number: {}'.format(  self.name,
                                            self.board_name,
                                            self.start_pos,
                                            self.curr_pos,
                                            [move for move in self.moves],
                                            self.value,
                                            self.number)

  def __repr__(self):
    return self.name

  def get_position(self):
    return self.curr_pos

  def set_position(self, pos):
    self.curr_pos = pos

  # deprecated, replaced by set_position()
  def move_player(self, new_pos):
    pass
