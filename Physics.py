# Authored by Athena Osborne

import math
import pygame as pg

class PointMass:
    radius = 1
    IDCounter = 0

    def __init__(self, position: pg.Vector2, velocity: pg.Vector2, acceleration: pg.Vector2):
        self.position: pg.Vector2 = position
        self.velocity: pg.Vector2 = velocity
        self.acceleration: pg.Vector2 = acceleration # Not currently using
        self.id = self.IDCounter
        print("Created PointMass with id " + str(self.IDCounter))
        PointMass.IDCounter += 1
    
    def __str__(self):
        return "Point" + str(self.id)
    
    def __eq__(self, value: object) -> bool:
        if self.__str__ == object.__str__:
            return True
        return False

def cross(a: pg.Vector2, b: pg.Vector2):
    return a.x * b.y - a.y * b.x

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

class Constraint:
    
    def __init__(self, index0: int, index1: int, distance: float, hard:bool =False, springConst: float=5):
        self.index0 = index0
        self.index1 = index1
        self.distance = distance
        self.hard = hard # If it's a hard constraint, the two points must be *within* the specified distance of each other.
        self.springConst = springConst

    def __str__(self):
        return "point" + str(self.index0) + "!point" + str(self.index1) + " < " + str(self.distance) + ":" + str(self.hard)

class SoftBody:

    IDCounter = 0

    def __init__(self) -> None:
        self.id = self.IDCounter
        self.points: list[PointMass]
        self.constraints: list[Constraint]
        self.outerPointID: list[int] # This list will include one point twice at the beginning and end for easy iteration
        self.scale: float
        self.IDCounter += 1
    
    def dottedSquare(self, width: float, height: float, pos: pg.Vector2):

        # Initialize width and height vectors (facing down and right)
        widthVec = pg.Vector2(1, 0) * width
        heightVec = pg.Vector2(0, 1) * height

        # Create points in all four corners
        topRight = PointMass(pos + widthVec/2 - heightVec/2, pg.Vector2(0,0), pg.Vector2(0,0))
        topLeft = PointMass(pos - widthVec/2 - heightVec/2, pg.Vector2(0,0), pg.Vector2(0,0))
        botLeft = PointMass(pos - widthVec/2 + heightVec/2, pg.Vector2(0,0), pg.Vector2(0,0))
        botRight = PointMass(pos + widthVec/2 + heightVec/2, pg.Vector2(0,0), pg.Vector2(0,0))
        # And in the center
        center = PointMass(pos, pg.Vector2(0,0), pg.Vector2(0,0))

        # Link points together
        # Outers
        self.constraints.append(Constraint(topRight.id, topLeft.id, width))
        self.constraints.append(Constraint(topLeft.id, botLeft.id, height))
        self.constraints.append(Constraint(botLeft.id, botRight.id, width))
        self.constraints.append(Constraint(botRight.id, topRight.id, height))
        
        # Inners
        self.constraints.append(Constraint(topRight.id, center.id, (widthVec/2 + heightVec/2).length()))
        self.constraints.append(Constraint(topLeft.id, center.id, (widthVec/2 + heightVec/2).length()))
        self.constraints.append(Constraint(botLeft.id, center.id, (widthVec/2 + heightVec/2).length()))
        self.constraints.append(Constraint(botRight.id, center.id, (widthVec/2 + heightVec/2).length()))

        # Put outers on outerPointID
        self.outerPointID.extend([topRight.id, topLeft.id, botLeft.id, botRight.id, topRight.id])

        return self
    

    def scaleShapeMult(self, delta: float):
        for c in self.constraints:
            c.distance *= delta
        return self
    
    def scaleShapeAdd(self, delta: float): # Probably never going to use this lol but could be funny
        for c in self.constraints:
            c.distance += delta
        return self

class Vertex:

    IDCounter: int = 0

    def __init__(self, position: pg.Vector2, direction: pg.Vector2 = pg.Vector2(0, 0), stiffness: float = 0) -> None:
        self.position: pg.Vector2 = position
        self.id = self.IDCounter
        self.direction = direction # The direction along which it prefers to move along. Useful for hallways primarily I think
        self.stiffness = stiffness # How much pushes will be redirected along the direction
        self.IDCounter += 1
