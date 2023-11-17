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
import datetime
import multiprocessing as mp

from utils.userInput import userInput
from models import games
from models.Player_Template import Player_Template
from models.Team import Team
from models.Game import Game

from src.run_trials import run_trials

RESULTS = []

summary_dict = {"losses":0,"wins":0,"draws":0}

actions = [[], []]
rewards = [[], []]
history = {"cycle": 0, "actions": actions, "rewards": rewards, "value": 0}

score_board = {}
step_action_dict = defaultdict()
step_action_dict['random_moves'] = defaultdict()
step_action_dict['policy_moves'] = defaultdict()

numeric_names = {'w_R0': 1, 'w_K0': 2, 'w_B0': 3, 'w__K': 4, 'w__Q': 5, 'w_B1': 6, 'w_K1': 7, 'w_R1': 8, 'w_P0': 9, 'w_P1': 10, 'w_P2': 11, 'w_P3': 12, 'w_P4': 13, 'w_P5': 14, 'w_P6': 15, 'w_P7': 16, 'b_P0': -16, 'b_P1': -15, 'b_P2': -14, 'b_P3': -13, 'b_P4': -12, 'b_P5': -11, 'b_P6': -10, 'b_P7': -9, 'b_R0': -8, 'b_K0': -7, 'b_B0': -6, 'b__K': -5, 'b__Q': -4, 'b_B1': -3, 'b_K1': -2, 'b_R1': -1}

initial_state =  "010010010011010100010101010110010111011000011001011010011011011100011101011110011111100000100001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000010000011000100000101000110000111001000001001001010001011001100001101001110001111010000"

best_moves = 0
policy_moves = 0
random_moves = 0

def main():

  global cycle
  global HISTORY_FILE
  global score_board
  global summary_dict

  score_board[0] = []
  score_board[1] = []
  user_input = userInput()

  if user_input.num_trials <= 1000000:
    num_jobs = 1
  else:
    num_jobs = int(user_input.num_trials/1000000)

  print("starting:\t{}\tjobs\n".format(num_jobs))

  for i in range(num_jobs):
    t = time.localtime()
    timestamp = time.strftime('%b_%d_%Y_%H%M',t)

    HISTORY_FILE = '/data_data/reinforcement_learning/results/history_file_' + str(timestamp)

    print("Running JOB #{}\tto OUTPUT_FILE:\t{}".format(i,HISTORY_FILE))

    episodes = None

    episodes = run_trials(user_input,num_jobs)

    with open(HISTORY_FILE,'a+') as output_file:
      for episode in episodes:
        output_file.write(str(episode))

  t1  = time.mktime(t)
  t2  = time.mktime(time.localtime())

  #print(t1,t2) 
  #print(t2 - t1)
  #print("=================SUMMARY RESULTS====================")
  #print(summary_dict.items())
  #plot_results(user_input)

main()
