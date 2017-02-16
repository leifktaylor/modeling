import socket, select, pickle
import atexit
import time
from gameobjects.gameobject import get_object_by_id, get_room_from_lifeform
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
        # dictionary containing players and their permissions
        self.players = {}

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
            for client in clients_list:
                request = client.recv(1024)
                if request:
                    data = pickle.loads(request)
                    print(data)
                    response = self.decode_and_respond(data)
                    client.send(pickle.dumps(response))
                client.close()

    def decode_and_respond(self, data):
        if 'login:' in data[1]:
            # TODO:
            items = data[1].split()
            playername = items[0].split(':')[1]
            username = items[1].split(':')[1]
            password = items[1].split(':')[1]
            # find player json matching playername, make sure username and password correct

            # instantiate player and place in player's current room

            # return object id to client and room instance
            response = [5, room_instance]
        else:
            # Execute cli command from client
            r = execute_command(data[1])
            # Return updated room of player instance
            response = get_room_from_lifeform(data[0])
        return response

    def parse_request(self, request):
        """
        This method decodes:
        '<player_name>:<request_clause>'

        INFO clauses:
        'room' - return room instance
        'me' - return character instance
        'id:<number>' - return instance with id

        TASK clauses (if 'me' is substituted for an id, current player is assumed):
        'function <function_name> <args> <kwargs>' - use function with given arguments
        'method <id> <method_name> <args> <kwargs>' - class with id will use method with given arguments

        # Debug only clauses
        'ch <id> <class_attribute> <value>' - change attribute of given id to given value


        :param data:
        :return:
        """
        return 'you just said: {0}'.format(request)


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
#             # data = clientInList.recv(1024)
#             # data = pickle.loads(data)
#             # print(data)
#             # data = "Welcome"
#             # data = pickle.dumps(data)
#             # clientInList.send(data)
#             request = clientInList.recv(1024)
#             if request:
#                 data = pickle.loads(request)
#                 if data == 'give me a class':
#                     response = pickle.dumps(Thingy('Mike'))
#                     clientInList.send(response)
#             clientInList.close()
# server.close()
