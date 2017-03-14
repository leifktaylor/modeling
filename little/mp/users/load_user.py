import json
import os
import sys
from gameobjects.gameobject import load_lifeform
import pickle


def load_user(character, username, password, users_file='users.json'):
    print('login:{0} username:{1} password:{2}'.format(character, username, password))
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(location, users_file), 'r') as f:
        userdata = json.load(f)
        f.close()
    current_user = userdata[username]
    print('userdata -- login:{0} username:{1} password:{2}'.format(current_user,
                                                                   userdata[username], current_user['password']))
    if current_user['password'] != password:
        raise RuntimeError('Incorrect password')
    filename = current_user['characters'][character]
    return load_lifeform(os.path.join(location, filename))

# if __name__ == '__main__':
#     r = load_user('Atreyu', 'leif', 'mypw')
