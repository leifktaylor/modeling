from __future__ import print_function

import asyncore
import collections
import logging
import socket
import pickle
import atexit


MAX_LENGTH = 256000


class Cow(object):
    def __init__(self, name='Fretta'):
        self.name = name


class RemoteClient(asyncore.dispatcher):

    """Wraps a remote client socket."""

    def __init__(self, host, socket, address):
        asyncore.dispatcher.__init__(self, socket)
        self.host = host
        self.outbox = collections.deque()

    def say(self, message):
        message = pickle.dumps(message)
        self.outbox.append(message)

    def handle_read(self):
        client_message = self.recv(MAX_LENGTH)
        client_message = pickle.loads(client_message)
        self.host.broadcast(client_message)

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        # if len(message) > MAX_MESSAGE_LENGTH:
        #     raise ValueError('Message too long')
        self.send(message)


class Server(asyncore.dispatcher):

    log = logging.getLogger('Server')

    def __init__(self, address=('127.0.0.1', 4000)):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(5)
        self.remote_clients = []

    def handle_accept(self):
        socket, addr = self.accept() # For the remote client.
        print('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, socket, addr))

    def handle_read(self):
        print('Received message: %s', self.read())

    def broadcast(self, message):
        print('Broadcasting message: %s', message)
        for remote_client in self.remote_clients:
            remote_client.say(message)
            remote_client.handle_write()


class Client(asyncore.dispatcher):

    def __init__(self, host_address, name):
        asyncore.dispatcher.__init__(self)
        self.log = logging.getLogger('Client (%7s)' % name)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        print('Connecting to host at %s', host_address)
        self.connect(host_address)
        self.outbox = collections.deque()

    def say(self, message):
        message = pickle.dumps(message)
        self.outbox.append(message)
        print('Enqueued message: %s', message)

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        self.send(message)

    def handle_read(self):
        message = self.recv(MAX_LENGTH)
        message = pickle.loads(message)
        return message

#
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     print('Creating host')
#     server = Server()
#     print('Creating clients')
#     alice = Client(server.getsockname(), 'Alice')
#     bob = Client(server.getsockname(), 'Bob')
#     alice.say('Hello, everybody!')
#     print('Looping')
#     asyncore.loop()