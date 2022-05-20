from experience_manager import ExperienceManager

em = ExperienceManager(state_file = "initial_state.json", \
        scene_file = "scenes.json", plot_file = "plot.json", players_file= "players_data.json", choices_file='player_choices_sheet.csv')

em.set_player_role(0, 'Red')
em.set_player_role(1, 'Wolf')
print(em.get_first_scene(0))
print(em.get_first_scene(1))
print(em.get_next_scene(0))
print(em.get_next_scene(1))
print(em.get_next_scene(1))
print(em.validate_choices("Red-Decides-Restaurant", "Restaurant"))
em.apply_choice_postconditions("Red-Decides-Restaurant", "Restaurant", "Open")
em.end_narrative()
#print('\nFor Plot:', em.gamestate.plot['progression'])
#print("Wolf scenes:", em.gamestate.players[1].get_scenes(), '\n')