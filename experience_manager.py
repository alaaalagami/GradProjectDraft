class Player:
    def __init__(self, number):
        self.role = None
        self.number = number
    
    def set_role(self, role):
        self.role = role

class ExperienceManager():
    def __init__(self):
        self.current_state = "happy"
        self.players = (Player(0), Player(1))
    
    def update_state(self, new_state):
        self.current_state = new_state

    def get_next_scene(self):
        return self.current_state
    
    def set_player_role(self, player_num, role):
        self.players[player_num].set_role(role)
    
    def all_players_assigned(self):
        all_assigned = True
        for player in self.players:
            if player.role == None:
                all_assigned = False
                break
        return all_assigned