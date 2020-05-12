########################################################################################################################
#
# CHESSY v1.0: A generic OOP framework for board games [aspirationally]
#
#
# Author: Ranga Muvavarirwa
#
#
# Motivation:
## Many situations arise whereby two sides need to simultaneously use a public good [e.g. a river, a game board etc] in
## pursuit of their own self-regarding goals (e.g. cross river, get as many pieces as possible to otherend of the board]
## Traditional solutions to such situations have typically modelled participant behavior and the ensuring game-strategy
## as none-coopertive/winner-takes-all/zero-sum games: the outcomes of which (war, tragedy of the commons etc) are often
## often inefficient and/or unacceptable
#
#
# Hypothesis
## Participants (societies, game players etc) would select a cooperative approach -- if they could identify a set of
## viable paths whose collective cost (number of participants for whom a path could not be found) was less than some
## predetermined cost of a zero-sum approach (cost of one side losing + cost of half-winning side)
#
#
# Goal
# Create a cooperative version of a board game (v1 supports chess), whose main objective is to determine whether both
# sides can achieve a shared objective (get as many pieces as possible to the other side of the board) -- without
# 'taking any pieces from the 'opposing' team. v2 will provide a mechanism for comparing the distribution of costs/value
# between cooperative vs competitive iterations
#
#
# KEY CONCEPTS
# Framework supports any game scenario whose geometry can be implemented programmatically (chess, chechers, go etc)
# Players can enter game at any point in time (need not be simultaneous). Available in v2
# Players can have different skill levels [1 = Novice 10 = Expert]
## Creates a harness for evaluating expert performance -- relative to a random agent
## Subsequent iterations could use this harness to train the expert (by evaluating moves by a random agent that beats
## the expert ( Bayesian approaches might be useful here ).
#
#
# ARCHITECTURE
# Chessy employs two patterns:
## a form of dependency injection whereby metadata specifying the rules of a game are
## presented in JSON/Python-dictionary format [refer games dictionary object below]
##
## dynamic class creation using the "TYPE" method for specifying classes [King, Queen, Bishop etc] as well as for
## instantiating specific players [b_Pawn_01, w_King, b_K1 etc)
#
#
# ORGANIZATION
#
## CLASSES
##
### Game: Controller. Creates board. Invokes Team() to create teams+players. Updates and maintains game state (time_step)
### Team: Instance per team. Invoked by Game(). Invokes Player_Template
### Player_Template: Generic player class. Invoked by Team()
### Incorrect_Input_error: Generic exception handler for inputs
### UserInput: [arguably duplicative] class by which an object is initialized with user_inputs as properties
#
#
## METHODS
### Main: initiates program
### run_trials: Iterates through num_trials. Candidate for multiprocessing refactor.
### plot_results: Display results using MatPlotLib
#
#
#
########################################################################################################################

