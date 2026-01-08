import networkx as nx
import random
from enum import Enum
import matplotlib.pyplot as plt


# Authored by Athena Osborne with help from Jamie Osborne, derived from the "complex method" described in Jess Martin's "Algorithmic Beauty of Buildings".

'''
Some data strcuture notetaking from Algorithmic Beauty of Buildings by Jess Martin:


ROOMS:
Each room is represented as a NODE in a GRAPH
Rooms are connected by undirected edge in graph.
I'll use networkx for managing this graph.

Rooms are classified by two metrics: their class (public/private), and their type (the word we use for the room, like "bedroom," or "kitchen"). First can be a boolean attribute, second can be a string
So a room might be an object with a boolean and a string field?

More fields for rooms: their size (float)

The size/magnitude is used to determine the relative size between multiple rooms in a layout, respecting the fact that the 
absolute size of rooms scales depending on the type of space as well as its value.
Based on this, it seems like an implementation of this would have a room be an ABSTRACT CLASS, with each type of room being a 
subclass with a declared magnitude? This clashes with some earlier intuitions.

In reference to (missing) appendicies, the paper makes reference to "room type and their associated magnitudes and room class"
which seems to support the notion of a data structure which is typed based on the room type, and has fields of magnitude and class.

TERMINALS AND NON-TERMINALS:
The paper talks about terminals and non-terminals in the graph, and this seems to be a reference to the *observable* relationships
of nodes in the graph, rather than a kind of description in some field of the data structure or code property.

Maybe not? The difference between terminals and nonterminals as written is that non-terminals need to be specified further
in a way that terminals do not. Non-terminals specify the classification of the room and potentially its magnitude
but not its type.


STATISTICS:
Some UML is provided, a statistic is an OBJECT with the following fields:
RoomClass : roomClass
RoomType : roomType
Room : mustAttachRoom
Vector : attachingRooms
int : min
int : max

One statistic object is maintained per RoomType

This indicates that all of RoomClass, RoomType, and Room are objects? Wack.
RoomClass and RoomType can be typed easily enough as just a string representation with some builtins,
more unclear what "Room" is meant to be. Maybe a Room object is an object which contains RoomClass and RoomType fields?
Is a room object meant to be the vertex object in the graph?

RULES:
Rules dictate how the process of the terminal/nonterminal replacement grammar plays out during generation.
It doesn't seem like a class? Not sure.

Room-type relation:
Clearly, a room is not a roomtype
also, a roomtype is not a room

if a Room has a RoomType -> Room Object has a RoomType field. Does a RoomType need to be an object? Seems more likely to be an enum.

Also consider: "Beyond maintaining information about specific rooms and their public/private classification..."

Could use networkx to maintain a rule structure as a bunch of already initialized graphs, and use ability to append/directly
replace in order to follow through on rules.

SO...

The algorithm to generate a finished graph from an initial state is as follows:

Public rooms are added without specifying type:
- The graph begins with one node, which is a FD (Front Door) node.
    - This node contains/is a Room Object

The algorithm consults the RULES to determine how to replace each node.
- Iterate over all nodes, performing replacement until the "space is filled" (to be defined further).
    - We might consider this to be (some derivative of the magic number OR area of the space - sum of magnitudes
    of all currently placed nodes)

The algorithm attaches subgraphs of private rooms to the existing public graph.
    - Walks a random distance from the front door and attaches a private non-terminal to a public non-terminal.
    - Checks the ruleset to see what terminal private rooms can be produced from the private nonterminal.
    - Propose such a replacement
    - Consult the statistics objects for each proposed roomtype to ensure that it is a valid replacement

The algorithm converts social rooms to specific social rooms.
    - Replace the node immediately after the front door with a foyer or great room
'''

class RoomClass(Enum):
    PUBLIC = 1
    PRIVATE = 2

class RoomType(Enum):
    UNKNOWN = 0
    FOYER = 1
    GREATROOM = 2
    LIVINGROOM = 3
    KITCHEN = 4
    GAMEROOM = 5
    DININGROOM = 6
    BEDROOM = 7
    BATHROOM = 8
    MASTERBED = 9
    MASTERBATH = 10
    OFFICE = 11
    LAUNDRYROOM = 12

