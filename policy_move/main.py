from typing import List, Union

from fastapi import FastAPI, Query
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from exception_handlers import request_validation_exception_handler, http_exception_handler, unhandled_exception_handler
from middleware import log_request_middleware

from typing_extensions import Annotated

import sys
import os
import csv
import numpy as np
import pandas as pd

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import gc

from random import random

for r in range(5):
    torch.cuda.empty_cache()
    gc.collect()

device = torch.device("cpu")

fc1 = 16384
fc2 = 8192
fc3 = 4096
fc4 = 1024
fc5 = 512
fc6 = 256
fc7 = 128
fc8 = 16

LR = 0.005
state_size = 448
action_size = 0
batch_size = 64

request_cnt = 0

class QNetwork(nn.Module):
    """Actor (Policy) Model."""

    def __init__(self, state_size, reward_size, fc1_units=fc1, fc2_units=fc2, fc3_units=fc3, fc4_units=fc4, fc5_units=fc5, fc6_units=fc6, fc7_units=fc7, fc8_units=fc8):
        """Initialize parameters and build model.
        Params
        ======
            state_size (int): Dimension of each state
            action_size (int): Dimension of each action
            seed (int): Random seed
            fc1_units (int): Number of nodes in first hidden layer
            fc2_units (int): Number of nodes in second hidden layer
        """
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size , fc1_units)
        #torch.nn.BatchNorm1d(fc1_units)
        self.fc2 = nn.Linear(fc1_units, fc2_units)
        #torch.nn.BatchNorm1d(fc2_units)
        self.fc3 = nn.Linear(fc2_units, fc3_units)
        #torch.nn.BatchNorm1d(fc3_units)
        self.fc4 = nn.Linear(fc3_units, fc4_units)
        #torch.nn.BatchNorm1d(fc4_units)
        self.fc5 = nn.Linear(fc4_units, fc5_units)
        self.fc6 = nn.Linear(fc5_units, fc6_units)
        self.fc7 = nn.Linear(fc6_units, fc7_units)
        self.fc8 = nn.Linear(fc7_units, fc8_units)
        self.fc9 = nn.Linear(fc8_units, reward_size)

    def forward(self, state):
        """Build a network that maps state -> action values."""
        x = F.relu(self.fc1(state))
        x = 2*F.sigmoid(self.fc2(x)) - 1
        x = F.relu(self.fc3(x))
        x = 2*F.sigmoid(self.fc4(x)) - 1
        x = F.relu(self.fc5(x))
        x = 2*F.sigmoid(self.fc6(x)) - 1
        x = F.relu(self.fc7(x))
        x = F.relu(self.fc8(x))
        x = self.fc9(x)
        return x


binary_names = {
   '0': [0,0,0,0,0,0,0],
   '1': [1,0,1,0,1,0,1],
   '2': [1,0,1,0,1,1,1],
   '3': [1,0,1,1,0,0,1],
   '4': [1,0,1,1,1,1,1],
   '5': [1,0,1,1,0,1,1],
   '6': [1,0,1,1,0,0,1],
   '7': [1,0,1,0,1,1,1],
   '8': [1,0,1,0,1,0,1],
   '9': [1,0,0,0,0,1,1],
   '10': [1,0,0,0,0,1,1],
   '11': [1,0,0,0,0,1,1],
   '12': [1,0,0,0,0,1,1],
   '13': [1,0,0,0,0,1,1],
   '14': [1,0,0,0,0,1,1],
   '15': [1,0,0,0,0,1,1],
   '16': [1,0,0,0,0,1,1],
   '-16': [1,1,0,0,0,1,1],
   '-15': [1,1,0,0,0,1,1],
   '-14': [1,1,0,0,0,1,1],
   '-13': [1,1,0,0,0,1,1],
   '-12': [1,1,0,0,0,1,1],
   '-11': [1,1,0,0,0,1,1],
   '-10': [1,1,0,0,0,1,1],
   '-9': [1,1,0,0,0,1,1],
   '-8': [1,1,1,0,1,0,1],
   '-7': [1,1,1,0,1,1,1],
   '-6': [1,1,1,1,0,0,1],
   '-5': [1,1,1,1,1,1,1],
   '-4': [1,1,1,1,0,1,1],
   '-3': [1,1,1,1,0,0,1],
   '-2': [1,1,1,0,1,1,1],
   '-1': [1,1,1,0,1,0,1],
   }


def getBinaryName(numeric_states):
   binary_states = []
   for numeric_state in numeric_states:
        binary_state = np.array([binary_names[str(int(position))] for position in numeric_state])
        binary_states.append(binary_state)
   return np.array(binary_states,dtype=np.float16).flatten()

predictNet = QNetwork(state_size+action_size, 1).to(device)

print(predictNet)

predictNet.load_state_dict(torch.load("Model"))

print("Setting model to eval()")

predictNet.eval()

app = FastAPI()

app.middleware("http")(log_request_middleware)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

@app.get('/policy_move/')
async def getReward(q: Annotated[list[str] | None, Query()] = None):
    global request_cnt
    query_items = {"q": q}
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    input_states_batch = []

    states = q[0].split("_")
    for state in states:
        state_ = [int(s) for s in state.split(":")]
        input_states_batch.append(state_)
        #print(input_states_batch)

    input_states_batch = np.array(input_states_batch, dtype=np.float16)
    
    num_states = input_states_batch.shape[0]
    
    next_states_batch = torch.Tensor(getBinaryName(input_states_batch).reshape((num_states,state_size))).to(device)
    
    request_cnt += 1
    
    rewards = np.array(predictNet(next_states_batch).detach().cpu().tolist(),dtype=np.float64).flatten()
    
    #print("REWARDS:\t{}\n".format(rewards))
    bestMove = int(np.argmax(rewards))
    
    #print("bestMOVE:\t{}\n".format(bestMove))
    #print("=======================================================================================")
    return bestMove

