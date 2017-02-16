import socket, pickle
import atexit


class GameClient(object):
    """

    Cli commands that can be sent to server:

    move <direction>
        (up, left, right, down)
    teleport <zone> <x> <y>

    attack <id>
    cast <id> <spell>

    equip_item <itemid>
    unequip_item <equip_slot>
    drop_item <itemid>
    add_item <itemid>
    trade_item <itemid> <targetid>
    use_item <itemid>

    """
    def __init__(self, playername=None, ip='127.0.0.1', username='admin', password='password'):
        # Character is the unique character name on server
        self.playername = playername
        self.playerid = None

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
        if not self.clisession:
            self.load_player_on_server()
        request = pickle.dumps([self.playerid, request])
        self.server.send(request)
        data = self.server.recv(1024)
        if data:
            data = pickle.loads(data)
        self.disconnect()
        return data

    def cli_to_python(self, cli_command):
        """
        Convert cli command like:
            'move right'
        To python command like:
            get_object_by_id(5).move('right')
        :param cli_command: valid cli command (see class docstring)
        :return: python command as string
        """
        method = cli_command.split()[0]
        if len(cli_command) > 1:
            args = ','.join([item if item.isdigit() else "'{0}'".format(item) for item in cli_command.split()][1:])
        else:
            args = ''
        final_command = 'get_object_by_id({0}).{1}({2})'.format(self.id, method, args)
        return final_command

    def load_player_on_server(self):
        # TODO
        # Send playername, username and password to server
        request = pickle.dumps([None, 'login:{0} username:{1} password:{2}'.format(self.playername,
                                                                                   self.username, self.password)])
        self.server.send(request)

        # Server queries list of json files and finds player, instantiates in game, and returns gameobject id, and
        # current room instance
        data = self.server.recv(1024)
        if data:
            data = pickle.loads(data)
        self.disconnect()

        # Server returns objectid of player instance
        self.playerid = data[0]

        # Cli session is created using player instance number


        # Game engine is activated, current room is instantiated and rendered

        # Player is granted control of character



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
