
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


from games  import games
from player import Player_Template
from userinput import userInput

from games import games
from player import Player_Template

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
        return 'Team({},{},{},{},{},{},{},{},{})'.format(self.game, self.name, self.team, [("Player_Template(" + str(i) + ")") for i in range(len(self.players))],[move for move in self.feasible_moves], self.side, self.strategy,self.rating, [move for move in self.move_choice])
    
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
                players[board_name] = self.class_list[role](role, board_name, s_pos,moves[self.team], value)
            
            elif number == 2:
                for i in range(number):
                    board_name = prefix[self.team] + role[0].upper() + str(i)
                    s_pos = start_pos[i][self.team]
                    players[board_name] = self.class_list[role](role, board_name, s_pos,moves[self.team], value)
            else:
                for i in range(number):
                    board_name = prefix[self.team] + role[0].upper() + str(i)
                    #print("BOARD_NAME: ", board_name)
                    #print("DEBUGGING: tuple(start_pos[self.team]): \n", tuple(start_pos[self.team]), "\n tuple((0, int(i))): ", tuple((0, int(i))) )
                    #print("ZIP: ", zip(tuple(start_pos[self.team]), tuple(tuple((0, int(i))))).__next__(), "INT(i) = ", i)
                    
                    s_pos = (tuple(sum((position)) for position in zip(tuple(start_pos[self.team]), tuple((0, int(i))))))
                    players[board_name] = self.class_list[role](role, board_name, s_pos, moves[self.team], value)
        
        return players
    
    
    def create_move_choices(self):
        return (random.choices([0, 1], [1 - self.rating, self.rating], k=1000))
    
    def get_roles(self):
        [print( type(self.class_list[a_class]), "\t", self.class_list[a_class].name,"\t", self.class_list[a_class].number, "\t", self.class_list[a_class].value) for a_class in self.class_list]
    

    def get_players(self):
        #print("CLASS \t\t\t\t\t\tINSTANCE\tSTART_POS\tCURR_POS\tMOVES")
        [print(type(self.players[player]), "\t", self.players[player].board_name,"\t\t", self.players[player].start_pos, "\t",self.players[player].start_pos, "\t", self.players[player].moves) for player in self.players]


