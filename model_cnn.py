import math
import random
import copy

from collections import namedtuple, deque

import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

from args import args

def hidden_init(layer):
    fan_in = layer.weight.data.size()[0]
    lim = 1. / np.sqrt(fan_in)
    return (-lim, lim)


class ActorNetwork(nn.Module):
    """Actor (Policy) Model."""

    def __init__(self, state_size, action_size):

        super(ActorNetwork, self).__init__()
        self.conv1  = nn.Conv2d(in_channels=args['in_channels_1'],out_channels=args['out_channels_1'], kernel_size=args['kernel_1_size'], stride=args['stride_1_size']).to(args['device'])
        self.conv2  = nn.Conv2d(in_channels=args['in_channels_2'],out_channels=args['out_channels_2'], kernel_size=args['kernel_2_size'], stride=args['stride_2_size']).to(args['device'])
        self.linear = nn.Linear(args['in_channels_l']*args['out_channels_l'], args['action_size']).to(args['device'])

        self.reset_parameters()

    def reset_parameters(self):
        self.conv1.weight.data.uniform_(*hidden_init(self.conv1))
        self.conv2.weight.data.uniform_(*hidden_init(self.conv2))
        self.linear.weight.data.uniform_(-3e-3, 3e-3)
        
    def forward(self, x):
        try:
            x      = x.reshape(args['reshape_size']).unsqueeze(0).unsqueeze(0)
        except:
            x      = x.reshape(args['reshape_buffer']).unsqueeze(0).unsqueeze(0)
        out    = F.relu(self.conv1(x))
        out    = F.relu(self.conv2(out))
        logits = self.linear(out.view(-1, args['in_channels_l']*args['out_channels_l']))
        probs  = torch.mean(F.softmax(logits, dim=1), axis=0)
        
        return probs
    
    
class CriticNetwork(nn.Module):
    """Critic (Policy) Model."""

    def __init__(self, state_action_size):

        super(CriticNetwork, self).__init__()
        self.seed = torch.manual_seed(args['seed'])
        #self.fc1 = nn.Linear(state_size+action_size, args['FC1_UNITS'])
        self.fc1 = nn.Linear(state_size+action_size, args['FC1_UNITS'])
        self.fc2 = nn.Linear(args['FC1_UNITS'], args['FC2_UNITS'])
        self.fc3 = nn.Linear(args['FC2_UNITS'], args['FC3_UNITS'])
        self.fc4 = nn.Linear(args['FC3_UNITS'], 1)
        self.reset_parameters()

    def reset_parameters(self):
        self.fc1.weight.data.uniform_(*hidden_init(self.fc1))
        self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
        self.fc3.weight.data.uniform_(*hidden_init(self.fc3))
        self.fc4.weight.data.uniform_(-3e-3, 3e-3)
        
    def forward(self, state, action):
        """Build a network that maps state -> action values."""

        x = F.relu(self.fc1(torch.cat((state, action),dim=1)))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)
    
class CriticNetwork2(nn.Module):
    """Critic (Policy) Model."""

    def __init__(self, state_action_size):

        super(CriticNetwork, self).__init__()
        self.seed = torch.manual_seed(args['seed'])
        self.fc1 = nn.Linear(state_action_size, args['FC1_UNITS'])
        self.fc2 = nn.Linear(args['FC1_UNITS'], args['FC2_UNITS'])
        self.fc3 = nn.Linear(args['FC2_UNITS'], args['FC3_UNITS'])
        self.fc4 = nn.Linear(args['FC3_UNITS'], 1)
        self.reset_parameters()

    def reset_parameters(self):
        self.fc1.weight.data.uniform_(*hidden_init(self.fc1))
        self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
        self.fc3.weight.data.uniform_(*hidden_init(self.fc3))
        self.fc4.weight.data.uniform_(-3e-3, 3e-3)
        
    def forward(self, state_action):
        """Build a network that maps state -> action values."""

        x = F.relu(self.fc1(state_action))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)
    
    
class MCritic():
    """Interacts with and learns from the environment."""

    def __init__(self, state_action_size):

        self.state_action_size   = state_action_size
        self.seed         = args['seed']
        self.device       = args['device']

        self.network      = CriticNetwork2(state_action_size).to(self.device)
        self.target       = CriticNetwork2(state_action_size).to(self.device)
        self.optimizer    = optim.Adam(self.network.parameters(), lr=args['LR_CRITIC'], weight_decay=args['WEIGHT_DECAY'])
        
        #Model takes too long to run --> load model weights from previous run (took > 24hours on my machine)
        #self.network.load_state_dict(torch.load(args['mcritic_path']), strict=False)
        #self.target.load_state_dict(torch.load(args['mcritic_path']), strict=False)
