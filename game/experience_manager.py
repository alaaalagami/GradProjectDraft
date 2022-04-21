from em_functionalities import *
from em_search import EM_Searcher

class ExperienceManager():

    def __init__(self, state_file, scene_file, plot_file, players_file):
        self.gamestate = get_initial_gamestate(state_file, scene_file, plot_file, players_file)
        print("Created Experience Manager Instance")
    

   ############################################## UPDATING STATE ################################################

    def apply_choice_postconditions(self, label, menu_label, choice):
        apply_choice_postconditions(label, menu_label, choice, self.gamestate)

    def apply_scene_postconditions(self, label, players_id):
        apply_scene_postconditions(self, label, players_id, self.gamestate)

    def check_choice(self, label, menu_label):
        return check_choice(self, label, menu_label, self.gamestate)

    ############################################## SCENE SELECTION ################################################

    def get_first_scene(self, player_id):
        return get_first_scene(player_id, self.gamestate)

    def plan_next_scene(self, player_id):
        searcher = EM_Searcher()
        solutions = searcher.plan(self.gamestate)
        solutions.sort(key=lambda sol: sol[-1])
        print('plan sols', solutions)
        for sol in solutions:
            for action in sol[0]:
                print('action', action)
                if action[0] == 'menu':
                    continue
                if action[1][0][0] != player_id:
                    continue
                return action[1][1]
        
    def get_next_scene(self, player_id):
#        return get_next_scene(player_id, self.gamestate)
        player = self.gamestate.players[player_id]

        handled = handle_edge_cases(player_id, self.gamestate)

        if handled[0] is None:
            waiting_player = handled[1]
        else:
            return handled

        viable_scenes_list = get_viable_scenes(player_id, self.gamestate)

        print(viable_scenes_list)
        # If there are no suitable scenes, then the player should wait for other players to change the state
        # and check again later if there are any viable scenes
        if len(viable_scenes_list) == 0:
            player.wait()
            return [player_id], 'wait_scene'

        print('in-----------------------------------------------------')
        next_scene = self.plan_next_scene(player_id)
        print('out-----------------------------------------------------')
        return handle_multiplayer_scenes(player_id, self.gamestate, next_scene, waiting_player)

    
    ############################################## PLAYER HELPERS ################################################

    def set_player_role(self, player_id, role):
        set_player_role(player_id, role, self.gamestate)
    
    def all_players_assigned(self):
        return all_players_assigned(self.gamestate)
    
    def is_other_player_waiting(self, player_id):
        return is_other_player_waiting(player_id, self.gamestate)
    
    def all_players_ended(self):
        return all_players_ended(self.gamestate)