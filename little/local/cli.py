class CliParser(object):
    def __init__(self, game):
        self.game = game
        self.hero = self.game.hero
        self.inputlog = self.game.inputlog

        self.out_going_message = None

    def parse(self, msgvalue):
        try:
            # r = a.send(msgvalue)
            self.inputlog.add_line(msgvalue)
            self.out_going_message = msgvalue
            if 'set' in msgvalue:
                if len(msgvalue.split()) == 3:
                    attribute = msgvalue.split()[1]
                    value = msgvalue.split()[2]
                    if value.isdigit():
                        value = int(value)
                    if hasattr(self.hero, attribute):
                        setattr(self.hero, attribute, value)
                        self.inputlog.add_line('System: Set {0} to {1}'.format(attribute, value))
                    else:
                        self.inputlog.add_line('System: {0} unknown attribute'.format(attribute))
                else:
                    self.inputlog.add_line('Help: set <attribute> <value>')
            elif 'who room' in msgvalue:
                lifeforms = self.current_room.lifeforms
                for id, lifeform in lifeforms.items():
                    self.inputlog.add_line('{0} : {1}'.format(id, lifeform.name))
            elif 'get' in msgvalue:
                if len(msgvalue.split()) == 3:
                    instance = msgvalue.split()[1]
                    attribute = msgvalue.split()[2]
                    value = getattr(eval(instance), attribute)
                    self.inputlog.add_line(str(value))
                else:
                    self.inputlog.add_line('Help: get <instance> <attribute>')
            elif 'eval' in msgvalue:
                result = eval(msgvalue.replace('eval', '').lstrip())
                self.inputlog.add_line(str(result))
            elif 'exec' in msgvalue:
                exec (msgvalue.replace('exec', '').lstrip())
            elif 'quit' == msgvalue.split()[0].lower():
                self.game.running = False
            elif 'camera' == msgvalue.split()[0].lower():
                self.hero.camera.spd = int(msgvalue.split()[1])
            elif 'debug' == msgvalue.split()[0].lower():
                global DEBUG_MODE
                if msgvalue.split()[1].lower() == 'on':
                    DEBUG_MODE = True
                else:
                    DEBUG_MODE = False
        except:
            self.inputlog.add_line('Some unknown error occurred')
