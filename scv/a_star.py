import math

from astar import AStar

### All this code is a remake of the maze example from the astar libary (the one imported above).
from hlt import Position
from hlt.game_map import GameMap


def make_maze(w=30, h=30):
    """returns an ascii maze as a string"""
    from random import shuffle, randrange
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
    hor = [["+--"] * w + ['+'] for _ in range(h + 1)]

    def walk(x, y):
        vis[y][x] = 1

        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]:
                continue
            if xx == x:
                hor[max(y, yy)][x] = "+  "
            if yy == y:
                ver[y][max(x, xx)] = "   "
            walk(xx, yy)

    walk(randrange(w), randrange(h))
    result = ''
    for (a, b) in zip(hor, ver):
        result = result + (''.join(a + ['\n'] + b)) + '\n'
    return result.strip()


def drawmaze(maze, set1=[], set2=[], c='#', c2='*'):
    """returns an ascii maze, drawing eventually one (or 2) sets of positions.
        useful to draw the solution found by the astar algorithm
    """
    set1 = list(set1)
    set2 = list(set2)
    lines = maze.strip().split('\n')
    width = len(lines[0])
    height = len(lines)
    result = ''
    for j in range(height):
        for i in range(width):
            if (i, j) in set1:
                result = result + c
            elif (i, j) in set2:
                result = result + c2
            else:
                result = result + lines[j][i]
        result = result + '\n'
    return result


class Terran(AStar):
    """Implementation of A Star algorithm to figure out moves for a halite bot."""

    def __init__(self, map: GameMap):
        self.map = map

    def heuristic_cost_estimate(self, n1, n2) -> float:
        """computes the 'direct' distance between two (x,y) tuples"""
        return math.hypot(n2[0] - n1[0], n2[1] - n1[1])

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adjacent"""
        return 1

    def neighbors(self, node):
        """ Halite gives us this already
        """
        possible_moves = Position(node[0], node[1]).get_surrounding_cardinals()
        return [(m.x, m.y) for m in possible_moves]
