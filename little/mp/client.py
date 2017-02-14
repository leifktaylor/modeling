import socket, pickle
import atexit


class Thingy(object):
    def __init__(self, name='Harold'):
        self.name = name


class GameClient(object):
    def __init__(self, ip='127.0.0.1', username='admin', password='password'):
        self.ip = ip
        self.password = password
        self.username = username
        self.server = None

    def connect(self, ip):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((ip, 4000))
        self.server = server
        atexit.register(self.disconnect)

    def disconnect(self):
        if self.server:
            self.server.close()
            self.server = None

    def send(self, request):
        if not self.server:
            self.connect(ip=self.ip)
        # Request is a list containing a tuple with username and password, and the request
        request = pickle.dumps([(self.username, self.password), request])
        self.server.send(request)
        data = self.server.recv(1024)
        if data:
            data = pickle.loads(data)
        self.disconnect()
        return data

# if __name__ == '__main__':
#     a = GameClient()
#     a.send('give me a class')

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.connect(('127.0.0.1', 4000))
#
# # while True:
# #     data = "I'm logged"
# #     data = pickle.dumps(data)
# #     server.send(data)
# #     data = server.recv(1024)
# #     data = pickle.loads(data)
# #     print(data)
#
# request = pickle.dumps('give me a class')
# server.send(request)
# data = server.recv(1024)
# data = pickle.loads(data)
# print(data.name)
#
# server.close()
