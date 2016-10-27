class Monster(object):
    def __init__(self):
        self.name = "Hanky"
        str = 5
        hp = 15

    def give_name(self, monster_name):
        self.name = monster_name

    def print_stats(self):
        print("{0}'s Stats:".format(self.name))
        print("HP: {0}, STR: {0}".format(self.hp, self.str))

    def getPowers(self, val1, val2, val3):
        dict = {'first': val1, 'second': val2, 'third': val3}
        return dict

    if __name__ == '__main__':
        a = Monster()
        a.give_name("Artooox")
        a.print_stats()
        b = a.getPowers("Stinky Breath", "Orange Eyes", "Giant Nose")
        print(b['first'])
