

### CHESSY v1.0: A generic OOP framework for board games [aspirationally]
Author: Ranga Muvavarirwa

#### Motivation:
Many situations arise whereby two sides need to simultaneously use a public good [e.g. a river, a game board etc] in
pursuit of their own self-regarding goals (e.g. cross river, get as many pieces as possible to otherend of the board]
Traditional solutions to such situations have typically modelled participant behavior and the ensuring game-strategy
as none-coopertive/winner-takes-all/zero-sum games: the outcomes of which (war, tragedy of the commons etc) are often
often inefficient and/or unacceptable

#### Hypothesis
Participants (societies, game players etc) would select a cooperative approach -- if they could identify a set of
viable paths whose collective cost (number of participants for whom a path could not be found) was less than some
predetermined cost of a zero-sum approach (cost of one side losing + cost of half-winning side)

#### Goal
Create a cooperative version of a board game (v1 supports chess), whose main objective is to determine whether both
sides can achieve a shared objective (get as many pieces as possible to the other side of the board) -- without
'taking any pieces from the 'opposing' team. v2 will provide a mechanism for comparing the distribution of costs/value
between cooperative vs competitive iterations

#### Key Concepts
Framework supports any game scenario whose geometry can be implemented programmatically (chess, chechers, go etc)
Players can enter game at any point in time (need not be simultaneous). Available in v2
Players can have different skill levels [1 = Novice 10 = Expert]
- Creates a harness for evaluating expert performance -- relative to a random agent
- Subsequent iterations could use this harness to train the expert (by evaluating moves by a random agent that beats
the expert ( Bayesian approaches might be useful here ).

#### Architecture
Chessy employs two patterns:
- a form of dependency injection / factory-pattern whereby metadata specifying the rules of a game are
presented in JSON/Python-dictionary format [refer games dictionary object below]

- dynamic class creation using the "TYPE" method for specifying classes [King, Queen, Bishop etc] as well as for
instantiating specific players [b_Pawn_01, w_King, b_K1 etc)


#### Organization

##### Classes

- Game: Controller. Creates board. Invokes Team() to create teams+players. Updates and maintains game state (time_step)
- Team: Instance per team. Invoked by Game(). Invokes Player_Template
- Player_Template: Generic player class. Invoked by Team()
- Incorrect_Input_error: Generic exception handler for inputs
- UserInput: [arguably duplicative] class by which an object is initialized with user_inputs as properties


##### Methods
- Main: initiates program
- run_trials: Iterates through num_trials. Candidate for multiprocessing refactor.
- plot_results: Display results using MatPlotLib


