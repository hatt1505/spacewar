'''
Copyright (C) 2012 Brendan Scott

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/

Version info:
1.0beta 22 November 2012

'''

import math
import pygame
from constants import *

from pygameVec2d import Vec2d
from copy import deepcopy
import itertools
import logging
import pickle

## Test


if __name__=="__main__":
    LOGFILE = 'vl.log'
    f = open(LOGFILE, 'w')
    f.close()
    logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)
    Logd= logging.debug
    Logd('This message should go to the log file')
    # from testLSC import  testLSC

Logd = logging.debug
from pointMass import pointMass
if __name__ =="__main__":
    SCREEN_WIDTH= 400
    SCREEN_HEIGHT = 400
    SCREEN_CENTRE = Vec2d(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

TWO_PI = math.pi*2
TYPE_TUPLE = type ((0, 0))
TYPE_VEC2D = type(Vec2d(0, 0))
COLLS_COLOUR=(255, 255, 0)
DEBUG_DRAW_COLLISION_LS= False

# I give up, using pygame's Vec2d
DEFAULT_FILL_COLOUR = (1, 1, 1)
DEFAULT_LINE_COLOUR= WHITE
FP_ERROR = 1E-6

class Vec2dShell(object):
    def __init__(self):
        self.centre = None
        self.p1 = None
        self.p2 = None
        self.points=[]
        self.baseCollisionLSList=[]
        self.baseLSList= self.baseCollisionLSList  
        # naming bounced around.  Now I think baseLSList is better for models 
        # baseLSList will be used for creating wreckage
        self.baseCollisionArcList=[]  
        self.baseArcList = self.baseCollisionArcList
        
class v2d(object):
    def __init__(self, x=0,  y =0):
        # if x is a tuple, then assign from x and ignore y
        if type(x)== type((0, 0)):
            self.x = x[0]
            self.y = x[1]
        else: # assume that they are floats or ints 
            self.x= x
            self.y = y
    def asTuple(self):
        return (self.x, self.y)
    def __mul__(self, factor):
        ''' only supports scalar multiplication'''
        return v2d(self.x*factor, self.y*factor)
    __rmul__ = __mul__
    def __div__(self, factor):
        return v2d(self.x/factor, self.y/factor)
    def __str__(self):
        return "(%s, %s)"%(self.x, self.y)


class BasicVectorFont():
    def __init__(self,  discarded,  width):
        # load predefined font  - will likely break if modelComponent class changes
        fn = "vlvectorFontMC_Dict.pickle"
        f = open(fn, 'rb')
        self.mcDict = pickle.load(f)
        f.close()
        self.width = width
        self.spriteDict={}
        for k in list(self.mcDict.keys()):
            self.spriteDict[k] = vectorSprite(renderWidth = width,  modelComponents=[self.mcDict[k]])
            self.spriteDict[k].update(1)
        
        self.renderable = list(self.spriteDict.keys())
        
        
    def render(self, textToRender, discard1=None, discard2=None, discard3 = None):
        '''Hmmm, create a  vector sprite from the text, update the vector sprite's image
        blit the image to a surface, return the surface
        Assume all characters are upper case
        lowercase will involve scaling the upper to give small caps 
        Can't pre-render because width can't be predicted '''
        
        baloney=[]
        width = int(self.width)
        
        for i in range(len(textToRender)):
            try:
                c = ord(textToRender[i].upper())
            except:
                baloney.append(" ")
                continue
            if c <48 or c >= (65+26):
                baloney.append(" ")
                continue
            elif c>57 and c < 65:  # we already know c >=48 and < 65+26
                baloney.append(" ")                
                continue
            else:
                baloney.append(chr(c))
        
        normalisedText = ''.join(baloney)
#        print "NormalisedText = %s"%normalisedText
        
        l = len(normalisedText)
        textSet = set(normalisedText.upper())
#        spriteDict = {}
#        for t in textSet:
#            if t == ' ':
#                continue
#            spriteDict[t] = vectorSprite(renderWidth = width,  modelComponents=[self.mcDict[t]])
        
        # hmmm... the sprite calculates on a square sprite so that it can rotate
        # however, the letters are longer than they are wide, 
        # so for spacing should use a width which is a proportion of the stated width
        w = int( self.width*4.0/5.0)
        surf = pygame.Surface((l*w, self.width))
        
        
        for i in range(len(normalisedText)):
            k = textToRender[i].upper()
            if k not in self.renderable:
                continue
            surf.blit(self.spriteDict[k].image, (i*w, 0))

        return surf
            
            
            


class LineSegment():
    def __init__(self, v2d1, v2d2):
        ''' 
        don't use!
        
        Define a line segment between two points represented by 2d vectors v2d1 and v2d2
        '''
        self.p1 = deepcopy(v2d1)
        self.p2 = deepcopy(v2d2)
        
    def __repr__(self):
        return "(%.0f,%.0f)-(%.0f,%.0f)"%(self.p1.x, self.p1.y, self.p2.x, self.p2.y)

class vec2dLineSegment(Vec2dShell):
    def __init__(self, vec2d1, vec2d2):
        ''' 
        Define a line segment between two points represented by 2d vectors v2d1 and v2d2
        '''
        Vec2dShell.__init__(self)
        self.p1 = vec2d1
        self.p2 = vec2d2
        self.p1p2 = self.p2-self.p1  # vector describing the line from p1 to p2g
        self.length = self.len()

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.p1 == other.p1 and self.p2 == other.p2:
            return True
        else:
            return False
            

    def basePointsAsLineSegmentList(self):
        '''return a list comprised of each line segment forming the rendered polygon 
        (ie rotated and translated)'''
        p1 = Vec2d(self.p1.x, self.p1.y)
        p2 = Vec2d(self.p2.x, self.p2.y)
        result = []
        result.append(vec2dLineSegment(p1, p2))
        return result

    def toOffsetTo(self, p):
        ''' given a point p, translate all points in self.points to be offsets from this point'''
        self.p1 = self.p1-p
        self.p2 = self.p2-p
    
    def len(self):
        v = self.p2-self.p1
        return v.get_length()

    def have_same_signs(self, a, b):
        if a > 0 and b > 0:
            return True
        if a<0 and b<0:
            return True
        return False

    def collideLSList(self, LineSegmentList):
        for L in LineSegmentList:
            if self.collideLS(L):
                return true
        return False

    def collideArc(self, arc):
        # only circle implemented!!!!
        pass
    
    def closest_point_on_seg(self, seg_a, seg_b, circ_pos):
        '''From: http://doswa.com/2009/07/13/circle-segment-intersectioncollision.html'''
        seg_v = seg_b - seg_a
        pt_v = circ_pos - seg_a
        if seg_v.get_length() <= 0:
            Logd("closest_point_on_seg: Got segment of length zero: ",  seg_a,  seg_b,  self.p1,  self.p2)
            raise ValueError("Invalid segment length")
        seg_v_unit = seg_v / seg_v.get_length()
        proj = pt_v.dot(seg_v_unit)
        if proj <= 0:
            return Vec2d(seg_a.x, seg_a.y)
        if proj >= seg_v.get_length():
            return Vec2d(seg_b.x, seg_b.y)
        proj_v = seg_v_unit * proj
        closest = proj_v + seg_a
        return closest

    def collideArc(self,  arc,  trueFalse = True):
        '''Based on http://doswa.com/2009/07/13/circle-segment-intersectioncollision.html
        Returns either true or false (if trueFalse is true) or a vector between the point of closest approach
        and the centre of the circle or (0,0) if no collision
        '''
        seg_a = self.p1
        seg_b = self.p2
        circ_pos = arc.centre
        circ_rad = arc.radius
        closest = self.closest_point_on_seg(seg_a, seg_b, circ_pos)
        dist_v = circ_pos - closest
        if dist_v.get_length() > circ_rad:
            if trueFalse:
                return False
            else:
                return Vec2d(0, 0)
        if dist_v.get_length() <= 0:
            if trueFalse:
                return True
            else:
                return closest
                #raise ValueError, "Circle's center is exactly on segment" so what??
        if trueFalse:
            return True
        offset = dist_v / dist_v.get_length() * (circ_rad - dist_v.get_length())
        return offset

    def collideLS(self, ls2):
        '''
        Test to see whether line segment ls1 collides with line segment ls2
        Collinear == collision
        Adapted from: http://pygameweb.no-ip.org/snippets/5/
        #Original author: david clark (silenus at telus.net) - submission date: april 03, 2001
        '''
        NO_COLLISION = False
        COLLISION = True
        x1 = self.p1.x
        y1 = self.p1.y
        x2 = self.p2.x
        y2 = self.p2.y
        x3 = ls2.p1.x
        y3 = ls2.p1.y
        x4 = ls2.p2.x
        y4 = ls2.p2.y

        a1 = y2 - y1  
        b1 = x1 - x2  
        c1 = (x2 * y1) - (x1 * y2)

        r3 = (a1 * x3) + (b1 * y3) + c1  
        r4 = (a1 * x4) + (b1 * y4) + c1

        if ((r3 != 0) and (r4 != 0) and self.have_same_signs(r3, r4)):
            return(NO_COLLISION)
        # this seems to assume integer arithmetic

        a2 = y4 - y3  
        b2 = x3 - x4  
        c2 = x4 * y3 - x3 * y4

        r1 = a2 * x1 + b2 * y1 + c2  
        r2 = a2 * x2 + b2 * y2 + c2

        if ((r1 != 0) and (r2 != 0) and self.have_same_signs(r1, r2)):  
             return(NO_COLLISION)

        denom = (a1 * b2) - (a2 * b1)  
        if denom == 0:  
            return(COLLISION)
        elif denom < 0:
            offset = (-1 * denom / 2)
        else:
            offset = denom / 2
        
        num = (b1 * c2) - (b2 * c1)
        if num < 0:
            x = (num - offset) / denom
        else:
            x = (num + offset) / denom

        num = (a2 * c1) - (a1 * c2)  
        if num <0:
            y = (num - offset) / denom
        else:
            y = (num - offset) / denom

        # I could probably drop some of this. But who cares. 
        #return (x, y)
        return COLLISION
        
        
    def __repr__(self):
        return "(%.0f,%.0f)-(%.0f,%.0f)"%(self.p1.x, self.p1.y, self.p2.x, self.p2.y)
        
class drawableVec2dLineSegment(vec2dLineSegment):
    def __init__(self, v2d1, v2d2,  lineColour= DEFAULT_LINE_COLOUR, 
                ignoreColourRequests= False, 
                defaultWidth = 1):
        self.lineColour = lineColour
        self.ignoreColourRequests = False
        self.defaultWidth = defaultWidth
        
        vec2dLineSegment.__init__(self, v2d1, v2d2)
        self.setMaxMin()
        self.setLongestRayLength()
        
        self.baseCollisionArcList=[]
        self.baseCollisionLSList= self.basePointsAsLineSegmentList()
        # will need to be re-initialised after translated to being relative to rotation point

    def generateBaseCollisionLists(self):
        self.baseCollisionLSList= self.basePointsAsLineSegmentList()

    def setLongestRayLength(self):
        ''' Gets longest ray from the centre.  Is more relevant after these points have been translated
        to be relative to (Eg) rotation point '''
        spam =  [math.sqrt(p.x**2.0+p.y**2.0) for p in [self.p1, self.p2]]
        spam.sort()
        self.longestRayLength =  spam[-1]
        
    def updateRenderList(self,  alpha,  scaleFactor=1,  offset=Vec2d(0, 0)):
        # one day I will scale the points once rather than each time...
        
        self.renderP1= Vec2d(self.p1.x, self.p1.y) # don't need deepcopy overhead
        self.renderP2 = Vec2d(self.p2.x, self.p2.y) # don't need deepcopy overhead
        
        self.renderP1.rotateR(alpha)
        self.renderP1 = self.renderP1*scaleFactor
        self.renderP1 = self.renderP1+offset
        
        self.renderP2.rotateR(alpha)
        self.renderP2 = self.renderP2*scaleFactor
        self.renderP2= self.renderP2+offset

    def drawMe(self, surface,  requestedColour= None,  width=1):
        if requestedColour is None or self.ignoreColourRequests:
            if width == 0:
                colour = self.fillColour
            else:
                colour= self.lineColour
        else:
            colour = requestedColour
#pygame.draw.line(Surface, color, start_pos, end_pos, width=1): return Rect
#        print "in ls- drawme p1, p2  =", self.renderP1, self.renderP2
        return pygame.draw.line(surface,  colour,  self.renderP1, self.renderP2,   width)

    def fillMe(self, surface,  requestedColour= None,  width=1):
        # no filling of a line Segment
        # just ignore
        return
    

    def setMaxMin(self):
        # hard way to do it b/c I copied/pasted from somewhere else...
        self.minx =self.p1.x  
        self.miny = self.p1.y
        self.maxx =  self.minx
        self.maxy = self.miny
        for p in [self.p1, self.p2]:
            if p.x < self.minx:
                self.minx = p.x
            if p.y < self.miny:
                self.miny = p.y
            if p.x >self.maxx:
                self.maxx= p.x
            if p.y >self.maxy:
                self.maxy = p.y


def add2d(p1, p2):
    '''Where p1 and p2 are 2-tuples'''
    return (p1[0]+p2[0], p1[1] + p2[1])
    
def scale2d(p, factor):
    return (p[0]*factor, p[1]*factor)

def rotate2d(p, alpha):
    '''Rotate through angle of alpha radians'''
    cosa = math.cos(alpha)
    sina = math.sin(alpha)
    return (p[0]*cosa - p[1]*sina, p[0]*sina+p[1]*cosa)

        
class Vec2dCircArc(Vec2dShell):
    def __init__(self,  centre,  radius,  arc = None):
        ''' Something to hold a representation of a circular arc
        p is a vec2d or a 2-tuple  representing the location of the centre of the arc
        radius is the radius of the arc, arc is a 2-tuple representing the start and finish
        of the arc in radians (from alpha = 0).  arc = None means that it is a full circle
        for collisions betwen an arc and a line segment use collideArc in the line segment
        use collideArc here for collisions with other circles - ATM arcs not implemented 
        '''
        Vec2dShell.__init__(self)
        if type(centre) == TYPE_VEC2D:
            self.centre = centre
        elif type(centre)== TYPE_TUPLE:
            self.centre = Vec2d(centre)
        self.radius = radius
        self.diameter = radius*2.0
        self.arc = arc
#        if self.arc[0] > self.arc[1]: 
#            # normalise the arc - all arcs must go anti clockwise
#            # I should probably also make these modulo 2 pi...
#            a = self.arc[0]
#            b = self.arc[1]
#            self.arc[0] = b
#            self.arc[1] = a
        ## Derived values:
        # as I am addding Vec2dCircArcs in the update section of the game maybe I shouldn't
        # be calculating minx,miny etc in the class??
        if self.arc is None:
            self.updateMinMax()
        else:
            logging.error("Arc requested, but arcs not implemented yet!!!!!")

    def toOffsetTo(self, p):
        ''' given a point p, translate centre to be an offset from this point'''
        Logd("in toOffsetTo, finding offset to point %s"%p)
        self.centre = self.centre-p
        Logd("after, centre = %s"%self.centre)

    def collideArc(self, arc):
        ''' Only for circles at the moment
        if the distance between centres is less than the sum of radii then they've collided
        '''
        c1c2 = arc.centre -self.centre
        minr = min(self.radius, arc.radius)
        maxr = max(self.radius, arc.radius)
        d = c1c2.get_length()

        # complexity to accoung for when one circle is inside the other but not intersecting
        if d > maxr+minr:
            return False
        if d < maxr-minr: # smaller circle inside larger circle
            return False
        # otherwise d is between maxr-minr and maxr+minr
        return True

    def updateMinMax(self):
        self.minx = self.centre.x - self.radius
        self.maxx = self.centre.x + self.radius
        self.miny = self.centre.y - self.radius
        self.maxy = self.centre.y + self.radius

    def __repr__(self):
#        return "Vec2dCircArc[%s, r: %s, d: %s minx: %s, maxx %s, miny %s, maxy %s]" %(
#                        self.centre, self.radius, self.diameter, self.minx, self.maxx, self.miny, self.maxy)
        return "Vec2dCircArc[%s, r: %s, d: %s]" %(
                        self.centre, self.radius, self.diameter)
        

class drawableV2dCA(Vec2dCircArc):
    def __init__(self, centre,  radius,  arc = None,  
                 lineColour= DEFAULT_LINE_COLOUR,  fillColour= DEFAULT_FILL_COLOUR, 
                 ignoreColourRequests = False ):
        self.lineColour = lineColour
        self.fillColour = fillColour
        self.ignoreColourRequests = ignoreColourRequests
        Vec2dCircArc.__init__(self,  centre,  radius,  arc)
        self.setMaxMin()
#        self.longestRayLength = self.getLongestRayLength()
        
        Logd("Initialising centre of drawableV2dCA")
        self.baseCollisionLSList=[]
        spam = Vec2d(self.centre.x, self.centre.y)
        self.baseCollisionArcList = [Vec2dCircArc(spam,  self.radius)]
        '''  A collision arc is a Vec2dCircArc comprising of a Vec2d for centre, and a radius   '''
        
        # will need to be re-initialised after translated to being relative to rotation point
    
    def generateBaseCollisionLists(self):
        spam = Vec2d(self.centre.x, self.centre.y)
        self.baseCollisionArcList = [Vec2dCircArc(spam,  self.radius)]
    
    def setLongestRayLength(self):
        ''' Gets longest ray from the centre.  Is more relevant after these points have been translated
        to be relative to (Eg) rotation point '''
        self.longestRayLength = math.sqrt(self.centre.x**2.0+self.centre.y**2.0) + self.radius 

    def updateRenderList(self,  alpha,  scaleFactor=1,  offset=Vec2d(0, 0)):
        # one day I will scale the points once rather than each time...
        
        self.renderList = []
        self.renderCentre = Vec2d(self.centre.x, self.centre.y) # don't need deepcopy overhead
        self.renderCentre.rotateR(alpha)
        self.renderCentre= self.renderCentre*scaleFactor
        self.renderCentre = self.renderCentre+offset
        self.renderCentre.toInt()
#        self.renderCentre.x = int(self.renderCentre.x)
#        self.renderCentre.y = int(self.renderCentre.y)
        self.renderRadius = int(self.radius  * scaleFactor)
        # just a number, so don't need deepcopy etc


    def drawMe(self, surface,  requestedColour= None,  width=1):
        if requestedColour is None or self.ignoreColourRequests:
            if width == 0:
                colour = self.fillColour
            else:
                colour= self.lineColour
        else:
            colour = requestedColour
        return pygame.draw.circle(surface,  colour,  self.renderCentre,  self.renderRadius, width)

    def fillMe(self, surface,  requestedColour= None,  width=0):
        self.drawMe(surface, requestedColour, width = 0)

    def setMaxMin(self):
        self.minx =self.centre.x- self.radius  
        self.miny = self.centre.y-self.radius
        self.maxx = self.centre.x+self.radius
        self.maxy = self.centre.y + self.radius


class PolygonModel( Vec2dShell):
    ''' A Class for representing polygons - mainly to preserve colouring of lines and fill colour
    All polygons are closed... Use a list of line segments for open polygons '''
    def __init__(self,  points=[]):
        # if tuples are pased to points, change to Vec2d
        # if something else passed to points - worry!
        Vec2dShell.__init__(self)
        self.points = [] 
        for p in points:
            if type(p) == type((0, 0)):
                p = Vec2d(p[0], p[1])
                self.points.append(p)
            elif type(p)==TYPE_VEC2D:
                self.points.append(p)
            
    
    def toOffsetTo(self, p):
        ''' given a point p, translate all points in self.points to be offsets from this point'''
        for i in range(len(self.points)):
            self.points[i] = self.points[i] -p
    
    def basePointsAsLineSegmentList(self):
        '''return a list comprised of each line segment forming the  base polygon 
        that is after translation to be offsets from a rotation point, but before scaling and other rotation. 
        '''
        p1 = Vec2d(self.points[-1].x, self.points[-1].y)
        p2 = Vec2d(self.points[0].x, self.points[0].y)
        result = []
        result.append(vec2dLineSegment(p1, p2))
        
        if len(self.points) > 2:  #if only two points, then only one line segment
            for i in range(len(self.points)-1):
                p1 = Vec2d(self.points[i].x, self.points[i].y)
                p2 = Vec2d(self.points[i+1].x, self.points[i+1].y)
                result.append(vec2dLineSegment(p1, p2))
        return result


class drawablePolygonModel(PolygonModel):
    '''Points needs to be a nonempty list of points (otherwise what's the point - so to speak)'''
    def __init__(self, points,  lineColour=DEFAULT_LINE_COLOUR, 
                                    fillColour=DEFAULT_FILL_COLOUR,  
                                    ignoreColourRequests = False, 
                                    ):
        self.lineColour = lineColour
        self.fillColour = fillColour
        self.ignoreColourRequests=ignoreColourRequests
        self.points = points
        PolygonModel.__init__(self, points)
        self.setMaxMin()
        self.setLongestRayLength()
        self.baseCollisionLSList = self.basePointsAsLineSegmentList() 
        self.baseCollisionArcList = []
        # will need to be re-initialised after translated to being relative to rotation point
        # this can only be done after the vectorModel has been initialised
    
    def generateBaseCollisionLists(self):
        self.baseCollisionLSList = self.basePointsAsLineSegmentList()
        self.baseLSList = self.baseCollisionLSList
    
    def updateRenderList(self,  alphaRadians,  scaleFactor=1,  offset=Vec2d(0, 0)):
        # one day I will scale the points once rather than each time...
        self.renderList = []
        for p in self.points:
            pprime = Vec2d(p.x, p.y) # don't need deepcopy overhead
            pprime.rotateR(alphaRadians)
            pprime = pprime*scaleFactor
            pprime = pprime+offset
            self.renderList.append(pprime)
    
    def setLongestRayLength(self):
        ''' Gets longest ray from the centre.  Is more relevant after these points have been translated
        to be relative to (Eg) rotation point  -ie centre at 0,0'''
        spam =  [math.sqrt(p.x**2.0+p.y**2.0) for p in self.points]
        spam.sort()
        self.longestRayLength=  spam[-1]

    def drawMe(self, surface,  requestedColour= None,  width=1):
        if requestedColour is None or self.ignoreColourRequests:
            if width == 0:
                colour = self.fillColour
            else:
                colour= self.lineColour
        else:
            colour = requestedColour

        return pygame.draw.polygon(surface,  colour,  self.renderList,   width)

    def fillMe(self, surface,  requestedColour= None,  width=1):
        self.drawMe(surface,  requestedColour,  width=0)

    def setMaxMin(self):
        self.minx =self.points[0].x  
        self.miny = self.points[0].y
        self.maxx = self.minx
        self.maxy = self.miny
        for p in self.points:
            if p.x < self.minx:
                self.minx = p.x
            if p.y < self.miny:
                self.miny = p.y
            if p.x > self.maxx:
                self.maxx= p.x
            if p.y > self.maxy:
                self.maxy = p.y
        

class modelComponent(object):
    '''A class for optional components of a vector model.   These components are only drawn when particular keys
    are set in the model. 
    Expects a single list of objects, each of which can be one of the following:
    colouredPolygonModel
    colouredLineSegment
    colouredCircularArc
    do I ever use this?
    '''
    def __init__(self,  trigger="always", drawableObjectList=[],   collideable = True):
        Logd("initialising model component.  Objectlist = \n%s"%drawableObjectList)
        self.trigger = trigger  
        self.drawableObjectList = deepcopy(drawableObjectList)
        self.collideable = collideable
        self.setMaxMin()
#        self.setLongestRayLength()  # this doesn't work until after the offset to centre has been calculated.

    def toOffsetTo(self, p):
        ''' Convert all relevant values to being relative to a Vec2d object p'''
        for o in self.drawableObjectList:
            Logd("modelComponent before to offset, points = %s, p1=%s, p2=%s"%(o.points, o.p1, o.p2))
            o.toOffsetTo(p)
            Logd("modelComponent after to offset,  points = %s, p1=%s, p2=%s"%(o.points, o.p1, o.p2))
            
    def drawMe(self, surface, requestedColour=None, width = 1):
        for o in self.drawableObjectList:
            o.drawMe(surface, requestedColour, width)
            
    def fillMe(self, surface, requestedColour=None, width = 0):
        # really just a call to drawMe with a width of 0
        # except line segments have a null fillMe function 
        for o in self.drawableObjectList:
            o.fillMe(surface, requestedColour, 0)

    def setMaxMin(self):
        spam = [o.minx for o in self.drawableObjectList]
        spam.sort()
        self.minx = spam[0]
        spam = [o.miny for o in self.drawableObjectList]
        spam.sort()
        self.miny = spam[0]
        spam = [o.maxx for o in self.drawableObjectList]
        spam.sort()
        self.maxx = spam[-1]
        spam = [o.maxy for o in self.drawableObjectList]
        spam.sort()
        self.maxy = spam[-1]
        
    def setLongestRayLength(self):
        for o in self.drawableObjectList:
            o.setLongestRayLength()
        spam = [o.longestRayLength for o in self.drawableObjectList]
        spam.sort()
        Logd( "MC.selflongestray -> %s" %spam)
        self.longestRayLength = spam[-1]

    def updateRenderList(self, alphaRadians, scaleFactor, offset):
        for o in self.drawableObjectList:
            o.updateRenderList(alphaRadians , scaleFactor, offset )
    
    def getRenderList(self):
        renderList = []
        for o in self.drawableObjectList:
            renderList = renderList+o.renderList
        
        return renderList
    
    def generateBaseCollisionLists(self):
        ''' the component objects generate a base collision list on init. '''
        
        self.baseCollisionLSList = []
        self.baseCollisionArcList = []
        if not self.collideable:
            return
        for o in self.drawableObjectList:
            o.generateBaseCollisionLists()
            self.baseCollisionLSList = self.baseCollisionLSList + o.baseCollisionLSList
            self.baseCollisionArcList = self.baseCollisionArcList + o.baseCollisionArcList
        #these are aggregated and flattened later
        
class vectorModel(object):
    ''' A list of points which will constitute the model, 
    On init determine the longest axis of the model 
    Use this to scale the model to a square of side width in pixels - so whatever angle it is rotated through it will 
    remain within a box of that size. 
    method to recalculate the points based on current angle
    Not intended for large sprites - as uses a single rect for updates/blits etc. 
    Creates its own surface, so requires pygame to be init() before instantiating an instance
    TODO: pieces which can be optionally rendered
    TODO: Maybe do arcs 
    
    Optional components: these components are drawn when a corresponding key is set.  They need to be normalised
    to the rest of the model, so on import they will go through the same normalisation process.  If they extend beyond 
    the edges of the basic model, then they will effectively resize the base model, so this needs to be taken into account 
    when sizing. 
    TODO: initial normalisation of optional points.
    TODO: some way of  filling optional polys with a nominated solid color (eg: white for thrusters)
    TODO: If collideable is set, then the lines etc for the optional component can become part of the relevant collision list.
    '''
    
    def __init__(self, renderWidth,
                 # basePointList=[], basePolygonList = [], baseLSList = [],  
                 #baseArcList=[], 
                 modelComponents= [],   # should be a list of modelComponent objects
                 collisionLSList = None,  alpha=0, omega=0,  
                 rotationPoint= None,  
                 fgColour= WHITE, 
                 bgColour=BLACK, 
                 alphaColour = BLACK, 
                 polyFillColour= (1, 1, 1)):  # not quite black, so not alpha channel
        ''' baseArcList should be a list of Vec2dCircArc objects
        '''
        
        self.AlphaColour = alphaColour
        self.bgColour = bgColour
        self.polyBG = polyFillColour
        self.fgColour = fgColour
        self.topLeft=(200, 200)
        self.alpha = alpha  # initial angle to horizontal
        self.centre = Vec2d(renderWidth/2.0, renderWidth/2.0) 
        self.rotationPoint = rotationPoint
        self.visible = True  #used????
        self.modelComponents =deepcopy(modelComponents)  #expensive, but worth it. 

        self.triggers = {'always':True}
        # tigger keys are important, values are irrelevant.
        # set the always key so that things which should always be drawn are drawn
        
#        print "got basePoly:\n", basePolygonList
        
        self.importPointLists()
        # during importation also builds basePointList and self.rotationPoint

        self.longestRay = self.getLongestRay()
        self.updateRenderWidth(renderWidth)  # need to set renderwidth through the function so it also updates the scaleFactor
        self.updateRenderList()
        #print "##########->",self.renderList

            
        self.omega =omega # initial angular velocity around centre of model in radians per second
    '''
    DONE: pass in circles 
    DONE: collision detection between circles and lines and circles and circles. 
    DONE: Collision detection <sigh>
    DONE: Pass in Polygon list, line list, circle list, render each (allows rendering of filled polygons)
    '''
    
    def getRenderList(self):
        r = []
        for o in self.modelComponents:
            r = r + o.getRenderList()
        
        return list(itertools.chain.from_iterable(r))
    
    def generateBaseLists(self):
        ''' 
        if no collisionPointList is supplied, then generate one based on the drawn lines calculated
        model components have collision lists pre-generated on init
        '''
        Logd("Generating base collision lists")
        LSAccumulator = []
        ArcAccumulator = []
        accumulator = []
        for mc in self.modelComponents:
            mc.generateBaseCollisionLists()
            LSAccumulator.append(mc.baseCollisionLSList)
            ArcAccumulator.append(mc.baseCollisionArcList)
        
        self.baseCollisionLSList = list(itertools.chain.from_iterable(LSAccumulator))
        self.baseCollisionArcList= list(itertools.chain.from_iterable(ArcAccumulator))
        self.baseLSList = deepcopy(self.baseCollisionLSList)
        self.baseArcList = deepcopy(self.baseCollisionArcList)
        Logd("BASE: LS list = %s\nArclist = %s"%(self.baseCollisionLSList, self.baseCollisionArcList))

                
    def importPointLists(self, collisionLSList = None):
        '''For each of the point lists provided, convert each point to a Vec2d representation
        basePointList will be used to do initial calculations.  But not used for rendering
        Use a combination of polyons and line segments instead'''

        Logd("Importing point lists -> setting rotation point")
        if self.rotationPoint is None:
            self.rotationPoint = self.getCentre()
        
        Logd("rotation point  = %s"%self.rotationPoint)
        for i in range(len(self.modelComponents)):
            self.modelComponents[i].toOffsetTo(self.rotationPoint)
        ### I think rotation Point could probably now be discarded (since everything is translated
        ### so it is effectively (0,0)?

        self.generateBaseLists() 
#            Logd("generated collision LS List = ")
            # TODO: need to update for modelComponent
            # this is built using pointlists relative to the rotation point
        if collisionLSList is not None:
            self.baseCollisionLSList = collisionLSList 
            # hmmm.... may need to translate these????
            logging.error("Need to do more work on user provided collisionLSList  - needs translation and rotation")

#        print "$$$$$$", self.baseCollisionLSList

    def updateRenderWidth(self, renderWidth):
        Logd("update Render Width")
        self.renderWidth=renderWidth
        self.scaleFactor = (self.renderWidth-1) /(2*self.longestRay ) 
        # subtract one as margin for rounding error
        # divide by 2* because longestRay is a half width

        self.image= pygame.Surface([self.renderWidth, self.renderWidth]).convert()
        self.image.set_colorkey(self.AlphaColour)
        self.bg= pygame.Surface([self.renderWidth, self.renderWidth]).convert()
        self.bg.fill(self.bgColour)
        self.renderR = pygame.Rect(0, 0, self.renderWidth, self.renderWidth)
        # self.image.get_bounding_rect didn't seem to work
        self.renderR.topleft  = self.topLeft

    def update(self, deltaT = 1/30.0):
        Logd("In update")
        self.rotateByTime(deltaT)
        self.image.blit(self.bg, (0, 0))
        self.updateRenderList()
            
        for o in self.modelComponents:
            if o.trigger in self.triggers:
                o.fillMe(self.image)
                o.drawMe(self.image, requestedColour=self.fgColour)
        
 
    
    def rotateByTime(self, timeInSecs):
        self.alpha += self.omega*timeInSecs

    def getCentre(self):
        '''return unweighted midpoint of max/min x/y
        '''
        minx =miny =maxx=maxy = None
        
        spamo =  [o.minx for o in self.modelComponents]
        spamo.sort()
#        print "minx: spamo = ", spamo
        try:
            optionalMinx=spamo[0]
            if minx is None or  optionalMinx < minx:
                minx = optionalMinx
        except IndexError:
            pass

            
        spamo= [o.miny for o in self.modelComponents]
        spamo.sort()
        try:
            optionalMiny=spamo[0]
            if miny is None or optionalMiny < miny:
                miny = optionalMiny
        except IndexError:
            pass            

            
        spamo= [o.maxx for o in self.modelComponents]
        spamo.sort()
        try:
            optionalMaxx= spamo[-1]
            if maxx is None or optionalMaxx > maxx:
                maxx =optionalMaxx
        except IndexError:
            pass

        spamo=[o.maxy for o in self.modelComponents]
        spamo.sort()
        try:
            optionalMaxy= spamo[-1]
            if maxy is None or optionalMaxy > maxy:
                maxy = optionalMaxy
        except IndexError:
            pass
        
        return Vec2d((minx+maxx)/2.0, (miny+maxy)/2.0)
            

    def d(self, p1, p2):
        '''distance between two points p1 and p2 (each a 2-tuple)'''
        return math.sqrt((p1[0]-p2[0])**2.0 + (p1[1]-p2[1])**2)

    def getLongestRay(self):
        '''
        Don't actually need longest line between two points
        Sufficient to determine longest distance from any point to the rotation point
        On import all of the points are converted to offsets from the rotation point
        So can just get the max of their lengths
        
        '''
        distances = []
        for o in self.modelComponents:
            o.setLongestRayLength()
            distances.append(o.longestRayLength)
            
        distances.sort()
#        print "optional Distances are:", distances
        try:
            odL = distances[-1]
        except:
            odL = 1
        return odL
        
        
    
    def dumpVals(self):
        for att in ['baseCollisionLSList', 'baseCollisionArcList', 
                            'scaleFactor','longestRay','renderWidth', 'centre', 
                            'renderR','collisionLSList', 'collisionArcList',
                            'alpha', 'omega', 'rotationPoint']:
            print("%s: %s"%(att, self.__getattribute__(att)))
        for o in self.modelComponents:
            print(o.baseCollisionLSList)
          
    def updateRenderList(self):
        # rotate and scale the basePointList to match current alpha, scaleFactor
        Logd("updating render list")

        for o in self.modelComponents:
            o.updateRenderList(alphaRadians = self.alpha, scaleFactor= self.scaleFactor, offset = self.centre)

        #TODO: update collision list for each optional bit.

        Logd("updating collsion lists")
        self.collisionLSList= []
        for LS  in self.baseCollisionLSList:
            p1 = self.updatePoint(Vec2d(LS.p1.x, LS.p1.y))
            p2 = self.updatePoint(Vec2d(LS.p2.x, LS.p2.y))
            p1 = p1+self.renderR.topleft  # need to off set it by the top left of the rectangle 
            p2 = p2+self.renderR.topleft  # to locate the sprite on the screen for collisions...
            self.collisionLSList.append(vec2dLineSegment(p1, p2))
        
        self.collisionArcList = []
        for arc in self.baseCollisionArcList:
            p1 = self.updatePoint(Vec2d(arc.centre.x, arc.centre.y))
            p1 = p1+self.renderR.topleft
            radius = arc.radius*self.scaleFactor
            self.collisionArcList.append(Vec2dCircArc(p1, radius))
        Logd("topleft = %s, scaleFactor = %s"%(self.renderR.topleft,  self.scaleFactor))
        Logd("actual LSlist = %s\nActual ArcList= %s"%(self.collisionLSList, self.collisionArcList))
        
        
    def updatePoint(self, point):
        '''This, in effect, takes a base point in the model, then rotates it and translates it so that it is 
        centred withiin the sprite's display surface - but does *not* reflect the position 
        of the point on the screen.  This will be further offset by self.rect.topleft or somesuch
        Point needs to be a Vec2d'''
        point.rotateR(self.alpha)  # what in heaven's name is going on??
        point = point*self.scaleFactor
#        print "%%%% =>", point, self.scaleFactor
        return point+self.centre
        

class vectorSprite (vectorModel, pointMass):
    '''Sprite made of drawn line vectors rather than images
    Similar methods to sprite class, but suspect probably don't want it to subclass sprite. 
    '''
    def __init__(self, renderWidth,
                            #basePointList=[], basePolygonList = [], baseLSList = [],  
                            #baseArcList=[], 
                            modelComponents=[], 
                            collisionLSList = None,  
                            alpha=0.0, omega=0.0,  
                            rotationPoint= None, 
                            m=1, u=(0, 0), p=(0, 0),  g=None, spriteName="A sprite"):
                                
        vectorModel.__init__(self, renderWidth, 
                             #basePointList,  basePolygonList, baseLSList,  
                            #baseArcList, 
                            modelComponents, 
                            collisionLSList,  
                            alpha, omega,  
                            rotationPoint)
                            
        pointMass.__init__( self, m, u, p, g) 
        self.spriteName = spriteName
        
    
    def dumpVals(self):
        print("*************** Dumping values for sprite: %s"%self.spriteName)
        print("\n** vectorModel")
        vectorModel.dumpVals(self)
        print("\n** pointMass")
        pointMass.dumpVals(self)
    
    def update(self, timeInSecs):
#        print "updating point mass, time = ", timeInSecs
        pointMass.update(self, timeInSecs)
        
        self.renderR.topleft  = self.p -self.centre 
        # the point mass is assumed to be at the centre of the *sprite*
        # if it moves as a result of its velocity, then this needs to be reflected in RenderR
        # however, must offset by *surface* centre to get a value for topleft...
        vectorModel.update(self, timeInSecs)

    
    def collideOtherSprite(self, otherVectorSprite):
        # First do naive collision detection on their render rectangles
        maxWidth = max(self.renderR.width, otherVectorSprite.renderR.width)
        maxHeight = max(self.renderR.height, otherVectorSprite.renderR.height)

        # find max width based on width recorded in render rectangles
        if  self.renderR.left-otherVectorSprite.renderR.left>otherVectorSprite.renderR.width:
            # is other close enough to right of this sprite?
            return  (False, -1, -1)
        if otherVectorSprite.renderR.left -self.renderR.left > self.renderR.width:
            # is this sprite close enough to right of other sprite? others similarly
            return  (False, -1, -1)
        if self.renderR.top - otherVectorSprite.renderR.top > otherVectorSprite.renderR.height:
            # increasing y points down
            return  (False, -1, -1)
        if otherVectorSprite.renderR.top - self.renderR.top > self.renderR.height:
            return  (False, -1, -1)
            
        compareLSList = otherVectorSprite.collisionLSList
        compareArcList = otherVectorSprite.collisionArcList
        Logd("Self collisionLSList = %s"%self.collisionLSList)
        Logd("CompareLSlist = %s\nArclist= %s"%(compareLSList, compareArcList))
        lengthOffset = len(compareLSList)
        for i in range(len (self.collisionLSList)):
            ls1 = self.collisionLSList[i]
            if ls1.length ==0:
                Logd("%s" %ls1)
                continue
            
            for j in range(len(compareLSList)):
                ls2 = compareLSList[j]
                if ls1.collideLS(ls2):
                    Logd("Collision detected, at i,j = %s,%s"%(i, j))
                    return (True, i, j)  
                    # return a tuple with whether there's a collision
                    # and, if so, the first line segments which collide (there may be more,
                    #but give up once first is found)
            for j in range(len(compareArcList)):
                arc = compareArcList[j]
                if ls1.collideArc(arc):
                    return (True,  i, j+lengthOffset)  
                    # add offset to indicate an arc ie if > length of line segments then is an arc
                    
        return (False, -1, -1)



def centralGravity(p):
    centre = SCREEN_CENTRE
    direction = centre-p
    direction = direction.normalized()*9.8
    return direction
    

if __name__ =="__main__":
#(self, basePointList, renderWidth, collisionPointList = None,  mass = 100,  alpha=0, omega=0,  gravityFunction = None,  rotationPoint= None):

    pygame.init() 
    

#    testPoints = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 0), (0, -1)]
#    rectangle = [(1, -0.5), (1, 0.5), (-1, 0.5), (-1, -0.5)]
#    
#    h1 = -100.0
#    bh = h1*2.0/3.0  # height of the base
#    h2 = 100.0
#    w1 = 50.0
#    w2 = w1*6.0/5.0
#    phi  = 1.0/2.0*math.sin(2.0*math.pi/3.0) 
#    s = -h1 * phi 
#    #  s is the length of the side of the top hexagon 
#    # if the height of the hexagon is h1, then this is equal to 2x length of side x sin 120 (ie the internal angle of a hexagon)
#    # working backwards gives s
#    hx1 = s/2.0  # x coord of start of hexagon. 
#    hx0 = hx1 - s *math.cos(2.0*math.pi/3.0)
#    hx2 = -hx1
#    hh = h1
#    # legs (reach to as deep as the top is high)
#    ly0 = -bh/3.0
#    ly1 = -h1
#    lx0 = -w1
#    lx1 = 2*lx0
#    
#    lemDes = [# bottom rectangle
#                 (-w1, -bh), 
#                 # Left support/leg
##                 (lx0, ly0), (lx1, ly1), (lx0, ly0), 
#                 # rest of base
#                 (-w1, 0), (w1, 0), 
#                 # right support/leg
##                 (-lx0, ly0), (-lx1, ly1), (-lx0, ly0), 
#                 # Finish the base
#                 (w1, -bh)]  
##                 (-w1, -bh), 
#                 # overwrite to start top hexagon
#                 #(-w1, 0)]
#                 # draw hexagon (can omit base)
#    lemAsc=[ (hx1, 0), (hx0, hh/2.0), (hx1, hh), (hx2, hh),(-hx0, hh/2.0), (hx2, 0) 
#                 ]
#                 
#    lLeg = [(lx0, ly0), (lx1, ly1)]
#    rLeg = [(-lx0, ly0), (-lx1, ly1)]
#
#    polyList = [lemDes, lemAsc]
#    lsList = [lLeg, rLeg]


#    polyList.append(rectangle)
    screen = pygame.display.set_mode([SCREEN_WIDTH,  SCREEN_HEIGHT])
    background = pygame.Surface([SCREEN_WIDTH,  SCREEN_HEIGHT])
    background.fill(BLACK)

    
   #vm = vectorModel(50, basePolygonList= polyList, baseLSList= lsList,  omega=math.pi)
#    vm.dumpVals()
    
    
    # sw model 1
    mcList= []
    mcList.append(drawablePolygonModel(points=[(50.0,973.0),(100.0,958.0),(50.0,943.0),(65.0,953.0),(65.0,963.0)]))
    mcList.append(drawablePolygonModel(points= [(60.0,962.0),(65.0,962.0), (65.0,953.0),(60.0,954.0)]))#           ,(60.0,962.0)]))
    mcList.append(drawableVec2dLineSegment(Vec2d(75,965),Vec2d(80,958)) )
    mcList.append(drawableVec2dLineSegment(Vec2d(80,958), Vec2d(75,950)) )
    body= modelComponent(drawableObjectList = mcList)
    mc2 = [drawablePolygonModel(points=[(60.0, 962), (50, 957.5), (60.0, 953.0)], fillColour=WHITE)]
    thruster = modelComponent(drawableObjectList=mc2, trigger="thruster")

    swm1= vectorSprite(50, 
                        modelComponents = [body, thruster], 
                        collisionLSList=None, 
                        omega=0,   rotationPoint= None, 
                        m=1, u=(15, 0), p=(100, 100),  g=centralGravity,  spriteName="TriangularShip") 

    #sw model 2
    m2pl = []
    head = drawablePolygonModel(points=[(87,920),(98,920),(104,910),(98,900),(87,900),(81,910)])
    ship2bits = [head]
    for strut in [ [(84,915),(63,910)], 
                            [(63,910), (84,904)], 
                            [(76.0,907.0), (63.0,895.0)], 
                            [(76,913), (63,925)]            
                            ]:
        p1 =Vec2d(strut[0])
        p2 = Vec2d(strut[1])
        ship2bits.append(drawableVec2dLineSegment(p1, p2))

    for engineblock in [ [(73.0,925.0), (48.0,925.0)], 
                                         [(73.0,895.0), (48.0,895.0)]
                        ]:
        p1 =Vec2d(engineblock[0])
        p2 = Vec2d(engineblock[1])                            
        ship2bits.append(drawableVec2dLineSegment(p1, p2))

    baseShip2 = modelComponent(drawableObjectList=ship2bits)
    thrusters2bits = []
    for thrusters in [ [(73.0,925.0), (48.0,925.0), (48.0, 927.0), (73.0, 927.0)],
                                     [(73.0,895.0), (48.0,895.0), (48.0, 897.0), (73.0, 897.0)]
                                     ]:
        thrusters2bits.append(drawablePolygonModel(points=thrusters,  fillColour=WHITE))
    
    ship2Thrusters = modelComponent(drawableObjectList=thrusters2bits, trigger="thruster")
    
    swm2 =  vectorSprite(50, 
                         modelComponents= [baseShip2, ship2Thrusters], 
                         collisionLSList=None, 
                        omega=math.pi/1.9,   rotationPoint= None, 
                        m=1, u=(-3, 0), p=(200, 100),  g=centralGravity,  spriteName="Hex Ship")



##    m2al=[]
##    m2al.append(Vec2dCircArc(Vec2d(93, 910 ), radius =12,  arc = None))
#
##    m2al.append(Vec2dCircArc(Vec2d(76.5, 910.0), radius =12,  arc = None))
#
#
#    swm2 =  vectorSprite(50, basePolygonList= m2pl, baseLSList= m2ls,  
#                        baseArcList = [], 
#                        collisionLSList=None, 
#                        omega=math.pi/1.9,   rotationPoint= None, 
#                        m=1, u=(-3, 0), p=(200, 100),  g=centralGravity,  spriteName="Enterprise")
#
    #Static Box
    box = drawablePolygonModel(points= [(100, 100), (-100, 100), (-100, -100), (100, -100)])
    mcBox = modelComponent(drawableObjectList=[box])
    staticBox =  vectorSprite(100,
                             modelComponents=[mcBox], 
                        collisionLSList=None, 
                        omega=math.pi/1.9,   rotationPoint= None, 
                        m=1, u=(0, 0), p=(200,200),  g=0.0,  spriteName="Centre Box")
    
    bulletArcList = []
    bulletModel = drawableV2dCA(Vec2d(100, 100),  radius = 10,  arc = None)
    mcBullet = modelComponent(drawableObjectList=[bulletModel])
    bullet = vectorSprite(10, 
                          modelComponents=[mcBullet], 
                        collisionLSList=None, 
                        omega=0,   rotationPoint= None, 
                        m=1, u=(20, 0), p=(100,100),  g=centralGravity,  spriteName="Bullet") 
    
    
    bagOSprites=[]
    for s in [staticBox, swm1,  swm2,  bullet]:
#    for s in [ swm1, swm2]:
        # s1 is static box s2 is triangle ship s3 must be star trek one
        bagOSprites.append(s)

   # vm.dumpVals()
    
    screen.blit(background, (0, 0))
    
    pygame.display.update()
    clock = pygame.time.Clock()
    MAINLOOP = True
    FPS = 30
    rotationRatePerSecond = 1.0
    rotating = 1
#    vm.update(1/30.0)
    r = None #screen.blit(vm.image, vm.renderR)
    #pygame.display.update([r])
    whiteSquare = pygame.Surface([30, 30]).convert()
    whiteSquare.fill(WHITE)
    
#    pm =pointMass()
#    pm.dumpVals()
    slowMo = 1
    paused = False
    count = 0
    
    while MAINLOOP:
        deltaTMillis = clock.tick(FPS)
        deltaT = deltaTMillis/(1000.0*slowMo)
        count += 1
#        if r is not None:
#            print "blitting background"
#            bgR = screen.blit(background, r, r)
#            dirtyList.append(bgR)
            

#        r = screen.blit(vm.bg, vm.renderR)

#        r = screen.blit(whiteSquare, vm.renderR)
#        dirtyList.append(r)
        if not paused:
            dirtyList = []

            for s in bagOSprites:
                r = screen.blit(background, s.renderR, s.renderR)
                dirtyList.append(r)

            for s in bagOSprites:
                s.update(deltaT)
                r = screen.blit(s.image,s.renderR) 
                dirtyList.append(r)
            
            if DEBUG_DRAW_COLLISION_LS:
                for s in bagOSprites:
                    for colLS in s.collisionLSList:
                        p1 = colLS.p1
                        p2 = colLS.p2
                        r = pygame.draw.line(screen, COLLS_COLOUR, p1, p2,  1)
                        dirtyList.append(r)
               
            
            pygame.display.update(dirtyList)
          
            for s in bagOSprites:
                if rotating != 0:
                    spam = rotating*rotationRatePerSecond*deltaT
#                    Logd("In rotate: spam= %s,  s.alpha = %s"%(spam, s.alpha))
                    s.alpha +=  spam
                    #s.update(deltaT)
            s1 = bagOSprites[0]
            s2 = bagOSprites[1]
            s3 = bagOSprites[2]
            s4 = bagOSprites[3]
            s1.fgColour = WHITE
            s2.fgColour = WHITE
            s3.fgColour = WHITE
            s4.fgColour = WHITE
            
            spam  = s1.collideOtherSprite(s2) 
            # ie box collides with triangle
            # spam is a 3 tuple of collided, i and j (being indices of collided line segments)
            #print spam
            if spam[0]:
                s1.fgColour=RED
                s2.fgColour=RED
            spam = s1.collideOtherSprite(s3)
            if spam[0]:
                s1.fgColour=RED
                s3.fgColour=RED
            spam = s2.collideOtherSprite(s3)
            if spam[0]:
                s2.fgColour=RED
                s3.fgColour=RED
                
            spam = s1.collideOtherSprite(s4)
            if spam[0]:
#                print spam
                s1.fgColour= RED
                s4.fgColour = RED
            spam = s2.collideOtherSprite(s4)
            if spam[0]:
                s2.fgColour=RED
                s4.fgColour=RED
            spam = s3.collideOtherSprite(s4)
            if spam[0]:
                s3.fgColour=RED
                s4.fgColour=RED
            
      
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                MAINLOOP = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    MAINLOOP= False
                    
                if event.key == pygame.K_LEFT:
                    print("got a left rotate")
                    rotating = 1
                    
                if event.key == pygame.K_RIGHT:
                    print("got a right rotate")
                    rotating = -1
                
                if event.key == pygame.K_s:
                    slowMo = 10
                
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    # fire thrusters
                    print("got a thruster fire")
                    s2.triggers["thruster"]=True
                    s3.triggers["thruster"]=True
                    
                    
                    #lander.dumpVals()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    print("stop right rotate")
                    rotating = 0
                        
                if event.key == pygame.K_RIGHT:
                    print("stop right rotate")
                    rotating = 0
                    
                if event.key == pygame.K_p:
                    if paused: 
                        paused = False
                    else:
                        paused = True

                if event.key == pygame.K_d:
                    for s in bagOSprites:
                        s.dumpVals()

                 
                if event.key == pygame.K_s:
                    slowMo = 1

                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    # stop thrusters
                    del s2.triggers['thruster']
                    del s3.triggers["thruster"]
                    print("got a stop thruster")      
        if count ==1:
              paused = True

    
    
