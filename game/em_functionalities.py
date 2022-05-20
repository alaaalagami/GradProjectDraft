import json
from enum import Enum
import random

class PlayerState(Enum):
    WAITING = 0
    READY = 1
    END = 2

class Player:

    def __init__(self, id):
        self.role = None
        self.id = id
        self.scenes = [] # List of labels of scenes that the player has viewed so far
        self.state = PlayerState.READY
        self.awaiting_scene = None
        self.beat_count = 0
    
    def set_role(self, role):
        self.role = role
    
    def get_role(self):
        return self.role
    
    def add_scene(self, label):
        self.scenes.append(label)
    
    def is_new_scene(self, label):
    # Check if the player has not viewed this scene
        for scene in self.scenes:
            if scene == label:
                return False
        return True
    
    def wait(self):
#        print('Changed player', self.id, 'state to waiting')
        self.state = PlayerState.WAITING
    
    def release(self):
#        print('Changed player', self.id, 'state to ready')
        self.state = PlayerState.READY
    
    def end(self):
#        print('Changed player', self.id, 'state to end')
        self.state = PlayerState.END
    
    def is_waiting(self):
        return self.state == PlayerState.WAITING

    def ended(self):
        return self.state == PlayerState.END
    
    def get_id(self):
        return self.id
    
    def set_awaiting_scene(self, scene):
        self.awaiting_scene = scene

    def get_awaiting_scene(self):
        awaiting = self.awaiting_scene
        self.awaiting_scene = None
        return awaiting
    
    def get_beat_count(self):
        return self.beat_count

    def set_beat_count(self, value):
        self.beat_count = value

    def increment_beat_count(self):
#        print('Incremented Beat Count for player', self.id, 'to', self.beat_count+1, self.scenes)
        self.beat_count += 1
    
    def decrement_beat_count(self):
        self.beat_count -= 1
    
    def get_scenes(self):
        return self.scenes

class GameState:
    def __init__(self, current_state, players, scenes_list, plot, players_data, gate_window):
        self.current_state = current_state
        self.players = players
        self.choices_made = []
        self.scenes_list = scenes_list
        self.plot = plot
        self.players_data = players_data
        self.gate_window = gate_window


def load_file(file):
    f = open(file)
    data = json.load(f)
    f.close()
    return data

def get_initial_gamestate(state_file, scene_file, plot_file, players_file):

    scenes_list = load_file(scene_file)
    players_data = load_file(players_file)
    plot = load_file(plot_file)
    
    current_state = load_file(state_file)
    players = []
    for i in range(int(players_data["players_count"])):
        players.append(Player(i))
    
    gate_window = int(plot["gate every"])  # value assigned by author to determine how many beats between
        # every mandatory gate. Value should be set based on length and dramatic value of the story's avg. beat.
    
    return GameState(current_state, players, scenes_list, plot, players_data, gate_window)

    
############################################## UPDATING STATE ################################################

def apply_changes(changes, gamestate):
# Modify the current state based on the 'changes' dictionary
#    print('State before:', gamestate.current_state)
    for key in changes:
        if changes[key][0] == "add":
            gamestate.current_state[key] = float(gamestate.current_state[key]) + float(changes[key][1])
        elif changes[key][0] == "set":
            gamestate.current_state[key] = float(changes[key][1])
#    print('State after:', gamestate.current_state, '\n')

def apply_choice_postconditions(label, menu_label, choice, gamestate):
#    print('Selected', choice, 'from menu', menu_label)
    gamestate.choices_made.append((label, menu_label, choice))
#    print('Applying choice postconditions')
    changes = gamestate.scenes_list[label]["menus"][menu_label][choice]
    apply_changes(changes, gamestate)

def apply_scene_postconditions(label, players_id, gamestate):
#    print('Applying scene', label, 'postconditions')
    changes = gamestate.scenes_list[label]['postconditions']
    apply_changes(changes, gamestate)
    # If this is an ending scene, change the player state to END
    for id in players_id:
        check_and_apply_ending(label, id, gamestate)

def check_choice(label, menu_label, gamestate):
    for choice_made in gamestate.choices_made:
        if label == choice_made[0] and menu_label == choice_made[1]:
            return choice_made[2]
    return 'None'

def check_and_apply_ending(label, player_id, gamestate):
    if "end scene" in gamestate.scenes_list[label]:
        gamestate.players[player_id].end()

