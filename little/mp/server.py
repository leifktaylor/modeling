import socket, select, pickle
import atexit
import time
from gameobjects.gameobject import get_object_by_id, get_room_from_lifeform, get_room_from_uniquename
from gameobjects.gameobject import load_lifeform, add_lifeform_to_room, load_user, create_room_from_template
import sys
import StringIO
import contextlib


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def execute_command(command):
    with stdoutIO() as s:
        try:
            exec(command)
            return s.getvalue()
        except:
            return 'ERROR'


class GameServer(object):
    def __init__(self):
        self.server = None
        # dictionary containing {<username>:<player gameobject id>, ...}
        self.known_users = {}

        # que of messages to be broadcasted to other players, list of tuples containing message,
        # target playerid, and original playerid
        self.broadcast_que = []

        # TEMP TODO Create Hub room
        self.hub_room = create_room_from_template('gameobjects/room/template.rm')

    def server_start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', 4000))
        # Kill any zombie connection:
        # ps - fA | grep python
        server.listen(5)
        self.server = server
        atexit.register(self.server_stop)

    def server_stop(self):
        if self.server:
            self.server.close()
            self.server = None

    def get_clients(self):
        if not self.server:
            self.server_start()

        clients = []
        Connections, wlist, xlist = select.select([self.server], [], [], 0.05)

        for Connection in Connections:
            client, Informations = Connection.accept()
            clients.append(client)

        return clients

    def listen(self, clients):
        try:
            clients_list, wlist, xlist = select.select(clients, [], [], 0.05)
        except select.error:
            pass
        else:
            pass
            for client in clients_list:
                # Send text broadcasts from other users
                request = client.recv(1024)
                if request:
                    request = pickle.loads(request)
                    if request == 'broadcast?':
                        data = pickle.dumps({'broadcast': self.get_broadcast_message(request[0])})
                        print(data)
                        client.send(data)
                    else:
                        response = self.decode_and_respond(request)
                        response = pickle.dumps(response)
                        client.send(response)
                        client.close()
                        return

                # Send updated room instance (big data)
                request = client.recv(256000)
                if request:
                    data = pickle.loads(request)
                    print(data)
                    response = self.decode_and_respond(data)
                    print(response)
                    response = pickle.dumps(response)
                    client.send(response)
                client.close()

    def decode_and_respond(self, data):
        if 'login:' in data[1]:
            # TODO:
            items = data[1].split()
            playername = items[0].split(':')[1]
            username = items[1].split(':')[1]
            password = items[2].split(':')[1]

            if username not in self.known_users.keys():
                # find player json matching playername, make sure username and password correct
                player = self.load_player_from_json(playername, username, password)

                # get player object id
                playerid = player.id
                self.known_users[username] = playerid

                # put player in starting location
                room_instance = get_room_from_uniquename('dk_hallway1')
                # TODO: non default values here please
                coords = (10, 10)  # Get starting coordinates
                add_lifeform_to_room(playerid, room_instance, coords)

                # respond to client with playerid and roominstance
                response = [playerid, room_instance]

                # Debug print
                for k, lifeform in room_instance.lifeforms.items():
                    print('gameobjectid: {0} room_index: {1} lifeform_name: {2}'.format(lifeform.id, k, lifeform.name))

            else:
                response = 'User {0} already connected!'.format(username)

        elif 'say:' in data[1]:
            # Dialogue message to be broadcasted to all players
            self.add_to_broadcast_que(data[0], data[1])

        else:
            # Execute cli command from client
            r = execute_command(data[1])
            # Return updated room of player instance
            response = get_room_from_lifeform(data[0])
        return response

    def load_player_from_json(self, playername, username, password):
        # TODO: Add credentials check and non default lifeform value
        print('Going to load user with: playername: {0}, username: {1} password: {2}'.format(playername,
                                                                                             username, password))
        return load_user(playername, username, password)

    def add_to_broadcast_que(self, originalplayerid, message):
        for username, playerid in self.known_users.items():
            if playerid != originalplayerid:
                self.broadcast_que.append((message, originalplayerid, playerid))

    def get_broadcast_message(self, playerid):
        message_list = [message[0] for message in self.broadcast_que if message[2] == playerid]
        return message_list


if __name__ == '__main__':
    a = GameServer()
    while True:
        a.listen(clients=a.get_clients())
#
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(('', 4000))
# server.listen(5)
#
#
# while True:
#     clients = []
#     Connections, wlist, xlist = select.select([server], [], [], 0.05)
#
#     for Connection in Connections:
#         client, Informations = Connection.accept()
#         clients.append(client)
#     try:
#         clientsList, wlist, xlist = select.select(clients, [], [], 0.05)
#     except select.error:
#         pass
#     else:
#         for clientInList in clientsList:
#             # data = clientInList.recv(256000)
#             # data = pickle.loads(data)
#             # print(data)
#             # data = "Welcome"
#             # data = pickle.dumps(data)
#             # clientInList.send(data)
#             request = clientInList.recv(256000)
#             if request:
#                 data = pickle.loads(request)
#                 if data == 'give me a class':
#                     response = pickle.dumps(Thingy('Mike'))
#                     clientInList.send(response)
#             clientInList.close()
# server.close()