games = {
  "chessy": {
    "players": {
      "Pawn": {
        "name": "p",
        "start_pos": [(1, 0), (6, 0)],
        "moves": [[(1, 0), (1, -1), (1, 1)], [(-1, 0), (-1, -1), (-1, 1)]],
        "number": 8,
        "value": 1,
        "image": [u"\u265F", u"\u2659"]
      },
      "Knight": {
        "name":
        "K",
        "start_pos": [[(0, 1), (7, 1)], [(0, 6), (7, 6)]],
        "moves": [[(1, -2), (1, 2), (2, -1), (2, 1)], [(-1, -2), (-1, 2),
                                                       (-2, -1), (-2, 1)]],
        "number":
        2,
        "value":
        3,
        "image": [u"\u265E", u"\u2658"]
      },
      "King": {
        "name": "_K",
        "start_pos": [(0, 3), (7, 3)],
        "moves": [[(1, -1), (1, 0), (1, 1)], [(-1, -1), (-1, 0), (-1, 1)]],
        "number": 1,
        "value": 20,
        "image": [u"\u265A", u"\u2654"]
      },
      "Queen": {
        "name": "_Q",
        "start_pos": [(0, 4), (7, 4)],
        "moves": [[(1, -1), (1, 0), (1, 1)], [(-1, -1), (-1, 0), (-1, 1)]],
        "number": 1,
        "value": 9,
        "image": [u"\u265B", u"\u2655"]
      },
      "Bishop": {
        "name": "B",
        "start_pos": [[(0, 2), (7, 2)], [(0, 5), (7, 5)]],
        "moves": [[(1, -1), (1, 1)], [(-1, -1), (-1, 1)]],
        "number": 2,
        "value": 3,
        "image": [u"\u265D", u"\u2657"]
      },
      "Rook": {
        "name": "R",
        "start_pos": [[(0, 0), (7, 0)], [(0, 7), (7, 7)]],
        "moves": [[(1, 0)], [(-1, 0)]],
        "number": 2,
        "value": 5,
        "image": [u"\u265C", u"\u2656"]
      }
    }
  },
  "checkers": {
    "players": {
      "Men": {
        "name":
        "M",
        "start_pos": [[((0, 1)), ((0, 3)), ((0, 5)), ((0, 7)), ((1, 0)), (
          (1, 2)), ((1, 4)), ((1, 6)), ((2, 1)), ((2, 3)), ((2, 5)), ((2, 7))],
                      [(7, 0), (7, 2), (7, 4), (7, 6), (6, 1), (6, 3), (6, 5),
                       (6, 7), (5, 0), (5, 2), (5, 4), (5, 6)]],
        "moves": [[(1, -1), (1, 1)], [(-1, -1), (-1, 1)]],
        "number":
        12,
        "value":
        1,
        "image": [u"\u26C0", u"\u26C2"]
      }
    }
  }
}

########################################################################################################################

import random
import matplotlib.pyplot as plot
import numpy as np
import os

import time, os, fnmatch, shutil

import matplotlib
#matplotlib.use('Agg')
HISTORY_FILE = None

cycle = 0

actions = [[], []]
rewards = [[], []]
history = {"cycle": cycle, "actions": actions, "rewards": rewards, "value": 0}

score_board = {}

########################################################################################################################


