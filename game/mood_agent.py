while True:
    mood = input('How is Moemen feeling? (happy/sad) ')
    with open('next_scene.txt', 'w') as next_file:
        next_file.write(mood)