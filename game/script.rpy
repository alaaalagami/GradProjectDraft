# type: ignore

define red = Character('Red Riding Hood')
define wolf = Character('Wolf')

init python:
    import os
    import subprocess
    import socket
    import time
    import json

    cwd =  '../RenPyTest' # os.getcwd()

    current_scene = None

    def start_client(port):
        subprocess.Popen(['python', cwd + '/game/client.py', str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def send_to_server(message):
        client_socket.sendall(message.encode('utf-8'))

    def recv_from_server():
        message = client_socket.recv(4096)
        return message.decode('utf-8')
        
    
    def get_join_key():
        key = recv_from_server()
        assert len(key) == 4
        return key
    
    def send_choice(label, menu_label, choice):
        event = {'type': 'choice', 'label': label, 'menu_label': menu_label, 'choice': choice}
        send_to_server(json.dumps(event))
    
    def get_next_scene():
        event = {'type': 'show_request'}
        send_to_server(json.dumps(event))
        scene = recv_from_server()
        return scene
    
    try:
        port = 5000
        start_client(port)
        time.sleep(2)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_address = ('localhost', port)
        client_socket.connect(client_address)
    except:
        port = 6000
        start_client(port)
        time.sleep(2)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_address = ('localhost', port)
        client_socket.connect(client_address)


label start:
    jump login

menu login:
    "Do you want to host a new game or join an already-existing one?"
    "Host": 
        python:
            send_to_server('host')
            narrator("Waiting for server to send join key", interact=False)
            renpy.pause(0.1, hard=True)
            join_key = get_join_key()
            narrator("Your join key is "+join_key)
            narrator("Waiting for other player to join...", interact=False)
            renpy.pause(0.1, hard=True)
            signal = recv_from_server()
            assert signal == 'start'
            narrator("Other player joined!")

        jump pickRole

    "Join": 
        python:
            send_to_server('join')
            join_key = renpy.input('Please enter the join key: ', length=4)
            narrator("Joining game...", interact=False)
            renpy.pause(0.1, hard=True)
            send_to_server(join_key)
            signal = recv_from_server()
            assert signal == 'joined'
            narrator("Joined Successfully!")
            
        jump pickRole

menu pickRole:
    "Pick a role!"
    "Red Riding Hood":
       python:
        send_to_server('Red')
        first_scene = recv_from_server()
        current_scene = first_scene
        renpy.jump(first_scene)

    "Wolf":
       python:
        send_to_server('Wolf')
        first_scene = recv_from_server()
        current_scene = first_scene
        renpy.jump(first_scene)
    

    

label Red1:
    red "Hello I am Red Riding Hood!"
    red "I am going to my grandma's house"
    red "As I am walking I find a sword on the ground"
    python:
        red("Do I take it?", interact=False)
        choice = renpy.display_menu([("Take the Sword", "Take"), ("Leave the Sword", "Leave")])
        send_choice(current_scene, "Sword", choice)
        if choice == "Take":
            red("Alright! Got it!")
        else:
            red("I better leave it alone")
    red "I see my grandma's house approaching"
    red "I knock on the door and enter"

    jump next

label Wolf1:
    wolf "Hello I am the big bad wolf"
    wolf "I am very hungry right now"
    wolf "I see a house nearby"
    wolf "I enter the house and find Red Riding Hood's grandma lying bed"
    
    python:
        wolf("Do I eat her?", interact=False)
        choice = renpy.display_menu([("Eat the Grandma", "Eat"), ("Leave her alone", "Leave")])
        send_choice(current_scene, "Grandma", choice)
        if choice == "Eat":
            red("Ah yes! What a delicious meal!")
        else:
            red("I better leave her alone")

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
    wolf "I see the dessert has arrived!"
    "Red Riding Hood swiftly takes out the sword"
    wolf "Ah shit"
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


label next:
    python:
        narrator("Loading scene...", interact=False)
        renpy.pause(0.1, hard=True)
        next_scene = get_next_scene()
        current_scene = next_scene
        renpy.jump(next_scene)

label end_scene:
    "The End"
    return

label wait_scene:
    python:
        narrator("Waiting for other player...", interact=False)
        renpy.pause(1, hard=True)
        next_scene = get_next_scene()
        renpy.jump(next_scene)