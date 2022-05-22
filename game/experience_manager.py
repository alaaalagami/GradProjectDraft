from em_functionalities import *
from em_search import EM_Searcher
from probability_calculator import ProbabilityCalculator

class ExperienceManager():

    def __init__(self, state_file, scene_file, plot_file, players_file, choices_file):
        self.gamestate = get_initial_gamestate(state_file, scene_file, plot_file, players_file)
        self.probability_calculator = ProbabilityCalculator(choices_file)
        print("Created Experience Manager Instance")
    

   ############################################## UPDATING STATE ################################################

    def apply_choice_postconditions(self, label, menu_label, choice):
        valid_choices = self.validate_choices(label, menu_label)
        self.gamestate.choice_entries[parse_entry(label, menu_label, choice)] = 1
        for other_choice in valid_choices:
            if other_choice != choice:
                self.gamestate.choice_entries[parse_entry(label, menu_label, other_choice)] = 0
        apply_choice_postconditions(label, menu_label, choice, self.gamestate)

    def apply_scene_postconditions(self, label, players_id):
        apply_scene_postconditions(self, label, players_id, self.gamestate)

    def check_choice(self, label, menu_label):
        return check_choice(self, label, menu_label, self.gamestate)
    
    def validate_choices(self, label, menu_label):
        searcher = EM_Searcher()
        solutions = searcher.plan(self.gamestate)
        valid_choices = []

        for sol in solutions:
            first_action = sol[0][0]
            if first_action[0] == 'menu' and first_action[1][0] == label and first_action[1][1] == menu_label:
                valid_choices.append(first_action[1][2])

        return list(set(valid_choices))

    ############################################## SCENE SELECTION ################################################

    def get_first_scene(self, player_id):
        return get_first_scene(player_id, self.gamestate)

    def plan_next_scene(self, player_id):
        # Solutions are in the form: ([('menu', menu_details), ('scene', scene_details)], error)
        # menu_details: [label, menu_label, choice]
        # scene_details: [[player_id], label]

        def separate_solutions(solutions):
            group_0 = []
            group_1 = []
            for sol in solutions:
                if sol[0][0][0] == 'menu':
                    if sol[0][0][2] == 0:
                        group_0.append(sol)
                    else:
                        group_1.append(sol)
                elif sol[0][0][0] == 'scene':
                    if sol[0][0][1][0][0] == 0 or len(sol[0][0][1][0]) > 1:
                        group_0.append(sol)
                    else:
                        group_1.append(sol)

            return group_0, group_1
        
        def evaluate_scene(solutions):
            print('sols', solutions)
            possible_next_scene_labels = list(set([sol[0][0][1][1] for sol in solutions]))
            labels_and_errors = []
            for label in possible_next_scene_labels:
                label_solutions = [(sol[0][1:], sol[1]) for sol in solutions if sol[0][0][1][1] == label]
                if len(label_solutions) == 1:
                    labels_and_errors.append((label, label_solutions[0][1]))
                    continue
                total_error = 0
                p0_solutions, p1_solutions = separate_solutions(label_solutions)

                if len(p0_solutions) > 0:
                    if  p0_solutions[0][0][0][0] == 'menu':
                        total_error += evaluate_menu(p0_solutions)
                        if evaluate_menu(p0_solutions) == 4.0:
                            print(p0_solutions)
                    else:
                        total_error += evaluate_scene(p0_solutions)[1]

                if len(p1_solutions) > 0:
                   if p1_solutions[0][0][0][0] == 'menu':
                       total_error += evaluate_menu(p1_solutions)
                   else:
                       total_error += evaluate_scene(p1_solutions)[1]

                total_error /= (len(p0_solutions) > 0) + (len(p1_solutions) > 0)
                labels_and_errors.append((label, total_error))
            
            print('labels and errors', labels_and_errors)
            least_error_label = min(labels_and_errors, key=lambda x: x[1])
            return least_error_label
        
        def evaluate_menu(solutions):
            possible_choices = list(set([sol[0][0][1][2] for sol in solutions]))
            total_error = 0
            scene_label = solutions[0][0][0][1][0]
            menu_label = solutions[0][0][0][1][1]
            choices_and_probs = self.probability_calculator.calculate(self.gamestate.choice_entries, scene_label, menu_label, possible_choices)
            for choice in possible_choices:
                additional_error = 0
                choice_solutions = [(sol[0][1:], sol[1]) for sol in solutions if sol[0][0][1][2] == choice]

                if len(choice_solutions) == 1:
                    total_error += choice_solutions[0][1]
                    continue

                p0_solutions, p1_solutions = separate_solutions(choice_solutions)

                if len(p0_solutions) > 0:
                    if  p0_solutions[0][0][0][0] == 'menu':
                        additional_error += evaluate_menu(p0_solutions)
                    else:
                        additional_error += evaluate_scene(p0_solutions)[1]

                if len(p1_solutions) > 0:
                    if p1_solutions[0][0][0][0] == 'menu':
                        additional_error += evaluate_menu(p1_solutions)
                    else:
                        additional_error += evaluate_scene(p1_solutions)[1]

                total_error += (additional_error / ((len(p0_solutions) > 0) + (len(p1_solutions) > 0))) * choices_and_probs[choice]

            return total_error
                            
        searcher = EM_Searcher()
        solutions = searcher.plan(self.gamestate)

        # Filter out solutions that start with the other player's menus and scenes
        viable_solutions = []
        for sol in solutions:
            first_action = sol[0][0]
            if first_action[0] == 'menu':
                continue
            if player_id not in first_action[1][0]:
                continue
            viable_solutions.append(sol)
        print('viable', viable_solutions)
        least_error_label = evaluate_scene(viable_solutions)

        return least_error_label[0]

                            
    def get_next_scene(self, player_id):

        player = self.gamestate.players[player_id]

        handled = handle_edge_cases(player_id, self.gamestate)

        if handled[0] is None:
            waiting_player = handled[1]
        else:
            return handled

        viable_scenes_list = get_viable_scenes(player_id, self.gamestate)

        # If there are no suitable scenes, then the player should wait for other players to change the state
        # and check again later if there are any viable scenes
        if len(viable_scenes_list) == 0:
            player.wait()
            return [player_id], 'wait_scene'

        next_scene = self.plan_next_scene(player_id)
        return handle_multiplayer_scenes(player_id, self.gamestate, next_scene, waiting_player)
    
    def end_narrative(self):
        self.probability_calculator.add_entry(self.gamestate.choice_entries)

    
    ############################################## PLAYER HELPERS ################################################

    def set_player_role(self, player_id, role):
        set_player_role(player_id, role, self.gamestate)
    
    def all_players_assigned(self):
        return all_players_assigned(self.gamestate)
    
    def is_other_player_waiting(self, player_id):
        return is_other_player_waiting(player_id, self.gamestate)
    
    def all_players_ended(self):
        return all_players_ended(self.gamestate)