while True:
    phrase = input('What do you want Moemen to say? ')
    with open('script.rpy', 'a') as script_file:
        script_file.write("\n    moemen \"{0}\"".format(phrase))