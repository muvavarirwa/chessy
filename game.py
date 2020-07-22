import json
import random
import matplotlib.pyplot as plot
import numpy as np
import os
import jsonlines
import ast
import time, os, fnmatch, shutil
from collections import defaultdict
import matplotlib
import requests

from sparse_action_dict import sparse_action_dict
from games  import games
from player import Player_Template
from team   import Team
from userinput import userInput


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
        self.score_board = []
        self.horizon = ""
        self.states = [] 
        self.last_action = ""
        self.last_action_sparse = None
        self.last_reward     = None
        self.wins            = 0
        self.losses          = 0
        self.draws           = 0
        self.random_moves    = 0
        self.policy_moves    = 0
        self.best_moves      = 0
        self.feasible_moves_ = None 
        self.action_ids      = np.arange(0,len(sparse_action_dict.keys()),1)
        self.action_id_dict  = {y:x for x,y in zip(action_ids,sparse_action_dict.keys())}


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
        return 'Game({},{},({},{}))'.format(self.game, self.size, [("Team(" + str(i) + ")")for i in range(len(self.team))], self.score_board)
    
    # Creates board as a dictionary object {(row, col):None}
    def create_board(self):
        return {(row, col): None for row in range(0, self.size) for col in range(0, self.size)}
    
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
        [self.update_board(team.players[player], team.players[player].curr_pos) for player in team.players]
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
                    new_position = (tuple(sum(tuples) for tuples in zip(tuple(curr_pos), tuple(move))))
                
                    if new_position[0] < size and new_position[0] >= 0 and new_position[1] < size and new_position[1] >= 0:
                    
                        if team.strategy == "competitive":    
                            if self.board[new_position] is None:
                                move_list.append((team.players[player], move, curr_pos,new_position))
                        
                        elif str(self.board[new_position][0]).lower() != str(team.players[player].board_name[0]).lower():
                            move_list.append((team.players[player], move, curr_pos,new_position))
                        
                        else:
                            pass
                    elif team.strategy == "cooperative":
                        if self.board[new_position] is None:
                            move_list.append((team.players[player], move, curr_pos,new_position))
                    else:
                        pass
        return move_list
    # Returns the apriori conception of a best move (move most valuable players first) from the feasible_moves list
    # In this version of the game: Expert team (rating 10), always calls get_best_move for each play

    def get_best_move(self, turn, state):
        """Loops through feasible_moves and returns best moves -- based on value"""
        
        global best_moves
        global policy_moves
        global random_moves
        global step_action_dict

        moves = list(set([(player, move, curr_pos, new_position) for player, move, curr_pos, new_position in self.team[turn].feasible_moves]))
        
        try:
            #Testing whether policy_dict returns policy
            state = str(state).replace(" ","")
            
            # I got really lazy here -- need to figure out why data is improperly formatted in the first place
            #player, move, curr_pos, new_position =  policy_dict[state].split("(")[1:]
            request = os.path.join('http://127.0.0.1:8000/policy',state)
            response = requests.get(request)
            player_func, move, curr_pos, new_position = eval(response.json())
            player = player_func()
            best_policy = (player, move, curr_pos, new_position)
            for player_, move_,curr_pos_, new_pos_ in moves:
                if curr_pos_ == curr_pos:
                    best_policy = (player_, move_, curr_pos_, new_pos_)
                    self.policy_moves += 1
                    #if not self.move_count in self.step_action_dict['policy_moves']:
                    #    self.step_action_dict['policy_moves'][self.move_count] = 0
                    #self.step_action_dict['policy_moves'][self.move_count] += 1
                    return best_policy
                else:
                    pass         
        except:
            global random_moves
            """Loops through feasible_moves, selects and returns random moves"""
            moves = list(set([(player, move, curr_pos, new_position) for player, move, curr_pos, new_position in self.team[turn].feasible_moves]))
            random_move = random.choice(moves)
            self.random_moves += 1
            #if not self.move_count in self.step_action_dict['random_moves']: 
            #    self.step_action_dict[self.move_count] = 0
            #    self.step_action_dict['random_moves'][self.move_count] += 1
            #    #print("\nmove:\t{}\n".format(random_move))
            return random_move
        
        # Returns a random selection from teh feasible_moves list
        # In this version of the game: Novice team (rating 1), always calls get_random_move for each play


    def get_random_move(self, turn):
        global random_moves
        """Loops through feasible_moves, selects and returns random moves"""
        global random_moves
        moves = list(set([(player, move, curr_pos, new_position) for player, move, curr_pos, new_position in self.team[turn].feasible_moves]))
        random_move = random.choice(moves)
        self.random_moves += 1

        #print("\nmove:\t{}\n".format(random_move))
        #if not self.move_count in self.step_action_dict['random_moves']:
        #    self.step_action_dict['random_moves'][self.move_count] = 0
        #    self.step_action_dict['random_moves'][self.move_count] += 1

        return random_move


    def getBin(self, num):
            
        if int(num) != 0:
            return "{0:{fill}6b}".format(int(num)+17, fill='0')
        else:
            return "{0:{fill}6b}".format(0, fill='0')

      # Controls game execution by letting each team play (self.move_count % self.sides)
      # Runs until "not_deadlocked" status turns false, which occurs when number of available moves for the team whose
      # turn it is to play is zero. e.g. len(self.team[turn]feasible_moves == 0)

    def step(self,cycle,user_input):
        """ Invoked by run_trials() -- runs until there are no more board-positions for players to take"""

        global not_deadlocked
        global actions
        global rewards
        global history
        
        t = time.localtime()
        timestamp = time.strftime('%b_%d_%Y_%H%M', t)
        
        HISTORY_FILE = ("/data_data/reinforcement_learning/results/history_file_" + str(user_input.num_trials) + "_trials_" + str(user_input.num_sides) + "_sides_" + str(timestamp))
        
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

        self.feasible_moves_ = self.team[turn].feasible_moves
 
        if action_size == 0 or "w__K" not in self.team[0].players or "b__K" not in self.team[1].players:
            #print("\n\nCould not identify any feasible moves....")
            
            for turns in range(len(self.sides)):
                
                summary = str(cycle) + "," + str(self.team[turns].name) + "," + str(self.move_count) + "," + str(self.team[turns].Points)
                
                #score_board[turns].append(tuple((cycle, self.team[turns].Points)))
                
                if len(self.team[turn].feasible_moves) == 0 or "w__K" not in self.team[0].players or "b__K" not in self.team[1].players:
                    
                    
                    if "w__K" not in self.team[0].players:
                        
                        value   = -1
                        #summary_dict['losses'] += 1
                        self.last_reward = -1
                        
                    elif "b__K" not in self.team[1].players:
                        
                        value   = 1
                        #summary_dict['wins'] += 1
                        self.last_reward = 1 
                    else:
                        
                        value   = 0
                        #summary_dict['draws'] += 1
                        self.last_reward = 0
                    
                state_action = self.last_action.split("\t")
                
                state_action[-5] = str(value)            
                
                state_action[-2] = str(0)
                
                state_action[-1] = str(1) + "\n"
                
                state_action = "\t".join(state_action)
                
                self.horizon += state_action
                
            with open(HISTORY_FILE, "a") as history_file:
                horizon = str(self.horizon)
                history_file.write(horizon)
                history_file.write("\n")

            self.not_deadlocked = False
            
        else:

            if self.team[turn].move_choice[self.move_count]:
                try:
                    player, move, curr_pos, new_position = self.get_best_move(turn,state)                    
                except:            
                    player, move, curr_pos, new_position = self.get_random_move(turn)
            else:
                player, move, curr_pos, new_position = self.get_random_move(turn)

            action_verbose  = str((player, move, curr_pos, new_position)).replace(" ","")
            
            state   = "".join([self.getBin(x) for x in board.flatten()])
            
            value   = -1

            if player.start_pos[0] > 1:
                player_id = player.start_pos[0]*8 + player.start_pos[1] - 64
            else:
                player_id = player.start_pos[0]*8 + player.start_pos[1] + 1

            action_sparse = str(player_id).replace(" ","") + "," + str( move[0]).replace(" ","") + "," + str( move[1]).replace(" ","")
            
            state_action = str(cycle) + "\t" + str(self.move_count) + "\t" + str(state).replace(" ","") + "\t" +  str(value) + "\t" + str(action_sparse) + "\t" + action_verbose + "\t" + str(action_size) +"\t" + str(0) + "\n"

            self.horizon += state_action
            self.last_action = state_action
            self.last_action_sparse = action_sparse
            self.last_reward = -1
            self.states.append(state)    
            self.board[curr_pos] = None

            self.update_board(player, new_position)

            [self.team[turn].players[playerr].set_position(new_position) for playerr in self.team[turn].players if self.team[turn].players[playerr].board_name == player.board_name ]

            self.team[turn].Points += player.value

            self.team[turn].feasible_moves.clear()
            if self.display_board_positions:
                self.__str__()
            self.move_count += 1