class Game:
  """Game controller. Creates board. Invokes Team() to create teams+players. Updates and maintains game state"""

  move_count = 0
  not_deadlocked = True
  global score_board

  def __init__(self, game, size=8, sides=[], display_board_positions=True):
    self.game = game
    self.size = size
    self.board = self.create_board()
    self.sides = sides
    self.team = {}
    self.display_board_positions = display_board_positions
    self.score_board = score_board
    self.horizon = ""
    self.states = [] 
    self.last_action = ""

  def __str__(self):
    os.system('clear')

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
        print(self.team[0].players.keys())
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

  def get_best_move(self, turn):
    """Loops through feasible_moves and returns best moves -- based on value"""

    moves = list(
      set([(player, move, curr_pos, new_position)
           for player, move, curr_pos, new_position in self.team[turn]
           .feasible_moves]))
    #print("\n\n","=="*30,"\n\n")
    best_move = moves[0]

    for player, move, curr_pos, new_pos in moves:
      if player.value > best_move[0].value:
        best_move = (player, move, curr_pos, new_pos)
        #print("\nmove:\t{}\n".format(best_move))
        #print("BEST MOVE:\t{}".format(best_move))
    return best_move

  # Returns a random selection from teh feasible_moves list
  # In this version of the game: Novice team (rating 1), always calls get_random_move for each play

  def get_random_move(self, turn):
    """Loops through feasible_moves, selects and returns random moves"""
    moves = list(
      set([(player, move, curr_pos, new_position)
           for player, move, curr_pos, new_position in self.team[turn]
           .feasible_moves]))
    random_move = random.choice(moves)
    #print("\nmove:\t{}\n".format(random_move))
    return random_move

  # Controls game execution by letting each team play (self.move_count % self.sides)
  # Runs until "not_deadlocked" status turns false, which occurs when number of available moves for the team whose
  # turn it is to play is zero. e.g. len(self.team[turn]feasible_moves == 0)
  def time_step(self):
    """ Invoked by run_trials() -- runs until there are no more board-positions for players to take"""

    global not_deadlocked
    global actions
    global rewards
    global history
    global HISTORY_FILE

    turn = self.move_count % len(self.sides)

    state = self.board

    board = np.zeros(len(state.keys()), int).reshape(8, 8)

    numeric_names_ = dict([(x[1], x[0] + 1)
                           for x in enumerate(filter(None, state.values()))])

    temp_num_names = numeric_names_.values()

    temp_list = []

    for num_name in temp_num_names:
      if num_name > 16:
        temp_list.append(num_name - 33)
      else:
        temp_list.append(num_name)

    numeric_names = dict(zip(numeric_names_, temp_list))

    for board_position in state.keys():
      try:
        if numeric_names[state[board_position]] < 64:
          board[board_position] = numeric_names[state[board_position]]
        else:
          pass
      except:
        pass

    self.team[turn].feasible_moves.clear()
    self.team[turn].feasible_moves = self.get_feasible_moves(self.team[turn])

    
    if len(self.team[turn].feasible_moves) == 0 or "w__K" not in self.team[0].players or "b__K" not in self.team[1].players:
      #print("\n\nCould not identify any feasible moves....")
      
      for turns in range(len(self.sides)):

        summary = str(cycle) + "," + str(self.team[turns].name) + "," + str(
          self.move_count) + "," + str(self.team[turns].Points)

        score_board[turns].append(tuple((cycle, self.team[turns].Points)))
      
        if len(self.team[turn].feasible_moves) == 0 or "w__K" not in self.team[0].players or "b__K" not in self.team[1].players:

          if "w__K" not in self.team[0].players:
              value   = -20
          elif "b__K" not in self.team[1].players:
              value   = 20
          else:
              value   = 0

        state_action = self.last_action.split("\t")

        state_action [-5] = str(value)

        state_action = "\t".join(state_action)

        self.horizon += state_action

      with open(HISTORY_FILE, "a") as history_file:
        horizon = str(self.horizon)
        history_file.write(horizon)
        history_file.write("\n")


      self.not_deadlocked = False

    else:

      if self.team[turn].move_choice[self.move_count]:
        player, move, curr_pos, new_position = self.get_best_move(turn)


      else:

        player, move, curr_pos, new_position = self.get_random_move(turn)
      
      action_verbose  = str((player, move, curr_pos, new_position)).replace(" ","")
      state   = [x for x in board.flatten()]
      value   = -1

      if player.start_pos[0] > 1:
          player_id = player.start_pos[0]*8 + player.start_pos[1] - 65
      else:
          player_id = player.start_pos[0]*8 + player.start_pos[1]

      action_sparse = str(player_id).replace(" ","") + "," + str( move[0]).replace(" ","") + "," + str( move[1]).replace(" ","")

      state_action = str(cycle) + "\t" + str(self.move_count) + "\t" + str(state).replace(" ","") + "\t" +  str(value) + "\t" + str(action_sparse) + "\t" + action_verbose + "\t" + str(0) +"\t" + str(0) + "\n"

      self.horizon += state_action
      self.last_action = state_action
      
      self.board[curr_pos] = None
      self.update_board(player, new_position)

      [
        self.team[turn].players[playerr].set_position(new_position)
        for playerr in self.team[turn].players
        if self.team[turn].players[playerr].board_name == player.board_name
      ]

      self.team[turn].Points += player.value
      #print("Player:\t{}\tCurrent_Position:\t{}\tNew_Position:\t{}".format(player, curr_pos, new_position))

      #print("\nTotal Points for TEAM: ", self.team[turn].name, " IS: ", self.team[turn].Points,"\n")
      self.team[turn].feasible_moves.clear()
      if self.display_board_positions:
        self.__str__()
      self.move_count += 1


########################################################################################################################
# Generic class for players
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


########################################################################################################################


