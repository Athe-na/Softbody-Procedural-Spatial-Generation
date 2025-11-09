# Authored by Athena Osborne

import pygame
import io
import sys
from Dinosaur import Dinosaur

def main():

    #initialize pygame
    pygame.init()

    #Begin by creating gen area
    WIDTH = int(sys.argv[1])
    HEIGHT = int(sys.argv[2])

    #initialize the window
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    window.fill((255,255,255))

    #example rectangle
    pygame.draw.rect(window, (0, 0, 255), [100, 100, 400, 100], 2)

    #create a dinosaur and draw it
    DinoOne = Dinosaur([150, 150], 10, 6)
    #for each vertex, we need to draw one edge
    pygame.draw.aalines(window, (255, 0, 0), True, DinoOne.getVerticies())
        

    pygame.display.update()

    #Sim loop flag
    running = True
    #Run the sim loop
    while running:
        #Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        



if __name__ == "__main__":
    main()