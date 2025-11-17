import networkx as nx

# Authored by Athena Osborne

class Generation:
    
    def __init__(self, Adj: nx.Graph, capacity: int, anchor: str):

        # Initialize an nx graph to put our room nodes into. This is the room structure we are generating
        G = nx.Graph()
        G.add_node(anchor)

def main():
    Adj = nx.Graph()
    Adj.add_nodes_from(["FOYER", "DINING", "LIVING", "FULLBATH", "HALFBATH", "MASTERBED", 
                        "BEDROOM", "GUESTBED", "OFFICE", "KITCHEN", "FAMILY", "GAME", "GARAGE", 
                        "GYM", "STAIRS", "LAUNDRY", "UTILITY"])
    Adj.add_edges_from([("FOYER", "DINING"), ("FOYER", "LIVING"), ("FOYER", "KITCHEN"), ("FOYER", "STAIRS"), ("FOYER", "GARAGE"),
                        ("DINING", "LIVING"), ("DINING", "KITCHEN"), ("DINING", "FAMILY"), ("DINING", "HALFBATH"),
                        ("LIVING", "STAIRS"), ("LIVING", "OFFICE"), ("LIVING", "HALFBATH"), ("LIVING", "GAME"), ("LIVING", "STAIRS"),
                        ("FULLBATH", "MASTERBED"), ("FULLBATH", "BEDROOM"), ("FULLBATH", "GUESTBED"),
                        ("HALFBATH", "BEDROOM"), ("HALFBATH", "GUESTBED"), ("HALFBATH", "GYM"), ("HALFBATH", "LAUNDRY"),
                        ("MASTERBED", "OFFICE"), ("MASTERBED", "GYM"),    
                        ("GUESTBED", "OFFICE"), ("GUESTBED", "LAUNDRY"), ("GUESTBED", "GYM"),
                        ("OFFICE", "FAMILY"), ("OFFICE", "GARAGE"),
                        ("KITCHEN", "FAMILY"), ("KITCHEN", "STAIRS"),
                        ("FAMILY", "GAME"), ("FAMILY", "GYM"), ("FAMILY", "STAIRS"), ("FAMILY", "LAUNDRY"),
                        ("GAME", "GARAGE"), ("GAME", "GYM"), ("GAME", "LAUNDRY"), ("GAME", "UTILITY"),
                        ("GARAGE", "GYM"), ("GARAGE", "LAUNDRY"), ("GARAGE", "UTILITY"),
                        ("GYM", "LAUNDRY"), ("GYM", "UTILITY"),
                        ("LAUNDRY", "UTILITY")])
# High level idea, places where edges cross are where hallways are placed, no edge cross indicates direct connection
# Alternatively, place hallways where rooms touch that aren't meant to be adjacent? (sometimes)
# When we place down room x from room y, see if room z connected to y is in x's acceptable adjacent rooms, if so, connect them.