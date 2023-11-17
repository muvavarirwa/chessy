import numpy as np
import random

from collections import defaultdict
step_action_dict = defaultdict()
step_action_dict['random_moves'] = defaultdict()
step_action_dict['policy_moves'] = defaultdict()

numeric_names = {'w_R0': 1, 'w_K0': 2, 'w_B0': 3, 'w__K': 4, 'w__Q': 5, 'w_B1': 6, 'w_K1': 7, 'w_R1': 8, 'w_P0': 9, 'w_P1': 10, 'w_P2': 11, 'w_P3': 12, 'w_P4': 13, 'w_P5': 14, 'w_P6': 15, 'w_P7': 16, 'b_P0': -16, 'b_P1': -15, 'b_P2': -14, 'b_P3': -13, 'b_P4': -12, 'b_P5': -11, 'b_P6': -10,'b_P7': -9, 'b_R0': -8, 'b_K0': -7, 'b_B0': -6, 'b__K': -5, 'b__Q': -4, 'b_B1': -3, 'b_K1': -2, 'b_R1': -1}

class Game:
  """Game controller. Creates board. Invokes Team() to create teams+players. Updates and maintains game state"""

  move_count = 0
  not_deadlocked = True
  score_board = {}

  def __init__(self, game, cycle, s, size=8, sides=[], display_board_positions=True):
    self.game = game
    self.size = size
    self.board = self.create_board()
    self.sides = sides
    self.team = {}
    self.display_board_positions = display_board_positions
    self.score_board = {}
    self.horizon = ""
    self.states = []
    self.last_action = ""
    self.wins = 0
    self.losses = 0
    self.draws = 0
    self.cycle = cycle
    self.s = s

  def __str__(self):
    #os.system('clear')
    print("\n\n")

    def print_board():
      col = 0

      print("\n", "==" * 30)

      for row_col, player in self.board.items():
        if col % 8 == 0 and col > 0:
          print(" ")
          print(" ")
        if self.board[row_col] == None:
          print("----", end="\t")
        else:
          print(self.board[row_col], end="\t")
        col += 1

    print_board()

  def __repr__(self):
    return 'Game({},{},({},{}))'.format(
      self.game, self.size, [("Team(" + str(i) + ")")
                             for i in range(len(self.team))], self.score_board)

  # Creates board as a dictionary object {(row, col):None}
  def create_board(self):
    return {(row, col): None
            for row in range(0, self.size) for col in range(0, self.size)}

  # Moves game piece to new location on the board
  # If playing competitively, replace incumbent piece
  def update_board(self, player, position):

    if self.board[position] is not None:
      #print("REPLACING: ", self.board[position])
      if (player.board_name.startswith("w")):
        del self.team[1].players[self.board[position]]
      else:
        del self.team[0].players[self.board[position]]

    self.board[position] = player.board_name



  # Inserts team onto board. Invoked when game starts
  def insert_team(self, team):

    self.team[team.team] = team

    [
      self.update_board(team.players[player], team.players[player].curr_pos)
      for player in team.players
    ]
    team.feasible_moves.clear()

    feasible_moves = self.get_feasible_moves(team)

    team.feasible_moves.append(feasible_moves)
    self.team[team.team].feasible_moves = feasible_moves

  # Calculates and returns a list (move_list) of feasible moves
  # Feasible moves are dependent on
  ## (a) where each of the pieces in a team can move to (e.g. all moves that a Pawn can make)
  ## (b) whether team is playing a:
  ### cooperative strategy:  not taking opponent's pieces or
  ### competitive strategy: taking opponent's pieces

  def get_feasible_moves(self, team):
    size = self.size
    move_list = []

    team.feasible_moves.clear()
    self.team[team.team].feasible_moves = []

    for player in team.players:
      curr_pos = team.players[player].curr_pos
      for moves in team.players[player].moves:
        for move in team.players[player].moves:
          new_position = (tuple(
            sum(tuples) for tuples in zip(tuple(curr_pos), tuple(move))))

          if new_position[0] < size and new_position[0] >= 0 and new_position[1] < size and new_position[1] >= 0:
            if team.strategy == "competitive":
              if self.board[new_position] is None:
                move_list.append((team.players[player], move, curr_pos,
                                  new_position))
              elif str(self.board[new_position][0]).lower() != str(
                  team.players[player].board_name[0]).lower():
                move_list.append((team.players[player], move, curr_pos,
                                  new_position))
              else:
                pass
            elif team.strategy == "cooperative":
              if self.board[new_position] is None:
                move_list.append((team.players[player], move, curr_pos,
                                  new_position))
            else:
              pass
    return move_list

  # Returns the apriori conception of a best move (move most valuable players first) from the feasible_moves list
  # In this version of the game: Expert team (rating 10), always calls get_best_move for each play

  def get_best_move(self, turn, _cur_state):
    """Loops through feasible_moves and returns best moves -- based on value"""

    s = self.s

    cur_state = _cur_state[:-1]

    #print("LENGTH of CURR_STATE:\t{}\n".format(len(cur_state)))

    feasible_moves = list( set([(player, move, curr_pos, new_position) for player, move, curr_pos, new_position in self.team[turn].feasible_moves]))

    #print("FEASIBLE_MOVES:\t{}\n".format(feasible_moves))

    svc_endpoint="http://127.0.0.1:9000/policy_move/?"

    def getBestMove(nextStates):
        try:
            best_move = int(s.get(svc_endpoint + "&q=" + nextStates).content)
        except:
            best_move = self.get_random_move(turn, 0)
        return best_move

    def getNextStates(cur_state, moves):
      #print("CURRENT_STATE:\t{}\n".format(cur_state.split(":")))
      #print("LENGTH_CURRENT_STATE:\t{}\n".format(len(cur_state.split(":"))))

      next_states = []

      for move in moves:
        next_state = np.array(cur_state.strip().split(":"),dtype=np.int32)
        cur_pos = move[2][0]*8 + move[2][1] - 1
        new_pos = move[3][0]*8 + move[3][1] - 1
        next_state[new_pos] = next_state[cur_pos]
        next_state[cur_pos] = 0
        #print(len(next_state))
        next_state = ":".join([str(x) for x in next_state])
        next_states.append(next_state)
      return "_".join(next_states)

    nextStates = getNextStates(cur_state,feasible_moves)

    #print(nextStates)

    bestMove = getBestMove(nextStates)

    return  feasible_moves[bestMove]

  # Returns a random selection from teh feasible_moves list
  # In this version of the game: Novice team (rating 1), always calls get_random_move for each play

  def get_random_move(self, turn,teamTurn):
      global random_moves
      """Loops through feasible_moves, selects and returns random moves"""
      moves = list(set([(player, move, curr_pos, new_position) for player, move, curr_pos, new_position in self.team[turn].feasible_moves]))

      random_move = None

      king = 'w__K' if turn == 0 else 'b__K'

      checkMatePos = teamTurn.players[king].curr_pos

      #print("Other King:\t{}\tPosition:\t{}\n".format(king, checkMatePos))

      newPositions = [x[3] for x in moves]

      #print("NEW_POSITIONS:\t{}\n".format(newPositions))

      checkMateMove = None

      try:
        checkMateMove = newPositions.index(checkMatePos)
      except:
        pass

      #print("checkMateMove:\t{}\tcheckMatePos:\t{}\n".format(checkMateMove, checkMatePos))

      if checkMateMove:
        print("CheckMate!!!!  CUR_POS:\t{}\tMOVE:\t{}\n".format(checkMatePos,checkMateMove))
        random_move = moves[checkMateMove]
      else:
        random_move = random.choice(moves)

      #random_moves += 1

      #print("\nmove:\t{}\n".format(random_move))
      if not self.move_count in step_action_dict['random_moves']:
          step_action_dict['random_moves'][self.move_count] = 0

      step_action_dict['random_moves'][self.move_count] += 1
      return random_move

  def getBin(self, num):
      if int(num) != 0:
          #return "{2:{fill}6b}".format(int(num)+17, fill='0')
          return str(num)+":"
      else:
          #return "{0:{fill}6b}".format(0, fill='0')
          return str(num)+":"

  # Controls game execution by letting each team play (self.move_count % self.sides)
  # Runs until "not_deadlocked" status turns false, which occurs when number of available moves for the team whose
  # turn it is to play is zero. e.g. len(self.team[turn]feasible_moves == 0)
  def step(self):
    """ Invoked by run_trials() -- runs until there are no more board-positions for players to take"""

    global not_deadlocked
    global actions
    global rewards
    global history
    global RESULTS
    global summary_dict

    turn = self.move_count % len(self.sides)

    state = self.board

    board = np.zeros(len(state.keys()), int).reshape(8, 8)

    for board_position in state.keys():
      try:
        if numeric_names[state[board_position]] < 64:
          board[board_position] = numeric_names[state[board_position]]
        else:
          pass
      except:
        pass

    state   = "".join([self.getBin(x) for x in board.flatten()])

    self.team[turn].feasible_moves.clear()
    self.team[turn].feasible_moves = self.get_feasible_moves(self.team[turn])

    #print("SELF[TURN].FEASIBLE_MOVES:\t{}".format(self.team[turn].feasible_moves))


    action_size = len(self.team[turn].feasible_moves)

    terminal_state = None
    #side_0_terminated = False
    #side_1_terminated = False

    side_0_terminated = "w__K" not in list(self.team[0].players.keys())
    side_1_terminated = "b__K" not in list(self.team[1].players.keys())


    if action_size == 0 or side_0_terminated or side_1_terminated:
        terminal_state = True
    else:
        terminal_state = False


    if not terminal_state:

      if self.team[turn].move_choice[self.move_count]:
        player, move, curr_pos, new_position = self.get_best_move(turn,state)
      else:
        otherTurn = 0 if turn == 0 else 1
        player, move, curr_pos, new_position = self.get_random_move(turn, self.team[otherTurn])

      action_verbose  = str((player, move, curr_pos, new_position)).replace(" ","")
      state   = "".join([self.getBin(x) for x in board.flatten()])
      value   = -1

      if player.start_pos[0] > 1:
        player_id = player.start_pos[0]*8 + player.start_pos[1] - 64
      else:
        player_id = player.start_pos[0]*8 + player.start_pos[1] + 1


      action_sparse = str(player_id).replace(" ","") + "," + str( move[0]).replace(" ","") + "," + str( move[1]).replace(" ","")
      state_action = str(self.cycle) + "\t" + str(turn) + "\t" + str(self.move_count) + "\t" + str(state).replace(" ","") + "\t" +  str(value) + "\t" + str(action_sparse) + "\t" + action_verbose + "\t" + str(action_size) +"\t" + str(0) + "\n"
      self.horizon += state_action
      self.last_action = state_action
      self.states.append(state)
      self.board[curr_pos] = None

      self.update_board(player, new_position)

      [
          self.team[turn].players[playerr].set_position(new_position)
          for playerr in self.team[turn].players
          if self.team[turn].players[playerr].board_name == player.board_name
      ]

      self.team[turn].Points += player.value

      self.team[turn].feasible_moves.clear()
      if self.display_board_positions:
        self.__str__()


      self.move_count += 1

    if terminal_state:

      side_0_terminated = "w__K" not in list(self.team[0].players.keys())
      side_1_terminated = "b__K" not in list(self.team[1].players.keys())

      for turns in range(len(self.sides)):

        summary = str(self.cycle) + "," + str(self.team[turns].name) + "," + str(
          self.move_count) + "," + str(self.team[turns].Points)

        #score_board[turns].append(tuple((self.cycle, self.team[turns].Points)))

      if side_0_terminated:
            value   = -1
            self.losses = 1
      elif side_1_terminated:
            value   = 1
            self.wins = 1
      else:
            value   = 0
            self.draws = 1

      state_action = self.last_action.split("\t")
      state_action[-5] = str(value)
      state_action[-2] = str(0)
      state_action[-1] = str(1) + "\n"
      state_action = "\t".join(state_action)
      self.horizon += state_action
      self.horizon += "\n"
      self.not_deadlocked = False