############################################## SCENE SELECTION ################################################
def get_player_scenes(player_id, gamestate):
    # Get all scenes that the player can view based on their role and the plot state (singleplayer/multiplayer)
    role = get_player_role(player_id, gamestate)
    scene_type = gamestate.plot["progression"][gamestate.players[player_id].get_beat_count()][0]
    player_scenes = []
    for label in gamestate.scenes_list:
        scene = gamestate.scenes_list[label]
        if role in scene['player']:
            if scene_type == "s" and len(scene['player']) == 1:
                player_scenes.append(label)
            elif scene_type == "m" and len(scene['player']) > 1:
                player_scenes.append(label)
    return player_scenes

def test_preconditions(player_id, label, gamestate):
    preconditions = gamestate.scenes_list[label]["preconditions"]
    scene_number = int(gamestate.scenes_list[label]["scene number"])
    state = gamestate.current_state
    if scene_number-1 != gamestate.players[player_id].get_beat_count():
        return False
    for key in preconditions:
     try:
        if preconditions[key][0] == "is":
            if float(preconditions[key][1]) != float(state[key]):
                return False
        elif preconditions[key][0] == "more than":
            if float(preconditions[key][1]) >= float(state[key]):
                return False
        elif preconditions[key][0] == "less than":
            if float(preconditions[key][1]) <= float(state[key]):
                return False
     except:
        return False
    return True


def get_error(label, player_id, gamestate):
    beat_count = gamestate.players[player_id].get_beat_count()
    progression = gamestate.plot["progression"][beat_count]
    if progression[0] == "s":
        progression_features = gamestate.plot["single player beat features"]
        features = gamestate.players_data["characters"][get_player_role(player_id, gamestate)]["objective features"]
        weights = gamestate.plot["single player beat weights"]
    else:
        features = gamestate.plot["multi player beat features"]
        progression_features = features
        weights = gamestate.plot["multi player beat weights"]
    
    objectives = progression[1]
    current_values_og = {}
    for feature in features:
        current_values_og[feature] = gamestate.current_state[feature]
    
    postconditions = gamestate.scenes_list[label]["postconditions"]
    current_values = current_values_og
    
    for feature in features:
        if feature in postconditions:
            if postconditions[feature][0] == "add":
                current_values[feature] = float(gamestate.current_state[feature]) + float(
                    postconditions[feature][1])
            else:
                current_values[feature] = postconditions[feature][1]
    error = 0
    for i in range(len(features)):
        feature = features[i]
        objective = objectives[progression_features.index(feature)]
        weight = weights[i]
        error += weight * abs(objective - float(current_values[feature]))
    
    return error

def evaluate_beats(viable_scenes, player_id, gamestate):
    beat_errors = {}
    for label in viable_scenes:
        beat_errors[label] = get_error(label, player_id, gamestate)
    return beat_errors

def gate(player_id, gamestate):
    player = gamestate.players[player_id]
    player_beat = player.get_beat_count()
    other_player_beat = gamestate.players[1 - player_id].get_beat_count()
    if other_player_beat > player_beat:
        return False
    if other_player_beat == player_beat and is_other_player_waiting(player_id, gamestate):
        return False
    player.wait()
    return True

def get_first_scene(player_id, gamestate):
    player = gamestate.players[player_id]
    role = get_player_role(player_id, gamestate)
    first_scene = gamestate.players_data['characters'][role]["first scene"]
    player.add_scene(first_scene)
    player.increment_beat_count()
    apply_scene_postconditions(first_scene, [player_id], gamestate)
    print('First scene for player', player_id, 'is', first_scene)
    return [player_id], first_scene

def handle_edge_cases(player_id, gamestate):
    player = gamestate.players[player_id]
    if player.is_waiting():
        return [player_id], 'wait_scene'
    elif player.ended():
        return [player_id], 'end_scene'

    # Checking for waiting players assumes only 2 players. Needs to be modified for generalized version.
    waiting_player = is_other_player_waiting(player_id, gamestate)

    # Release the other player from waiting in order to check if the current state (after applying postconditions)
    # allows any viable scenes for them. This allows the player to check again if the reason they are waiting for
    # is still valid after the state change done by other players.
    if waiting_player is not None:
        waiting_player.release()

    # Gate every "gate_window" number of scenes, where gate_window is specified by the author
    # Gating ensure no player will be starved
    if player.get_beat_count() % gamestate.gate_window == 0 and gate(player_id, gamestate):
        return [player_id], 'wait_scene'

    # If there is a scene that must be played after the current one, show it (usually a multiplayer scene picked
    # by other players)
    awaiting_scene = player.get_awaiting_scene()
    if awaiting_scene is not None:
        check_and_apply_ending(awaiting_scene, player_id, gamestate)
        player.increment_beat_count()
        return [player_id], awaiting_scene
    
    return None, waiting_player

