import multiprocessing as mp
import requests

s = requests.Session()

from src.run_trial import run_trial

def run_trials(user_input,num_jobs):
  """ Runs the num_trials """

  num_trials = user_input.num_trials
  num_sides = user_input.num_sides

  pool = mp.Pool(processes=100)

  jobs = []

  num_cycles  = int(user_input.num_trials/num_jobs)

  results     = [pool.apply_async(run_trial, args=(user_input, s,)) for x in range(num_cycles)]

  pool.close()

  return      [p.get() for p in results]
