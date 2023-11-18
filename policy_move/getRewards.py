import requests
import os
import numpy as np


svc_endpoint="http://127.0.0.1:8000/policy_move/?"

def getBestMove(states):
    rewards =  [float(requests.get(svc_endpoint + s.replace(",","&q=")).content) for s in states]
    #print(rewards)
    return np.argmax(rewards)


cur_states = [
        '1,2,3,4,5,6,0,8,0,10,11,12,14,15,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-14,-15,-16',
        '1,2,3,4,5,6,0,8,0,10,11,12,14,15,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-14,-15,-16',
        '1,2,3,4,5,6,0,8,0,10,11,12,14,15,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-11,-12,-10,-14,-15,-16',        
        '1,2,3,4,5,6,0,8,0,10,11,12,15,14,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-14,-15,-16',
        ]

#print(getBestMove(states))




feasible_moves = [(16,14,22),(15,13,21),(14,12,20),(12,10,18),(11,9,17),(10,8,16)]

def getNextStates(cur_state, moves):
    next_states = []
    for move in moves:
        next_state = np.array(cur_state.split(","),dtype=np.int32)
        next_state[move[1]] = 0
        next_state[move[2]] = move[0]
        next_state = ",".join([str(x) for x in next_state])
        next_states.append(next_state)
    return next_states

nextStates = getNextStates(cur_states[0],feasible_moves)

#print(nextStates)

bestMove = getBestMove(nextStates)

print("Best Move is:\t {}\n".format(feasible_moves[bestMove]))
