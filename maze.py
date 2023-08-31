import random
import math
import time
from astar import AStar
from direction import Direction
from entities import *
from player import Player


class Maze(AStar):
    def __init__(self, width=11, height=11):
        self.width = width
        self.height = height
        # The width and height must be an odd number
        # so we can carve wall in odd spots
        if self.width % 2 == 0:
            self.width += 1
        if self.height % 2 == 0:
            self.height += 1
        self.walls = []  # True if wall and False if floor
        self.floor_spots = []  # Tuples of floor (x, y)
        self.entities = []  # All entities in maze
        self.message = "Search for the key."
        self.start_time = time.time()
        self.current_time = self.start_time
        self.done = False

    def debug(self):
        print("%d x %d" % (self.width, self.height))
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if self.walls[y][x]:
                    row += "█"
                else:
                    entity = self.get_entity(x, y)
                    if entity is not None:
                        row += entity.get_debug_char()
                    else:
                        row += " "
            print(row)

    def generate(self):
        self.generate_walls_and_floors()
        self.generate_entities()

    # Given a spot x & y, return a list of possible
    # directions we can carve 2 spots away
    def get_carve_directions(self, x, y):
        directions = []
        if y - 2 > 0 and self.walls[y - 2][x]:
            directions.append(Direction.UP)
        if y + 2 < self.height - 1 and self.walls[y + 2][x]:
            directions.append(Direction.DOWN)
        if x - 2 > 0 and self.walls[y][x - 2]:
            directions.append(Direction.LEFT)
        if x + 2 < self.width - 1 and self.walls[y][x + 2]:
            directions.append(Direction.RIGHT)
        return directions

    # Given a spot x & y, return a list of possible
    # directions we can walk 1 spot away
    def get_walk_directions(self, x, y):
        directions = []
        if y - 1 > 0 and not self.walls[y - 1][x]:
            directions.append(Direction.UP)
        if y + 1 < self.height and not self.walls[y + 1][x]:
            directions.append(Direction.DOWN)
        if x - 1 > 0 and not self.walls[y][x - 1]:
            directions.append(Direction.LEFT)
        if x + 1 < self.width and not self.walls[y][x + 1]:
            directions.append(Direction.RIGHT)
        return directions

    def generate_walls_and_floors(self):
        # First fill the map with walls
        self.walls.clear()
        for y in range(self.height):
            self.walls.append([])
            for x in range(self.width):
                self.walls[y].append(True)

        # The usable spots are points where we can go
        # back and start carving out floors again once
        # we run in to a dead-end
        usable_spots = []

        # We're going to carve out the floors on odd
        # spots, so find a random odd spot to start with
        x = random.randrange(0, int(self.width / 2)) * 2 + 1
        y = random.randrange(0, int(self.height / 2)) * 2 + 1

        # Carve out the floor at this first spot
        self.walls[y][x] = False

        # Add the first spot to the usable spots
        usable_spots.append((x, y))

        # Now we need to carve out floors until we don't
        # have any usable spots left.  As we carve we'll
        # be adding every spot we move to to the usable
        # spots as long as it's not a dead-end.  That means
        # that once there are no more usable spots that
        # the maze area is full.
        while len(usable_spots) > 0:
            # Let's shuffle the usable spots before picking one
            random.shuffle(usable_spots)
            # Grab a spot and it's possible directions
            (x, y) = usable_spots.pop()
            directions = self.get_carve_directions(x, y)
            # Keep carving floors until we run out of directions
            while len(directions) > 0:
                # As we carve, if the spot that we're on has
                # more than one possible direction, add it to
                # the usable spots for later when we run in to
                # a dead end
                if len(directions) > 1:
                    usable_spots.append((x, y))
                # Pick a direction to carve
                direction = random.choice(directions)
                # Carve UP, DOWN, LEFT, or RIGHT 2 spots because
                # we are always moving from one even spot to another
                match direction:
                    case Direction.UP:
                        self.walls[y - 1][x] = False
                        self.walls[y - 2][x] = False
                        y -= 2
                    case Direction.DOWN:
                        self.walls[y + 1][x] = False
                        self.walls[y + 2][x] = False
                        y += 2
                    case Direction.LEFT:
                        self.walls[y][x - 1] = False
                        self.walls[y][x - 2] = False
                        x -= 2
                    case Direction.RIGHT:
                        self.walls[y][x + 1] = False
                        self.walls[y][x + 2] = False
                        x += 2
                # Get the possible directions for the new spot
                directions = self.get_carve_directions(x, y)

        # Now that we have all floors carved out,
        # save off the positions of floor spots
        for y in range(self.height):
            for x in range(self.width):
                if not self.walls[y][x]:
                    self.floor_spots.append((x, y))

    # AStar pieces
    # AStar - Computes the 'direct' distance between
    # two spots
    def heuristic_cost_estimate(self, n1, n2):
        (x1, y1) = n1
        (x2, y2) = n2
        return math.hypot(x2 - x1, y2 - y1)

    # AStar - this method always returns 1, as two
    # spots are always adjacent
    def distance_between(self, n1, n2):
        return 1

    # AStar - for a spot coordinate in the maze,
    # returns up to 4 adjacent (UP, DOWN, LEFT, and RIGHT)
    # spots
    def neighbors(self, node):
        (x, y) = node
        directions = self.get_walk_directions(x, y)
        neighbors = []
        for direction in directions:
            match direction:
                case Direction.UP:
                    neighbors.append((x, y - 1))
                case Direction.DOWN:
                    neighbors.append((x, y + 1))
                case Direction.LEFT:
                    neighbors.append((x - 1, y))
                case Direction.RIGHT:
                    neighbors.append((x + 1, y))
        return neighbors

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.set_maze(self)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    # Look for an entity at a spot
    def get_entity(self, x, y):
        spot_entity = None
        for entity in self.entities:
            if entity.x == x and entity.y == y:
                spot_entity = entity
        return spot_entity

    def get_entity_of_type(self, entity_type):
        for entity in self.entities:
            if isinstance(entity, entity_type):
                return entity
        return None

    def get_in_spot(self, x, y):
        # If this is outside the maze treat it as a wall
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        # Is there an entity like a key at this spot?
        entity = self.get_entity(x, y)
        if entity is not None:
            return entity
        # Check for an actual wall
        return self.walls[y][x]

    # Find all floor spots that only have one
    # direction to move
    def get_dead_ends(self):
        dead_ends = []
        for (x, y) in self.floor_spots:
            if len(self.get_walk_directions(x, y)) == 1:
                dead_ends.append((x, y))
        return dead_ends

    # From a list of spots, remove and return the
    # furthest away spot from a 1 or more other spots.

    # The furthest away is calculated by using an AStar
    # to calculate a path between the spots.  The distance
    # is the length of the path.  If more than one from
    # spot is passed in, the path length will be added
    # together for the distance score.
    def take_furthest_away_spot(self, spots, from_spots):
        def distance_score(spot):
            score = 0
            for from_spot in from_spots:
                score += len(list(self.astar(from_spot, spot)))
            return score

        spots.sort(key=distance_score)
        return spots.pop()

    def generate_entities(self):
        # For the start and end, we want to use dead-ends
        # to make it the most challenging.  Using dead-ends
        # will also allow us to easily put a single gate
        # that blocks the end.
        #
        # First find all the dead-ends and shuffle them.
        dead_ends = self.get_dead_ends()
        # self.debug()

        # Take one of the dead-end as the start position.
        (x, y) = dead_ends.pop()
        start = Start(x, y)
        self.add_entity(start)

        # For the end, let's take another dead-end that is
        # furthest away from the start.
        (x, y) = self.take_furthest_away_spot(dead_ends, [
            (start.x, start.y)
        ])
        end = End(x, y)
        self.add_entity(end)

        # For the gate, we'll put it one spot away from the
        # end since we know that the end is in a dead-end.
        x = end.x
        y = end.y
        match self.get_walk_directions(end.x, end.y)[0]:
            case Direction.UP:
                y -= 1
            case Direction.DOWN:
                y += 1
            case Direction.LEFT:
                x -= 1
            case Direction.RIGHT:
                x += 1
        gate = Gate(x, y)
        self.add_entity(gate)

        # For the key, we want a spot that is far away from
        # both the start and end.  Ideally this is a dead-end,
        # but if there are no dead-ends left, just puck a
        # regular floor spot.
        possible_key_spots = dead_ends if len(dead_ends) > 0 else self.floor_spots.copy()
        (x, y) = self.take_furthest_away_spot(possible_key_spots, [
            (start.x, start.y),
            (end.x, end.y),
        ])
        key = Key(x, y)
        self.add_entity(key)

    def get_time_passed(self):
        return self.current_time - self.start_time

    def update(self):
        # self.debug()

        # Update time
        self.current_time = time.time()

        # Find the player
        player = self.get_entity_of_type(Player)
        # If the player hasn't been added to the maze yet,
        # we don't need to do any updates
        if player is None:
            return
        # Does the player have the key?
        player_key = player.get_entity_of_type(Key)
        # Find the key in the maze
        key = self.get_entity_of_type(Key)
        # Get the maze gate before the end
        gate = self.get_entity_of_type(Gate)
        # Get the end
        end = self.get_entity_of_type(End)

        # If there is a key left in the maze,
        # see if the player collides with it
        # and picks it up.
        if key is not None and key.collides(player):
            self.remove_entity(key)
            player.add_entity(key)
            self.message = "You have the key! Find the gate."

        # If the player is at the gate and has the key,
        # remove the gate
        if gate is not None and player_key is not None and gate.collides(player):
            self.message = "The gate is open! Find the exit."
            self.remove_entity(gate)
            player.remove_entity(player_key)

        # If the player is at the end, we're done
        if end.collides(player):
            self.message = "You made it out!"
            self.done = True
