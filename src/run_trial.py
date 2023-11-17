from utils.getCycle import getCycle
from models.Team import Team
from models.Game import Game

initial_state =  "010010010011010100010101010110010111011000011001011010011011011100011101011110011111100000100001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000010000011000100000101000110000111001000001001001010001011001100001101001110001111010000"

def run_trial(user_input, s):
  global cycle
  cycle = getCycle()
  num_sides = user_input.num_sides
  sides = [x for x in range(num_sides)]
  env = Game(user_input.game,cycle,s, 8,sides, user_input.display_board_positions)

  for j in range(user_input.num_sides):
    team_name = "team_" + str(j)
    team_name = Team(user_input.game, user_input.teams[j]["team_name"], j,
               user_input.teams[j]["skill"] / 10,
               user_input.teams[j]["strategy"])

    env.insert_team(team_name)

  env.not_deadlocked = True
  env.states.append(initial_state)
  time_step = 0
  while env.not_deadlocked:
    state_prior = env.states[-1]
    env.step()
    next_state = ""
    state_prime = ""
    if time_step % 2 == 0:
       state_prime = env.states[-1]
    else:
       next_state = env.states[-1]
    time_step += 1


    #side_0_terminated = "w__K" not in list(env.team[0].players.keys())
    #side_1_terminated = "b__K" not in list(env.team[1].players.keys())

    #if side_0_terminated or side_1_terminated:
    #  env.not_deadlocked = False

    #print("============================================================================================")
    #print("Cycle:\t{}\tStep:\t{}\tNOT_Deadlocked ==\t{}\n".format(cycle, time_step, env.not_deadlocked))
    #print("--------------------------------------------------------------------------------------------")

  #return str(env.wins, env.losses, env.draws)+"\n"  
  return env.horizon
