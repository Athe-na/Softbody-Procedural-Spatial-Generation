# Authored by Athena Osborne

import ctypes

import pygame as pg
import io
import sys
import math
import random
from Dinosaur import Dinosaur
from Physics import Engine, PointMass, Wall, Constraint, SoftBody, cross

def main():

    # Code to undo display scaling from
    # https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
    print(awareness.value)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(1)

    # Seed the random function for later use with proc gen.
    random.seed(int(sys.argv[4]))

    # Initialize pygame
    pg.init()

    # Begin by creating gen area (and window size)
    WIDTH = int(sys.argv[1])
    HEIGHT = int(sys.argv[2])

    # Initialize the window
    window = pg.display.set_mode((WIDTH, HEIGHT))
    window.fill((255,255,255))
        
    # Create a list of SoftBodies
    softBodies: list[SoftBody] = [
                                  SoftBody().dottedRect(50, 50, pg.Vector2(100,100)),
                                  #SoftBody().dot(pg.Vector2(200, 110)),
                                  SoftBody().dottedRect(50, 50, pg.Vector2(800, 840))
                                  ]

    # Provide initial walls (NOT CURRENTLY IN USE)
    walls: list[Wall] = [Wall(pg.Vector2(0,0), pg.Vector2(100,0), 5)]

    
    # Initialize the engine
    e = Engine(softBodies, walls, 0.75, 0.5, 2, WIDTH, HEIGHT)
    drawEngine(e, window)
    pg.display.update()

    # Initialize sim clock and other guts of program
    clock = pg.time.Clock()
    running = True
    dt = 0
    elapsed = 0

    # By default, do not pause the program on the first frame.
    firstFramePause = False

    # If the 3rd arg is a 1, the program will initialize and stop on the first frame, going into a "stepping" mode.
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
                    if event.key == pg.K_SPACE: # This has a known error where dt is calculated as total elapsed time after unpausing from stepping mode
                        firstFramePause = False
                        dt = 60/1000
                    if event.key == pg.K_s:
                        print("Stepping forward")

                        e.update(dt)
                        elapsed += dt
                        window.fill((255, 255, 255))
                        drawEngine(e, window)
                        pg.display.update()            
                        dt = 60/1000
                

    #Run the sim loop
    while running:
        #Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE: # If space is pressed, pause
                    paused = True
                    while paused:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                paused = False
                                running = False
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_SPACE: # If space is pressed again, unpause
                                    clock.tick(60)
                                    paused = False
                                    dt = 60/1000
                                if event.key == pg.K_s: # If s is pressed, step forward a frame
                                    print("Stepping forward")
                                    e.update(dt)
                                    window.fill((255, 255, 255))
                                    drawEngine(e, window)
                                    pg.display.update()            
                                    dt = 60/1000
        
        print("scale: " + str(scaleFunc(elapsed)))
        e.expand(scaleFunc(elapsed))
        e.update(dt)
        elapsed += dt
        window.fill((255, 255, 255))
        drawEngine(e, window)
        pg.display.update()            
        dt = clock.tick(60)/1000

    print("Sim ended.")

def scaleFunc(elapsed):
    if elapsed <= 10:
        print("scaling by " + str(1 + math.sqrt(0.000001 * elapsed)))
        return (1 + math.sqrt(0.000005* elapsed))
    return 1


def drawEngine(e: Engine, window):
    for c in e.innerConstraints: # Loop to draw inner constraints as single lines
       
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

    for c in e.outerConstraints: # Loop to draw the outer constraints as a set of two lines
        
        # Get points so we can grab their position and also calculate the distance between them
        point0: PointMass = e.points[c.index0]
        point1: PointMass = e.points[c.index1]

        offset: pg.Vector2 = (point1.position - point0.position).rotate(90) # Grab the delta between them rotate that delta 90 degrees to get the offset vector
        offset.scale_to_length(point0.radius * 0.7) # Scale the offset to nearly the radius length

        # Create the four points based on the position +/- the offset
        point0L: pg.Vector2 = point0.position + offset
        point0R: pg.Vector2 = point0.position - offset
        point1L: pg.Vector2 = point1.position - offset
        point1R: pg.Vector2 = point1.position + offset

        # Draw the two lines
        pg.draw.aaline(window, (0,0,0), point0L, point1R)
        pg.draw.aaline(window, (0,0,0), point0R, point1L)

    for p in e.points: # Loop to draw each point
        print(str(p) + " @ " + str(p.position))
        pg.draw.circle(window, (0, 0, 0), p.position, p.radius)

if __name__ == "__main__":
    main()