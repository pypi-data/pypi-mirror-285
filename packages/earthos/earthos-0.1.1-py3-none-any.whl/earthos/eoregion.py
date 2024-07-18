

class EORegion:
    north = 0
    south = 0
    east = 0
    west = 0

    def __init__(self, north, south, east, west):
        self.north = north
        self.south = south
        self.east = east
        self.west = west
    
    def __str__(self):
        return f'{self.north},{self.south},{self.east},{self.west}'
    
    def to_dict(self):
        return {
            'north': self.north,
            'south': self.south,
            'east': self.east,
            'west': self.west,
        }
