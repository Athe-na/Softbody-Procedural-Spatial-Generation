# Authored by Athena Osborne

import pygame as pg
import io
import sys
import math
from Dinosaur import Dinosaur
from Physics import Engine, PointMass, Wall

def main():

    #initialize pygame
    pg.init()

    #Begin by creating gen area
    WIDTH = int(sys.argv[1])
    HEIGHT = int(sys.argv[2])

    #initialize the window
    window = pg.display.set_mode((WIDTH, HEIGHT))
    window.fill((255,255,255))

    #example rectangle
    pg.draw.rect(window, (0, 0, 255), [100, 100, 400, 100], 2)

    #create a dinosaur and draw it
    DinoOne = Dinosaur([150, 150], 10, 6)
    #for each vertex, we need to draw one edge
    pg.draw.aalines(window, (255, 0, 0), True, DinoOne.getVerticies())
    
    
    #provide some initial points
    points: list[PointMass] = [PointMass(pg.Vector2(100, 100), pg.Vector2(20, 0), pg.Vector2(0, 0)),
                               PointMass(pg.Vector2(200, 100), pg.Vector2(-20, 0), pg.Vector2(0, 0))]
    #points.append(PointMass(pg.Vector2(300, 100), pg.Vector2(-10, 0), pg.Vector2(0, 0)))

    # Provide initial walls (NOT CURRENTLY IN USE)
    walls: list[Wall] = [Wall(pg.Vector2(0,0), pg.Vector2(100,0), 5)]

    #initialize the engine
    e = Engine(points, walls, 0.5, 0.5, WIDTH, HEIGHT)
    drawEngine(e, window)

    pg.display.update()

    #initialize sim clock and other guts of program
    clock = pg.time.Clock()
    running = True
    dt = 0

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
                            if event.type == pg.K_SLASH: #if slash is pressed, step forward a frame
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
    for p in e.points:
        print(str(p) + " @ " + str(p.position))
        pg.draw.circle(window, (0, 0, 0), p.position, p.radius, 2)

def advanceFrame(Dinosaurs):
    for A in range(Dinosaurs.size).__reversed__():
        #for each dinosaur
        for B in range(A-1).__reversed__():
            #check each other unchecked dinosaur for collision
            pass

def checkForCollision(A, B):
    #for both shapes, check if each vertex on shape 1 is within the bounds of all line segments on shape 2.
    #store B's verticies to avoid constantly grabbing it
    vertB = B.getVerticies()

    #for each vertex in A
    for point in A.getVerticies():
        #and each vertex in B
        for base in range(B.getVertexCount()):
            c = B.getPos()
            x = vertB[base]
            if base != B.getVertexCount():
                y = vertB[base+1]
            else:
                y = vertB[0]

            #check that A is not on the inside portion of ALL SIDES OF THE SHAPE
            #where the inside portion of x is the portion that the center falls on
            #first check what side the center falls on (normalized)
            side = (c[0]-x[0])(y[1]-x[1]) - (c[1]-x[1])(y[0]-x[0])
            #then check what side point falls on (normalized)
            point = (point[0]-x[0])(y[1]-x[1]) - (point[1]-x[1])(y[0]-x[0])

            #if they fall on opposite sides of any line, then there is no collision.
            if point > 0 and side < 0:
                return False
            if point < 0 and side > 0:
                return False
            
        #if we get to this point and none of them have returned false, then Point is within B and collision needs to be handled.
if __name__ == "__main__":
    main()