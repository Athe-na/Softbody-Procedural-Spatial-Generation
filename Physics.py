# Authored by Athena Osborne

import math
import pygame as pg

class PointMass:
    radius = 20
    IDCounter = 0

    def __init__(self, position: pg.Vector2, velocity: pg.Vector2, acceleration: pg.Vector2):
        self.position: pg.Vector2 = position
        self.velocity: pg.Vector2 = velocity
        self.acceleration: pg.Vector2 = acceleration
        self.id = self.IDCounter
        print("Created PointMass with id " + str(self.IDCounter))
        PointMass.IDCounter += 1

    def checkEdgeCollision(self):
        if self.position.x - self.radius < 0:
            self.velocity.x = 0
        if self.position.y - self.radius < 0:
            self.velocity.y = 0
    
    def __str__(self):
        return "Point" + str(self.id)

class Collision:
    def __init__(self, normal, depth):
        self.normal: pg.Vector2 = normal
        self.depth: float = depth

    def __str__(self):
        return str(self.normal) + ", " + str(self.depth)

class Engine:
    
    def __init__(self, points: list[PointMass]):
        self.points: list[PointMass] = points

    def update(self, dt):

        print("position step of update")
        #update position as the current position plus the velocity x the change in time
        for p in self.points:
            p.position += p.velocity * dt
            print(str(p) + " @ " + str(p.position))

        print("collision step of update")
        #check for collisions and resolve
        #for each point
        for p in self.points:
            #create a list of collisions
            collisions: list[Collision] = findCollision(p, self.points)

            for collision in collisions:
                print("collision: " + str(collision)) 
            #for each collision
            for c in collisions:
                #check if the depth is negative (if the objects are inside each other)
                if c.depth > 0:
                    #if so, remove them along the axis of the normal
                    p.position += c.normal * c.depth

# creates Collisions for all sets of particles with respect to a particle p
def findCollision(p: PointMass, points: list[PointMass]) -> list[Collision]:
    
    #remove p from points to avoid considering consideration of self collision
    copy = points.copy()
    copy.remove(p)

    Collisions: list[Collision] = []
    for q in copy:
        delta: pg.Vector2 = p.position - q.position
        print("pqdelta: " + str(delta))
        distance: float = delta.length()
        print("pqdist: " + str(distance))
        normal: pg.Vector2 = delta/distance
        depth: float = p.radius + q.radius - distance
        Collisions.append(Collision(normal, depth))
    return Collisions