'''
class SoftBody: # Possibly obsolete
            
    def __init__(self) -> None:
        self.verticies: list[Vertex] # This is the list of unmoving abstract verticies that compose the ideal shape
        self.scale: float
        self.indexMin: int
        self.indexMax: int

    def circle(self, vertexCount: int, radius: int): # Create a circle as specified
        # Start by doing some basic accounting
        divisions: float = 360/vertexCount
        angle: pg.Vector2 = pg.Vector2(1, 0)

        # Then create verticies at the set angle intervals such that we create a circle of verticies at the given radius
        for v in range(vertexCount):
            newVert = Vertex(angle * radius)
            if v == 0: # If the loop index is 0, this will be the min id for verticies for this soft body.
                self.indexMin = newVert.id
            if v == vertexCount - 1: # Oppositely, if it's the last index, set it to be the max id for this soft body
                self.indexMax = newVert.id
            self.verticies.append(newVert) # Create a point
            angle.rotate_ip(divisions) # Rotate the angle in place.
        
        print("Created circle")
        return self
'''



class Resolution:
    def __init__(self, id: int, pos: pg.Vector2, vel: pg.Vector2, accel: pg.Vector2) -> None:
        self.pointID = id
        self.position = pos
        self.velocity = vel
        self.acceleration = accel

