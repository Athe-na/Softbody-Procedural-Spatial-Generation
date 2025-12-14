# Authored by Athena Osborne

import math
import pygame as pg

class Resolution:
    def __init__(self, pos: pg.Vector2, vel: pg.Vector2, accel: pg.Vector2) -> None:
        self.position = pos
        self.velocity = vel
        self.acceleration = accel

    def __add__(self, value):
        self.position += value.position
        self.velocity += value.velocity
        self.acceleration += value.acceleration
        return self
    
    def __str__(self):
        return str("@" + str(self.position) + "w/" + str(self.velocity))


class PointMass:
    radius = 5
    IDCounter = 0

    def __init__(self, position: pg.Vector2, velocity: pg.Vector2, acceleration: pg.Vector2):
        self.position: pg.Vector2 = position
        self.velocity: pg.Vector2 = velocity
        self.acceleration: pg.Vector2 = acceleration # Not currently using. Will eventually shift to exerting all forces as accelerations
        self.id = self.IDCounter
        self.resolution: Resolution = Resolution(pg.Vector2(0,0), pg.Vector2(0,0), pg.Vector2(0,0))
        print("Created PointMass with id " + str(self.IDCounter))
        PointMass.IDCounter += 1
    
    def __str__(self):
        return "Point" + str(self.id)
    
    def __eq__(self, value: object) -> bool:
        if self.__str__ == object.__str__:
            return True
        return False
    
    def clearResolution(self):
        self.resolution = Resolution(pg.Vector2(0,0), pg.Vector2(0,0), pg.Vector2(0,0))

    def amendResolution(self, resolution: Resolution):
        '''
        Performs the add operation on the current and provided resolution in place
        '''
        self.resolution += resolution

    def applyResolution(self):
        '''
        Applies the current resolution in place, then clears the resolution
        '''
        self.position += self.resolution.position
        self.velocity += self.resolution.velocity
        self.acceleration += self.resolution.acceleration
        self.clearResolution()

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
        self.index0: int = index0
        self.index1: int = index1
        self.distance: float = distance
        self.hard: bool = hard # If it's a hard constraint, the two points must be *within* the specified distance of each other.
        self.springConst: float = springConst

    def __str__(self):
        return "point" + str(self.index0) + "!point" + str(self.index1) + " < " + str(self.distance) + ":" + str(self.hard)

