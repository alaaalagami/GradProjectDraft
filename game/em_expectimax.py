from em_functionalities import *
from abstract_helpers import StochasticGame
from em_search import EM_Search_Problem, Node
from math import inf


def H_expecti_min(game, node, max_depth):
    '''H-Expecti-Min implementation.'''
    depth = 0

    def min_value(state):
        mini = inf
        for a in game.actions(state):
            mini = min(mini, chance_node(state, a, depth+1, max_depth))
        return mini

    def chance_node(node, action, depth, max_depth):
        res_state = game.result(node.state, action)
        if depth == max_depth or game.goal_test(res_state):
            return node.path_cost
        sum_chances = 0
        num_chances = len(game.chances(res_state))
        if num_chances is 0: print(res_state)
        for chance in game.chances(res_state):
            res_state = game.outcome(res_state, chance)
            utility = 0
            if game.player(state) == player:
                utility = max_value(res_state)
            else:
                utility = min_value(res_state)
            sum_chances += utility * game.probability(chance)
        return sum_chances / num_chances
    
    def next_node(node, action, depth, max_depth):
        if action[0] == 'menu':
            return chance_node(node, action, depth, max_depth)
        elif action[0] == 'scene':
            return min_value(node, action, depth, max_depth)

    return min(game.actions(node.state), key= lambda a: next_node(node, a, depth, max_depth) if action[0] != 'menu' else inf, default=None)

from random import choice

game = EM_Search_Problem()
node = Node.root(game.init_state)

while(True):
    action = H_expecti_min(game, node, 10)
    node = Node.child(game.result(node.state, action))
    if game.goal_test(node.state): 
        print('End')
        break

from copy import deepcopy

def get_next_menu(label, state):
       if 'menus' in state.scenes_list[label]:
           menus = state.scenes_list[label]['menus']
           for menu in menus:
               if check_choice(label, menu, state) == 'None':
                   return [label, menu, menus[menu]]  
       return 'None'

def get_current_scenes(state):
        scenes = []
        players = state.players
        for player in players:
            scenes.append(player.scenes[-1])
        return scenes

def plan_next_scene(player_id, error, gamestate):
    # Get all possible next scenes
    all_next_scenes = [scene[1] for scene in get_all_next_scenes(player_id, gamestate) if type(scene) == tuple]

    def evaluate_scene(player_id, label, error, gamestate):
        # Apply scene effects
        apply_scene_postconditions(label, player_id, gamestate)
        gamestate.players[player_id].increment_beat_count()
        gamestate.players[player_id].add_scene(label)

        if all_players_ended(gamestate):
            return error

        additional_error = 0

        # Check if both players have menus. If not then they query their next scenes
        num_children = 0
        scenes = get_current_scenes(gamestate)

        for i in range(2):
            next_menu = get_next_menu(scenes[i], gamestate)

            if next_menu != 'None':
                additional_error += evaluate_menu(i, next_menu[0], next_menu[1], next_menu[2], error, deepcopy(gamestate))
                num_children += 1
            else:
                next_scenes = [scene[1] for scene in get_all_next_scenes(i, gamestate) if type(scene) == tuple]
                additional_error += min(next_scenes, lambda scene: evaluate_scene(player_id, scene, 
                                    error + get_error(scene, player_id, gamestate), deepcopy(gamestate)))
                num_children += 1  

        return error + (1/num_children) * additional_error      


    def evaluate_menu(player_id, label, menu_label, choices, error, gamestate):
        num_choices = 0
        for choice in choices:
            


    return min(all_next_scenes, lambda scene: evaluate_scene(player_id, scene, 
                                    error + get_error(scene, player_id, gamestate), deepcopy(gamestate)))
    
