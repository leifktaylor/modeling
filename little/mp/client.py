import socket, pickle
import atexit
import sys


class PacketSizeMismatch(Exception):
    pass


class ServerResponseError(Exception):
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
    def __init__(self, ip='127.0.0.1', charactername='Zaxim', username='ken', password='mypw'):
        self.id = None

        self.ip = ip
        self.charactername = charactername
        self.password = password
        self.username = username
        self.server = None

        # Incoming broadcast from server
        self.incoming_broadcast = None

    def login(self):
        """
        Create character instance on the server.

        Server will send 'response' containing:
        {'id': id, 'coords': gameobject.coords, 'sprite': gameobject.graphic}, 'current_room': gameobject.current_room}
        :return:
        """
        response = self.send('login')
        try:
            self.id = response['response']['id']
        except KeyError:
            pass
        print('Response from server:\n{0}'.format(response))
        return response

    def logout(self):
        """ Logout character from server """
        response = self.send('logout')
        return response

    def _request(self, request, args=None):
        """
        Form request dictionary to be pickled and sent to server.
        Convert request, and args to:
        {'username': 'someuser', 'password': 'mypw', 'charactername': 'Zorax',
         'id': id, 'request': request, 'args': args}

        :param request: string like 'login' or 'attack'
        :param args: list of arguments like [itemid, targetid]
        :return: dictionary like example above
        """
        request = {'username': self.username, 'password': self.password, 'charactername': self.charactername,
                   'id': self.id, 'request': request, 'args': args}
        return request

    def send(self, request, args=None):
        """
        Request format must be like:
            {'charactername': 'Madaar', 'username': 'Nat', 'password': 'mypw', 'id': id,
             'request': 'say', 'args': ['hello!']}
        Payload will be received in the following format:
            {'status': 0, 'response': {'key': 'value', 'otherkey': 'value', ... } }
        :param request: dictionary like example above
        :return: payload from server
        """
        # TODO: This change will break things
        request = self._request(request, args)
        print('Request to be sent: {0}'.format(request))
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
            return {'status': -1, 'response': {'message': 'Socket error'}}

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
            if {'status', 'response'} == set(payload.keys()):
                if payload['status'] != 0:
                    raise ServerResponseError(payload['response']['message'])
                else:
                    return payload
            else:
                return {'status': -1, 'response': {'message': 'response from server malformed'}}

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
            print('--Socket closed')
            self.server.close()
            self.server = None
