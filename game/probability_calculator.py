import pandas as pd

class ProbabilityCalculator():
    def __init__(self, choices_file):
        self.choices_file_path = choices_file
        self.player_choices_df = pd.read_csv(choices_file, index_col=0)
    
    def calculate(self, choice_entries, scene_label, menu_label, choices):
        
        print('aaaaa', choice_entries)
        targets = ['_'.join([scene_label, menu_label, choice]) for choice in choices]

        similar_session_labels = self.player_choices_df.apply(lambda row: 
                                    all([row[key] == choice_entries[key] for key in choice_entries]))

        similar_sessions = self.player_choices_df[[key for key in similar_session_labels.keys() 
                                    if similar_session_labels[key]]]
        
        target_rows = similar_sessions.loc[targets].dropna(axis=1)

        probabilities = []
        for target in targets:
          target_values = list(target_rows.loc[target])
          target_values.append(1)
          probabilities.append(sum(target_values) / len(target_values))

        probabilities = [p/sum(probabilities) for p in probabilities]

        choices_and_probs = {}
        for i in range(len(probabilities)):
            choices_and_probs[choices[i]] = probabilities[i]

        print(choices_and_probs)
        return choices_and_probs

    def add_entry(self, choice_entries):
        for key in self.player_choices_df.index:
            if key not in choice_entries.keys():
              choice_entries[key] = None

        self.player_choices_df['session_'+str(self.player_choices_df.shape[1])] = pd.Series(choice_entries)
        self.player_choices_df.to_csv(self.choices_file_path)
        