class Team:
  """ Generic Team class: Invoked by Game to create once per each team.
        Maintains game status for each team.
        Referenced by Game object via game.teams[num] property """

  class_list = {}
  Points = 0

  def __init__(self, game, name, team, rating, strategy="cooperative"):
    self.game = game
    self.name = name
    self.team = team
    self.players = self.create_team()
    self.feasible_moves = []
    self.side = team
    self.strategy = strategy
    self.rating = rating
    self.move_choice = self.create_move_choices()

  def __str__(self):
    return 'Team of game: {}, name: {}, ' \
           'team: {}, players: {}, ' \
           'feasible_moves: {}, side: {}, rating: {}, ' \
           'strategy: {},' \
           'move_choice: {}'.format(    self.game,
                                        self.name,
                                        self.team,
                                        [("Player_Template(" + str(i) + ")") for i in range(len(self.players))],
                                        [move for move in self.feasible_moves],
                                        self.side,
                                        self.strategy,
                                        self.rating,
                                        [move for move in self.move_choice])

  def __repr__(self):
    return 'Team({},{},{},{},{},{},{},{},{})'.format(
      self.game, self.name, self.team, [("Player_Template(" + str(i) + ")")
                                        for i in range(len(self.players))],
      [move for move in self.feasible_moves], self.side, self.strategy,
      self.rating, [move for move in self.move_choice])

  def __iter__(self):
    return self.__next__()

  def __next__(self):
    for i in range(self.num_players):
      yield list(self.players)[i]

  # Instantiates player objects
  # Stores and returns dictionary with player objects (players)
  def create_team(self):
    players = {}
    prefix = ["w_", "b_"]
    for role in games[self.game]["players"]:
      moves     = games[self.game]["players"][role]['moves']
      number    = games[self.game]["players"][role]['number'] 
      value     = games[self.game]["players"][role]['value'] 
      name      = games[self.game]["players"][role]['name']
      image     = games[self.game]["players"][role]['image']
      start_pos = games[self.game]["players"][role]['start_pos'] 
      # name, start_pos, moves, number, value, image = list(games[self.game]["players"][role].values())
      # print(games[self.game]["players"][role].keys())
      # print("NAME:\t{}\t:START_POS:\t{}\tMOVES:\t{}\tNUMBER:\t{}\tVALUE:\t{}\tIMAGE:\t{}".format(name, start_pos, moves, number, value, image))
      # print(name, start_pos, moves, number, value, image)

      my_dict = dict(games[self.game]["players"][role].items())

      # print("name:\t{}\tstart_pos:\t{}\tmoves:{}\tnumber:\t{}:\tvalue:\t{}".format(name,start_pos,moves, number,value))

      # Dynamic type creation using TYPE method
      # Used insights from https://youtu.be/fhqE7aS6cj8 at 2mins:20s
      self.class_list[role] = type(role, (Player_Template, ), my_dict)

      if number == 1:
        board_name = prefix[self.team] + "_" + role[0].upper()
        s_pos = start_pos[self.team]
        players[board_name] = self.class_list[role](role, board_name, s_pos,
                                                    moves[self.team], value)
      elif number == 2:
        for i in range(number):
          board_name = prefix[self.team] + role[0].upper() + str(i)
          s_pos = start_pos[i][self.team]
          players[board_name] = self.class_list[role](role, board_name, s_pos,
                                                      moves[self.team], value)
      else:
        for i in range(number):
          board_name = prefix[self.team] + role[0].upper() + str(i)
          #print("BOARD_NAME: ", board_name)
          #print("DEBUGGING: tuple(start_pos[self.team]): \n", tuple(start_pos[self.team]), "\n tuple((0, int(i))): ", tuple((0, int(i))) )
          #print("ZIP: ", zip(tuple(start_pos[self.team]), tuple(tuple((0, int(i))))).__next__(), "INT(i) = ", i)
          s_pos = (tuple(
            sum((position))
            for position in zip(
              tuple(start_pos[self.team]), tuple((0, int(i))))))
          players[board_name] = self.class_list[role](role, board_name, s_pos,
                                                      moves[self.team], value)
    return players

  def create_move_choices(self):
    return (random.choices([0, 1], [1 - self.rating, self.rating], k=1000))

  def get_roles(self):
    [
      print(
        type(self.class_list[a_class]), "\t", self.class_list[a_class].name,
        "\t", self.class_list[a_class].number, "\t",
        self.class_list[a_class].value) for a_class in self.class_list
    ]

  def get_players(self):
    #print("CLASS \t\t\t\t\t\tINSTANCE\tSTART_POS\tCURR_POS\tMOVES")
    [
      print(
        type(self.players[player]), "\t", self.players[player].board_name,
        "\t\t", self.players[player].start_pos, "\t",
        self.players[player].start_pos, "\t", self.players[player].moves)
      for player in self.players
    ]


########################################################################################################################


