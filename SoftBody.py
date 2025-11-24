# Authored by Athena Osborne, derived from Nikita Lisitsa's soft-body physics engine

import pygame as pg
import math

class SoftBody:

    class Vertex:
        IDCounter: int = 0
        
        def __init__(self, position: pg.Vector2, direction: pg.Vector2 = pg.Vector2(0, 0), stiffness: float = 0) -> None:
            self.position: pg.Vector2 = position
            self.index: int = self.IDCounter
            self.direction = direction # The direction along which it prefers to move along. Useful for hallways primarily I think
            self.stiffness = stiffness # How much pushes will be redirected along the direction
            self.IDCounter += 1
            
    def __init__(self) -> None:
        self.verticies: list

    def circle(self, vertexCount: int, radius: int) -> list[Vertex]: # Create a circle as specified
        # Start by doing some basic accounting
        divisions: float = 360/vertexCount
        angle: pg.Vector2 = pg.Vector2(1, 0)
        for v in range(vertexCount):
            pass
        
        return self.verticies