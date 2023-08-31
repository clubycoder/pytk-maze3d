import pstricks


class Entity:
    def __init__(self, x=0, y=0):
        self.maze = None
        self.x = x
        self.y = y
        # Some entities can hold other entities like a Player holding a Key
        self.entities = []

    def get_debug_char(self):
        return '?'

    def get_polygons(self):
        return []

    def get_image(self):
        return None

    def set_maze(self, maze):
        self.maze = maze

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    def get_entity_of_type(self, entity_type):
        for entity in self.entities:
            if isinstance(entity, entity_type):
                return entity
        return None

    def collides(self, entity, x=None, y=None):
        x = entity.x if x is None else x
        y = entity.y if y is None else y
        return self.x == x and self.y == y


class Start(Entity):
    def get_debug_char(self):
        return 'S'

    # For the start, we don't want to block moving the spot
    def collides(self, entity, x=None, y=None):
        if x is not None or y is not None:
            return False
        return super().collides(entity, x, y)


class End(Entity):
    POLYGONS = pstricks.load_polygons("end.pstricks.txt")

    def get_debug_char(self):
        return 'E'

    # For the end, we don't want to block moving the spot
    def collides(self, entity, x=None, y=None):
        if x is not None or y is not None:
            return False
        return super().collides(entity, x, y)

    def get_polygons(self):
        return End.POLYGONS


class Key(Entity):
    POLYGONS = pstricks.load_polygons("key.pstricks.txt")

    def get_debug_char(self):
        return 'Φ'

    # For the key, we don't want to block moving the spot
    def collides(self, entity, x=None, y=None):
        if x is not None or y is not None:
            return False
        return super().collides(entity, x, y)

    def get_polygons(self):
        return Key.POLYGONS


class Gate(Entity):
    POLYGONS = pstricks.load_polygons("gate.pstricks.txt")

    def get_debug_char(self):
        return '◙'

    def get_polygons(self):
        return Gate.POLYGONS

    # For the gate, we only want to block moving to the spot if the entity doesn't have the key
    def collides(self, entity, x=None, y=None):
        if (x is not None or y is not None) and entity.get_entity_of_type(Key) is not None:
            return False
        return super().collides(entity, x, y)
