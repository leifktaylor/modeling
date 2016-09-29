
class Board(object):  
    def __init__(self, rows=3, columns=3, win_amt=3):
        self.directions = {'UP': (-1, 0), 'UR': (-1, 1), 'RT': (0, 1), 'DR': (1, 1),
                           'DN': (1, 0), 'DL': (1, -1), 'LT': (0, -1), 'UL': (-1, -1)}
        self.board = []
        self.win_amt = win_amt
        for i in range(0, rows):
            self.board.append([' ']*columns)

    def print_board(self):
        for row in self.board:
            print(row)

    def get_player_coordinates(self, graphic):
        """
        Returns a list of the y,x co-ordinates of all a player's
        moves.
        :param graphic: the player's 'graphic'
        :return: list of typles containing (y, x)
        """
        coord_list = []
        for y in range(0, len(self.board)):
            for x in range(0, len(self.board[0])):
                if graphic in self.board[y][x]:
                    coord_list.append((y, x))
        return coord_list

    def check_for_win_state(self, graphic):
        """
        Checks for win state of the given player graphic.

        :param coords:
        :param graphic:
        :return:
        """
        coord_list = self.get_player_coordinates(graphic)
        for coord in coord_list:
            for k, dir in self.directions.iteritems():
                # check length in dir
                if self.check_length(coord, dir, graphic) >= self.win_amt:
                    print('Player {0} Wins!'.format(graphic))
                    return True
        return False

    def check_length(self, coords, dir, graphic, count=0):
        """
        Returns the length of a players consecutive moves in a given direction.

        :param coords: (y, x) tuple of where to check from
        :param dir: (y, x) tuple of direction to check
        :param graphic: player graphic, e.g. 'X'
        :param count: used for recursion (don't change)
        :return: the count (the length)
        """
        count = count
        # count starting position as length of 1
        if count == 0 and self.board[coords[0]][coords[1]] == graphic:
            count = 1
        y = coords[0] + dir[0]
        x = coords[1] + dir[1]
        try:
            if self.board[y][x] == graphic:
                count += 1
                # check next move in current direction
                #try:
                return self.check_length((y, x), dir, graphic, count)
                #except IndexError:
                #    return count
        except IndexError:
            return count
        else:
            return count

    def draw_board(self):
        pass


class Player(object):
    def __init__(self, graphic, board):
        self.b = board
        self.graphic = graphic

    def place(self, y, x):
        self.b.board[y][x] = self.graphic


# Regression Tests:

def run_test_suite():
    print('\n--- REGRESSION TEST RESULTS ---\n{0}'.format(
        str([test1(), test2()])))


def test1():
    """
    PASS: Win state achieved
    FAIL: Win state not achieved
    Tests that win state is detected when it should be.
    :return: True, False
    """
    print('\n')
    print('--- WIN STATE TEST ---')
    print('\n')
    b = Board(10, 10)
    p = Player('X', b)
    p.place(1, 2)
    p.place(1, 3)
    p.place(1, 4)
    p.place(3, 1)
    p.place(4, 1)
    p.place(5, 1)
    p.place(6, 1)
    p.place(4, 4)
    p.place(3, 5)
    p.place(2, 6)
    b.print_board()
    if b.check_for_win_state('X'):
        return 'PASS'
    else:
        return 'FAIL'


def test2():
    """
    PASS: Win state not achieved
    FAIL: Win state achieved
    Tests that win state is only detected when actual
    win state occurs.
    :return: True, False
    """
    print('\n')
    print('--- FALSE WIN STATE TEST ---')
    print('\n')
    b = Board(10, 10)
    p = Player('X', b)
    p.place(1, 0)
    p.place(1, 3)
    p.place(1, 4)
    p.place(3, 1)
    p.place(2, 1)
    p.place(0, 1)
    p.place(6, 1)
    p.place(8, 4)
    p.place(3, 9)
    p.place(2, 6)
    b.print_board()
    if not b.check_for_win_state('X'):
        return 'PASS'
    else:
        return 'FAIL'