class Incorrect_Input_error(Exception):
  """Generic input error handler: raised in the case that any of the user inputed data is incorrect"""
  pass


########################################################################################################################


class userInput:
  """ Class captures user input and initializes class-level properties that are subsequently used by other methods
    throughout the program. Although this code is a duplicative -- it simplifies and separates input error handling from
    class/object instantiations. i.e. userInput object separates input acquisition from object (game, team etc)
    instantiation -- by passing 'clean' variables/properties to the respective constructors/initilizers."""

  def __init__(self):
    self.game = self.get_game()
    self.num_sides = self.get_num_sides()
    self.teams = self.get_teams()
    self.num_trials = self.get_num_trials()
    self.display_board_positions = True
    self.get_display_status()

  def __str__(self):
    return 'userInput of game: {}, num_sides: {}, ' \
           'teams: {}, num_trials: {}, ' \
           'display_board_positions: {}'.format(self.game,
                                                self.num_sides,
                                                [("Team(" + str(i) + ")") for i in range(len(self.teams))],
                                                self.num_trials,
                                                self.display_board_positions)

  def __repr__(self):
    return 'userInput({},{},{},{},{})'.format(
      self.game, self.num_sides, [("Team(" + str(i) + ")")
                                  for i in range(len(self.teams))],
      self.num_trials, self.display_board_positions)

  def get_game(self):
    done = False
    while not done:
      try:
        game = input("select a game: ['chessy' or 'checkers']: ")
        if game not in games.keys():
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
      else:
        done = True
        return game

  def get_num_sides(self):
    """Prompts user for, error checks and returns number of sides in game"""
    done = False
    while not done:
      try:
        num_sides = int(input("select number of teams:  [0, 1 or 2] "))
        choices = [0, 1, 2]
        if num_sides > 2 or num_sides < 0:
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
        print(choices)
      else:
        done = True
        return num_sides

  def get_teams(self):
    """Prompts user for, error checks and returns specific information about each team."""

    teams = [{
      str("team_" + str(i)): {
        "team_name": None,
        "color": None,
        "skill": None,
        "strategy": None
      }
    } for i in range(self.num_sides)]
    colors = [
      "blue", "green", "red", "cyan", "magenta", "yellow", "black", "white"
    ]

    for i in range(self.num_sides):
      done = False
      while not done:
        try:
          team_board_name = input(
            "Choose a name for this team [e.g. 'blue_team' or 'green_team']: ")
          if not isinstance(team_board_name, str):
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
        else:
          done = True
          teams[i]["team_name"] = team_board_name

      done = False
      while not done:
        try:
          team_color = input("Choose a color for team_2 [e.g. 'blue': ")
          if team_color not in colors:
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
          print(colors)
        else:
          done = True
          teams[i]["color"] = team_color

      done = False
      while not done:
        try:
          skill_level = int(
            input(
              "Please enter team's skill_level [1 = Novice, 10 = expert]: "))
          choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
          if skill_level > 10 or skill_level < 0 or skill_level not in choices:
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
          print(choices)
        else:
          done = True
          teams[i]["skill"] = skill_level

      done = False
      while not done:
        try:
          strategy = int(
            input(
              "Please enter team's strategy [0 = 'cooperative', 1 = 'competitive']: "
            ).lower())
          choices = [0, 1]
          if strategy > 1 or skill_level < 0:
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
          print(choices)
        else:
          done = True
          if strategy:
            teams[i]["strategy"] = "competitive"
          else:
            teams[i]["strategy"] = "cooperative"

    return teams

  def get_num_trials(self):
    """Prompts user for, error checks and returns number of trials for this iteration of the game"""

    done = False
    while not done:
      try:
        trials = int(
          input("How many trials would you like to run? [1 - 1,000,000] "))
        if trials > 10000000 or trials < 0 or not isinstance(trials, int):
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
        print("[1 - 1,000,000]")
        # self.num_trials = trials
        # return trials
      else:
        done = True
        self.num_trials = trials
        return int(trials)

  def get_display_status(self):
    """Prompts user for, error checks and returns user preference for whether results should be displayed"""

    done = False
    while not done:
      try:
        display_results = str(
          input(
            "Do you want to see the board positions in realtime? [ 'Yes' or 'No' ]"
          )).lower()
        choices = ["yes", "no"]
        if display_results not in choices:
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
      else:
        done = True
        if display_results.lower() == choices[0]:
          self.display_board_positions = True
        else:
          self.display_board_positions = False


