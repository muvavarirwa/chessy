

import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from numeric_names import numeric_names

args = { 
    "update_every":100,
    "window_size":100,
    "BUFFER_SIZE":int(1e6),
    "BATCH_SIZE":1024,  
    "GAMMA":0.99,
    "TAU":2e-3,
    "LR_ACTOR":1e-3,
    "LR_CRITIC":1.1e-3,
    "WEIGHT_DECAY":0.0001,
    "UPDATE_EVERY":5,
    "EXPLORE_NOISE":0.05,
    "FC1_UNITS":10240,
    "FC2_UNITS":4096,
    "FC3_UNITS":256,
    "seed":0,
    "state_size":384,
    "action_size":88,
    "action_size_binary":12,
    "num_agents":2,
    "device":torch.device("cuda:0" if torch.cuda.is_available() else "cuda:1"),
    'mcritic_path':'/home/ubuntu/chessy/checkpoint_mCritic_twoSided.pth',
    'agent_p0_path':'/home/ubuntu/chessy/checkpoint_p0_twoSided.pth',
    'agent_p1_path':'/home/ubuntu/chessy/checkpoint_p1_twoSided.pth',
    'action_id_dict': {'1,1,0': 0, '2,1,-2': 1, '2,1,2': 2, '2,2,-1': 3, '2,2,1': 4, '3,1,-1': 5, '3,1,1': 6, '4,1,-1': 7, '4,1,0': 8, '4,1,1': 9, '5,1,-1': 10, '5,1,0': 11, '5,1,1': 12, '6,1,-1': 13, '6,1,1': 14, '7,1,-2': 15, '7,1,2': 16, '7,2,-1': 17, '7,2,1': 18, '8,1,0': 19, '9,1,0': 20, '9,1,-1': 21, '9,1,1': 22, '10,1,0': 23, '10,1,-1': 24, '10,1,1': 25, '11,1,0': 26, '11,1,-1': 27, '11,1,1': 28, '12,1,0': 29, '12,1,-1': 30, '12,1,1': 31, '13,1,0': 32, '13,1,-1': 33, '13,1,1': 34, '14,1,0': 35, '14,1,-1': 36, '14,1,1': 37, '15,1,0': 38, '15,1,-1': 39, '15,1,1': 40, '16,1,0': 41, '16,1,-1': 42, '16,1,1': 43, '-16,-1,0': 44, '-16,-1,-1': 45, '-16,-1,1': 46, '-15,-1,0': 47, '-15,-1,-1': 48, '-15,-1,1': 49, '-14,-1,0': 50, '-14,-1,-1': 51, '-14,-1,1': 52, '-13,-1,0': 53, '-13,-1,-1': 54, '-13,-1,1': 55, '-12,-1,0': 56, '-12,-1,-1': 57, '-12,-1,1': 58, '-11,-1,0': 59, '-11,-1,-1': 60, '-11,-1,1': 61, '-10,-1,0': 62, '-10,-1,-1': 63, '-10,-1,1': 64, '-9,-1,0': 65, '-9,-1,-1': 66, '-9,-1,1': 67, '-8,-1,0': 68, '-7,-1,-2': 69, '-7,-1,2': 70, '-7,-2,-1': 71, '-7,-2,1': 72, '-6,-1,-1': 73, '-6,-1,1': 74, '-5,-1,-1': 75, '-5,-1,0': 76, '-5,-1,1': 77, '-4,-1,-1': 78, '-4,-1,0': 79, '-4,-1,1': 80, '-3,-1,-1': 81, '-3,-1,1': 82, '-2,-1,-2': 83, '-2,-1,2': 84, '-2,-2,-1': 85, '-2,-2,1': 86, '-1,-1,0': 87},
    'id_action_dict': {0: '1,1,0', 1: '2,1,-2', 2: '2,1,2', 3: '2,2,-1', 4: '2,2,1', 5: '3,1,-1', 6: '3,1,1', 7: '4,1,-1', 8: '4,1,0', 9: '4,1,1', 10: '5,1,-1', 11: '5,1,0', 12: '5,1,1', 13: '6,1,-1', 14: '6,1,1', 15: '7,1,-2', 16: '7,1,2', 17: '7,2,-1', 18: '7,2,1', 19: '8,1,0', 20: '9,1,0', 21: '9,1,-1', 22: '9,1,1', 23: '10,1,0', 24: '10,1,-1', 25: '10,1,1', 26: '11,1,0', 27: '11,1,-1', 28: '11,1,1', 29: '12,1,0', 30: '12,1,-1', 31: '12,1,1', 32: '13,1,0', 33: '13,1,-1', 34: '13,1,1', 35: '14,1,0', 36: '14,1,-1', 37: '14,1,1', 38: '15,1,0', 39: '15,1,-1', 40: '15,1,1', 41: '16,1,0', 42: '16,1,-1', 43: '16,1,1', 44: '-16,-1,0', 45: '-16,-1,-1', 46: '-16,-1,1', 47: '-15,-1,0', 48: '-15,-1,-1', 49: '-15,-1,1', 50: '-14,-1,0', 51: '-14,-1,-1', 52: '-14,-1,1', 53: '-13,-1,0', 54: '-13,-1,-1', 55: '-13,-1,1', 56: '-12,-1,0', 57: '-12,-1,-1', 58: '-12,-1,1', 59: '-11,-1,0', 60: '-11,-1,-1', 61: '-11,-1,1', 62: '-10,-1,0', 63: '-10,-1,-1', 64: '-10,-1,1', 65: '-9,-1,0', 66: '-9,-1,-1', 67: '-9,-1,1', 68: '-8,-1,0', 69: '-7,-1,-2', 70: '-7,-1,2', 71: '-7,-2,-1', 72: '-7,-2,1', 73: '-6,-1,-1', 74: '-6,-1,1', 75: '-5,-1,-1', 76: '-5,-1,0', 77: '-5,-1,1', 78: '-4,-1,-1', 79: '-4,-1,0', 80: '-4,-1,1', 81: '-3,-1,-1', 82: '-3,-1,1', 83: '-2,-1,-2', 84: '-2,-1,2', 85: '-2,-2,-1', 86: '-2,-2,1', 87: '-1,-1,0'},
    'numeric_names' : numeric_names,
    'initial_state'  : "010010010011010100010101010110010111011000011001011010011011011100011101011110011111100000100001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000010000011000100000101000110000111001000001001001010001011001100001101001110001111010000",
    'SUMMARY_FILE':"/data_data/reinforcement_learning/results/summary_file.tsv",
    'HISTORY_FILE':None,
    'TAKE_KING_REWARD':10,
    'MORE_POINTS_REWARD':1,
    'EQUAL_POINTS_REWARD':0,
    'STEP_REWARD':-1,
    'WINS_DRAWS_LOSSES': [0,0,0],
    'in_channels_1':1,
    'in_channels_2':1,
    'in_channels_l':1,
    'out_channels_1':1,
    'out_channels_2':1,
    'out_channels_l':1,
    'kernel_1_size':(6,1),
    'kernel_2_size':(4,4),
    'kernel_l_size':(1,1),
    'stride_1_size':(6,1),
    'stride_2_size':(1,1),
    'stride_l_size':(1,1),
    'reshape_size':(1024,1,48,8),
    'reshape_buffer':(1, 384)
}
