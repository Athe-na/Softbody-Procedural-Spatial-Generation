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
    def __init__(self, normal: pg.Vector2, depth: float, vel1: pg.Vector2, vel2: pg.Vector2):
        self.normal: pg.Vector2 = normal
        self.depth: float = depth
        self.v2: pg.Vector2 = vel2
        self.v1: pg.Vector2 = vel1
        self.momentum: pg.Vector2 = vel1 + vel2

    def __str__(self):
        return str(self.normal) + ", " + str(self.depth) + ", " + str(self.v1) + ", " + str(self.v2)

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
        resolutions = []
        #check for collisions and resolve
        #for each point
        for p in self.points:
            resolutions.append(resolveCollisions(p, self.points))
        
        for rep in range(len(self.points)):
            self.points[rep].position += resolutions[rep][0]
            self.points[rep].velocity += resolutions[rep][1]
        #once all resolutions are collected, apply them!
            

# creates Collisions for all sets of particles with respect to a particle p
def findCollision(p: PointMass, points: list[PointMass]) -> list[Collision]:
    
    #remove p from points to avoid considering consideration of self collision
    copy = points.copy()
    copy.remove(p)

    Collisions: list[Collision] = []
    for q in copy:
        delta: pg.Vector2 = p.position - q.position
        distance: float = delta.length()
        normal: pg.Vector2 = delta/distance
        depth: float = p.radius + q.radius - distance
        Collisions.append(Collision(normal, depth, p.velocity, q.velocity))
    return Collisions

def resolveCollisions(p: PointMass, points: list[PointMass]) -> tuple:
    #create a prev variable to store the previous position so we can calculate change in velocity
    prev = p.position
    #create a list of collisions
    collisions: list[Collision] = findCollision(p, points)

    for collision in collisions:
        print(str(p) + "collision: " + str(collision))

    #if there are multiple collisions, we want to be able to sum the position and velocity effects
    sumPos = pg.Vector2(0, 0)
    sumVel = pg.Vector2(0, 0)

    #for each collision
    for c in collisions:
        if c.depth >= 0: #check if the depth is positive (if the objects are inside each other)
            if c.momentum.length() == 0: #if so and momentum will sum to nothing, remove them among the axis of the normal in half proportion
                sumPos += c.normal * (c.depth * 0.5) 
            else: #if so, and momentum is nonzero, remove them along the axis of the normal, proportional to p's proportion of momentum in the system
                sumPos += c.normal * (c.depth * (p.velocity.dot(c.normal)/c.v2.dot(c.normal)) / c.depth)

            #next, update velocity after the collision
            #momentum is preserved, so final momentum of the system is the combined momentum of the two colliders
            #velocity of point with respect to normal is vel dot normal for unit normal.
            #velocity of collision with respect to normal is (vel1+vel2) / 2.
            vn = c.normal * ((p.velocity.dot(c.normal) + c.v2.dot(c.normal)) / 2)
            print(str(p) + "velocity with respect to normal: " + str(vn))
            
            #thus, sumVel is the difference between the current velocity with respect to the normal and vn
            sumVel = vn - p.velocity.project(c.normal)

            print("Adding to " + str(p) + str(sumVel))
            
    #once we've gathered the sum of the effects of all collisions, bundle them and return it to the upper layer for eventual execution
    return (sumPos, sumVel)