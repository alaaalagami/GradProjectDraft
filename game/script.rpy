# type: ignore

define moemen = Character('Moemen')
define alaa = Character('Alaa')

init python:
    import os
    import subprocess

    cwd =  '../RenPyTest' # os.getcwd()
    next_file_path = cwd + '/game/info/next_scene.txt'
    choice_file_path = cwd + '/game/info/choice.txt'
    join_file_path = cwd + '/game/info/join_key.txt'
    
    def send_to_server(message):
        subprocess.call('python3 ' + cwd + '/game/out_channel.py '+message, shell=True)
    
    send_to_server('hello_again')

#    def recv_from_server():

label start:
    jump login

menu login:
    "Do you want to host a new game or join an already-existing one?"
    "Host": 
        jump host
    "Join": 
        jump join

label host:
    "Host"

label join:
    "Join"

menu pickRole:
    "Pick a role!"
    "I want to control how Moemen feels.":
        jump controller
    "I want to perceive how Moemen feels.":
        jump perceiver

label controller:
    python:
        narrator("How do you want Moemen to feel?", interact=False)
        mood = renpy.display_menu([("Happy", "happy"), ("Sad", "sad")])
        with open(next_file_path, 'w') as next_file:
            next_file.write(mood)
        narrator("Moemen is now "+mood+"!")
        renpy.jump("controller")
    
label perceiver:
    scene bg whitehouse
    show moemen main at left
    moemen "Hi I am Moemen"
    moemen "Let's see how I am feeling!"
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
        with open(next_file_path, 'r') as next_file:
            next_scene = next_file.read().strip()
        renpy.jump(next_scene)
