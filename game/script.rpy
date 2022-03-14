# type: ignore

define moemen = Character('Moemen')
define alaa = Character('Alaa')

init python:
    import os
    import subprocess
    import socket
    import time
    import json

    cwd =  '../RenPyTest' # os.getcwd()

    def start_client(port):
        subprocess.Popen(['python', cwd + '/game/client.py', str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def send_to_server(message):
        client_socket.sendall(message.encode('utf-8'))

    def recv_from_server():
        message = client_socket.recv(1024)
        return message.decode('utf-8')
        
    
    def get_join_key():
        key = recv_from_server()
        assert len(key) == 4
        return key
    
    def send_choice(choice):
        event = {'type': 'choice', 'pick': choice}
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
            assert signal == 'pick'
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
            assert signal == 'pick'
            narrator("Joined Successfully!")
            
        jump pickRole

menu pickRole:
    "Pick a role!"
    "I want to control how Moemen feels.":
       python:
        send_to_server('controller')
        signal = recv_from_server()
        assert signal == 'start'

       jump controller

    "I want to perceive how Moemen feels.":
       python:
        send_to_server('perceiver')
        signal = recv_from_server()
        assert signal == 'start'

       jump perceiver

label controller:
    python:
        narrator("How do you want Moemen to feel?", interact=False)
        mood = renpy.display_menu([("Happy", "happy"), ("Sad", "sad")])
        send_choice(mood)
        narrator("Moemen is now "+mood+"!")
        renpy.jump("controller")
    
label perceiver:
    scene bg whitehouse
    show moemen main at left
    moemen "Hi I am Moemen"
    jump next

label sad:
    moemen "I am sad"
    jump next

label happy:
    moemen "I am happy"
    jump next

label next:
    moemen "Let's see how I am feeling!"
    python:
        next_scene = get_next_scene()
        renpy.jump(next_scene)
