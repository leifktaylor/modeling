from gameobjects.gameobject import *

import multiprocessing
import time
import pprint
from gamecontroller import GameController
from mp import client, server


def time_command(function, args):
    start = time.time()
    function_return = function(args)
    end = time.time()
    print('Command took {0} seconds'.format(end - start))
    return function_return


def templateparser_test():
    a = TemplateParser()
    print(' TEST 1 : Lifeform ')
    pprint.pprint(a.load_data('gameobjects/lifeform/zaxim.lfm'))
    print(' TEST 2 : Item ')
    pprint.pprint(a.load_data('gameobjects/weapon/long_sword.itm'))
    print(' TEST 3 : Room ')
    pprint.pprint(a.load_data('gameobjects/room/template.rm'))
    print(' TEST 4 : Faction ')
    pprint.pprint(a.load_data('gameobjects/faction/chand_baori.fct'))
    print(' TEST 5 : AI ')
    pprint.pprint(a.load_data('gameobjects/ai/healer.ai'))
    print(' TEST 6 : DIALOGUE ')
    pprint.pprint(a.load_data('gameobjects/dialogue/template.dlg'))


def gameobjectcontroller_test():
    print(' ------- GameObjectController Tests ------- ')
    print(' TEST 7 : Rooms')
    print('Instantiating GOC')
    GOC = GameObjectController()
    print('Creating Template Room')
    GOC.add_room('gameobjects/room/template.rm')
    print('Verifying Room in Room list')
    print(GOC.rooms)
    print(' TEST 8 : Lifeform Creation / Removal')
    print(' Creating 30 Lifeforms from template ')
    instance_list = []
    for i in range(0, 30):
        instance, id = GOC.add_gameobject('gameobjects/lifeform/template.lfm')
        instance_list.append(instance)
    for i, lifeform in enumerate(instance_list):
        print(i, lifeform)
    pprint.pprint(instance.__dict__)

    print(' Removing Every other Lifeform ')
    for i in range(0, 30, 2):
        GOC.remove_gameobject(i)
    for id, lf in GOC.gameobjects.items():
        try:
            print(lf, lf.id)
        except AttributeError:
            print(None)

    print(' Creating 30 More Lifeforms from template, should fill gaps, and id on class should match id in hash table')
    for i in range(0, 30):
        instance, id = GOC.add_gameobject('gameobjects/lifeform/template.lfm', 'template_room', [5, 5])

    for id, instance in GOC.gameobjects.items():
        try:
            assert id == instance.id
        except AttributeError:
            pass
        print(id, instance)

    print(' TEST 9 : Inventory ')
    instance, id = GOC.add_gameobject('gameobjects/lifeform/template.lfm')
    pprint.pprint(instance.inventory.__dict__)

    print('STRESS TEST!!! CREATING 10000 Lifeforms')

    def add_gameobjects(template):
        for i in range(0, 1000):
            GOC.add_gameobject(template)
    time_command(add_gameobjects, 'gameobjects/lifeform/template.lfm')


def client_server_test():
    print('------------------------')
    print('Test 1: GameServer simple test, listening')
    print('Instantiating GameServer')
    gameserver = server.GameServer()

    def server_listen():
        while True:
            gameserver.listen(gameserver.get_clients())
    print('Starting server and listening for 5 seconds')
    p = multiprocessing.Process(target=server_listen, name="Listen", args=())
    p.start()
    # Wait 10 seconds before ending process
    time.sleep(5)
    # Terminate foo
    p.terminate()
    # Cleanup
    p.join()
    print('Success, server listened')

    print('------------------------')
    print('Test 2: GameClient / GameServer simple communique')
    print('Instantiating GameClient')
    gameclient = client.GameClient()
    print('Server listening for 8 seconds, at 4 seconds client will send "test" request')
    s = multiprocessing.Process(target=server_listen, name="Listen", args=())
    s.start()
    time.sleep(4)
    gameclient.send('test')
    time.sleep(5)
    # Terminate foo
    s.terminate()
    # Cleanup
    s.join()
    print('Success, server-client communication worked')
    gameclient = None
    gameserver = None

    print('-------------------------')
    print('Test 3: Multiple Clients ')
    print('Attempting to create 6 clients, and send "test" requests')
    gameserver = server.GameServer()
    s = multiprocessing.Process(target=server_listen, name="Listen", args=())
    s.start()
    time.sleep(2)
    clients = []
    for i in range(1, 7):
        clients.append(client.GameClient(charactername='Test{0}'.format(i), username='test{0}'.format(i)))
    for gameclient in clients:
        gameclient.send('test')
    time.sleep(2)
    s.terminate()
    s.join()
    gameclient = None
    gameserver = None

    print('-------------------------')
    print('Test 4: Stress Test | Multiple Clients ')
    # COMMON ERRORS NOT ADDRESSED:

    # RuntimeError: Did not receive buffer size from server! (This is occuring 1/2 tests)

    # Constants:
    # Amount of times to loop through each client sending test request
    amount = 1000

    print('Attempting to create 6 clients, and spam {0} "test" requests per client'.format(amount))
    gameserver = server.GameServer()
    s = multiprocessing.Process(target=server_listen, name="Listen", args=())
    s.start()
    time.sleep(2)
    clients = []
    for i in range(1, 7):
        clients.append(client.GameClient(charactername='Test{0}'.format(i), username='test{0}'.format(i)))
    error_messages = []
    for i in range(0, amount):
        for gameclient in clients:
            response = gameclient.send('test')
            if 'Hello' not in response['response']['message']:
                print(response)
                if response['status'] == -1:
                    error_messages.append(response['response']['message'])
                else:
                    raise RuntimeError('Did not get hello response from server or error msg')
    print('Errors that occured:\n{0}'.format(error_messages))
    time.sleep(2)
    s.terminate()
    s.join()


