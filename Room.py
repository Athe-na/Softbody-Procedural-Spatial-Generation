# Authored by Athena Osborne, with grammar conceptualization from Jess Martin and Christopher Alexander

import math

class Room:

    index: int = 0

    def __init__(self):
        self.id = self.index
        self.index += 1

    
    
class Foyer(Room):
    pass
class Dining(Room):
    pass
class Living(Room):
    pass
class Fullbath(Room):
    pass
class Halfbath(Room):
    pass
class Masterbed(Room):
    pass
class Bedroom(Room):
    pass
class Guestroom(Room):
    pass
class Office(Room):
    pass
class Kitchen(Room):
    pass
class Family(Room):
    pass
class Game(Room):
    pass
class Garage(Room):
    pass
class Gym(Room):
    pass
class Stairs(Room):
    pass
class Laundry(Room):
    pass
class Utility(Room):
    pass
class Pantry(Room):
    pass

class Statistic: # Create a Statistic class which functions very similarly to a grammar

    def __init__(self, room: Room, magicNum: int) -> None:
        self.roomClass: bool # Whether the room is public or private
        self.roomType: Room = room # What kind of room it is
        self.mustAttachRoom: Room # Not sure yet what to use this for
        self.attachingRooms: list # A list of rooms which can be attached to this room
        self.min: int # The fewest rooms of this type which can be in the floor plan
        self.max: int # The most rooms of this type which can be in the floor plan

        match room:
            case val if val == Foyer:
                self.roomClass = True
                self.attachingRooms = [Dining, Living, Kitchen, Family, Game, Stairs]
                self.min = 1
                self.max = 1
            case val if val == Dining:
                self.roomClass = True
                self.attachingRooms = [Foyer, Living, Kitchen, Family, Stairs]
                self.min = 1
                self.max = 1
            case val if val == Living:
                self.roomClass = True
                self.attachingRooms = [Foyer, Stairs, Office, Halfbath, Game, Dining]
                self.min = 1
                self.max = 1
            case val if val == Fullbath:
                self.roomClass = False
                self.attachingRooms = [Masterbed, Bedroom, Guestroom]
                self.min = 1
                self.max = math.ceil(magicNum / 25)
            case val if val == Halfbath:
                self.roomClass = False
                self.attachingRooms = [Bedroom, Guestroom, Gym, Laundry]
                self.min = 1
                self.max = math.ceil(magicNum / 33)
            case val if val == Masterbed:
                self.roomClass = False
                self.attachingRooms = [Fullbath, ]
