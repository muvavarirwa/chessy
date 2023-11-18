from models.games import games

class userInput:
  """ Class captures user input and initializes class-level properties that are subsequently used by other methods
    throughout the program. Although this code is a duplicative -- it simplifies and separates input error handling from
    class/object instantiations. i.e. userInput object separates input acquisition from object (game, team etc)
    instantiation -- by passing 'clean' variables/properties to the respective constructors/initilizers."""

  def __init__(self):
    self.game = self.get_game()
    self.num_sides = self.get_num_sides()
    self.teams = self.get_teams()
    self.num_trials = self.get_num_trials()
    self.display_board_positions = True
    self.get_display_status()

  def __str__(self):
    return 'userInput of game: {}, num_sides: {}, ' \
           'teams: {}, num_trials: {}, ' \
           'display_board_positions: {}'.format(self.game,
                                                self.num_sides,
                                                [("Team(" + str(i) + ")") for i in range(len(self.teams))],
                                                self.num_trials,
                                                self.display_board_positions)

  def __repr__(self):
    return 'userInput({},{},{},{},{})'.format(
      self.game, self.num_sides, [("Team(" + str(i) + ")")
                                  for i in range(len(self.teams))],
      self.num_trials, self.display_board_positions)

  def get_game(self):
    done = False
    while not done:
      try:
        game = input("select a game: ['chessy' or 'checkers']: ")
        if game not in games.keys():
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
      else:
        done = True
        return game

  def get_num_sides(self):
    """Prompts user for, error checks and returns number of sides in game"""
    done = False
    while not done:
      try:
        num_sides = int(input("select number of teams:  [0, 1 or 2] "))
        choices = [0, 1, 2]
        if num_sides > 2 or num_sides < 0:
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
        print(choices)
      else:
        done = True
        return num_sides

  def get_teams(self):
    """Prompts user for, error checks and returns specific information about each team."""

    teams = [{
      str("team_" + str(i)): {
        "team_name": None,
        "color": None,
        "skill": None,
        "strategy": None
      }
    } for i in range(self.num_sides)]
    colors = [
      "blue", "green", "red", "cyan", "magenta", "yellow", "black", "white"
    ]

    for i in range(self.num_sides):
      done = False
      while not done:
        try:
          team_board_name = input(
            "Choose a name for this team [e.g. 'blue_team' or 'green_team']: ")
          if not isinstance(team_board_name, str):
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
        else:
          done = True
          teams[i]["team_name"] = team_board_name

      done = False
      while not done:
        try:
          team_color = input("Choose a color for team_2 [e.g. 'blue': ")
          if team_color not in colors:
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
          print(colors)
        else:
          done = True
          teams[i]["color"] = team_color

      done = False
      while not done:
        try:
          skill_level = int(
            input(
              "Please enter team's skill_level [1 = Novice, 10 = expert]: "))
          choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
          if skill_level > 10 or skill_level < 0 or skill_level not in choices:
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
          print(choices)
        else:
          done = True
          teams[i]["skill"] = skill_level

      done = False
      while not done:
        try:
          strategy = int(
            input(
              "Please enter team's strategy [0 = 'cooperative', 1 = 'competitive']: "
            ).lower())
          choices = [0, 1]
          if strategy > 1 or skill_level < 0:
            raise Incorrect_Input_error
        except Incorrect_Input_error:
          print("Please select a choice within the proposed range:")
          print(choices)
        else:
          done = True
          if strategy:
            teams[i]["strategy"] = "competitive"
          else:
            teams[i]["strategy"] = "cooperative"

    return teams

  def get_num_trials(self):
    """Prompts user for, error checks and returns number of trials for this iteration of the game"""

    done = False
    while not done:
      try:
        trials = int(
          input("How many trials would you like to run? [1 -50,000,000] "))
        if trials > 50000000 or trials < 0 or not isinstance(trials, int):
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
        print("[1 - 50,000,000]")
        # self.num_trials = trials
        # return trials
      else:
        done = True
        self.num_trials = trials
        return int(trials)


  def get_display_status(self):
    """Prompts user for, error checks and returns user preference for whether results should be displayed"""

    done = False
    while not done:
      try:
        display_results = str(
          input(
            "Do you want to see the board positions in realtime? [ 'Yes' or 'No' ]"
          )).lower()
        choices = ["yes", "no"]
        if display_results not in choices:
          raise Incorrect_Input_error
      except Incorrect_Input_error:
        print("Please select a choice within the proposed range")
      else:
        done = True
        if display_results.lower() == choices[0]:
          self.display_board_positions = True
        else:
          self.display_board_positions = False
