from entities import Entity, Start
from direction import Direction


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.direction = Direction.UP

    def get_debug_char(self):
        ch = '☻'
        match self.direction:
            case Direction.UP:
                ch = '↑'
            case Direction.DOWN:
                ch = '↓'
            case Direction.LEFT:
                ch = '←'
            case Direction.RIGHT:
                ch = '→'
        return ch

    # When the player is added to the maze
    # we need to move it to the Start entity
    # and set the direction to the first walk
    # direction possible for that spot.
    def set_maze(self, maze):
        super().set_maze(maze)
        start = self.maze.get_entity_of_type(Start)
        self.x = start.x
        self.y = start.y
        self.direction = self.maze.get_walk_directions(self.x, self.y)[0]

    # The view is a 3x3 grid of what is in the
    # maze spots to the sides and in front of
    # the player.
    # * The player is in (0, 1)
    # * (0, 0) and (0, 2) are the left and right of
    #   the player
    # * (1, 0), (1, 1), and (1, 2) are the left,
    #   center, and right respectively directly in
    #   front of the player
    # # (2, 0), (2, 1), and (2, 2) are the left,
    #   center, and right respectively 2 spots in
    #   front of the player
    def get_view(self):
        # self.maze.debug()
        # Default to True for walls with player at (0, 1)
        view = [
            [True, self, True],
            [True, True, True],
            [True, True, True]
        ]
        match self.direction:
            case Direction.UP:
                view[0][0] = self.maze.get_in_spot(self.x - 1, self.y)
                view[0][2] = self.maze.get_in_spot(self.x + 1, self.y)
                view[1][0] = self.maze.get_in_spot(self.x - 1, self.y - 1)
                view[1][1] = self.maze.get_in_spot(self.x, self.y - 1)
                view[1][2] = self.maze.get_in_spot(self.x + 1, self.y - 1)
                view[2][0] = self.maze.get_in_spot(self.x - 1, self.y - 2)
                view[2][1] = self.maze.get_in_spot(self.x, self.y - 2)
                view[2][2] = self.maze.get_in_spot(self.x + 1, self.y - 2)
            case Direction.DOWN:
                view[0][0] = self.maze.get_in_spot(self.x + 1, self.y)
                view[0][2] = self.maze.get_in_spot(self.x - 1, self.y)
                view[1][0] = self.maze.get_in_spot(self.x + 1, self.y + 1)
                view[1][1] = self.maze.get_in_spot(self.x, self.y + 1)
                view[1][2] = self.maze.get_in_spot(self.x - 1, self.y + 1)
                view[2][0] = self.maze.get_in_spot(self.x + 1, self.y + 2)
                view[2][1] = self.maze.get_in_spot(self.x, self.y + 2)
                view[2][2] = self.maze.get_in_spot(self.x - 1, self.y + 2)
            case Direction.LEFT:
                view[0][0] = self.maze.get_in_spot(self.x, self.y + 1)
                view[0][2] = self.maze.get_in_spot(self.x, self.y - 1)
                view[1][0] = self.maze.get_in_spot(self.x - 1, self.y + 1)
                view[1][1] = self.maze.get_in_spot(self.x - 1, self.y)
                view[1][2] = self.maze.get_in_spot(self.x - 1, self.y - 1)
                view[2][0] = self.maze.get_in_spot(self.x - 2, self.y + 1)
                view[2][1] = self.maze.get_in_spot(self.x - 2, self.y)
                view[2][2] = self.maze.get_in_spot(self.x - 2, self.y - 1)
            case Direction.RIGHT:
                view[0][0] = self.maze.get_in_spot(self.x, self.y - 1)
                view[0][2] = self.maze.get_in_spot(self.x, self.y + 1)
                view[1][0] = self.maze.get_in_spot(self.x + 1, self.y - 1)
                view[1][1] = self.maze.get_in_spot(self.x + 1, self.y)
                view[1][2] = self.maze.get_in_spot(self.x + 1, self.y + 1)
                view[2][0] = self.maze.get_in_spot(self.x + 2, self.y - 1)
                view[2][1] = self.maze.get_in_spot(self.x + 2, self.y)
                view[2][2] = self.maze.get_in_spot(self.x + 2, self.y + 1)

        return view

    def turn(self, left=False):
        if left:
            match self.direction:
                case Direction.UP:
                    self.direction = Direction.LEFT
                case Direction.DOWN:
                    self.direction = Direction.RIGHT
                case Direction.LEFT:
                    self.direction = Direction.DOWN
                case Direction.RIGHT:
                    self.direction = Direction.UP
        else:
            match self.direction:
                case Direction.UP:
                    self.direction = Direction.RIGHT
                case Direction.DOWN:
                    self.direction = Direction.LEFT
                case Direction.LEFT:
                    self.direction = Direction.UP
                case Direction.RIGHT:
                    self.direction = Direction.DOWN

    def move(self, forward=True):
        x = self.x
        y = self.y
        amount = 1 if forward else -1
        match self.direction:
            case Direction.UP:
                y -= amount
            case Direction.DOWN:
                y += amount
            case Direction.LEFT:
                x -= amount
            case Direction.RIGHT:
                x += amount
        in_spot = self.maze.get_in_spot(x, y)
        if in_spot == True:
            return
        elif in_spot != False and in_spot.collides(self, x, y):
            return
        self.x = x
        self.y = y