class Engine:
    
    def __init__(self, softBodies: list[SoftBody], walls: list[Wall], elasticity: float, friction: float, springDamping: float, WIDTH: int, HEIGHT: int):
        
        self.softBodies: list[SoftBody] = softBodies
        self.points: list[PointMass]
        for b in self.softBodies:
            self.points.extend(b.points)
        self.walls: list[Wall] = walls
        self.elasticity: float = elasticity
        self.friction: float = friction
        self.springDamping: float = springDamping
        self.WIDTH: int = WIDTH
        self.HEIGHT: int = HEIGHT
        self.constraints: list[Constraint]

    #update method that we'll call to simulate one "tick" of physics
    def update(self, dt):

        # Initialize a resolutions array
        resolutions: list[list[pg.Vector2]] = []

        #update position as the current position plus the velocity x the change in time
        for p in self.points:
            p.position += p.velocity * dt

        # Check for the various types of forces and other things we need to apply to each point
        for p in self.points:
            # Check for point2point and bounding collisions and append to resolution list
            resolutions.append(self.resolveCollisions(p, self.points, self.walls))
            
            
        for c in self.constraints: # For each constraint, identify the points involved and update their resolution based on the constraint
            
            # Grab position values for the two involved points
            p0 = self.points[c.index0].position
            p1 = self.points[c.index1].position

            # Find the delta and distance
            delta: pg.Vector2 = p1 - p0 # This points from p0 to p1
            distance: float = delta.magnitude()
            
            if c.hard: # If the constraint is hard, all we need to do is make sure the point doesn't exceed the distance value

                if distance > c.distance: # If the distance between the two points is greater than the constraint distance, make that not be the case :sob:
                    # It's slightly more complicated, but can be thought about the same as resolving a direct collision:

                    depth = distance - c.distance

                    # Initialize sumPos and force for 0 and 1
                    sumPos0: pg.Vector2 = pg.Vector2(0,0)
                    sumPos1: pg.Vector2 = pg.Vector2(0,0)
                    force0: pg.Vector2 = pg.Vector2(0,0)
                    force1: pg.Vector2 = pg.Vector2(0,0)

                    # Find the normal between the two points
                    normal: pg.Vector2 = delta/distance
                    # p0 should be pushed in the direction of the normal, p1 against
                    # Grab velocities
                    v0 = self.points[c.index0].velocity
                    v1 = self.points[c.index1].velocity

                    # Find relative velocity and split into components
                    relVelocity = v1 - v0
                    relVelocityN = relVelocity.project(normal)
                    relVelocityT = relVelocity - relVelocityN

                    #next, update velocity after the collision by computing forces on both points
                    #elastic force (normal)
                    force0 = relVelocityN * -self.elasticity
                    force1 = relVelocityN * self.elasticity

                    #inelastic force (normal)
                    force0 += relVelocityN/2 * -(1-self.elasticity)
                    force1 += relVelocityN/2 * (1-self.elasticity)

                    #tangential force (friction)
                    force0 += relVelocityT/2 * -self.friction
                    force1 += relVelocityT/2 * self.friction

                    if v0 == pg.Vector2(0,0): # If point 0 isn't moving, remove 1 along the normal completely
                        sumPos1 += normal * (-depth)
                    elif v1 == pg.Vector2(0,0): # And opposite case.
                        sumPos0 += normal * depth
                    else: # Otherwise, remove them equally along the normal
                        sumPos0 += normal * depth/2
                        sumPos1 += normal * -(depth/2)
                    

                    # Add the calculated sumPos and forces to the resolutions array for the appropriate point
                    resolutions[c.index0][0] += sumPos0
                    resolutions[c.index1][0] += sumPos1
                    resolutions[c.index0][1] -= force0
                    resolutions[c.index1][1] -= force1
            else: # If the constraint isn't hard, then apply dampened force towards the desired distance according to the spring constant
                
                normal: pg.Vector2 = delta / distance # Find the normal
                targetDelta: pg.Vector2 = normal * c.distance # Find the desired position along that normal
                force: pg.Vector2 = (targetDelta - delta) * c.springConst # Find undampened force based on desired minus actual times constant

                # Grab velocities for calculations
                v0: pg.Vector2 = self.points[c.index0].velocity
                v1: pg.Vector2 = self.points[c.index1].velocity

                # Initialize sumVel vectors for both points.
                sumVel0: pg.Vector2 = force * -dt
                sumVel1: pg.Vector2 = force * dt

                # Grab relative velocity and damping factor
                relVelocityN: pg.Vector2 = ((v1 + sumVel1) - (v0 + sumVel0)).project(normal)
                dampingFactor: float = math.exp(-self.springDamping * dt)

                # Find the new relative velocity according to the damping factor and the difference between current and desired
                newRelVelocityN: pg.Vector2 = relVelocityN * dampingFactor
                relVelocityDelta: pg.Vector2 = newRelVelocityN - relVelocityN

                # Then apply that difference to each point.
                sumVel0 -= relVelocityDelta
                sumVel1 += relVelocityDelta

                # Add this to the current resolution for that point
                resolutions[c.index0][1] += sumVel0
                resolutions[c.index1][1] += sumVel1

        

        for rep in range(len(self.points)):
            self.points[rep].position += resolutions[rep][0]
            self.points[rep].velocity += resolutions[rep][1]
            print("Resolved " + str(self.points[rep]) + " to " + str(self.points[rep].velocity) + "(" + str(round(self.points[rep].velocity.magnitude(), 2)) + ")@" + str(self.points[rep].position))
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

    def resolveCollisions(self, p: PointMass, points: list[PointMass], walls: list[Wall]) -> list[pg.Vector2]:
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

                # CREDIT TO: Iksha Phipps for assistance with this math
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
        return [sumPos, sumVel]
    

    # Check for point to edge collision
    # Can do this by projecting the point onto the edge and creating a circle at that point equal to the width of the edge.
    # If the circles intersect, collision
    def findEdgeCollisions(self, p: PointMass, points: list[PointMass], edges: list[Constraint]) -> list[Collision]:
        
        for e in edges: # For each edge
            surf: pg.Vector2 = points[e.index0].position - points[e.index1].position # Create a vector pointing from p0 to p1
            projector: pg.Vector2 = p.position - points[e.index0].position # Determine where 

        return [Collision()]

    def resolveEdgeCollisions(self, p: PointMass, c: Constraint) -> tuple[pg.Vector2, pg.Vector2]:
        pass 
        return(pg.Vector2(0,0), pg.Vector2(0,0))