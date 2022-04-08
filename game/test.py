from experience_manager import ExperienceManager

em = ExperienceManager(state_file = "game/initial_state.json", \
        scene_file = "game/scenes.json", plot_file = "game/plot.json", players_file= "game/players_data.json")

em.set_player_role(0, 'Red')
em.set_player_role(1, 'Wolf')
print(em.get_first_scene(0))
print(em.get_first_scene(1))
em.apply_choice_postconditions("Red1", "Sword", "Take")
print(em.get_next_scene(0))
print(em.get_next_scene(0))
print(em.get_next_scene(0))
em.apply_choice_postconditions("Wolf1", "Grandma", "Eat")
print(em.get_next_scene(1))
print(em.check_choice('RedKillsWolf', 'Regret'))
em.apply_choice_postconditions("RedKillsWolf", "Regret", "Yes")
print(em.check_choice('RedKillsWolf', 'Regret'))
em.apply_choice_postconditions("RedKillsWolf", "Fear", "Yes")
print(em.check_choice('RedKillsWolf', 'Fear'))