def handle_multiplayer_scenes(player_id, gamestate, next_scene, waiting_player):
    player = gamestate.players[player_id]
    # Check if the next scene requires more than one player
    if gamestate.scenes_list[next_scene]['player count'] > 1:
        # If there are no waiting players, wait for any of them to be released.
        if waiting_player is None:
            player.wait()
            return [player_id], 'wait_scene'
        else:
            # If the other player is waiting, show the scene to both of them. (Assumes 2 players)
            player.add_scene(next_scene)
            waiting_player.add_scene(next_scene)
            waiting_player.set_awaiting_scene(next_scene)
            player.increment_beat_count()
            apply_scene_postconditions(next_scene, [player_id], gamestate)
            return [player_id], next_scene
    else:
        # If the next scene requires only one player, show it immediately.
        apply_scene_postconditions(next_scene, [player_id], gamestate)
        player.add_scene(next_scene)
        player.increment_beat_count()
        print('Play scene', next_scene, 'for player(s)', player_id)
        return [player_id], next_scene
        

def get_viable_scenes(player_id, gamestate):
    player_scenes = get_player_scenes(player_id, gamestate)
    viable_scenes_list = []
    
    for label in player_scenes:
        # If the scene has not been shown before to the player and its preconditions are statisfied, it is viable
        if gamestate.players[player_id].is_new_scene(label) and test_preconditions(player_id, label, gamestate):
            viable_scenes_list.append(label)
    return viable_scenes_list

def get_all_next_scenes(player_id, gamestate):
    
    player = gamestate.players[player_id]
    handled = handle_edge_cases(player_id, gamestate)
    
    if handled[0] is not None:
        return handled

    viable_scenes_list = get_viable_scenes(player_id, gamestate)

    # If there are no suitable scenes, then the player should wait for other players to change the state
    # and check again later if there are any viable scenes
    if len(viable_scenes_list) == 0:
        player.wait()
        return [player_id], 'wait_scene'
    

    return [([player_id], scene) for scene in viable_scenes_list]

def get_next_scene(player_id, gamestate):
    
    # Returns a tuple of two elements. The first element is a list of player IDs to show the scene.
    # The second is the scene label.
    
    player = gamestate.players[player_id]
    handled = handle_edge_cases(player_id, gamestate)

    if handled[0] is None:
        waiting_player = handled[1]
    else:
        return handled

    viable_scenes_list = get_viable_scenes(player_id, gamestate)

    # If there are no suitable scenes, then the player should wait for other players to change the state
    # and check again later if there are any viable scenes
    if len(viable_scenes_list) == 0:
        player.wait()
        return [player_id], 'wait_scene'
    
    # Find viable scenes' distance from the plot
    beat_errors = evaluate_beats(viable_scenes_list, player_id, gamestate)
    print(beat_errors)
    min_error = min(beat_errors.values())
    highest_scored_scenes_list = [key for key in beat_errors if beat_errors[key] == min_error]

    # Randomly pick label of one of the best scoring scenes according to objective function
    scene_index = random.randint(0, len(highest_scored_scenes_list)-1)
    next_scene = highest_scored_scenes_list[scene_index]
    return handle_multiplayer_scenes(player_id, gamestate, next_scene, waiting_player)

############################################## PLAYER HELPERS ################################################
def set_player_role(player_id, role, gamestate):
    print('Player', player_id, 'set to role', role)
    gamestate.players[player_id].set_role(role)

def get_player_role(player_id, gamestate):
    return gamestate.players[player_id].get_role()

def all_players_assigned(gamestate):
    all_assigned = True
    for player in gamestate.players:
        if player.role == None:
            all_assigned = False
            break
    return all_assigned

def is_other_player_waiting(player_id, gamestate):
# Check if there are any waiting players and return their ID if found (Assumes only 2 players)
    for player in gamestate.players:
        if player.get_id() != player_id and player.is_waiting():
            return player
    return None

def all_players_ended(gamestate):
    for player in gamestate.players:
        if not player.ended():
            return False
    return True