class SoftBody:

    IDCounter = 0

    def __init__(self) -> None:
        self.id = self.IDCounter
        self.points: list[PointMass] = []
        self.innerConstraints: list[Constraint] = []
        self.outerConstraints: list[Constraint] = [] # The list of indexes which correspond to outer edges in self.constraints
        self.scale: float = 1
        self.IDCounter += 1
        print("Initialized softbody " + str(self.id))
        print("Constraints initialized in SoftBody: " + str(self.innerConstraints + self.outerConstraints))
    
    def dot(self, pos: pg.Vector2):
        '''
        Creates a body consisting of a singular PointMass at the specified position
        '''
        self.addPointAtPos(pos)

        return self

    def line(self, pos0: pg.Vector2, pos1: pg.Vector2):
        '''
        Creates a body consisting of two PointMasses connected by an outer constraint
        '''
        # Create points
        point0 = self.addPointAtPos(pos0)
        point1 = self.addPointAtPos(pos1)

        # Add constraint
        self.outerConstraints.append(Constraint(point0, point1, (pos0 - pos1).length()))

        return self


    def dottedRect(self, width: float, height: float, pos: pg.Vector2):
        '''
        Creates a rectangular arrangement of interconnected PointMasses with a PointMass in the middle

        Parameters
        ----------
        pos : pg.Vector2
            The position of the central PointMass
        '''
        # Initialize width and height vectors (facing down and right)
        widthVec = pg.Vector2(1, 0) * width
        heightVec = pg.Vector2(0, 1) * height

        # Create points in all four corners
        topRight = self.addPointAtPos(pos + widthVec/2 - heightVec/2)
        topLeft = self.addPointAtPos(pos - widthVec/2 - heightVec/2)
        botLeft = self.addPointAtPos(pos - widthVec/2 + heightVec/2)
        botRight = self.addPointAtPos(pos + widthVec/2 + heightVec/2)

        # And in the center
        center = self.addPointAtPos(pos)

        # Link points together
        # Outers
        self.outerConstraints.append(Constraint(topRight, topLeft, width))
        self.outerConstraints.append(Constraint(topLeft, botLeft, height))
        self.outerConstraints.append(Constraint(botLeft, botRight, width))
        self.outerConstraints.append(Constraint(botRight, topRight, height))
        
        # Inners
        self.innerConstraints.append(Constraint(topRight, center, (widthVec/2 + heightVec/2).length()))
        self.innerConstraints.append(Constraint(topLeft, center, (widthVec/2 + heightVec/2).length()))
        self.innerConstraints.append(Constraint(botLeft, center, (widthVec/2 + heightVec/2).length()))
        self.innerConstraints.append(Constraint(botRight, center, (widthVec/2 + heightVec/2).length()))

        return self
    

    def scaleShapeMult(self, delta: float):
        '''
        Multiplicatively scale the distance attribute in all constraints by the provided factor
        '''
        for c in self.outerConstraints + self.innerConstraints:
            c.distance *= delta
        return self
    
    def scaleShapeAdd(self, delta: float): # Probably never going to use this lol but could be funny
        '''
        Additively scale the distance attribut4e in all constraints by the provided factor
        '''
        for c in self.outerConstraints + self.innerConstraints:
            c.distance += delta
        return self

    def addPointAtPos(self, pos: pg.Vector2):
        '''Helper method for creating a point at a specified position.
        
        Parameters
        ----------
        pos : pg.Vector2
            Position of created point. (Noooooooooo...)

        Returns
        -------
        int
            id of created PointMass
        '''
        # Add the point to the point list, creating it at the specified spot
        point = PointMass(pos, pg.Vector2(0,0), pg.Vector2(0,0))
        self.points.append(point)
        return point.id
        
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
        

