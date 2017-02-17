from mp.server import *
a = GameServer()
while True:
	a.listen(a.get_clients())
