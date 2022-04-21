from experience_manager import ExperienceManager

em = ExperienceManager(state_file = "initial_state.json", \
        scene_file = "scenes.json", plot_file = "plot.json", players_file= "players_data.json")

em.set_player_role(0, 'Red')
em.set_player_role(1, 'Wolf')
print(em.get_first_scene(0))
print(em.get_first_scene(1))
em.apply_choice_postconditions("Wolf1", "Mushroom", "Eat")
print(em.get_next_scene(0))
print(em.get_next_scene(1))
print(em.get_next_scene(1))