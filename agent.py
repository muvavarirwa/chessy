
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

import noise
from noise import OUNoise
from replaybuffer import ReplayBuffer
from model import ActorNetwork, CriticNetwork, MCritic
from args  import args

class Agent():
    """Interacts with and learns from the environment."""

    def __init__(self, state_size, action_size, agent_id):

        self.state_size  = state_size
        self.action_size = action_size
        self.seed        = args['seed']
        self.device      = args['device']
        #self.args        = args

        # Q-Network
        self.actor_network    = ActorNetwork(state_size, action_size).to(self.device)
        self.actor_target     = ActorNetwork(state_size, action_size).to(self.device)
        self.actor_optimizer  = optim.Adam(self.actor_network.parameters(), lr=args['LR_ACTOR'])
        
        #Model takes too long to run --> load model weights from previous run (took > 24hours on my machine)
        #if not agent_id:
        #    self.actor_network.load_state_dict(torch.load(args['agent_p0_path']), strict=False)
        #    self.actor_target.load_state_dict(torch.load(args['agent_p0_path']), strict=False)
        #else:
        #    self.actor_network.load_state_dict(torch.load(args['agent_p1_path']), strict=False)
        #    self.actor_target.load_state_dict(torch.load(args['agent_p1_path']), strict=False)
        
        # Replay memory
        self.memory      = ReplayBuffer(action_size, args['BUFFER_SIZE'], args['BATCH_SIZE'], self.device, self.seed)
        
        # Noise process
        self.noise       = OUNoise(action_size, self.seed)
        
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step      = 0
        
        self.mCriticLoss = 0
        
        self.actorLoss   = 0
        
    
    def step(self, state, action, reward, next_state, done, mCritic):
        # Save experience in replay memory
        
        self.memory.add(state, action, reward, next_state, done)
        
        if len(self.memory) > args['BATCH_SIZE']:
            experiences = self.memory.sample()
            self.train(experiences, mCritic)
            

    def act(self, current_state):
        
        with torch.no_grad():
                
            self.actor_network.eval()
                
            input_state = torch.from_numpy(current_state).float().to(self.device)
                
            with torch.no_grad():
                action  = self.actor_network(input_state).cpu().data.numpy()

            self.actor_network.train()
                
            #action     += self.noise.sample()
            
        return action

    def reset(self):
        self.noise.reset()
        
        
    def train(self, experiences, mCritic):
        
        global states_
        global next_states_
        global actions_
        global max_min_actions_vector
        global max_min_states_vector

        states, actions, rewards, next_states, dones = experiences

        
        # ---------------------------- update critic ---------------------------- #
        
        with torch.no_grad():
            # Get predicted next-state actions and Q values from target models
            actions_next   = self.actor_target(next_states)
            Q_targets_next = mCritic.target(next_states, actions_next)

            # Compute Q targets for current states (y_i)
            Q_targets      = rewards + (args['GAMMA'] * Q_targets_next * (1 - dones))
        
        
        # Compute critic loss
        Q_expected     = mCritic.network(states, actions)
        mCritic_loss    = F.mse_loss(Q_expected, Q_targets)
        
        self.mCriticLoss = mCritic_loss
        
        # Minimize the loss
        mCritic.optimizer.zero_grad()
        mCritic_loss.backward()
        mCritic.optimizer.step()

        
        # ---------------------------- update actor ---------------------------- #
        # Compute actor loss
        actions_pred = self.actor_network(states)
        actor_loss = -mCritic.network(states, actions_pred).mean()
        
        self.actorLoss = actor_loss
        
        # Minimize the loss
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        
        # ----------------------- update target networks ----------------------- #
        self.soft_update(mCritic.network, mCritic.target, args['TAU'])
        self.soft_update(self.actor_network,  self.actor_target,  args['TAU'])     
        

    def soft_update(self, local_model, target_model, tau):
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target

        Params
        ======
            local_model: PyTorch model (weights will be copied from)
            target_model: PyTorch model (weights will be copied to)
            tau (float): interpolation parameter 
        """
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(tau*local_param.data + (1.0-tau)*target_param.data)
                

