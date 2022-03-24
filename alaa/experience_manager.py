import json


class Player:
    def __init__(self, number):
        self.role = None
        self.number = number

    def set_role(self, role):
        self.role = role


def load_file(file):
    f = open(file)
    data = json.load(f)
    f.close()
    return data


class ExperienceManager:
    def __init__(self, state_file, scene_file, plot_file, players_file):
        self.current_state = load_file(state_file)
        self.players_data = load_file(players_file)
        self.scene_count = 1  # number of upcoming scene (+1 at end of get_next_scene)
        self.players = []
        self.scenes_list = load_file(scene_file)
        self.plot = load_file(plot_file)
        self.next_scene = {}
        self.next_scene_groups = None
        self.current_scene_groups = None
        self.current_scene_menu_character_order = None
        self.total_menu_count = 0
        self.current_menu_count = 0
        for i in range(int(self.players_data["players_count"])):
            self.players.append(Player(i))
            self.next_scene[self.players_data["characters"][i]] = None

    def update_state(self, label, menu_label, choice):
        choice_maker = self.current_scene_menu_character_order[self.current_menu_count]
        changes = self.scenes_list[label]["menus"][menu_label][choice]
        for key in changes:
            if changes[key][0] == "add":
                self.current_state[key] = float(self.current_state[key]) + float(changes[key][1])
            else:
                if key == "next scene":
                    others_next_scene = changes[key][1]
                else:
                    self.current_state[key] = changes[key][1]

        affected_group = []
        for group in self.current_scene_groups:
            if choice_maker in group:
                affected_group = group
                break

        for player in affected_group:
            if player == choice_maker:
                continue
            self.next_scene[player] = others_next_scene + "_" + player

        self.current_menu_count += 1

        if self.current_menu_count == self.total_menu_count:
            for i in range(len(self.next_scene_groups)):
                for j in range(len(self.next_scene_groups[i])):
                    if j == 0:
                        self.next_scene[self.next_scene_groups[i][j]] = None
                    else:
                        self.next_scene[self.next_scene_groups[i][j]] = "WAIT"

    def test_preconditions(self, label, player):
        if player != self.scenes_list[label]["player"]:
            return False
        preconditions = self.scenes_list[label]["preconditions"]
        state = self.current_state
        for key in preconditions:
            if preconditions[key][1] == "None":
                continue
            if preconditions[key][0] == "is":
                if preconditions[key][1] != state[key]:
                    return False
            elif preconditions[key][0] == "more than":
                if float(preconditions[key][1]) <= float(state[key]):
                    return False
            elif preconditions[key][0] == "less than":
                if float(preconditions[key][1]) >= float(state[key]):
                    return False
        return True

    def get_next_scene(self, label, player_id):

        player = self.players_data["characters"][player_id]

        changes = self.scenes_list[label]["postconditions"]

        # If this scene is necessarily followed by a specific other scene (whether due it a condition on itself or on
        # a choice), return that necessary next scene
        if self.next_scene[player] is not None:
            if self.next_scene[player] == "WAIT":
                return "empty_scene"
            else:
                label_to_return = self.next_scene[player] # Next scene doesn't update scene count (doesn't progress plot) since it's made only for
                # multiplayer scenes
                self.next_scene[player] = "WAIT"
                return label_to_return

        # Apply postconditions of previous scene
        for key in changes:
            if changes[key][0] == "add":
                self.current_state[key] = float(self.current_state[key]) + float(changes[key][1])
            else:
                if key == "next scene":
                    self.next_scene[self.scenes_list[label]["player"]] = changes[key][1]
                else:
                    self.current_state[key] = changes[key][1]

        viable_scenes_list = []
        scene_errors = {}
        scene_error_sums = {}

        for label in self.scenes_list:
            if self.test_preconditions(label, player):
                viable_scenes_list.append(label)

        objective = self.plot[self.scene_count][0]

        for label in viable_scenes_list:
            errors = {}
            scene_error_sums[label] = 0
            for key in self.plot[self.scene_count]:
                if self.scenes_list[label]["postconditions"][key][0] == "add":
                    value = float(self.current_state[key]) + float(self.scenes_list[label]["postconditions"][key][1])
                else:
                    value = self.scenes_list[label]["postconditions"][key][1]
                error = abs(float(objective[key]) - float(value))
                errors[key] = error
                scene_error_sums[label] = scene_error_sums[label] + error
            scene_errors[label] = errors

        # If there are no upcoming menus, set next_scene as "WAIT" for all non-next scene makers and none for next
        # scene makers
        if self.total_menu_count == 0:
            for i in range(len(self.next_scene_groups)):
                for j in range(len(self.next_scene_groups[i])):
                    if j == 0:
                        self.next_scene[self.next_scene_groups[i][j]] = None
                    else:
                        self.next_scene[self.next_scene_groups[i][j]] = "WAIT"
        # If there are upcoming menus, set next_scene as "WAIT" for all (will be changed to None for next scene
        # makers after all menus are complete)
        else:
            for key in self.next_scene:
                self.next_scene[key] = "WAIT"

        self.scene_count += 1
        self.current_scene_groups = self.next_scene_groups
        self.next_scene_groups = self.plot[self.scene_count][1]

        label_to_return = min(scene_error_sums, key=scene_error_sums.get)

        self.current_scene_menu_character_order = self.scenes_list["label_to_return"]["menu characters order"]
        self.total_menu_count = len(self.scenes_list["label_to_return"]["menu characters order"])
        self.current_menu_count = 0

        return label_to_return

    def set_player_role(self, player_num, role):
        self.players[player_num].set_role(role)

    def all_players_assigned(self):
        all_assigned = True
        for player in self.players:
            if player.role == None:
                all_assigned = False
                break
        return all_assigned