class Engine:
    
    def __init__(self, softBodies: list[SoftBody], walls: list[Wall], elasticity: float, friction: float, springDamping: float, WIDTH: int, HEIGHT: int):
        
        self.softBodies: list[SoftBody] = softBodies
        self.points: list[PointMass] = []
        self.outerConstraints: list[Constraint] = []
        self.innerConstraints: list[Constraint] = []
        for b in self.softBodies:
            self.points.extend(b.points)
            self.outerConstraints.extend(b.outerConstraints)
            self.innerConstraints.extend(b.innerConstraints)
        self.walls: list[Wall] = walls
        self.elasticity: float = elasticity
        self.friction: float = friction
        self.springDamping: float = springDamping
        self.WIDTH: int = WIDTH
        self.HEIGHT: int = HEIGHT

        self.points.append(PointMass(pg.Vector2(175, 100), pg.Vector2(-200, 0), pg.Vector2(0, 0)))

    def update(self, dt):
        '''
        Function that simulates one "tick" of physics, where the length of the tick is dictated by the dt variable.
        '''

        #update position as the current position plus the velocity x the change in time.
        for p in self.points:
            p.position += p.velocity * dt

        # NOTE: I think during the expansion step this won't work. This may require more exhaustive collision detection/resolution

        # Check for the various types of forces and other things we need to apply to each point
        for p in self.points:

            # Create a list of point2point collisions for point p
            collisions = self.findCollision(p)
            r = self.resolveCollisions(p, collisions) # Based on that list of collisions, create a resolution for point p
            if r != None: # If there actually is a resulting resolution
                p.amendResolution(r) # Amend p's current resolution
            
            resolution = self.checkAndResolveEdgeCollisions(p)
            if resolution != None: # If there actually is a resolution
                p.amendResolution(resolution[0]) # Amend the resolution of the current point

                for r in range(len(resolution[1])):
                    self.points[resolution[1][r][1]].amendResolution(resolution[1][r][0])
            

        '''
        CONSTRAINT RESOLUTION
        For each constraint, identify the points involved and update their resolution based on the constraint
        '''
        for c in self.outerConstraints + self.innerConstraints: 
            
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
                    

                    # Create Resolutions for both points and amend both points' resolution attributes
                    self.points[c.index0].amendResolution(Resolution(sumPos0, -force0, pg.Vector2(0,0)))
                    self.points[c.index1].amendResolution(Resolution(sumPos1, -force1, pg.Vector2(0,0)))
                    
            else: # If the constraint isn't hard, then apply dampened force towards the desired distance according to the spring constant
                
                sumPos0: pg.Vector2 = pg.Vector2(0,0)
                sumPos1: pg.Vector2 = pg.Vector2(0,0)

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
                self.points[c.index0].amendResolution(Resolution(sumPos0, sumVel0, pg.Vector2(0,0)))
                self.points[c.index1].amendResolution(Resolution(sumPos1, sumVel1, pg.Vector2(0,0)))
        '''
        END CONSTRAINT RESOLUTION
        '''

        for p in self.points: # For each point, apply its resolution
            
            print(str(p) + " pre-resolution: " + str(p.resolution))
            p.applyResolution()
            print(str(p) + " post-resolution: " + str(p.resolution))

    # creates Collisions for particle p with respect to all other particles
    def findCollision(self, p: PointMass) -> list[Collision]:   

        #remove p from points to avoid considering consideration of self collision. 
        #This works since structural changes aren't back propogated in a shallow copy
        copy = self.points.copy()
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

        return Collisions

    # Resolves Collisions for particle p with respect to all other particles
    def resolveCollisions(self, p: PointMass, collisions: list[Collision]) -> Resolution | None:

        #if there are multiple collisions, we want to be able to sum the position and velocity effects
        sumPos = pg.Vector2(0, 0)
        sumVel = pg.Vector2(0, 0)
        sumAccel = pg.Vector2(0, 0)

        noCollisions: bool = True # If true, return a NoneType
        #for each collision
        for c in collisions:

            if c.depth > 0: #check if the depth is positive (if the objects are inside each other)
                noCollisions = False # Set the noCollisions flag to false, so we will return a Resolution object.
                
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

                print("Point2Point: Adding to " + str(p) + str(sumVel))
            
        if noCollisions:
            return None
        # Once we've gathered the sum of the effects of all collisions, bundle them as a resolution object
        # and return it to the upper layer for eventual execution
        return Resolution(sumPos, sumVel, sumAccel)
    
    def checkAndResolveEdgeCollisions(self, p: PointMass) -> tuple[Resolution, list[tuple[Resolution, int]]] | None:
        '''
        Function that checks if the provided PointMass is colliding with any outerConstraints. If so, calculate and provide resolutions for all involved points, and indicate which points are involved.
        '''

        # Create variables to store changes for the point
        sumPos = pg.Vector2(0, 0)
        sumVel = pg.Vector2(0, 0)
        sumAccel = pg.Vector2(0, 0)

        sumVel0 = pg.Vector2(0, 0)
        sumVel1 = pg.Vector2(0, 0)

        
        noCollisions = True # Set a noCollisions flag so we can return a None if it is never flipped
        otherResolutions: list[tuple[Resolution, int]] = []

        # NOTE: Can cull duplicate/triplicate collisions by removing from consideration edges which are connected to points that have been collided with
        # Find PointMass to Edge collisions among eligible edges (all edges minus any connected to p, and any connected to a point p has collided with this frame)
        for c in self.outerConstraints: # Each constraint acts as an edge, so we iterate through edges to check for collision

            # Do not perform for constraints connected to current PointMass
            if p.id == c.index0 or p.id == c.index1:
                continue

            # Can do this by projecting the point onto the edge and determining the point's distance from that projection

            # Surf is a vector which has the length and angle of the constraint, but casts out from the origin.
            surf: pg.Vector2 = self.points[c.index1].position - self.points[c.index0].position
            # relocate is the point in question, but which exists relative to the origin in the same way it exists relative to the point at the beginning of the constraint
            relocate: pg.Vector2 = p.position - self.points[c.index0].position
            # proj is the relocated point projected onto the vector of the surface
            proj: pg.Vector2 = relocate.project(surf)

            # Thus, if the relocated point would project onto the length of the surface, it exists at the angle of the constraint's normal to SOME point on the constraint
            if proj.magnitude() < surf.magnitude() and (proj + surf).magnitude() > surf.magnitude(): # If the projection would fall on the edge
                
                delta: pg.Vector2 = relocate - proj
                distance: float = delta.length()
                normal: pg.Vector2 = delta/distance
                depth: float = p.radius + p.radius*0.7 - distance
                slider: float = proj.magnitude() / surf.magnitude() # this is how proportionally close the projection and point of contact is to point1 from point0
                
                # This is probably mathematically incorrect, but we might calculate the projection's velocity as the sum of the endpoint velocities proportional to the slider
                projVel: pg.Vector2 = (self.points[c.index0].velocity * (1-slider)) + (self.points[c.index1].velocity * slider)

                # Check the distance between the relocated point and its projection. If it's less than radius*1.6, then collision.
                if depth > 0: # Resolve collision
                    noCollisions = False
                    # Need to remember that in this case, the projected point has momentum proportional to how close it is to the center of mass
                    momentumMult = (1+(1-2*abs(0.5-slider)))

                    # COLLISION RESOLUTION FOR INDEPENDENT POINT
                
                    # Remove point completely along the normal
                    sumPos += normal * depth
                    print(str(p) + " in static collision " + str(c) + ", removed @" + str(sumPos))

                    # NOTE: Want to revisit this to work in proportional removal.
                
                    # Compute relative momentum (and split it into tangential and normal)
                    relMomentum = p.velocity - momentumMult * projVel
                    relMomentumN = relMomentum.project(normal)
                    relMomentumT = relMomentum - relMomentumN

                    # Next, update velocity after the collision by computing forces on p
                    # Elastic force (normal)
                    impulse: pg.Vector2 = relMomentumN * self.elasticity

                    # Inelastic force (normal)
                    impulse += relMomentumN*2/3 * (1-self.elasticity)

                    # Tangential force (friction)
                    impulse += relMomentumT*2/3 * self.friction

                    sumVel -= impulse

                    print("Edge: Adding to " + str(p) + str(sumVel))
                    
                    # COLLISION RESOLUTION FOR POINTS ON CONSTRAINT

                    # Angular momentum is given L = rmv_N. Thus, the angular momentum on a point at r_0 given a collision at r_1 is
                    # L = r_1mv_N = r_0mv. Mass doesn't change, so the resulting v is equal to r_1/r_0mv_N = r_1/r_0*P_N
                    # We'll use the other point as the pivot/frame of reference.
                    # Resolution for point 0
                    # Elastic force (normal)
                    sumVel0: pg.Vector2 = (1-slider) * relMomentumN * self.elasticity
                    # Inelastic force (normal)
                    sumVel0 += relMomentumN/3 * (1-self.elasticity)
                    # Tangential force (friction)
                    sumVel0 += relMomentumT/3 * self.friction

                    print("Adding to point0 " + str(sumVel0))
                    otherResolutions.append((Resolution(pg.Vector2(0,0), sumVel0, pg.Vector2(0,0)), c.index0))
                    

                    # Resolution for point 1
                    # Elastic force (normal)
                    sumVel1: pg.Vector2 = slider * relMomentumN * self.elasticity
                    # Inelastic force (normal)
                    sumVel1 += relMomentum/3 * (1-self.elasticity)
                    # Tangential force (friction)
                    sumVel1 += relMomentumT/3 * self.friction

                    print("Adding to point1 " + str(sumVel1))
                    print("index1?" + str(c.index1))
                    otherResolutions.append((Resolution(pg.Vector2(0,0), sumVel1, pg.Vector2(0,0)), c.index1))

        
        if noCollisions:
            return None

        # Once we've gathered the sum of the effects of all collisions, bundle them as a resolution object
        # and return it to the upper layer for eventual execution
        return (Resolution(sumPos, sumVel, sumAccel), otherResolutions)

    def expand(self, x: float):
        '''
        Function which calls scaleShapeMult on every softBody with the provided x value.
        '''
        for b in self.softBodies:
            b.scaleShapeMult(x)