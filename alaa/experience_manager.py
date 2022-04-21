import json
import random
from enum import Enum


class PlayerState(Enum):
    WAITING = 0
    READY = 1
    END = 2


class Player:

    def __init__(self, id):
        self.role = None
        self.id = id
        self.scenes = []  # List of labels of scenes that the player has viewed so far
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
        print('Changed player', self.id, 'state to waiting')
        self.state = PlayerState.WAITING

    def release(self):
        print('Changed player', self.id, 'state to ready')
        self.state = PlayerState.READY

    def end(self):
        print('Changed player', self.id, 'state to end')
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
        self.beat_count += 1


def load_file(file):
    f = open(file)
    data = json.load(f)
    f.close()
    return data


class ExperienceManager:
    def __init__(self, state_file, scene_file, plot_file, players_file):
        self.current_state = load_file(state_file)
        self.players_data = load_file(players_file)
        self.scenes_list = load_file(scene_file)
        self.plot = load_file(plot_file)
        self.gate_window = int(self.plot["gate every"])  # value assigned by author to determine how many beats between
        # every mandatory gate. Value should be set based on length and dramatic value of the story's avg. beat.

        self.players = []

        for i in range(int(self.players_data["players_count"])):
            self.players.append(Player(i))

        self.choices_made = []

        print("Created Experience Manager Instance")

    ############################################## UPDATING STATE ################################################

    def apply_changes(self, changes):
        # Modify the current state based on the 'changes' dictionary
        print('State before:', self.current_state)
        for key in changes:
            if changes[key][0] == "add":
                self.current_state[key] = float(self.current_state[key]) + float(changes[key][1])
            elif changes[key][0] == "set":
                self.current_state[key] = float(changes[key][1])
        print('State after:', self.current_state, '\n')

    def apply_choice_postconditions(self, label, menu_label, choice):
        print('Selected', choice, 'from menu', menu_label)
        self.choices_made.append((label, menu_label, choice))
        print('Applying choice postconditions')
        changes = self.scenes_list[label]["menus"][menu_label][choice]
        self.apply_changes(changes)

    def apply_scene_postconditions(self, label, players_id):
        print('Applying scene postconditions')
        changes = self.scenes_list[label]['postconditions']
        self.apply_changes(changes)

        # If this is an ending scene, change the player state to END
        for id in players_id:
            self.check_and_apply_ending(label, id)

    def check_choice(self, label, menu_label):
        for choice_made in self.choices_made:
            if label == choice_made[0] and menu_label == choice_made[1]:
                return choice_made[2]
        return 'None'

    def check_and_apply_ending(self, label, player_id):
        if "end scene" in self.scenes_list[label]:
            self.players[player_id].end()

    ############################################## SCENE SELECTION ################################################

    def get_player_scenes(self, player_id):
        # Get all scenes that the player can view based on their role and the plot state (singleplayer/multiplayer)
        role = self.get_player_role(player_id)
        scene_type = self.plot["progression"][self.players[player_id].get_beat_count()][0]
        player_scenes = []
        for label in self.scenes_list:
            scene = self.scenes_list[label]
            if role in scene['player']:
                if scene_type == "s" and len(scene['player']) == 1:
                    player_scenes.append(label)
                elif scene_type == "m" and len(scene['player']) > 1:
                    player_scenes.append(label)
        return player_scenes

    def test_preconditions(self, label):
        preconditions = self.scenes_list[label]["preconditions"]
        state = self.current_state
        for key in preconditions:
            try:
                if preconditions[key][0] == "is":
                    if float(preconditions[key][1]) != float(state[key]):
                        return False
                elif preconditions[key][0] == "more than":
                    if float(preconditions[key][1]) <= float(state[key]):
                        return False
                elif preconditions[key][0] == "less than":
                    if float(preconditions[key][1]) >= float(state[key]):
                        return False
            except:
                return False

        return True

    def evaluate_beats(self, viable_scenes, player_id):
        beat_errors = {}
        beat_count = self.players[player_id].get_beat_count()
        progression = self.plot["progression"][beat_count]
        if progression[0] == "s":
            features = self.plot["single player beat features"]
            weights = self.plot["single player beat weights"]
        else:
            features = self.plot["multi player beat features"]
            weights = self.plot["multi player beat weights"]

        objectives = progression[1]

        current_values_og = {}
        for feature in features:
            current_values_og[feature] = self.current_state[feature]

        for label in viable_scenes:
            if self.players[player_id].is_new_scene(label):
                postconditions = self.scenes_list[label]["postconditions"]
                current_values = current_values_og
                beat_errors[label] = 0
                for feature in features:
                    if feature in postconditions:
                        if postconditions[feature][0] == "add":
                            current_values[feature] = float(self.current_state[feature]) + float(
                                postconditions[feature][1])
                        else:
                            current_values[feature] = postconditions[feature][1]
                error = 0
                for i in range(len(features)):
                    feature = features[i]
                    objective = objectives[i]
                    weight = weights[i]
                    error += weight * abs(objective - current_values[feature])
                beat_errors[label] = error

        return beat_errors

    def gate(self, player_id):
        player = self.players[player_id]
        player_beat = player.get_beat_count()
        other_player_beat = self.players[1 - player_id].get_beat_count()
        if other_player_beat > player_beat:
            return False
        if other_player_beat == player_beat and self.is_other_player_waiting(player_id):
            return False
        player.wait()
        return True

    def get_first_scene(self, player_id):
        role = self.get_player_role(player_id)
        first_scene = self.players_data['characters'][role]["first scene"]
        self.players[player_id].add_scene(first_scene)
        print('First scene for player', player_id, 'is', first_scene)
        return first_scene

    def get_next_scene(self, player_id, gamestate=None):
        # Returns a tuple of two elements. The first element is a list of player IDs to show the scene.
        # The second is the scene label.
        if gamestate is None:
            gamestate = self.gamestate

        player = gamestate.players[player_id]

        if player.is_waiting():
            return [player_id], 'wait_scene'
        elif player.ended():
            return [player_id], 'end_scene'

        # Checking for waiting players assumes only 2 players. Needs to be modified for generalized version.
        waiting_player = self.is_other_player_waiting(player_id)

        # Release the other player from waiting in order to check if the current state (after applying postconditions)
        # allows any viable scenes for them. This allows the player to check again if the reason they are waiting for
        # is still valid after the state change done by other players.
        if waiting_player is not None:
            waiting_player.release()

        # Gate every "gate_window" number of scenes, where gate_window is specified by the author
        # Gating ensure no player will be starved
        if player.get_beat_count() % self.gate_window == 0:
            gated = self.gate(player_id)
        if gated:
            return [player_id], 'wait_scene'

        # If there is a scene that must be played after the current one, show it (usually a multiplayer scene picked
        # by other players)
        awaiting_scene = player.get_awaiting_scene()
        if awaiting_scene is not None:
            self.check_and_apply_ending(awaiting_scene, player_id, gamestate)
            player.increment_beat_count()
            return [player_id], awaiting_scene

        player_scenes = self.get_player_scenes(player_id)

        viable_scenes_list = []

        for label in player_scenes:
            # If the scene has not been shown before to the player and its preconditions are statisfied, it is viable
            if gamestate.players[player_id].is_new_scene(label) and self.test_preconditions(label, gamestate):
                viable_scenes_list.append(label)

        # Find viable scenes' distance from the plot
        beat_errors = self.evaluate_beats(viable_scenes_list, player_id)
        min_error = min(beat_errors.values())
        highest_scored_scenes_list = [key for key in beat_errors if beat_errors[key] == min_error]

        # If there are no suitable scenes, then the player should wait for other players to change the state
        # and check again later if there are any viable scenes
        if len(highest_scored_scenes_list) == 0:
            player.wait()
            return [player_id], 'wait_scene'

        # Randomly pick label of one of the best scoring scenes according to objective function
        scene_index = random.randint(0, len(highest_scored_scenes_list))
        next_scene = highest_scored_scenes_list[scene_index]

        # Check if the next scene requires more than one player
        if self.scenes_list[next_scene]['player count'] > 1:
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
                self.apply_scene_postconditions(next_scene, [player_id], gamestate)
                return [player_id], next_scene
        else:
            # If the next scene requires only one player, show it immediately.
            self.apply_scene_postconditions(next_scene, [player_id], gamestate)
            player.add_scene(next_scene)
            player.increment_beat_count()
            print('Play scene', next_scene, 'for player(s)', player_id)
            return player_id, next_scene

    ############################################## PLAYER HELPERS ################################################

    def set_player_role(self, player_id, role):
        print('Player', player_id, 'set to role', role)
        self.players[player_id].set_role(role)

    def get_player_role(self, player_id):
        return self.players[player_id].get_role()

    def all_players_assigned(self):
        all_assigned = True
        for player in self.players:
            if player.role is None:
                all_assigned = False
                break
        return all_assigned

    def is_other_player_waiting(self, player_id):
        # Check if there are any waiting players and return their ID if found (Assumes only 2 players)
        for player in self.players:
            if player.get_id() != player_id and player.is_waiting():
                return player
        return None
