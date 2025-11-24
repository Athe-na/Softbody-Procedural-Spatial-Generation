# Authored by Athena Osborne

import pygame as pg
import io
import sys
import math
import random
from Dinosaur import Dinosaur
from Physics import Engine, PointMass, Wall, Constraint, cross

def main():

    random.seed(int(sys.argv[4]))

    #initialize pygame
    pg.init()

    #Begin by creating gen area
    WIDTH = int(sys.argv[1])
    HEIGHT = int(sys.argv[2])

    #initialize the window
    window = pg.display.set_mode((WIDTH, HEIGHT))
    window.fill((255,255,255))
    
    
    #provide some initial points
    points: list[PointMass] = [PointMass(pg.Vector2(200, 100), pg.Vector2(0, 0), pg.Vector2(0, 0)),
                               PointMass(pg.Vector2(250, 100), pg.Vector2(0, 0), pg.Vector2(0, 0)),
                               PointMass(pg.Vector2(175, 175), pg.Vector2(40, -140), pg.Vector2(0, 0))
                                ]
    #points.append(PointMass(pg.Vector2(300, 100), pg.Vector2(-10, 0), pg.Vector2(0, 0)))

    constraints: list[Constraint] = [Constraint(0, 1, 100, False, springConst=5),
                                     Constraint(1, 2, 240, True)
                                    ]

    # Provide initial walls (NOT CURRENTLY IN USE)
    walls: list[Wall] = [Wall(pg.Vector2(0,0), pg.Vector2(100,0), 5)]

    circle: list[PointMass] = [PointMass(pg.Vector2(300, 300), pg.Vector2(0, 0), pg.Vector2(0, 0)),
                                ]
    depth: int = 10
    unit: pg.Vector2 = pg.Vector2(1, 0)
    indexOffset = len(points)
    for i in range(depth):
        newPoint = PointMass(pg.Vector2(300, 300) + (unit * 40), pg.Vector2(random.randint(0, 100), random.randint(0, 100)), pg.Vector2(0, 0))
        circle.append(newPoint)
        constraints.append(Constraint(circle[0].id, newPoint.id, 100, springConst=5)) # Append spoke constraints
        if i != depth-1:
            constraints.append(Constraint(newPoint.id, newPoint.id + 1, 50, hard=True)) # Append wheel constraints
        else:
            print("Appending last point " + str(newPoint.id))
            constraints.append(Constraint(newPoint.id, indexOffset + 1, 50, hard=True))
        unit.rotate_ip(360/depth)
    
    points.extend(circle)

    #initialize the engine
    e = Engine(points, walls, constraints, 0.75, 0.5, 2, WIDTH, HEIGHT)
    drawEngine(e, window)
    pg.display.update()

    #initialize sim clock and other guts of program
    clock = pg.time.Clock()
    running = True
    dt = 0

    firstFramePause = False
    if str(sys.argv[3]) == "1":
        print("Paused first frame")
        e.update(dt)
        window.fill((255, 255, 255))
        drawEngine(e, window)
        pg.display.update()            
        dt = 60/1000
        firstFramePause = True
        while firstFramePause:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    firstFramePause = False
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        firstFramePause = False
                

    #Run the sim loop
    while running:
        #Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE: #if space is pressed, pause
                    paused = True
                    while paused:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                paused = False
                                running = False
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_SPACE: # if space is pressed again, unpause
                                    clock.tick(60)
                                    paused = False
                                if event.key == pg.K_s: #if s is pressed, step forward a frame
                                    print("Stepping forward")
                                    e.update(dt)
                                    window.fill((255, 255, 255))
                                    drawEngine(e, window)
                                    pg.display.update()            
                                    dt = 60/1000

        e.update(dt)
        window.fill((255, 255, 255))
        drawEngine(e, window)
        pg.display.update()            
        dt = clock.tick(60)/1000                    
        
def drawEngine(e: Engine, window):
    for c in e.constraints:
        # Get points so we can grab their position and also calculate the distance between them
        point0: PointMass = e.points[c.index0]
        point1: PointMass = e.points[c.index1]

        if c.hard: # The coloring procedure we want to use for hard constraints
            deltaLength = (point0.position - point1.position).length()
            # Use the distance to scale the color of the constraint from 0 to 1: 
            # 0 is as close together as possible (GREEN) (not possible because they'd be inside each other)
            # 1 is as far apart as possible (RED)
            colorScale = deltaLength/c.distance
            if colorScale > 1: colorScale = 1
            print(colorScale)
            # Draw a line from point0 to point1, colored according to how close they are to violating the constraint
            pg.draw.aaline(window, (int(255*colorScale), int(255*(1-colorScale)), 0), point0.position, point1.position)
        else:
            deltaLength = (point0.position - point1.position).length()
            # Use the distance to scale the color of the constraint along the parabola.
            # 2 * c.distance is max, 0 is also max, c.distance is min
            colorScale = (((deltaLength - c.distance) * (1/c.distance))  ** 2)
            if colorScale > 1: colorScale = 1 # Cap the value at 1
            
            # Draw a line from point0 to point1, colored according to how far away from neutral they are
            pg.draw.aaline(window, (50, 50, int(255 * colorScale)), point0.position, point1.position)

    for p in e.points:
        print(str(p) + " @ " + str(p.position))
        pg.draw.circle(window, (0, 0, 0), p.position, p.radius, 2)

if __name__ == "__main__":
    main()