########################################################################################################################


def plot_results(user_input):
  """ Plots results from num_trials"""

  team_scores = []
  min_score = 99999999
  max_score = 0

  for j in range(user_input.num_sides):
    team_scores.append([team_points for cycle, team_points in score_board[j]])
    plot.hist(
      team_scores[j],
      bins=100,
      label=user_input.teams[j]["team_name"],
      color=user_input.teams[j]["color"])

    min_j_score = min(team_scores[j])
    max_j_score = max(team_scores[j])

    if min_j_score < min_score:
      min_score = min_j_score
    if max_j_score > max_score:
      max_score = max_j_score

    x_spacing = (max_score - min_score) / 10
    y_spacing = user_input.num_trials / 50

    text_x_pos = min_score
    text_y_pos = 2 * y_spacing

  def create_plot():
    for j in range(user_input.num_sides):
      rating_string = user_input.teams[j]["team_name"] + "_rating: " + str(
        user_input.teams[j]["skill"]) + "\n"
      plot.text(
        text_x_pos,
        text_y_pos + j * y_spacing + y_spacing / 4,
        rating_string,
        size=8,
        color=user_input.teams[j]["color"])
      strategy_string = user_input.teams[j]["team_name"] + "_strategy: " + str(
        user_input.teams[j]["strategy"]) + "\n"
      plot.text(
        text_x_pos,
        text_y_pos + j * y_spacing - y_spacing / 4,
        strategy_string,
        size=8,
        color=user_input.teams[j]["color"])

    plot.title('Chessy: Point distribution by team.')
    plot.xlabel('Score')
    plot.ylabel('Frequency of score')
    plot.legend(loc='upper left')
    plot.grid(color="white")

    plot.text(
      text_x_pos,
      text_y_pos + 2 * y_spacing,
      "#Trials = ",
      size=8,
      color=user_input.teams[0]["color"])
    plot.text(
      text_x_pos + 2 * x_spacing,
      text_y_pos + 2 * y_spacing,
      user_input.num_trials,
      size=8,
      color=user_input.teams[0]["color"])
    plot.tight_layout()

  create_plot()

  plot.show()


########################################################################################################################


def run_trials(user_input):
  """ Runs the num_trials """

  global cycle
  global HISTORY_FILE

  t = time.localtime()
  timestamp = time.strftime('%b_%d_%Y_%H%M', t)

  num_trials = user_input.num_trials
  num_sides = user_input.num_sides

  HISTORY_FILE = ("/data_data/reinforcement_learning/results/history_file_" + str(num_trials) + "_trials_" +
                  str(num_sides) + "_sides_" + str(timestamp))
  """ Clear output file """

  with open(HISTORY_FILE, "w") as history_file:
    history_file.write("\n")

  for i in range(num_trials):
    sides = [x for x in range(num_sides)]
    g1 = Game(user_input.game, 8, sides, user_input.display_board_positions)

    def run_trial():
      for j in range(user_input.num_sides):
        team_name = "team_" + str(j)
        team_name = Team(user_input.game, user_input.teams[j]["team_name"], j,
                         user_input.teams[j]["skill"] / 10,
                         user_input.teams[j]["strategy"])

        ## UNCOMMENT IF YOU WANT TO SEE THE CLASS STRUCTURE
        #if i == 0:
        #    print("\n\n", team_name, "\n\nTeam Roles [Parent Classes]: ")
        #    team_name.get_roles()
        #    print("\n\n", team_name, "\n\nTeam Members [Class instances]: ")
        #    print("=="*30)
        #    team_name.get_players()
        #    pause = input("Press ENTER to continue")

        g1.insert_team(team_name)

      g1.not_deadlocked = True

      while g1.not_deadlocked:
        g1.time_step()

    run_trial()

    cycle += 1


########################################################################################################################


def main():

  global cycle
  global HISTORY_FILE
  global score_board
  score_board[0] = []
  score_board[1] = []
  user_input = userInput()
  run_trials(user_input)
  plot_results(user_input)


main()

########################################################################################################################


