from fastapi import FastAPI
import json
from collections import defaultdict
import ast

app = FastAPI()

policy_file = '/data_data/reinforcement_learning/results/combined_file'

policy_dict = defaultdict()

with open(policy_file,'r') as policy_infile:
    policies = policy_infile.readlines()
    for policy in policies:
        state, action_ = policy.split("\t")
        action = ast.literal_eval(action_)['policy']
        policy_dict.update({state:action})


@app.get('/policy')
def hello_world():
    keys = list(policy_dict.items())[:5]
    #return  {"keys":keys}
    return [{state:action} for state,action in list(policy_dict.items())[:5]]

@app.get('/policy/{state}')
def getPolicy(state: str):
    try:
        policy = policy_dict[state.strip()]
    except:
        policy = None

    return policy

