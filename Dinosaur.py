import math
# Authored by Athena Osborne

class Dinosaur:

    def __init__(self, pos, size, vertexCount):
        self.size = size # Size is a rough approximation of the amount of force an object will exert during expansion
        self.vertexCount = vertexCount # Edges is the count of how many corners (and sides) the dinosaur will have

        #initialize edge coord list
        self.verticies = [[10 for i in range(2)] for vertex in range(self.vertexCount)]
        #
        for vertex in range(vertexCount):
            #find angle of current vertex
            angle = math.radians(((360/self.vertexCount)/2) + (360/self.vertexCount)*vertex)
            print("angle: " + str(angle))
            #initialize base coordinate position based on angle
            self.verticies[vertex][0] = pos[0] + math.floor(100 * math.cos(angle))
            self.verticies[vertex][1] = pos[1] + math.floor(100 * math.sin(angle))
            print("point: " + str(self.verticies[vertex][0]) + ", " + str(self.verticies[vertex][1]))
    
    def expandPreview(self):
        pass

    def expand(self, verticies):
        self.verticies = verticies

    def getVerticies(self):
        return self.verticies
    
    def getVertexCount(self):
        return self.vertexCount
    
    def getSize(self):
        return self.size

