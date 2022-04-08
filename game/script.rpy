# type: ignore

define red = Character('Red Riding Hood')
define wolf = Character('Wolf')

label Red1:
    red "Hello I am Red Riding Hood!"
    red "I am going to my grandma's house"
    red "As I am walking I find a sword on the ground"

    python:
        make_choice(character = red,
            current_scene = current_scene, 
            menu_label = "Sword",
            prompt = "Do I take it?",
            choices = [("Take the Sword", "Take"), ("Leave the Sword", "Leave")], 
            reactions = ["Alright! Got it!", "I better leave it alone"])

    red "I see my grandma's house approaching"
    red "I knock on the door and enter"

    jump next

label Wolf1:
    wolf "Hello I am the big bad wolf"
    wolf "I am very hungry right now"
    wolf "I see a house nearby"
    wolf "I enter the house and find Red Riding Hood's grandma lying bed"

    python:
        make_choice(character = wolf,
            current_scene = current_scene, 
            menu_label = "Grandma",
            prompt = "Do I eat her?",
            choices = [("Eat the Grandma", "Eat"), ("Leave her alone", "Leave")], 
            reactions = ["Ah yes! What a delicious meal!", "I better leave her alone"])

    jump next

label WolfEatsRed:
    red "Hi grandma I am here!"
    "Red Riding Hood sees the wolf has eaten her grandma"
    red "Oh my god"
    "The wolf starts approaching her"
    wolf "I see the dessert has arrived!"
    red "I wish I had taken the sword from before"
    "The wolf eats Red Riding Hood"
    jump next

label RedKillsWolf:
    red "Hi grandma I am here!"
    "Red Riding Hood sees the wolf has eaten her grandma"
    red "Oh my god"
    "The wolf starts approaching her"
    wolf "I see the dessert has arrived! Let me see if I regret anything."
    python:
        make_choice(character = wolf,
            current_scene = current_scene, 
            menu_label = "Regret",
            prompt = "Do I regret what I am doing?",
            choices = [("Yes", "Yes"), ("No", "No")], 
            reactions = ["My hunger is stronger than my regret!", "NO REGRETS!"])

    "Red Riding Hood swiftly takes out the sword"
    wolf "Ah shit"

    python:
        make_choice(character = red,
            current_scene = current_scene, 
            menu_label = "Fear",
            prompt = "Am I afraid of committing murder?",
            choices = [("Yes", "Yes"), ("No", "No")], 
            reactions = ["I don't care he killed my grandma!", "NO FEARS!"])
            
    "Red Riding Hood kills the wolf and rescues her grandma"
    red "(To Wolf) No cookies for you"
    "Red Riding Hood and her grandma eat cookies over the wolf's corpse"
    jump next

label WolfEscapes:
    red "Hi grandma I am here!"
    "Red Riding Hood sees the wolf standing next to her grandma"
    "She assumes the worst and takes out her sword"
    "The wolf sees it and runs away in fear"
    red "Thank god I arrived before something bad happens"
    jump next

label RedWolfFriends:
    red "Hi grandma I am here!"
    "Red Riding Hood sees the wolf standing next to her grandma"
    red "Oh my god grandma run!"
    wolf "Don't worry Red Riding Hood. I am a good wolf."
    red "Really?"
    wolf "Yes"
    red "Really?"
    wolf "Yes"
    red "Ok I believe you"
    "Red takes out her cookies"
    "They all eat cookies together and become besties"
    jump next