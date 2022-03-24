import json
from enum import Enum

class PlayerState(Enum):
    WAITING = 0
    READY = 1
    END = 2

class Player:

    def __init__(self, id):
        self.role = None
        self.id = id
        self.scenes = []
        self.state = PlayerState.READY
    
    def set_role(self, role):
        self.role = role
    
    def get_role(self):
        return self.role
    
    def add_scene(self, label):
        self.scenes.append(label)
    
    def is_new_scene(self, label):
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

def load_file(file):
    f = open(file)
    data = json.load(f)
    f.close()
    return data

class ExperienceManager():
    def __init__(self, state_file, scene_file, plot_file, players_file):
        self.current_state = load_file(state_file)
        self.players_data = load_file(players_file)
        self.scene_count = 1  # number of upcoming scene (+1 at end of get_next_scene)
        self.players = []
        self.scenes_list = load_file(scene_file)
        self.plot = load_file(plot_file)
        for i in range(int(self.players_data["players_count"])):
            self.players.append(Player(i))
        print("Created Experience Manager Instance")
    

   ############################################## UPDATING STATE ################################################

    def apply_changes(self, changes):
        print('State before:', self.current_state)
        for key in changes:
            if changes[key][0] == "add":
                self.current_state[key] = float(self.current_state[key]) + float(changes[key][1])
            elif changes[key][0] == "set":
                self.current_state[key] = float(changes[key][1])
        print('State after:', self.current_state, '\n')


    def apply_choice_postconditions(self, label, menu_label, choice):
        print('Selected', choice, 'from menu', menu_label)
        print('Applying choice postconditions')
        changes = self.scenes_list[label]["menus"][menu_label][choice]
        self.apply_changes(changes)

    def apply_scene_postconditions(self, label, players_id):
        print('Applying scene postconditions')
        changes = self.scenes_list[label]['postconditions']
        self.apply_changes(changes)
        if "end scene" in self.scenes_list[label]:
            for id in players_id:
                self.players[id].end()


    ############################################## SCENE SELECTION ################################################

    def get_player_scenes(self, player_id):
        role = self.get_player_role(player_id)
        player_scenes = []
        for label in self.scenes_list:
            scene = self.scenes_list[label]
            if role in scene['player']:
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
    
    def get_first_scene(self, player_id):
        role = self.get_player_role(player_id)
        first_scene = self.players_data['characters'][role]["first scene"]
        self.players[player_id].add_scene(first_scene)
        print('First scene for player', player_id, 'is', first_scene)
        return first_scene

    def get_next_scene(self, player_id):
        
        player = self.players[player_id]

        if player.is_waiting():
            return ([player_id], 'wait_scene')
        elif player.ended():
            return ([player_id], 'end_scene')

        player_scenes = self.get_player_scenes(player_id)

        viable_scenes_list = []

        for label in player_scenes:
            if  self.players[player_id].is_new_scene(label) and self.test_preconditions(label):
                viable_scenes_list.append(label)

        if len(viable_scenes_list) == 0:
            player.wait()
            return ([player_id], 'wait_scene')

        next_scene = viable_scenes_list[0]

        waiting_player = self.is_other_player_waiting(player_id)

        if waiting_player != None:
            waiting_player.release()
            
        if self.scenes_list[next_scene]['player count'] > 1:
            if waiting_player is None:
                player.wait()
                return ([player_id], 'wait_scene')
            else:
                player.add_scene(next_scene)
                waiting_player.add_scene(next_scene)
                waiting_player.release()
                self.apply_scene_postconditions(next_scene, [player_id, waiting_player.get_id()])
                return ([player_id, waiting_player.get_id()], next_scene)

        self.apply_scene_postconditions(next_scene, [player_id])
        player.add_scene(next_scene)

        print('Play scene', next_scene, 'for player(s)', player_id)
        return (player_id, next_scene)

    
    ############################################## PLAYER HELPERS ################################################

    def set_player_role(self, player_id, role):
        print('Player', player_id, 'set to role', role)
        self.players[player_id].set_role(role)
    
    def get_player_role(self, player_id):
        return self.players[player_id].get_role()
    
    def all_players_assigned(self):
        all_assigned = True
        for player in self.players:
            if player.role == None:
                all_assigned = False
                break
        return all_assigned
    
    def is_other_player_waiting(self, player_id):
        for player in self.players:
            if player.get_id() != player_id and player.is_waiting():
                return player
        return None