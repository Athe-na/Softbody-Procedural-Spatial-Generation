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
    
    def __str__(self):
        return "Point" + str(self.id)
    
class Wall:
    IDCounter = 0

    def __init__(self, pos0: pg.Vector2, pos1: pg.Vector2, radius: float):
        #initialize wall
        self.pos0 = pos0
        self.pos1 = pos1
        self.length = pos0.distance_to(pos1)
        self.radius = radius

        #slightly more complex properties that are nonetheless worthwhile to do here
        self.center = pos0 + (pos1-pos0).normalize() * self.length/2

        self.id = self.IDCounter
        print("Created Wall with id " + str(self.IDCounter))
        Wall.IDCounter += 1

    def __str__(self):
        return "Wall" + str(self.id)

class Collision:
    def __init__(self, normal: pg.Vector2, depth: float, vel1: pg.Vector2, vel2: pg.Vector2, wall: bool):
        self.normal: pg.Vector2 = normal
        self.depth: float = depth
        self.v2: pg.Vector2 = vel2
        self.v1: pg.Vector2 = vel1
        self.momentum: pg.Vector2 = vel1 + vel2
        self.wall: bool = wall

    def __str__(self):
        return str(self.normal) + ", " + str(self.depth) + ", " + str(self.v1) + ", " + str(self.v2) + ", " + str(self.wall)

class Engine:
    
    def __init__(self, points: list[PointMass], walls: list[Wall], elasticity: float, friction: float, WIDTH: int, HEIGHT: int):
        self.points: list[PointMass] = points
        self.walls: list[Wall] = walls
        self.elasticity: float = elasticity
        self.friction: float = friction
        self.WIDTH: int = WIDTH
        self.HEIGHT: int = HEIGHT

    #update method that we'll call to simulate one "tick" of physics
    def update(self, dt):

        # Initialize a resolutions array
        resolutions = []

        #update position as the current position plus the velocity x the change in time
        for p in self.points:
            p.position += p.velocity * dt

        #check for PointMass collisions and resolve
        for p in self.points:
            resolutions.append(self.resolveCollisions(p, self.points, self.walls))
        
        for rep in range(len(self.points)):
            self.points[rep].position += resolutions[rep][0]
            self.points[rep].velocity += resolutions[rep][1]
            print("Resolved " + str(self.points[rep]) + " to " + str(self.points[rep].velocity) + "@" + str(self.points[rep].position))
        #once all resolutions are collected, apply them!
            

    # creates Collisions for all sets of particles with respect to a particle p
    def findCollision(self, p: PointMass, points: list[PointMass], walls: list[Wall]) -> list[Collision]:   

        #remove p from points to avoid considering consideration of self collision. 
        #This works since structural changes aren't back propogated in a shallow copy
        copy = points.copy()
        copy.remove(p)

        Collisions: list[Collision] = []

        # Find bounding collisions
        if (p.position.x + p.radius) > self.WIDTH:
            normal: pg.Vector2 = pg.Vector2(-1, 0)
            depth: float = (p.position.x + p.radius) - self.WIDTH
            Collisions.append(Collision(normal, depth, p.velocity, pg.Vector2(0, 0), True))
        if (p.position.x - p.radius) < 0:
            normal: pg.Vector2 = pg.Vector2(1, 0)
            depth: float = 0 - (p.position.x - p.radius)
            Collisions.append(Collision(normal, depth, p.velocity, pg.Vector2(0, 0), True))
        if (p.position.y + p.radius) > self.HEIGHT:
            normal: pg.Vector2 = pg.Vector2(0, -1)
            depth: float = (p.position.y + p.radius) - self.HEIGHT
            Collisions.append(Collision(normal, depth, p.velocity, pg.Vector2(0, 0), True))
        if (p.position.y - p.radius) < 0:
            normal: pg.Vector2 = pg.Vector2(0, 1)
            depth: float = 0 - (p.position.y - p.radius)
            Collisions.append(Collision(normal, depth, p.velocity, pg.Vector2(0, 0), True))
            
        # Find PointMass collisions
        for q in copy:
            delta: pg.Vector2 = p.position - q.position
            distance: float = delta.length()
            normal: pg.Vector2 = delta/distance
            depth: float = p.radius + q.radius - distance
            Collisions.append(Collision(normal, depth, p.velocity, q.velocity, False))
        
    
        # Find Wall collisions (NOT CURRENTLY IN USE)
        for w in walls:
            # Take delta from each endpoint
            delta0: pg.Vector2 = p.position - w.pos0
            delta1: pg.Vector2 = p.position - w.pos1

            # Calculate Tangent to flat part of wall
            flatTangent: pg.Vector2 = (w.pos0 - w.pos1).normalize()

            # And use that to calculate the normal
            flatNormal: pg.Vector2 = pg.Vector2(0, 0)
            flatNormal.xy = flatTangent.yx
            flatNormal.y *= -1

            # Make sure the normal is oriented in the right direction by checking to see whether adding it takes us closer or farther from the wall
            if (p.position + flatNormal).distance_to(w.center) < p.position.distance_to(w.center): # If not, reverse it
                flatNormal *= -1
            
            # With all this, create distanceC
            

        return Collisions

    def resolveCollisions(self, p: PointMass, points: list[PointMass], walls: list[Wall]) -> tuple[pg.Vector2, pg.Vector2]:
        #create a prev variable to store the previous position so we can calculate change in velocity
        prev = p.position
        #create a list of point collisions
        collisions: list[Collision] = self.findCollision(p, points, walls)

        #if there are multiple collisions, we want to be able to sum the position and velocity effects
        sumPos = pg.Vector2(0, 0)
        sumVel = pg.Vector2(0, 0)

        #for each collision
        for c in collisions:
            if c.depth > 0: #check if the depth is positive (if the objects are inside each other)
                # Debug: print out collision details
                print(str(p) + "collision: " + str(c))
                if c.v2 == pg.Vector2(0, 0): # If the other object isn't moving, remove along the normal but completely.
                    sumPos += c.normal * c.depth
                    print(str(p) + " in static collision " + str(c) + ", removed @" + str(sumPos))
                else:
                    # Calculate the proportion of the momentum that p has relative to the normal, and remove it by that amount
                    proportion: float = p.velocity.project(c.normal).length() / (p.velocity.project(c.normal).length() + c.v2.project(c.normal).length())
                    sumPos += c.normal * c.depth * proportion

                #compute relative velocity (and split it into tangential and normal)
                relVelocity = p.velocity - c.v2
                relVelocityN = relVelocity.project(c.normal)
                relVelocityT = relVelocity - relVelocityN

                #next, update velocity after the collision by computing forces on p
                #elastic force (normal)
                force: pg.Vector2 = relVelocityN * self.elasticity

                #inelastic force (normal)
                force += relVelocityN/2 * (1-self.elasticity)

                #tangential force (friction)
                force += relVelocityT/2 * self.friction

                # If the collision is with a wall, the wall will not move, and the energy is returned to the PointMass proportional to friction
                if c.wall:
                    force += relVelocityN * self.elasticity

                sumVel -= force

                print("Adding to " + str(p) + str(sumVel))
                
        #once we've gathered the sum of the effects of all collisions, bundle them and return it to the upper layer for eventual execution
        return (sumPos, sumVel)
    
    def resolveWallCollisions(self, p: PointMass, walls: list[Wall]) -> tuple[pg.Vector2, pg.Vector2]:
        pass 
        return(pg.Vector2(0,0), pg.Vector2(0,0))