class Room:

    def __init__(self, roomClass: RoomClass):
        self.roomClass: RoomClass = roomClass
        self.roomType: RoomType = RoomType.UNKNOWN

    def addType(self, roomType: RoomType):
        self.roomType = roomType

    def __str__(self):
        return str(self.roomType).split(".")[1]

class Rule:
    def __init__(self, roomClass: RoomClass, graphs: list[nx.Graph], chances: list[float]) -> None:
        self.roomClass = roomClass
        self.graphs = graphs
        self.chances = chances

        # Ensure that the chances sum to 1
        if sum(chances) != 1:
            raise ValueError("Rule chance sum is not equal to 1")
        
        # Initialize accumulator variables
        accum: float = 0
        prev: float = 0
        # Change chances list to be ascending structure for roll method
        for chance in chances:
            accum += prev
            prev = chance
            chance = accum

    def roll(self, val: float):
        '''
        Function that returns a graph based on the provided roll value [0, 1]
        '''
        for i in range(len(self.graphs)):
            if val >= self.chances[i]:
                return self.graphs[i]


class Ruleset:
    '''
    A ruleset is a tuple of Rules.
    '''

    def __init__(self) -> None:
        self.ruleset = None

    def suburban(self):
        
        # Initialize a few public room objects to be used in graphs
        pub0 = Room(RoomClass.PUBLIC)
        pub1 = Room(RoomClass.PUBLIC)
        pub2 = Room(RoomClass.PUBLIC)

        # Construct a simple line of public rooms
        simpleLine: nx.Graph = nx.Graph()
        simpleLine.add_nodes_from([pub0, pub1])
        simpleLine.add_edge(pub0, pub1)

        # Construct a connected branch of public rooms
        branch: nx.Graph = nx.Graph()
        branch.add_nodes_from([pub0, pub1, pub2])
        branch.add_edges_from([(pub0, pub1), (pub0, pub2), (pub1, pub2)])

        self.ruleset = {
            RoomClass.PUBLIC : [[simpleLine, 0.6], [branch, 0.4]]
        }

        priv = Room(RoomClass.PRIVATE)
        bath = Room(RoomClass.PRIVATE).addType(RoomType.BATHROOM)
        bed0 = Room(RoomClass.PRIVATE).addType(RoomType.BEDROOM)
        bed1 = Room(RoomClass.PRIVATE).addType(RoomType.BEDROOM)
        masterbed = Room(RoomClass.PRIVATE).addType(RoomType.MASTERBED)
        masterbath = Room(RoomClass.PRIVATE).addType(RoomType.MASTERBATH)
        laundryroom = Room(RoomClass.PRIVATE).addType(RoomType.LAUNDRYROOM)

        toBath: nx.Graph = nx.Graph()
        toBath.add_node(bath)

        toBed: nx.Graph = nx.Graph()
        toBed.add_node(bed0)


        

class Generation:

    def __init__(self, ruleset: Ruleset, capacity: int, anchor: Room):

        # Initialize an nx graph to put our room nodes into. This is the room structure we are generating
        G = nx.Graph()
        G.add_node(anchor)

def main():

    pub0 = Room(RoomClass.PUBLIC)
    pub1 = Room(RoomClass.PUBLIC)
    pub2 = Room(RoomClass.PUBLIC)

    simpleLine: nx.Graph = nx.Graph()
    simpleLine.add_nodes_from([pub0, pub1])
    simpleLine.add_edge(pub0, pub1)

    branch: nx.Graph = nx.Graph()
    branch.add_nodes_from([pub0, pub1, pub2])
    branch.add_edges_from([(pub0, pub1), (pub0, pub2), (pub1, pub2)])

    G = branch
    subax1 = plt.subplot(121)
    nx.draw(G, with_labels=True, font_weight='bold', font_size=5)
    plt.show()


# Some thoughts about how hallways can be negotiated within this framework:
# High level idea, places where edges cross are where hallways are placed, no edge cross indicates direct connection
# Alternatively, place hallways where rooms touch that aren't meant to be adjacent? (sometimes) (PENISES)
# When we place down room x from room y, see if room z connected to y is in x's acceptable adjacent rooms, if so, connect them.
# Pre place bathrooms in generation graph, initialize connections from rooms being built in breadth first when rolled?
# Also, paper indicates that hallways typically connect social rooms to a cluster of branching off private rooms.
# When a public room rolls a cluster of private rooms, roll another value for how many of those private rooms will
# connect to the public room via a hallway.

if __name__ == "__main__":
    main()