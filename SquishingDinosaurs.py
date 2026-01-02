# Authored by Athena Osborne

import ctypes

import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import io
import sys
import math
import random
from Physics import Engine, PointMass, Wall, SoftBody


# Initialize global events
RESET_EVENT = pg.USEREVENT + 1
SCALE_EVENT = pg.USEREVENT + 2

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

    # Run the sim for the first time, setting the reset flag on its return value 
    reset = runSim(WIDTH, HEIGHT)
    while reset: # If the reset flag is on, reset globals for relevant classes and run the sim again.
        resetSim()
        reset = runSim(WIDTH, HEIGHT)

def runSim(WIDTH, HEIGHT) -> bool:

    # Initialize the main window
    window = pg.display.set_mode((WIDTH, HEIGHT))
    window.fill((255,255,255))

    # Create the simulation window
    simWindow = pg.Surface((WIDTH-400, HEIGHT))
    simWindow.fill((255,255,255))

    # Create the side panel window
    sidePanel = pg.Surface((400, HEIGHT))
    sidePanel.fill((217, 186, 209))
    
    # Draw the side panel for the first frame
    drawSidePanel(sidePanel)

    # Place textboxes
    scaleBox = TextBox(window, WIDTH-380, 400, 100, 50, placeholdertext="Scale", fontsize=150) 

    # Place buttons
    resetButton = Button(window, WIDTH-150, 100, 100, 50, text="Reset", fontSize=25, margin=20,
                         onClick=lambda: pg.event.post(pg.event.Event(RESET_EVENT)))
    scaleX2Button = Button(window, WIDTH-150, 200, 100, 50, text="Scale x2", fontSize=25, margin=20,
                           onClick=lambda: pg.event.post(pg.event.Event(SCALE_EVENT, scale=2)))
    scaleXHALFButton = Button(window, WIDTH-150, 300, 100, 50, text="Scale x0.5", fontSize=25, margin=20,
                           onClick=lambda: pg.event.post(pg.event.Event(SCALE_EVENT, scale=0.5)))
    scaleButton = Button(window, WIDTH-150, 400, 100, 50, text="Apply Scale", fontSize=25, margin=20,
                           onClick=lambda: pg.event.post(pg.event.Event(SCALE_EVENT, scale=getScaleFromTextBox(scaleBox))))

    # Initialize sim clock and other guts of program
    clock = pg.time.Clock()
    running = True
    dt = 0
    elapsedFrames = 0 
    reset = False

    # Create a list of SoftBodies
    softBodies: list[SoftBody] = [
                                  SoftBody().dottedRect(100, 100, pg.Vector2(100,100)),
                                  SoftBody().dottedRect(100, 100, pg.Vector2(800, 840)),
                                  ]

    # Provide initial walls (NOT CURRENTLY IN USE)
    walls: list[Wall] = [Wall(pg.Vector2(0,0), pg.Vector2(100,0), 5)]

    
    # Initialize the engine
    e = Engine(softBodies, walls, 0.75, 0.5, 2, WIDTH-400, HEIGHT)
    drawEngine(e, simWindow)
    pg.display.update()

    '''
    NOT CURRENTLY USING
    # By default, do not pause the program on the first frame.
    firstFramePause = False

    # If the 3rd arg is a 1, the program will initialize and stop on the first frame, going into a "stepping" mode.
    if str(sys.argv[3]) == "1":
        print("Paused first frame")
        e.update(dt)
        simWindow.fill((255, 255, 255))
        drawEngine(e, simWindow)
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
                        elapsedFrames += 1
                        
                        simWindow.fill((255,255,255)) # Fills the sim window to wipe previous frame.
                        drawEngine(e, simWindow) # Draws the softbodies in the simWindow
                        drawApp(WIDTH, HEIGHT, window, simWindow, sidePanel) # Combines the simWindow and the sidePanel onto the main window
                        pg.display.update() # Performs the window update
            
                        dt = 60/1000
    '''                

    #Run the sim loop
    while running:
        #Event handling
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT: # If the event is a quit, stop running the program
                running = False
            
            if event.type == RESET_EVENT: # If the event is a custom reset event, set flags for reset
                reset = True
                running = False
                print("RESET_EVENT triggered")

            if event.type == SCALE_EVENT: # If the event is a custom scale event, scale according to the input from the event
                print(type(event.scale))
                softBodyScale(e, event.scale)

            if event.type == pg.KEYDOWN: # If a key is pressed...
                if event.key == pg.K_r: # If r is pressed, set flags for reset
                    reset = True
                    running = False
                if event.key == pg.K_SPACE: # If space is pressed, pause
                    paused = True
                    dt = 60/1000
                    while paused:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                paused = False
                                running = False
                                reset = False
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_SPACE: # If space is pressed again, unpause
                                    clock.tick(60)
                                    paused = False
                                    dt = 60/1000
                                if event.key == pg.K_s: # If s is pressed, step forward a frame
                                    print("Stepping forward")
                                    e.update(dt)

                                    # Code for drawing the app. Really needs to be cleaned up.
                                    simWindow.fill((255,255,255)) # Fills the sim window to wipe previous frame.
                                    drawEngine(e, simWindow) # Draws the softbodies in the simWindow
                                    drawApp(WIDTH, HEIGHT, window, simWindow, sidePanel) # Combines the simWindow and the sidePanel onto the main window
                                    pg.display.update() 

                                    dt = 60/1000

                                if event.key == pg.K_r: # If r is pressed, reset the sim
                                    reset = True
                                    paused = False
                                    running = False
                                    break

        if reset:
            break
        # Quarter step the update so that it's harder for fast moving things to break
        for i in range(4):
            e.update(dt/4)
        elapsedFrames += 1
        dt = clock.tick(60)/1000

        # Code for drawing the app. Really needs to be cleaned up.
        simWindow.fill((255,255,255)) # Fills the sim window to wipe previous frame.
        drawEngine(e, simWindow) # Draws the softbodies in the simWindow


        # Whites out the engine canvas and then draws the whole app (engine + panel) onto the window
        window.fill((255, 255, 255), rect=(0,0,WIDTH-400, HEIGHT))
        window.blit(simWindow, (0,0))
        window.blit(sidePanel, (WIDTH-400, 0))
        
        pw.update(events)
        pg.display.update() 
        

    print("Sim ended.")
    return reset

def resetSim():
    PointMass.IDCounter = 0
    Wall.IDCounter = 0
    SoftBody.IDCounter = 0
    print("Resetting...")

def getScaleFromTextBox(box: TextBox):
    text = box.getText()
    try:
        num = float(text)
        return num
    except:
        print("Invalid scale provided. Please input a number.")
        return 1
    
def softBodyScale(e: Engine, factor: float):
    e.scaleSoftBodies(factor)

def drawApp(WIDTH, HEIGHT, base: pg.Surface, engineWindow: pg.Surface, sidePanel: pg.Surface):
    
    base.fill((255, 255, 255), rect=(0,0,WIDTH-400, HEIGHT))
    base.blit(engineWindow, (0,0))
    base.blit(sidePanel, (WIDTH-400, 0))


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
            #print(colorScale)
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
        #print(str(p) + " @ " + str(p.position))
        pg.draw.circle(window, (0, 0, 0), p.position, p.radius)

def drawSidePanel(window: pg.Surface):
    pg.font.init()
    font = pg.font.Font("resources/Exo2-Regular.ttf", 200)


if __name__ == "__main__":
    main()