# TODO: Create draw_board function and switch empty spaces to None
# TODO: 'Player.place' return False if player already on space (not None)
# TODO: Create In-Game script with turn taking (Rotate through player list)
# TODO: Create AI that randomly moves, then expand from it:


class Board(object):
    """
    The Game Board. Populated by player moves.

    rows: how tall the board is (y axis)
    columns: how wide the board is (x axis)
    win_amt: length of consecutive moves to win game
    """
    def __init__(self, rows=3, columns=3, win_amt=3):
        self.directions = {'UP': (-1, 0), 'UR': (-1, 1), 'RT': (0, 1), 'DR': (1, 1),
                           'DN': (1, 0), 'DL': (1, -1), 'LT': (0, -1), 'UL': (-1, -1)}
        self.board = []
        self.win_amt = win_amt
        # Create game board
        for i in range(0, rows):
            self.board.append([' ']*columns)

    def print_board(self):
        """
        Prints board data to screen for debugging.
        For pretty ascii representation use 'draw_board'
        :return:
        """
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
                return self.check_length((y, x), dir, graphic, count)
        except IndexError:
            return count
        else:
            return count

    def draw_board(self):
        pass


class Player(object):
    """
    Player instance places its graphic on the Board.
    Player can be controlled by ai or by user input.
    Any number of players can be instantiated.
    NOTE:
        Graphic must be different for each instantiated player.
        Duplicate graphic will result in errors.
    """
    def __init__(self, graphic, board):
        self.b = board
        self.graphic = graphic

    def place(self, y, x):
        """
        Places character graphic on space on board.
        Returns True if successful, False if non-existent coordinate.
        :param y: y coordinate on board
        :param x: x coordinate on board
        :return: True or False
        """
        try:
            self.b.board[y][x] = self.graphic
        except IndexError:
            return False
        return True

# Regression Tests:

def run_test_suite():
    """
    Run suite of regression tests.
    Test results displayed on screen.
    :return:
    """
    print('\n--- REGRESSION TEST RESULTS ---\n{0}'.format(
        str([test1(), test2(), test3()])))


def test1():
    """
    PASS: Win state achieved
    FAIL: Win state not achieved
    Tests that win state is detected when it should be.
    :return: PASS, FAIL
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
    :return: PASS, FAIL
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

def test3():
    """
    PASS: PLACING OUTSIDE OF BOARD HANDLES EXCEPTION
    FAIL: ERROR STOPS PROGRAM
    Tests that IndexError is handled for placing out of board
    :return: PASS, FAIL
    """
    print('\n')
    print('--- INDEX ERROR BOARD COORD BOUNDS TEST ---')
    print('\n')
    b = Board(10, 10)
    p = Player('X', b)
    try:
        p.place(1, 20)
        p.place(13, 3)
        p.place(13, 44)
        p.place(31, 123)
        p.place(22, 1)
        p.place(02, 1)
        p.place(642, 1)
        p.place(8, 4)
        p.place(31, 9)
    except IndexError:
        b.print_board()
        return 'FAIL'
    b.print_board()
    return 'PASS'
