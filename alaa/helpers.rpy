# type: ignore

init python:
    import os
    import subprocess
    import socket
    import time
    import json
    from contextlib import closing

    cwd =  '../RenPyTest' # os.getcwd()

    current_scene = None
    role = None

    def find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

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
    
    def is_choice_done(label, menu_label):
        event = {'type': 'check_choice', 'label': label, 'menu_label': menu_label}
        send_to_server(json.dumps(event))
        choice = recv_from_server()
        if choice == 'None':
            return None
        return choice
    
    def make_choice(character, current_scene, menu_label, prompt, choices, reactions):
        if role.name == character.name:
            character(prompt, interact=False)
            choice = renpy.display_menu(choices)
            send_choice(current_scene, menu_label, choice)
        else:
            choice = is_choice_done(current_scene, menu_label)
            while choice is None:
                character("Hmmmmmmm, Let me think....", interact=False)
                renpy.pause(2, hard=True)
                choice = is_choice_done(current_scene, menu_label)
      
        if choice == choices[0][1]:
            character(reactions[0])
        else:
            character(reactions[1])

    def make_jump_choice(character, current_scene, menu_label, prompt, choices, jump_to):
        if role.name == character.name:
            character(prompt, interact=False)
            choice = renpy.display_menu(choices)
            send_choice(current_scene, menu_label, choice)
        else:
            choice = is_choice_done(current_scene, menu_label)
            while choice is None:
                character("Hmmmmmmm, Let me think....", interact=False)
                renpy.pause(2, hard=True)
                choice = is_choice_done(current_scene, menu_label)

        if choice == choices[0][1]:
            renpy.jump(jump_to[0])
        else:
            renpy.jump(jump_to[1])


############################# LOGIN ##################################

label start:
   python:
    narrator("Contacting Server...", interact=False)
    renpy.pause(0.1, hard=True)
    port = find_free_port()
    start_client(port)
    time.sleep(2)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_address = ('localhost', port)
    client_socket.connect(client_address)
    
    renpy.jump('login')

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
        role = red
        renpy.jump(first_scene)
        

    "Wolf":
       python:
        send_to_server('Wolf')
        first_scene = recv_from_server()
        current_scene = first_scene
        role = wolf
        renpy.jump(first_scene)

############################## NEXT SCENE ####################################

label next:
    python:
        narrator("Loading scene...", interact=False)
        renpy.pause(0.1, hard=True)
        next_scene = get_next_scene()
        current_scene = next_scene
        renpy.jump(next_scene)


############################## WAITING #######################################

label wait_scene:
    python:
        narrator("Waiting for other player...", interact=False)
        renpy.pause(3, hard=True)
        next_scene = get_next_scene()
        current_scene = next_scene
        renpy.jump(next_scene)


############################ END SCENE #######################################

label end_scene:
    "The End"
    return