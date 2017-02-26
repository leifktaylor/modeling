import socket, pickle
import atexit
import json
import select
import sys

from retrying import retry


class PacketSizeMismatch(Exception):
    pass


class GameClient(object):
    """
    Request is issued in the following format:
    {'username': <username>, 'charactername': <charactername>, 'password': <password>,
    'request': <cli_command>, 'args': []}

    Cli commands that can be sent to server --> Method called on server by RemoteClient class
    (remember to also pass list of 'args')
    
    'logout'                -->  logout()
    'move'                  -->  move(coords) # coords is a list like [x, y]  Updates server-side player location
    'target'                -->  target(targetid)
    'say'                   -->  say(targetid, dialogue)
    'ooc'                   -->  ooc(dialogue)
    'use_item'              -->  use_item(itemid)
    'equip_item'            -->  equip_item(self, itemid)
    'unequip_item'          -->  unequip_item(self, itemid)
    'add_item'              -->  add_item(self, itemid)
    'drop_item'             -->  drop_item(self, itemid)
    'give_item'             -->  give_item(itemid, targetid)
    'cast'                  -->  cast(self, spellid)
    'attack'                -->  attack(self, targetid)
    'update_coords'         -->  update_coords(self)
    'update_gameobjects'    -->  update_gameobjects(self)
    'change_room'           -->  change_room(self, roomname)

    """
    def __init__(self, ip='127.0.0.1', charactername='Mike', username='leif', password='mypw'):
        # Character is the unique character name on server
        self.charactername = charactername
        self.playerid = None
        self.current_room = None

        # Gameplay attributes
        self.target = None

        self.ip = ip
        self.password = password
        self.username = username
        self.server = None

        # Incoming broadcast from server
        self.incoming_broadcast = None

    def login(self):
        """
        Create character instance on the server.
        Server will send response containing {..., 'playerid': <someid>, 'current_room': <room_instance>}
        :return:
        """
        response = self.send(self._request('login', []))
        self.verify_response(response)
        print('Response from server:\n{0}'.format(response))
        self.playerid = response['response']['playerid']
        self.current_room = response['response']['current_room']
        return response

    def verify_response(self, response):
        """
        Verifies that response from server is valid.
        Will raise error if response invalid
        :param response: dictionary like {'status': <rc>, 'response': <response object>}
        :return:
        """
        if {'status', 'response'} == set(response.keys()):
            if response['status'] == 0:
                return 0
            else:
                raise RuntimeError('Server command failed with returncode: {0}'.format(response['status']))
        else:
            raise RuntimeError('Response from server is malformed!\n{0}'.format(response))

    def _request(self, request, args):
        """
        Form request dictionary to be pickled and sent to server.
        Convert request, and args to:
        {'username': 'someuser', 'password': 'mypw', 'charactername': 'Zorax', 'request': request, 'args', args}

        :param request: string like 'login' or 'attack'
        :param args: list of arguments like [itemid, targetid]
        :return: dictionary like example above
        """
        request = {'username': self.username, 'password': self.password, 'charactername': self.charactername,
                   'request': request, 'args': args}
        return request

    def send_command(self, request, args):
        return self.send(self._request(request, args))

    # @retry(stop_max_attempt_number=10)
    def send(self, request):
        """
        Request format must be like:
            {'charactername': 'Madaar', 'username': 'Nat', 'password': 'mypw', 'request': 'say', 'args': ['hello!']}
        :param request: dictionary like example above
        :return: payload from server
        """
        # Bounce the server
        self.disconnect()
        print('****** Starting Request   *******')
        self.connect(ip=self.ip)
        print('Connected')
        print('Sending request to server: {0}'.format(str(request)))
        self.server.send(pickle.dumps(request))

        # Receive buffer size of response from server
        try:
            buffer_size = self.receive_packet(128)
            if buffer_size is not None:
                print('--Received buffer size from server: {0}'.format(buffer_size))
            else:
                raise RuntimeError('Did not receive buffer size from server!')
        except socket.error:
            print(socket.error.message)
            self.disconnect()
            raise

        # Send confirmation to server that we are ready to receive payload
        if isinstance(buffer_size, int):
            self.server.send(pickle.dumps(buffer_size))
        else:
            self.server.send(pickle.dumps(-1))
            self.disconnect()
            raise

        # Receive data payload from server
        print('--Listening for payload...')
        payload = self.receive_packet(buffer_size, raise_error=True)
        if not payload:
            print('--Payload not found, retrying')
            raise RuntimeError('Did not receive payload from server')
        else:
            self.disconnect()
            print('****** Request Successful *******')
            return payload

    def receive_packet(self, buffer_size, raise_error=False):
        print('Expecting packet size: {0}'.format(buffer_size))
        packet = self.server.recv(buffer_size)
        actual_size = sys.getsizeof(packet)
        print('Actual packet size: {0}'.format(actual_size))
        if raise_error:
            if actual_size != buffer_size:
                self.disconnect()
                print('Packet size mismatch has occured: Expected {0}, Got: {1}'.format(buffer_size, actual_size))
                raise PacketSizeMismatch('Expected size: {0}, Actual size: {1}'.format(buffer_size, actual_size))
        if packet:
            data = pickle.loads(packet)
            print('received the following data: {0}'.format(data))
            return data
        else:
            print('Packet empty, returning None')
            return None

    def connect(self, ip):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((ip, 4000))
        self.server = server
        atexit.register(self.disconnect)

    def disconnect(self):
        if self.server:
            print('--Disconnected')
            self.server.close()
            self.server = None
