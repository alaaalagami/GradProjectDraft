import subprocess
message = subprocess.check_output('python3 in_channel.py', shell=True)
print(message.decode('utf-8')[:-1])