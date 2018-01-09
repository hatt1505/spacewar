
import math
from vectorLibrary import Vec2d, Vec2dCircArc
import vectorLibrary as vl
from constants import *
import logging

logd = logging.debug


#################3
#
#  Using new structure for vector model class
#
#################

# sw model 1
mcList= []
mcList.append(vl.drawablePolygonModel(points=[(50.0,973.0),(100.0,958.0),(50.0,943.0),(65.0,953.0),(65.0,963.0)]))
mcList.append(vl.drawablePolygonModel(points= [(60.0,962.0),(65.0,962.0), (65.0,953.0),(60.0,954.0)]))#           ,(60.0,962.0)]))
mcList.append(vl.drawableVec2dLineSegment(Vec2d(75,965),Vec2d(80,958)) )
mcList.append(vl.drawableVec2dLineSegment(Vec2d(80,958), Vec2d(75,950)) )
body= vl.modelComponent(drawableObjectList = mcList)
mc2 = [vl.drawablePolygonModel(points=[(60.0, 962), (50, 957.5), (60.0, 953.0)], fillColour=WHITE)]
thruster = vl.modelComponent(drawableObjectList=mc2, trigger="thruster")

ship1ModelComponents =[body, thruster]

#sw model 2
m2pl = []
head = vl.drawablePolygonModel(points=[(87,920),(98,920),(104,910),(98,900),(87,900),(81,910)])
ship2bits = [head]
for strut in [ [(84,915),(63,910)], 
                        [(63,910), (84,904)], 
                        [(76.0,907.0), (63.0,895.0)], 
                        [(76,913), (63,925)]            
                        ]:
    p1 =Vec2d(strut[0])
    p2 = Vec2d(strut[1])
    ship2bits.append(vl.drawableVec2dLineSegment(p1, p2))

for engineblock in [ [(73.0,925.0), (48.0,925.0)], 
                                     [(73.0,895.0), (48.0,895.0)]
                    ]:
    p1 =Vec2d(engineblock[0])
    p2 = Vec2d(engineblock[1])                            
    ship2bits.append(vl.drawableVec2dLineSegment(p1, p2))

baseShip2 = vl.modelComponent(drawableObjectList=ship2bits)
thrusters2bits = []
for thrusters in [ [(73.0,925.0), (48.0,925.0), (48.0, 927.0), (73.0, 927.0)],
                                 [(73.0,895.0), (48.0,895.0), (48.0, 897.0), (73.0, 897.0)]
                                 ]:
    thrusters2bits.append(vl.drawablePolygonModel(points=thrusters,  fillColour=WHITE))
ship2Thrusters = vl.modelComponent(drawableObjectList=thrusters2bits, trigger="thruster")
ship2ModelComponents = [baseShip2, ship2Thrusters]

bulletArcList = []
bulletModel = vl.drawableV2dCA(Vec2d(0, 0),  radius = 10,  arc = None)
mcBullet = [vl.modelComponent(drawableObjectList=[bulletModel])]


##############
#
# Black Hole Sun, won't you come....
#
###############
bhsls= []
p1 = Vec2d(-100, 0)
p2 = Vec2d(100, 0)
piOn4 = math.pi/4.0

starLines =[]
for i in range(4):
    LS = vl.drawableVec2dLineSegment(p1, p2)
    starLines.append(LS)
    p1 = p1.rotatedR(piOn4)
    p2 = p2.rotatedR(piOn4)

centralStar = [vl.modelComponent(drawableObjectList=starLines)]
