
def plot_results(user_input):
  """ Plots results from num_trials"""

  team_scores = []
  min_score = 99999999
  max_score = 0

  for j in range(user_input.num_sides):
    team_scores.append([team_points for cycle, team_points in score_board[j]])
    plot.hist(
      team_scores[j],
      bins=100,
      label=user_input.teams[j]["team_name"],
      color=user_input.teams[j]["color"])

    min_j_score = min(team_scores[j])
    max_j_score = max(team_scores[j])

    if min_j_score < min_score:
      min_score = min_j_score
    if max_j_score > max_score:
      max_score = max_j_score

    x_spacing = (max_score - min_score) / 10
    y_spacing = user_input.num_trials / 50

    text_x_pos = min_score
    text_y_pos = 2 * y_spacing

  def create_plot():
    for j in range(user_input.num_sides):
      rating_string = user_input.teams[j]["team_name"] + "_rating: " + str(
        user_input.teams[j]["skill"]) + "\n"
      plot.text(
        text_x_pos,
        text_y_pos + j * y_spacing + y_spacing / 4,
        rating_string,
        size=8,
        color=user_input.teams[j]["color"])
      strategy_string = user_input.teams[j]["team_name"] + "_strategy: " + str(
        user_input.teams[j]["strategy"]) + "\n"
      plot.text(
        text_x_pos,
        text_y_pos + j * y_spacing - y_spacing / 4,
        strategy_string,
        size=8,
        color=user_input.teams[j]["color"])

    plot.title('Chessy: Point distribution by team.')
    plot.xlabel('Score')
    plot.ylabel('Frequency of score')
    plot.legend(loc='upper left')
    plot.grid(color="white")

    plot.text(
      text_x_pos,
      text_y_pos + 2 * y_spacing,
      "#Trials = ",
      size=8,
      color=user_input.teams[0]["color"])
    plot.text(
      text_x_pos + 2 * x_spacing,
      text_y_pos + 2 * y_spacing,
      user_input.num_trials,
      size=8,
      color=user_input.teams[0]["color"])
    plot.tight_layout()

  create_plot()

  plot.show()
