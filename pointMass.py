
from pygameVec2d import Vec2d

DEFAULT_GRAVITY = 4.8 # metres per second per second

MAX_SPEED = 500 # not sure speed limiting helps...

class pointMass(object):
    '''A class to deal with the physics of an object as if it was a point mass at a given point.
    object has a mass m, initial velocity u and is located at a point p
    also pass in a gravity function g.  g should take a location p and return the (gravitational) force 
    on a unit mass at point p as a vector 
    I need to work out how to do a function generator to generate a function g based on (eg) constant
    acceleration due to gravity
    
    Acceleration (a) is expressed in terms of metres per second per second
    a is the rate of change of velocity
    velocity (v) has units of metres per second
    So, for acceleration to be a rate of change of v, it must tell you by how much the velocity changes every second
    hence m/s/s 
    Example:
    initial velocity = 1
    a = 0 
    after 1 second velocity is 1 + 0*1 = 1, so with no acceleration, the velocity stays the same = 1 m/s
    if a was 2 m/s/s
    after 1 second the velocity is 1 + 2*1 = 3 so with accleration of 2 m/s/s, velocity would be 3 m/s
    after 2 seconds the velocity is 1 + 2*2 = 5 so with accleration of 2 m/s/s, velocity would be 5 m/s
    
    In the other file I have put together a class to draw wireframe (=vector) models 
    However, it can't work out the physics involved.  You don't need physics to do a game, but if you want
    it to realistically represent the physical interactions... then you do need physics. 
    
    Basic rules of physics are:
    F=ma - force is equal to mass times acceleration
    and 
    s = ut  - distance is equal to initial velocity multiplied by time. 
    
    a "vector" is like a distance, but it also has a direction. 
    If I tell you I left the house at 10 m/s you don't know where I am after 1 second because you don't know which 
    way I was going.    All you know is that I am 10 m away from the house. 
    If I tell you I left the house at 10 m/s along Bland St in the direction of the school then you know exactly where
    I am after 1 second. 
    So you need more than 1 number to represent a vector. 
    
    Vectors typically represent either a location or a velocity. 
    On a screen in Pygame, you identify points on the screen by their x and y coordinates. 
    x represents how far away you are from the left hand side of the screen
    y represents how far away you are from the top of the screen  - y is a bit weird.  As y increases, the position
    on the screen goes down. 
    This is a convention which has emerged from usage in relation to computers.  Normally, coordinates are 
    x,y increasing to the left and up respectively. 
      
    So the point (100,100) is 100 pixels from the left and 100 pixels down from the top
    
    It can also represent a velocity.  In this case, (100,100) would represent movement, at a speed of 
    100 by the square root of 2 in the direction (1,1) - diagonally down to the right at an angle of 45 degrees
   
    The speed is given by the length of the vector. 
    
    So, if we know the position of a point mass (that is, a mass which has no length, depth, or width) at one time
    and we know its velocity, then we can tell where it is at a later time. 
    '''
    
    def __init__(self, m=1, u=(0, 0), p=(0, 0),  g=None):
        self.m = m  # mass [in kilograms] mebi I should exclude 0 mass objects?
        self.v= self.convert2Vec2d(u) # v = velocity (in metres per second) should be a Vec2d object or 2-tuple
        self.p = self.convert2Vec2d(p) # p = location of the point mass should be a Vec2d object or 2-tuple
        if g is None:
            self.g = self.DEFAULT_GRAVITY
        if callable(g):
            self.g = g
        if type(g) == type(0.0):
            self.g = self.gravityFactory(g)
            
    def convert2Vec2d(self, x):
        tup = (0, 0)
        vec = Vec2d(0, 0)
        if type(x) == type(tup):
            return Vec2d(x[0], x[1])
        if type(x)== type(vec):
            return x
            # you can read my comments to see if you understand what is going on...
    
    def netForce(self,  externalForce = Vec2d(0, 0)):
        ''' Maybe also include stuff for centripetal forces?'''
        return self.g(self.p)*self.m + self.internalForce()+externalForce
    
    def DEFAULT_GRAVITY(self, p):
        return Vec2d(0, 0) # ie no gravity
    
    def gravityFactory(self, mps):
        def g( p):
            ''' Return default gravity (ie pointing down) at a rate of mps metres per second'''
            return Vec2d(0, mps)
        return g
    
    def update(self,  timeInSecs):
        '''Update the attributes of the mass based on the passage of timeInSecs (seconds) based on the previous
        values'''
#        print self.p,  self.v,  timeInSecs
        self.p = self.p + self.v *timeInSecs
        a = self.netForce()/self.m
        if self.v.length < MAX_SPEED:
            self.v += a*timeInSecs
        
#        print self.p
        
    def internalForce(self):
        # a function to model forces produced internally to the point mass - like thrust etc
        # these things will typically depend on physical characteristics of the object like how far 
        # it has been rotated
        # to be overridden when subclassed. 
        return (0, 0)
       

        
    def dumpVals(self):
        for att in ['m', 'v','p']:
            print "%s: %s"%(att, self.__getattribute__(att))
    

if __name__=='__main__':
    pass
    
