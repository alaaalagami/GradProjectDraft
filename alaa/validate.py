from experience_manager import ExperienceManager
import numpy as np

game = ExperienceManager(state_file="initial_state.json", scene_file="scenes.json", plot_file="plot.json",
                         players_file="players_data.json")

initial_state = game.current_state
beat_counts = [0, 0]
stack = []  # Includes state, beat_count, past_scenes
viewed_scenes = []
# Get first scenes
roles = game.players_data['characters']
first_scenes = []
for role in roles:
    first_scenes.append(game.players_data['characters'][role]["first scene"])
stack.append(
    {"state": initial_state, "beat counts": beat_counts, "scenes": first_scenes})
# Save states (game state, beat_count, and past_scenes) that lead to a deadend
deadend_states = []

# While stack is not empty
while len(stack) > 0:

    # Pop item from stack
    popped = stack.pop()
    # Add viewed scenes from popped item to viewed_scenes list
    past_scenes = popped["scenes"]
    for label in past_scenes:
        viewed_scenes.append(label)
    # Set experience manager beat counts
    beat_counts = popped["beat counts"]
    game.players[0].set_beat_count(beat_counts[0])
    game.players[1].set_beat_count(beat_counts[1])
    # Set experience manager current state
    game.current_state = popped["state"]
    # Remember initial state
    initial_state = game.current_state
    # Count of how many times the item reaches a deadend (item is a "deadend state" if both players cannot find scenes
    # after it => count = 2)
    deadend_count = 0

    for player_id in range(2):

        # Get the player
        player = game.players[player_id]
        # Apply gating if needed (if the player is in a gate scene while the other player has not yet arrived,
        # skip finding new scenes for this player at current state)
        if player.get_beat_count() % game.gate_window == 0:
            if game.players[1 - player_id].get_beat_count() < player.get_beat_count():
                continue

        # Get scene type (single player/ multiplayer)
        scene_type = game.plot["progression"][player.get_beat_count()][0]

        if scene_type == "m":
            # If the upcoming scene for this player is a multiplayer scene and the other player has not arrived,
            # skip finding new scenes for this player at current state)
            if game.players[1 - player_id].get_beat_count() < player.get_beat_count():
                continue
            # If the upcoming scene for this player is a multiplayer scene and both players arrived and we are now
            # searching the scenes for the first player, increment player id from 0 to 1 to avoid repeating this
            # stack item (the same game state and past scenes will lead to the same next multiplayer scene for both
            # players
            if game.players[1 - player_id].get_beat_count() == player.get_beat_count():
                if player_id == 0:
                    player_id == 1

        # Run next scene algorithm to find viable next scenes
        player_scenes = game.get_player_scenes(player_id)
        viable_scenes_list = []
        for label in player_scenes:
            # If the scene has not  beenshown before to the player and its preconditions are statisfied, it is viable
            if label not in past_scenes and game.test_preconditions(label):
                viable_scenes_list.append(label)

        if len(viable_scenes_list) == 0:
            deadend_count += 1
            if deadend_count == 2:
                deadend_states.append(popped)
                break

        # Find viable scenes' distance from the plot
        beat_errors = game.evaluate_beats(viable_scenes_list, player_id)
        min_error = min(beat_errors.values())
        highest_scored_scenes_list = [key for key in beat_errors if beat_errors[key] == min_error]

        # Update beat counts
        temp_beat_counts = beat_counts
        temp_beat_counts[player_id] += 1
        if scene_type == "m":  # if scene was a multiplayer scene, increment beat count for both players
            temp_beat_counts[1 - player_id] += 1

        for label in highest_scored_scenes_list:
            if "end scene" not in game.scenes_list[label]:
                # Update past scenes
                temp_past_scenes = past_scenes
                temp_past_scenes.append(label)
                # Add item to stack
                game.apply_scene_postconditions(label, [player_id])
                item = {"state": game.current_state, "beat counts": temp_beat_counts, "scenes": temp_past_scenes}
                game.current_state = initial_state

viewed_scenes = np.array(viewed_scenes)
unique_viewed_scenes = np.unique(viewed_scenes)
unviewed_scenes = []
for label in game.scenes_list:
    if label not in unique_viewed_scenes:
        unviewed_scenes.append(label)

if len(unviewed_scenes) == 0:
    print("There are no unreachable scenes")
else:
    print("Unreachable scenes are " + unviewed_scenes)

if len(deadend_states) == 0:
    print("Scenes are correctly validated!")
else:
    print("Scenes were incorrectly validated. The following scenarios lead to deadend: " + deadend_states)
