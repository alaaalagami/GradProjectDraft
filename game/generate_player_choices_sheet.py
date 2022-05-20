import json
import pandas as pd
from em_functionalities import parse_entry

def load_file(file):
    f = open(file)
    data = json.load(f)
    f.close()
    return data

scene_file = "scenes.json"
scenes_list = load_file(scene_file)
indices = []

for label in scenes_list:
    scene = scenes_list[label]
    for menu_label in scene['menus']:
        menu = scene['menus'][menu_label]
        for choice in menu:
            indices.append(parse_entry(label, menu_label, choice))

sheet = pd.DataFrame(index=indices)
sheet.to_csv('./player_choices_sheet.csv')