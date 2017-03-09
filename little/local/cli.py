from game_locals import *
from mp.client import ServerResponseError


# TODO : Add emotes!


class CliParser(object):
    def __init__(self, game):
        self.game = game
        self.hero = self.game.hero
        self.inputlog = self.game.inputlog
        self.out_going_message = None

    def parse(self, msgvalue):
        # try:
        self.out_going_message = msgvalue
        if msgvalue.split()[0] in ['/t', '/tell', '/w', '/whisper']:
            target_player = msgvalue.split()[1]
            if target_player != self.game.charactername:
                message = '{0}: {1}'.format(self.hero.charactername, ' '.join(msgvalue.split()[2:]))
                try:
                    self.game.client.send('tell', {'message': message, 'target': target_player})
                    self.inputlog.add_line(message, TELL_COLOR)
                except ServerResponseError:
                    self.inputlog.add_line('Player not logged in.', SYSTEM_COLOR)
            else:
                self.inputlog.add_line('Talking to yourself again?', SYSTEM_COLOR)

        elif msgvalue.startswith('/set'):
            if len(msgvalue.split()) == 3:
                attribute = msgvalue.split()[1]
                value = msgvalue.split()[2]
                if value.isdigit():
                    value = int(value)
                if hasattr(self.hero, attribute):
                    setattr(self.hero, attribute, value)
                    self.inputlog.add_line('System: Set {0} to {1}'.format(attribute, value), SYSTEM_COLOR)
                else:
                    self.inputlog.add_line('System: {0} unknown attribute'.format(attribute), SYSTEM_COLOR)
            else:
                self.inputlog.add_line('Help: set <attribute> <value>')

        elif msgvalue.startswith('/who'):
            lifeforms = self.current_room.lifeforms
            for id, lifeform in lifeforms.items():
                self.inputlog.add_line('{0} : {1}'.format(id, lifeform.name), SYSTEM_COLOR)

        elif msgvalue.startswith('/get'):
            if len(msgvalue.split()) == 3:
                instance = msgvalue.split()[1]
                attribute = msgvalue.split()[2]
                value = getattr(eval(instance), attribute)
                self.inputlog.add_line(str(value), SYSTEM_COLOR)
            else:
                self.inputlog.add_line('Help: get <instance> <attribute>', SYSTEM_COLOR)

        elif msgvalue.startswith('/eval'):
            result = eval(msgvalue.replace('eval', '').lstrip())
            self.inputlog.add_line(str(result))

        elif msgvalue.startswith('/exec'):
            exec (msgvalue.replace('exec', '').lstrip())

        elif '/quit' == msgvalue.split()[0].lower():
            self.game.running = False

        elif '/camera' == msgvalue.split()[0].lower():
            self.hero.camera.spd = int(msgvalue.split()[1])

        elif '/debug' == msgvalue.split()[0].lower():
            global DEBUG_MODE
            if msgvalue.split()[1].lower() == 'on':
                DEBUG_MODE = True
            else:
                DEBUG_MODE = False

        else:
            # This is a /say command, visible to all players in room, and directed toward target NPC if selected
            target = self.hero.tgh.target
            if target:
                id = target['id']
            else:
                id = None
            message = '{0}: {1}'.format(self.game.client.charactername, msgvalue)
            self.game.client.send('say', {'message': message, 'id': id})
        # except:
        #     self.inputlog.add_line('Some unknown error occurred', SYSTEM_COLOR)
