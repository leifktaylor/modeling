import pytmx
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

tmx = pytmx.TiledMap('gameobjects/room/test8.tmx')


def path(start, end, tmx, layers=None):
    # Create matrix for A* to read
    if not layers:
        layers = [0, 1]
    matrix = [[0] * tmx.width for row in range(0, tmx.height)]
    for layer in layers:
        for row in range(0, tmx.height):
            for column in range(0, tmx.width):
                tile = tmx.get_tile_properties(column, row, layer)
                if tile:
                    if tile['wall'] == 'true':
                        matrix[column][row] = 1

    # Calculate path and return list of tiles along route
    grid = Grid(matrix=matrix)
    start = grid.node(*start)  # format (30, 30)
    end = grid.node(*end)
    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)
    return path


if __name__ == '__main__':
    print(path((30, 30), (45, 25), tmx))
