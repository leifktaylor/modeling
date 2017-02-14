import socket, select, pickle
import atexit
import time


class Thingy(object):
    def __init__(self, name='Harold'):
        self.name = name


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
                    username = data[0][0]
                    password = data[0][1]
                    command = data[1]
                    print('Username: {0}, Password: {1}, Request: {2}'.format(username, password, command))
                    response = self.decode_and_respond(command)
                    client.send(pickle.dumps(response))
                client.close()

    def decode_and_respond(self, data):
        action = self.parse_request(data)
        # Then do the action server side
        # Then return that action's output to the client

        # temp
        return action

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