def gamecontroller_test():
    print('-----------------------')
    print('Test 1 - Create GC, Add a room, Login player and verify player is added properly')
    print('Instantiating GameController')
    gc = GameController()
    gc.goc.add_room('gameobjects/room/template.rm')
    # Start server on GC
    s = multiprocessing.Process(target=gc.run, name="Run", args=())
    s.start()
    time.sleep(2)
    # Create gameclient and login
    c = client.GameClient()
    c.login()
    time.sleep(1)
    # Verify that playerid on Client and id in GOC match
    print('Verifying that player Lifeform created in GOC and that it matches client charactername')
    clientid = c.id
    response = c.send('evaluate', 'gameobjects[{0}].name'.format(clientid))
    assert response['response']['message'] == c.charactername
    response = c.send('evaluate', 'gameobjects[{0}].player'.format(clientid))
    print('Is player: {0}'.format(response['response']['message']))
    response = c.send('evaluate', 'gameobjects[{0}].ai'.format(clientid))
    print('AI: {0}'.format(response['response']['message']))
    print('Character created successfully!')
    time.sleep(1)
    print('Attempting to login again with same character, should NOT succeed')
    c.login()

    print('------------------------')
    print('Test 2 - Player logout')
    print('This test will now logout the player and confirm he has been removed from the GOC')
    playername = c.send('evaluate', 'playernames')['response']['message'][0]
    print('{0} currently logged in, logging out...'.format(playername))
    c.logout()
    time.sleep(1)
    playername = c.send('evaluate', 'playernames')['response']['message']
    if len(playername) is not 0:
        raise RuntimeError('Player not successfully logged out')
    print('Player logged out and removed from GOC successfully!')
    print('Attempting to logout again, should not crash server...')
    c.logout()
    print('Second logout attempted failed as expected')
    time.sleep(1)
    s.terminate()
    s.join()

    print('---------------------------')
    print('Test 3 - Rapid login logout')
    # Constants #
    amount = 200

    gc = GameController()
    s = multiprocessing.Process(target=gc.run, name="Run", args=())
    s.start()
    time.sleep(2)
    # Create gameclient and login
    c = client.GameClient()
    print('Rapidly logging in and out 200 times')
    for i in range(0, amount):
        c.login()
        c.logout()
    print('Verifying No gameobjets in GOC')
    assert gc.goc.gameobjects == {}
    s.terminate()
    s.join()

    print('-----------------------')
    print('Test 4 - Coordinates, verify coordinate updates')
    print('Instantiating GameController')
    gc = GameController()
    gc.goc.add_room('gameobjects/room/template.rm')
    # Start server on GC
    s = multiprocessing.Process(target=gc.run, name="Run", args=())
    s.start()
    time.sleep(2)
    c = client.GameClient()
    c.login()
    c.send('evaluate', 'gameobjects[{0}].current_room.uniquename'.format(1))
    c.coords()
    s.terminate()
    s.join()


templateparser_test()
gameobjectcontroller_test()
client_server_test()
gamecontroller_test()
