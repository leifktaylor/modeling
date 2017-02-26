import socket, select, pickle
import atexit
import time
from gameobjects.gameobject import get_object_by_id, get_room_from_lifeform
from gameobjects.gameobject import load_user
from gameobjects.gameobject import create_room_from_template, create_lifeform_from_template


# from gameobjects.gameobject import get_coords_map
import json
import sys
import pytmx
import StringIO
import contextlib

from retrying import retry
import random

# constants
USER_LIST = 'mp/users/users.json'
TILE_SIZE = 8
BUFFER_SIZE = 1024
HUB_ROOM = 'gameobjects/room/template.rm'
VERBOSE = False


class RemoteClient(object):
    """
    Represents remote client connection and relevant data.
    Methods will change gameobject details and send relevant data back to actual remote client

        Request from actual remote client is in format:
        {'username': <username>, 'charactername': <charactername>, 'password': <password>,
        'request': <cli_command>, 'args': [list, of, args]}

        'request' possible values
        Cli command from client     -->  RemoteClient method

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
    def __init__(self, playerid, lifeform, username, password, charactername):
        self.lifeform = lifeform
        self.playerid = playerid
        self.username = username
        self.password = password
        self.charactername = charactername

        # TODO: This is a default value and should be changed
        self.current_room = HUB_ROOM

        # Pointer to player's lifeform gameobject instance

        # Cli command  -->  Method mapping
        self.request_matrix = {'move': self.move, 'target': self.change_target,
                               'say': self.say, 'ooc': self.ooc, 'whisper': self.whisper,
                               'use_item': self.use_item, 'equip_item': self.equip_item,
                               'unequip_item': self.unequip_item, 'add_item': self.add_item,
                               'drop_item': self.drop_item, 'give_item': self.give_item,
                               'cast': self.cast, 'attack': self.attack, 'logout': self.logout,
                               'update_coords': self.update_coords,
                               'update_gameobjects': self.update_gameobjects,
                               'change_room': self.change_room}

    def get_payload(self, request):
        """
        This is the cornerstone of how this madness all works.

        Request is received from client, like:
            {...., 'request': <cli_command>, 'args': [list, of, arguments]}
        'request' value is the name of a method (see self.request_matrix)
        'args' are the arguments passed to that method

        The method is executed on the server, and a payload of relevant data is constructed.

        The return value of the executed method is returned from here, and then it should be passed on
            to the client.
        :param request:
        :return: payload to be sent to client
        """
        try:
            resp = self.request_matrix[request['request']](*request['args'])
            print('Response to client: {0}'.format(resp))
        except KeyError:
            resp = {'status': -1,
                    'response': 'Invalid CLI command, valid commands are:\n{0}'.format(str(self.request_matrix))}
        return resp

    # The following methods do:
    # - Issue command on serverside lifeform instance(s)
    # - Get return from that command
    # - Broadcast relevant information to any number of other clients
    # - Return payload to be sent to client

    def change_room(self, roomname):
        lifeform_return = self.lifeform.change_room(roomname)

    def change_target(self, targetid):
        lifeform_return = self.lifeform.change_target(targetid)

    def cast(self, spellid=None, targetid=None):
        lifeform_return = self.lifeform.cast(spellid, targetid)

    def attack(self, targetid):
        lifeform_return = self.lifeform.attack(targetid)

    def equip_item(self, id):
        lifeform_return = self.lifeform.inventory.equip_item(id)

    def unequip_item(self, equip_slot):
        lifeform_return = self.lifeform.inventory.unequip_item(equip_slot)

    def add_item(self, id):
        lifeform_return = self.lifeform.inventory.add_item(id)

    def drop_item(self, id):
        lifeform_return = self.lifeform.inventory.drop_item(id)

    def use_item(self, id):
        lifeform_return = self.lifeform.inventory.use_item(id)

    def give_item(self, id, targetid):
        lifeform_return = self.lifeform.give_item(id, targetid)

    def say(self, dialogue, targetid):
        lifeform_return = self.lifeform.say(dialogue, targetid)

    def logout(self):
        pass

    def move(self, coords):
        """
        From client --> Update co-ordinates of Serverside player
        :return:
        """
        print('{0}: Moving to {1}'.format(self.playerid, str(coords)))
        self.lifeform.coords = coords
        return {'status': 0, 'response': 'Moved {0} to {1}'.format(self.lifeform.id, self.lifeform.coords)}

    def ooc(self, dialogue):
        pass

    def whisper(self, dialogue, targetid):
        pass

    def update_coords(self):
        """
        Send to client --> List of all lifeforms in room
        :return:
        """
        return {'status': 0, 'response': self.lifeform.current_room.lifeforms}

    def update_gameobjects(self):
        """
        *expensive* Send to client --> Update gameobjects in current room
        :return:
        """
        pass

    def update_target(self):
        """
        Send to client --> Recent gameobject instance of target
        :return:
        """
        pass


class GameServer(object):
    def __init__(self):
        self.server = None
        # dictionary containing {<charactername>:<player gameobject id>, ...}
        self.remote_clients = {}
        # contains pointers to all the rooms currently instantiated
        # {<path/to/template.rm>: 'instance': <room_instance>, 'tmx_map': <pytmx TiledMap instance>}
        self.rooms = {}

        with open(USER_LIST, 'r') as f:
            self.user_data = json.load(f)

        # que of messages to be broadcasted to other players, list of tuples containing message,
        # target playerid, and original playerid
        self.broadcast_que = []

    def server_start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    def logout_client(self, request):
        """
        Delete player instance from room and delete remote client instance from remote_clients dict
        :param request: dictionary containing 'username', 'password' and 'charactername'
        :return:
        """
        charactername = request['charactername']
        username = request['username']
        password = request['password']

        with open('mp/users/{0}'.format(USER_LIST), 'r') as f:
            userdata = json.load(f)
            f.close()
        current_user = userdata[username]
        if current_user['password'] != password:
            return {'status': -1, 'response': 'Password was invalid, or character/user does not exist'}

        # check that user is logged in
        if charactername not in self.remote_clients.keys():
            print('Cannot logout, user is not logged in')
            return {'status': -1, 'response': 'User is not logged in'}
        # save character
        # todo All this stuff
        # logout character

    def login_client(self, request):
        """
        Instantiate player gameobject and login client
        :param request: dictionary containing 'username', 'password' and 'charactername'
        :return:
        """
        charactername = request['charactername']
        username = request['username']
        password = request['password']
        print('Someone attempting to log in...')

        # Check that character isn't already logged in
        if charactername in self.remote_clients.keys():
            print('User is already logged in')
            return {'status': -1, 'response': 'Password was invalid, or character/user does not exist'}

        # Find player json matching charactername, make sure username and password correct and instantiate
        player = self.load_player_from_json(charactername, username, password)
        if player == -1:
            print('Password was invalid, or character/user does not exist')
            return {'status': -1, 'response': 'Password was invalid, or character/user does not exist'}

        # Create RemoteClient instance and add to self.remote_clients dictionary
        playerid = player.id
        self.remote_clients[charactername] = RemoteClient(playerid=playerid, lifeform=player, username=username,
                                                          password=password, charactername=charactername)

        # Put player in starting/current location
        # TODO: non default values here please ********
        print('Creating room instance')
        room = self.add_room(HUB_ROOM)['instance']
        player.current_room = room
        coords = (132, 132)
        # Add player to room
        room.add_lifeform_by_id(playerid, coords)

        # respond to client with playerid and roominstance
        print('Login successful on serverside, sending response to client...')
        response = {'status': 0, 'response': {'playerid': playerid, 'current_room': room}}
        return response

    def add_room(self, template):
        # Create the room instance and add to server's room list
        if template not in self.rooms.keys():
            print('Loading room from template: {0}'.format(template))
            new_room = create_room_from_template(template)
            print('Loading Tiled .tmx file: {0}'.format(new_room.tmx_map))
            tmx_map = pytmx.TiledMap(new_room.tmx_map)
            # Instantiate all lifeforms required by room tmx file
            print('Spawning lifeforms from pytmx TiledMap: {0}'.format(tmx_map))
            new_room = self.spawn_room_lifeforms(new_room, tmx_map)
            self.rooms[template] = {'instance': new_room, 'tmx_map': tmx_map}
        return self.rooms[template]
    
    def spawn_room_lifeforms(self, room_instance, tiledtmx):
        """
        Instantiates all lifeform objects by reading Tiled tmx map
        :param room_instance: instantiated room object
        :param tiledtmx: pytmx TiledMap instance
        :return: 
        """
        lifeforms = self.get_lifeforms(tiledtmx)
        print('Lifeforms loaded from tmx: {0}'.format(lifeforms))
        for lifeform in lifeforms:
            # Instantiate each lifeform and add to room
            instance = create_lifeform_from_template(lifeform['template'])
            instance.coords = [lifeform['x'] * TILE_SIZE, lifeform['y'] * TILE_SIZE]
            print('Spawned: {0}'.format(instance.name))
            room_instance.add_lifeform_by_id(instance.id, instance.coords)
        return room_instance

    def get_lifeforms(self, tiledtmx, layer=1):
        """
        Searches each tile of the map and grabs lifeforms from given layer

        Lifeforms require these specific custom properties (make them in Tiled editor):
            template: string: path to .lfm template
            spawn_time: int: length of respawn timer when killed, if set to None, will not respawn

        :param tiledtmx: pytmx TiledMap instance
        :param layer: map layer to search for lifeforms (default is 1)
        :return: list of dictionaries
        """
        lifeforms = []
        for y in range(0, tiledtmx.height):
            for x in range(0, tiledtmx.width):
                lifeform = tiledtmx.get_tile_properties(x, y, layer)
                if lifeform:
                    try:
                        lifeforms.append({'x': x, 'y': y, 'template': lifeform['template'],
                                         'spawn_time': lifeform['spawn_time']})
                    except KeyError:
                        print('Lifeform in tmx map missing required custom properties')
        return lifeforms

    def listen(self, clients):
        try:
            clients_list, wlist, xlist = select.select(clients, [], [], 0.05)
        except select.error:
            pass
        else:
            for client in clients_list:
                print('--Client conneted, listening...')
                request = self.receive_packet(client, BUFFER_SIZE)
                if request:
                    if request == -1:
                        print('--Client returned error, disconnecting')
                        client.close()
                    else:
                        try:
                            payload = self.process_request(request)
                        except RuntimeError:
                            payload = {'status': -1, 'response': 'Unable to process request, was it malformed?'}
                        payload_string = str(payload)
                        payload = pickle.dumps(payload)
                        buffer_size = sys.getsizeof(payload)
                        response = pickle.dumps(buffer_size)

                        if VERBOSE: print('--Sending buffer size: {0}'.format(buffer_size))
                        client.send(response)

                        # Wait for confirmation from client for buffer size
                        if VERBOSE: print('--awaiting client response to send payload')
                        client_response = self.receive_packet(client, 128)

                        if client_response:
                            if VERBOSE: print('--client response to send payload received:{0}'.format(client_response))
                            if client_response == buffer_size:
                                if VERBOSE: print('--Sending payload (size): {0}'.format(buffer_size))
                                if VERBOSE: print('--Sending payload data: {0}'.format(payload_string))
                                client.send(payload)
                            elif client_response == -1:
                                print('--Received error message from client')

                        # Client needs to confirm that it received payload

                print('Disconnecting from client')
                client.close()

    @staticmethod
    def receive_packet(client, buffer_size):
        packet = client.recv(buffer_size)
        if packet:
            data = pickle.loads(packet)
            if data == -1:
                return -1
            else:
                print('received data:\n{0}'.format(data))
                return data
        else:
            return None

    def process_request(self, request):
        # If request is in valid format
        if {'username', 'charactername', 'password', 'request', 'args'} == set(request.keys()):
            if self.authenticate_credentials(request):
                # Login request should be {..., 'request': 'login', ...}
                if request['request'] == 'login':
                    return self.login_client(request)
                # Logout request should be {..., 'request': 'logout', ...}
                elif request['request'] == 'logout':
                    return self.logout_client(request)
                # Verify that already logged in, and then process any other request type
                elif request['charactername'] in self.remote_clients.keys():
                    return self.remote_clients[request['charactername']].get_payload(request)
        else:
            raise RuntimeError('Request is not in valid format\n'
                               'should be dictionary with keys:\n '
                               '"username", "charactername", "password", "request", "args"')

    def authenticate_credentials(self, request):
        username = request['username']
        password = request['password']
        charactername = request['charactername']
        if username in self.user_data:
            if password == self.user_data[username]['password']:
                if charactername in self.user_data[username]['characters']:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def load_player_from_json(self, charactername, username, password):
        # TODO: Add credentials check and non default lifeform value
        print('Loading charactername: {0}, username: {1} password: {2}'.format(charactername, username, password))
        try:
            lifeform_instance = load_user(charactername, username, password)
        except:
            lifeform_instance = -1
        return lifeform_instance

    def add_to_broadcast_que(self, originalplayerid, message):
        # TODO: Deprecated.. fix this
        for username, playerid in self.known_users.items():
            if playerid != originalplayerid:
                broadcaster_name = get_object_by_id(originalplayerid).name
                message = '{0}: {1}'.format(broadcaster_name, message[4:])
                self.broadcast_que.append((message, originalplayerid, playerid))

    def get_broadcast_message(self, playerid):
        # TODO: Deprecated.. Fix this
        # Find messages for this player, and then clear them from the broadcast que
        message_list = [message[0] for message in self.broadcast_que if message[2] == playerid]
        indexes_to_drop = [i for i, message in enumerate(self.broadcast_que) if message[2] == playerid]
        for index in indexes_to_drop:
            try:
                self.broadcast_que.pop(index)
            except IndexError:
                print('Some message was lost...')
        return message_list

if __name__ == '__main__':
    a = GameServer()
    while True:
        a.listen_test(clients=a.get_clients())




    # Backup of Listen method
    # def listen_test(self, clients):
    #     try:
    #         clients_list, wlist, xlist = select.select(clients, [], [], 0.05)
    #     except select.error:
    #         pass
    #     else:
    #         for client in clients_list:
    #             request = self.receive_packet(client, BUFFER_SIZE)
    #
    #             if request:
    #                 if request == -1:
    #                     print('Client returned error, disconnecting')
    #                     client.close()
    #                 else:
    #                     # Here is where you generate the response, and determine its size
    #                     # First send its size to the client, then send the object
    #                     random_object = pickle.dumps(random.getrandbits(random.randint(1, 10000)))
    #                     buffer_size = sys.getsizeof(random_object)
    #                     response = pickle.dumps(buffer_size)
    #
    #                     print('Sending buffer size: {0}'.format(buffer_size))
    #                     client.send(response)
    #
    #                     # Wait for confirmation from client for buffer size
    #                     print('awaiting client response to send payload')
    #                     client_response = self.receive_packet(client, BUFFER_SIZE)
    #
    #                     if client_response:
    #                         if client_response == buffer_size:
    #                             print('Sending payload (size): {0}'.format(buffer_size))
    #                             client.send(random_object)
    #                         elif client_response == -1:
    #                             print('Received error message from client')
    #             client.close()


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
