import pygame
pygame.init()  # init early because some imports rely on it

import time
import logging
LOGLEVEL = logging.WARNING
LOGFILE = 'sf.log'
f = open(LOGFILE, 'w')
f.close()
logFormat="%(lineno)d %(funcName)s - %(message)s"
logging.basicConfig(filename=LOGFILE,level=LOGLEVEL,  format=logFormat)
Logd= logging.debug
Logd('This message should go to the log file')


from vectorLibrary import *
import swModels as models
import math

import utilities
from constants import *
# settings can't be imported until video mode is set. 
#from SFsettings import Settings
#from settingsWidgets import settingsList

'''
TODO: tests <sigh>
TODO: problem with treatment of border.
TODO: logic for turning off messages
WONT: instructions
TODO: licensing
TODO: packaging!
TODO: fancy font effect
TODO: save settings
TODO: bullet time on collision
TODO: Seems to be a problem with thrust/speed ?
TODO: might be a problem with gravity...?
TODO: Hyperspace
TODO: customise key controls
TODO: angular momentum ?? 
TODO: partial explosions (blow off back engine etc)
TODO: explode arcs 
TODO: more models
TODO: treat border of screen as terrain.  Determine geometry by intersections etc. 
TODO: network play...
DONE: intro screen
DONE: messages
DONE: multi line messages
DONE: implement basic settings page
DONE: settings page proof of concept
DONE: number of hits should be for other ship id 
DONE: improve readOut - no overflying by ships.
DONE: auto spawn ships
DONE: no thruster graphic
DONE: wreckage gravity seems off
DONE: bullets are too small
DONE: fix wreckage creation
DONE!: Vector font :)

DONE: A geometry manager for hitting the side of the screen
DONE: thrusters 
DONE: ship controls 
  - ship 1 = aws, left shift
  - ship 2 = left,up, right, right shift
DONE: rotation
DONE: firing bullets
DONE: ship explosion 
DONE: improve explosions
DONE: for some reason initial velocity of wreckage seems to be dependent on angle alpha (???!!)
DONE: model for central sun
DONE: score

EXTRAS: gravity bombs, rotating binary suns, toroid and spherical geometries, bounce back,
electric fence, 
DONE: variations to bullet speed, gravity

'''

THRUSTER_FORCE = 150
ROTATION_RATE = math.pi*2/2.0 # 1 rotation in 4 seconds
DEFAULT_BULLET_SPEED = 120
DEFAULT_SHIP_SIZE = 25
DEFAULT_BULLET_SIZE = 5
BULLET_LIFETIME_MILLIS = 6000
DEFAULT_WRECKAGE_LIFETIME_MILLIS = 5000
DEFAULT_FPS = 40
PINK = (	255, 62, 150)
DEFAULT_EXPLOSION_SPEED =5
READOUTFONTSIZE =16
SPLASHFONTSIZE = 80
MESSAGEFONTSIZE =16
DEFAULT_READOUT_COLOR = WHITE
DEFAULT_SPLASH_COLOR = DEFAULT_READOUT_COLOR
DEFAULT_MESSAGE_COLOR = WHITE
BACKGROUND_COLOUR = BLACK
DEFAULT_RESPAWN_TIME= 3000 # measured in milliseconds
READOUT_WIDTH = 220
READOUT_HEIGHT = 60


class Controls(object):
    def __init__(self):
        self.p1Left =pygame.K_a
        self.p1Right =pygame.K_d
        self.p1Thrust =pygame.K_w
        self.p1Hyperspace =pygame.K_t
        self.p1Fire =pygame.K_TAB
        self.p1Explode =pygame.K_e
        self.p2Left =pygame.K_LEFT
        self.p2Right =pygame.K_RIGHT
        self.p2Thrust =pygame.K_UP
        self.p2Fire =pygame.K_RSHIFT
        self.p2Explode = pygame.K_o 
        self.pause =pygame.K_p
        self.quit =pygame.K_q 
        # bugger! they only have lowercase keys, need to create uppers from shift
        self.restart =pygame.K_r
        self.slowMo =pygame.K_s
        self.dumpVals =pygame.K_y
        self.settings= pygame.K_F1
        self.debugKey = pygame.K_y   # just keys to hook up functions to
        self.debugKey2 = pygame.K_u # just a key to hook up a function to
        self.introMsg = pygame.K_h



def initTerrain():
    pass

def zeroG(p):
    return (0, 0)
    
class spaceShip(vectorSprite):
    '''The space ship class takes care of a couple of additional features like:
    how many bullets it has fired (if they are accounted for)
    .... and.... errr... other characteristics of a space ship...'''
    def __init__(self, 
                            renderWidth= 35, basePointList=[], 
                            modelComponents=[], 
                            collisionLSList = None,  
                            alpha=0.0, omega=0.0,  
                            rotationPoint= None, 
                            m=1, u=(0, 0), p=(0, 0),  g=None, 
                            spriteName="A sprite", 
                            thrusterMultiplier = 1.0):
        
        vectorSprite.__init__(self, 
                                            renderWidth= renderWidth, 
                                            modelComponents=modelComponents, 
                                            collisionLSList = collisionLSList,  
                                            alpha=alpha, omega=omega,   
                                            rotationPoint= rotationPoint, 
                                            m=m, u=u, p=p,  g=g, 
                                            spriteName=spriteName)
    
        self.thrusterForce = THRUSTER_FORCE*thrusterMultiplier
        self.rotating = 0.0
        self.rotatingRate = ROTATION_RATE
        self.id = spriteName    # Ids need to be unique across sprites
        
    def update(self,  timeInSecs):
        if abs(self.rotating) > FP_ERROR:
#            print "Got a rotate..."
            offset= self.rotating*self.rotatingRate*timeInSecs
            self.alpha += offset
#            print "increased alpha by %s"%offset
        vectorSprite.update(self, timeInSecs)
    
    def setThrusterState(self, OnOff = False):
        if OnOff == True:
            self.triggers['thruster']= True  # triggers is inherited
        else:
            if 'thruster' in self.triggers:
                del self.triggers['thruster']
    
    def internalForce(self):
        if 'thruster' in self.triggers:
            unitVector = Vec2d(1, 0)
            unitVector.rotateR(self.alpha) #self.alpha is inherited from vectorModel
            return unitVector*self.thrusterForce

        else:
            return (0, 0)
        

class bullet(vectorSprite):
    '''Return a vectorSprite bullet object emerging from a ship
    may need to add a bullet spot vector on the ship?
    Unfortunately that would require mixing graphics concerns with other concerns in the wrong class
    <sigh> won't worry about it for now '''
    def __init__(self, ship, gravity,  bornAt,  id,  speedMultiplier = 1.0,  bulletLifeMultiplier = 1.0):
        Logd('making a bullet, speedMultiplier = %s'%speedMultiplier)
        initialDirection = Vec2d(1, 0)
        initialDirection.rotateR(ship.alpha)
        initialVelocity = initialDirection * DEFAULT_BULLET_SPEED* speedMultiplier
        v = ship.v + initialVelocity
        p = ship.p+(initialDirection*ship.renderWidth)
        #Logd("%s"%models.bullet['arcList'])
        vectorSprite.__init__(self, 
                        DEFAULT_BULLET_SIZE, 
                        modelComponents=models.mcBullet, 
                        collisionLSList=None, 
                        omega=0,   rotationPoint= None, 
                        m=1, u=v, p=p,  
                        g=gravity ,  spriteName="Bullet #%s"%id) 
        self.bornAt = bornAt
        self.dieAt = bornAt + BULLET_LIFETIME_MILLIS*bulletLifeMultiplier
        self.id = id
        self.whatAmI = "bullet"
        self.shipId = ship.id


class bulletManager(object):
    '''A class to keep track of bullets, including expring them if necessary 
    TODO: Track bullets per ship
    DONE: expire bullets after a certain flight time
    '''
    def __init__(self):
        self.bullets={}
        self.bulletCounter = 0
        
    def newBullet(self, ship, gravity,  gameTime,   geometryManager, speedMultiplier = 1.0, bulletLifeMultiplier = 1.0):
        '''Not sure if I should use gameTime or framecount to keep track of the bullets'''
        b = bullet(ship, gravity,   gameTime, self.bulletCounter,  speedMultiplier, bulletLifeMultiplier)
        self.bullets[self.bulletCounter]=b
#        Logd("Got %s bullets at the moment, and counter = %s"%(len(self.bullets), self.bulletCounter))
        self.bulletCounter +=1
        geometryManager.addObject(b)
        # managing expiry in game class, so don't need to do it here
        # may not have need for a bullet manager...
              
    def delBullet(self, b):
        del self.bullets[b.id]
        
class Terrain(vectorSprite):
    def __init__(self, terrainWidth, modelComponents,   
                 m,    p,  bornAt,  id, omega=0.0, u = (0, 0),  gravity=0.0, lifeTimeMillis=1e6):
        Logd('making terrain')
        vectorSprite.__init__(self, 
                        renderWidth=terrainWidth, 
                        modelComponents=modelComponents, 
                        collisionLSList=None, 
                        omega=omega,   rotationPoint= None, 
                        m=m, u=u, p=p,  
                        g=gravity ,  spriteName="Terrain.%s"%id) 
        self.bornAt = bornAt
        self.dieAt = bornAt + lifeTimeMillis
        self.id = id


class geometryManager(object):
    ''' Manage the geometry of the screen
    To manage an object, the geometryManager expects the object to have the attributes:
    renderR - render rectangle
    width = width of the "sprite" (hmmm part of renderR
    v  - velocity of the object
    an "update" method
    Initially the geometry is just "bounce off", (no change in orientation) but hopefully later will do other geometries.
    name - object name?  
    Objects must have a unique id attribute when passed in.
    This is the key used by the geometryManager to keep track of the objects
    How do I add/remove objects??? 
    Return an ID that the object stores?
    can't use object name because "bullet" will be a shared name 
'''
    def __init__(self,   screen,  background, screenWidth, screenHeight, ):
        self.screen = screen
        self.bg = background
        self.minx = 0
        self.miny = 0
        self.maxx = screenWidth
        self.maxy = screenHeight
        self.managedObjects ={}
        self.geometryFunction = self.bounceOff
        
    
    def addObject(self, object):
        k= object.id
        if k in self.managedObjects:  
            self.delObject(k)  # sigh,need to delete old object so it's blitted over on the screen 
        self.managedObjects[k] = object

    def delObject(self,k):
        try:
            o = self.managedObjects[k]
            r = self.screen.blit(self.bg, o.renderR, o.renderR)
            pygame.display.update(r)
            del self.managedObjects[k]
        except:
            Logd ("Geometry manager failed to delete key %s"%k)
            Logd("Existing keys are: %s", list(self.managedObjects.keys()))

    def update(self, timeInSecs):
        dirtyList = []
        
        for o in list(self.managedObjects.values()):
            r = self.screen.blit(self.bg, o.renderR, o.renderR)
            dirtyList.append(r)
        
        for o in list(self.managedObjects.values()):
            self.geometryFunction(o)
            o.update(timeInSecs)
            r = self.screen.blit(o.image,o.renderR)   
            Logd("Id: %s blitted o image: %s, renderR:%s"%(o.id, o.image, o.renderR))
            # I will probaby need to move the blitting to the geometryFunction
            dirtyList.append(r)
            
        pygame.display.update(dirtyList)


    def bounceOff(self, o):
        ''' called to determine if object o has hit a wall and, if so, bounce it off the wall '''
        tx = o.renderR.topleft[0]
        ty = o.renderR.topleft[1]
        w = o.renderR.width
        h = o.renderR.height
        # ideally would be getting maxx, minx, maxy,miny from the object otherwise won't bounce
        # directly from the object, but rather from the bounding rectangle

        #TODO: do I need to change the p  rather than topleft?  yes as topleft will be overwritten on first update?
        #TODO: I probably need some form of debounce here...

        if tx < self.minx:
            o.renderR.topleft = (self.minx, o.renderR.topleft[1])  # stop going past wall
            Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (o.id, tx, ty, w, h, o.v.x, o.v.y))
            if o.v.x < 0:
                o.v.x = -o.v.x  # reverse the x component of velocity
            return
        if tx + w > self.maxx:
            o.renderR.topleft = (self.maxx, o.renderR.topleft[1])
            if o.v.x > 0:
                o.v.x = -o.v.x
            Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (o.id, tx, ty, w, h, o.v.x, o.v.y))

        if ty < self.miny:
            o.renderR.topleft = (o.renderR.topleft[0], self.miny)
            if o.v.y < 0:
                o.v.y = -o.v.y
            Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (o.id, tx, ty, w, h, o.v.x, o.v.y))

        if ty + h > self.maxy:
            o.renderR.topleft = (o.renderR.topleft[0], self.maxy)
            if o.v.y > 0:
                o.v.y = -o.v.y
            Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (
            o.id, tx, ty, w, h, o.v.x, o.v.y))

        # if tx == self.minx:
        #     o.renderR.topleft = (self.maxx, o.renderR.topleft[1])  # stop going past wall
        #     Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (
        #     o.id, tx, ty, w, h, o.v.x, o.v.y))
        #     # if o.v.x < 0:
        #     #     o.v.x = -o.v.x  # reverse the x component of velocity
        #     return
        # if tx == self.maxx:
        #     o.renderR.topleft = (self.minx, o.renderR.topleft[1])
        #     # if o.v.x > 0:
        #     #     o.v.x = -o.v.x
        #     # Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (
        #     # o.id, tx, ty, w, h, o.v.x, o.v.y))
        #
        # if ty == self.miny:
        #     o.renderR.topleft = (o.renderR.topleft[0], self.maxy)
        #     # if o.v.y < 0:
        #     #     o.v.y = -o.v.y
        #     # Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (
        #     # o.id, tx, ty, w, h, o.v.x, o.v.y))
        #
        # if ty == self.maxy:
        #     o.renderR.topleft = (o.renderR.topleft[0], self.miny)
        #     # if o.v.y > 0:
        #     #     o.v.y = -o.v.y
        #     # Logd("bounce: Id: %s tx: %s, ty: %s, w: %s, h: %s o.v.x: %s, o.v.y: %s " % (
        #     # o.id, tx, ty, w, h, o.v.x, o.v.y))


def collisionDetection(game):



    # move this to be a method of game?
    for k, s in list(game.ships.items()):
        for b in list(game.bm.bullets.values()):
            spam = s.collideOtherSprite(b)
            if spam[0]:
                game.explode(s.id)
                game.noOfHits[s.id] +=1
                b.dieAt = 0 # expire the bullet
                break
        spam = s.collideOtherSprite(game.sun) # need to be more sophisticated with terrain
        if spam[0]:
            s.v = Vec2d(0, 0) # stop the ship!
            game.explode(s.id,  gravity=zeroG)
            game.noOfHits[s.id] +=1
            break
    
    for b in list(game.bm.bullets.values()):
        spam = game.sun.collideOtherSprite(b)
        # TODO: Check for all terrain collisions, not just sun (if other terrain)
        if spam[0]:
            Logd("Bullet collision id = %s"%b.id)
            game.gm.delObject(b.id)
            game.bm.delBullet(b) 
    
    if len(game.ships)>1:
        spam = game.ship1.collideOtherSprite(game.ship2)
        for k, s in list(game.ships.items()):
            if spam[0]:
                game.explode(s.id)
                # game.explode(game.ship2.id)
            # b.dieAt = 0  # expire the bullet
            # game.ship1.fgColour = PINK
            # game.ship2.fgColour = PINK
            

    
class wreckageSprite(vectorSprite):
    '''  
    feed in a single line segment to this and it will calculate the base values to 
    give the line segment with the  same render location 
    lineSegment gives render locations on the screen of the line segment.
    '''
    def __init__(self, copyFrom, 
                            lineSegment = drawableVec2dLineSegment(Vec2d(0, 0), Vec2d(1, 0)), 
                            alpha=0.0, omega=0.0,  
                            rotationPoint= None, 
                            m=1, u=(0, 0), p=(0, 0),  g=None, 
                            spriteName="Wreckage...", id = "Wreckage", 
                            bornAt = 0,  lifeTime = DEFAULT_WRECKAGE_LIFETIME_MILLIS):
        
        Logd("Initialising wreckageSprite")
        self.bornAt = bornAt
        self.dieAt = self.bornAt+lifeTime
        self.LS = lineSegment
        self.renderWidth = copyFrom.renderWidth
        self.alpha = copyFrom.alpha
        self.AlphaColour = copyFrom.AlphaColour
        self.bgColour = copyFrom.bgColour
        self.fgColour = copyFrom.fgColour
        self.centre =copyFrom.centre
        self.g = g
        self.topLeft = (copyFrom.topLeft[0], copyFrom.topLeft[1])
        self.longestRay = copyFrom.longestRay
        self.scaleFactor = copyFrom.scaleFactor
        self.id = id
        self.m = copyFrom.m
        self.p = Vec2d(copyFrom.p.x, copyFrom.p.y)
        self.omega = copyFrom.omega
        self.copyFromV = Vec2d(copyFrom.v.x, copyFrom.v.y)
        
        mc = modelComponent(drawableObjectList = [lineSegment])
        self.modelComponents = [mc]
        vectorSprite.generateBaseLists(self)        


        self.renderR = pygame.Rect(0, 0, self.renderWidth, self.renderWidth)
        self.renderR.topleft  = self.topLeft
        self.setInitialVelocity()
        Logd("BEFORE vector sprite init: renderR = %s p = %s"%(self.renderR, self.p))
        vectorSprite.__init__(self, 
                                            renderWidth= self.renderWidth, 
                                            modelComponents=[mc], 
                                            collisionLSList = [],  
                                            alpha=self.alpha, omega=self.omega,   
                                            rotationPoint= rotationPoint, 
                                            m=self.m, u=self.v, p=self.p,  g=self.g, 
                                            spriteName=spriteName)
        Logd("After vector sprite init: renderR = %s p = %s"%(self.renderR, self.p))

        

    def setInitialVelocity(self):
        '''This sprite is a piece of the ship which has exploded. It should have a velocity radially out from the centre.
        The centre of the sprite should be given by (0,0) so find the vector joining the midpoint of the line segment and
        (0,0), scale that as appropriate to give v.x
        Possibly could offset by velocity of the ship...?'''
        
        ''' Hmmm... despite being rotated, the wreckage pieces end up having the same mid points etc, when really
        they should be rotated through math.pi (actually copyFrom.angle) radians...
        So, how come they are drawn in the right location, but initial velocity is wrong?
        probably because LS is used as the base line segment and is therefore rotated through alpha
        when being rendered 
        Therefore I need to rotate through self.alpha here before calculating the initial velocity'''
        p1 =Vec2d(self.LS.p1.x, self.LS.p1.y)
        p2=Vec2d(self.LS.p2.x, self.LS.p2.y)
        p1.rotateR(self.alpha)
        p2.rotateR(self.alpha)
        p1p2 = p2-p1
        midpoint = p1 + (p1p2*0.5)
        pToMidpoint = midpoint-self.p
    
        Logd("SETINITIALVELOCITY: id: %s  LS = %s, p1p2 = %s midpoint = %s pToMidpoint = %s "%(self.id, self.LS, p1p2, midpoint, pToMidpoint))
        self.v = self.copyFromV + midpoint/midpoint.length*DEFAULT_EXPLOSION_SPEED
        

    def importPointLists(self, *args):
        pass

    def getLongestRay(self):
        pass
    
    def update(self, timeInSecs):
        Logd("BEFORE vector sprite %s update: renderR = %s p = %s v = %s (%s)"%(self.id, self.renderR, self.p,  self.v, self.v.length))
        
        vectorSprite.update(self, timeInSecs)
        
        Logd("After  vector sprite %s update: renderR = %s p = %s v = %s"%(self.id, self.renderR, self.p,  self.v))
    def updateRenderWidth(self, renderWidth):
        #self.renderWidth=renderWidth
        #self.scaleFactor = (self.renderWidth-1) /(2*self.longestRay ) 
        # subtract one as margin for rounding error
        # divide by 2* because longestRay is a half width

        self.image= pygame.Surface([self.renderWidth, self.renderWidth]).convert()
        self.image.set_colorkey(self.AlphaColour)
        self.bg= pygame.Surface([self.renderWidth, self.renderWidth]).convert()
        self.bg.fill(self.bgColour)


class Game(object):
    '''A class to hold all the 'globals' for the game
    spaceships and bullets need to have unique ids (=name for space ship) 
    to be able to be managed properly
    Not sure if Game should be a subclass of settings or whether it should just have a settings object in it. 
    '''
    class delayedAction(object):
        def __init__(self,  triggerAtGameTime, runFunctionOnTrigger,  argTuple):
            self.triggerAtGameTime = triggerAtGameTime
            self.runFunctionOnTrigger = runFunctionOnTrigger
            self.argTuple = argTuple
            # any need to have a retrigger ability????
    
    
    def __init__(self, screenWidth= SCREEN_WIDTH, screenHeight = SCREEN_HEIGHT,  
                 gravity = None,  # gravity ought to be a function which takes gravityScale as a parameter 
                 FPS = None,
                 ship1 = None,  ship2 = None, caption=CAPTION):
                     
        self.delayedActions = []
        self.clock = pygame.time.Clock()
        self.screenWidth = screenWidth
        self.screenHeight=screenHeight
        self.screen =  pygame.display.set_mode([screenWidth,  screenHeight])
        self.background =  pygame.Surface([screenWidth,  screenHeight])
        self.caption=pygame.display.set_caption(caption)
        # given that the background is just black, maybe I don't need such a bit surface?
        self.background.fill(BACKGROUND_COLOUR)
        self.screen.blit(self.background, (0, 0))
        self.readoutBackground = pygame.Surface([READOUT_WIDTH, READOUT_HEIGHT])
        self.readoutBackground.fill(BACKGROUND_COLOUR)
        pygame.display.update()  # could possibly do this a little later?
        
        from SWsettings import Settings
        from settingsWidgets import settingsList

        self.settings = Settings(header ="SPACE WAR SETTINGS",  footer = "",
                                     settingsList = settingsList,  # imported from constants
                                     fgColour=WHITE,  bgColour= BLACK)
        self.createAttrsFromSettings()
        self.messageFont = BasicVectorFont(None, MESSAGEFONTSIZE)
        self.msgRects = None  # owise a rect if there is a message being displayed.
        
        if gravity is None:  # pass 0.0 to gravity for no gravity
            self.gravity = utilities.gravityFactory( gravityScale = self.gravityScale) # default central gravity
        else:
            self.gravity = gravity
        
        if FPS is not None:
            self.FPS = FPS
        else:
            FPS = DEFAULT_FPS

        self.gm = geometryManager(self.screen, self.background, 
                                                self.screenWidth, self.screenHeight)
        
        self.bm = bulletManager()
        self.loopCounter = 0 
        self.gameTime = 0
        self.paused = False
        self.slowMo = 1.0
        self.MAINLOOP = True

        self.explosionSpeed = DEFAULT_EXPLOSION_SPEED
        self.sun = Terrain(terrainWidth=15,  modelComponents=models.centralStar,  m =1e6,  p =SCREEN_CENTRE, 
                                            bornAt= self.gameTime,  id="Local_Star", omega = math.pi/7.0,  u = (0, 0),  gravity = 0.0, 
                                            lifeTimeMillis = 1e6)
        self.gm.addObject(self.sun)
        
        self.initShips(ship1, ship2)
        self.noOfHits={self.ship1.id:0,  self.ship2.id:0}
        self.initAttrsFromSettings()
        # self.show_go_screen()
#        self.showIntroMessage()

    
    def createAttrsFromSettings(self):
        for s in self.settings.settingsList:
            k = s.id
            v = s.value  
            self.__setattr__(k, v)
            Logd("got attribute, %s at value %s"%(k, self.__getattribute__(k)))
    
    def showIntroMessage(self, i):
        introMessage = '''Press space bar to play again '''



        self.message(i+introMessage, 10000)

    def initAttrsFromSettings(self):
        # given settings, initialise attributes from the values stored in settings
        # when called initially, values will be default values. 
        for s in self.settings.settingsList:
            k = s.id
            v = s.value  
            self.__setattr__(k, v)
            Logd("got attribute, %s at value %s"%(k, self.__getattribute__(k)))
        # TODO: link these values to the game mechanics
        
        self.gravity = utilities.gravityFactory( gravityScale = self.gravityScale)  # needs some way of affecting a custom gravity factory/function
        self.ship1.g = self.gravity
        self.ship2.g = self.gravity
        self.ship1.thrusterForce = THRUSTER_FORCE*self.thrusterMultiplier
        self.ship2.thrusterForce = THRUSTER_FORCE*self.thrusterMultiplier


    def initSettingsFromAttrs(self):
        d = {}
        for s in self.settings.settingsList:
            k = s.id
            v = self.__getattribute__(k)
            d[k]=v
        self.settings.initFromDict(d)

    def initShips(self,  ship1 = None,  ship2= None):
        '''Idea is that ships can be initialised separately from the terrain etc
        That way (eg) bullets can continue flying when the ships are reinstated (or not?)'''

        if ship1 is None:
            ship1 =spaceShip(renderWidth=DEFAULT_SHIP_SIZE, 
                        modelComponents= models.ship1ModelComponents, 
                        collisionLSList=None, 
                        omega=0.0,   
                        rotationPoint= None, 
                        m=1, u=(0, 0), p=(100, 200),
                        alpha = 0.0,    # facing right  
                        g=self.gravity,  
                        spriteName="Triangle Ship", 
                        thrusterMultiplier = self.thrusterMultiplier)
        if ship2 is None:
           ship2 = spaceShip(renderWidth=DEFAULT_SHIP_SIZE, 
                    modelComponents=models.ship2ModelComponents, 
                    collisionLSList=None, 
                    omega=0.0,   
                    rotationPoint= None, 
                    m=1, u=(0, 0), p=(SCREEN_WIDTH-100, SCREEN_HEIGHT-200),  
                    alpha = math.pi,   # facing left
                    g=self.gravity,  
                    spriteName="Hex Ship", 
                    thrusterMultiplier = self.thrusterMultiplier)

    
        if 'ships' not in dir(self):
            self.ship1 = ship1
            self.ship2 = ship2
            self.ships = {self.ship1.id:self.ship1, self.ship2.id:self.ship2}
            self.gm.addObject(self.ship1) 
            self.gm.addObject(self.ship2)
        else:
            if  ship1.id not in self.ships:
                self.ship1 = ship1
                self.ships[self.ship1.id]=self.ship1
                self.gm.addObject(self.ship1) 
            if  ship2.id not in self.ships:
                self.ship2 = ship2
                self.ships[self.ship2.id]=self.ship2
                self.gm.addObject(self.ship2)

    def explode(self, shipId,  gravity=None):
        '''when a ship gets hit, decompose it into its camponent line segments and 
        create sprites out of each of them moving away from the centre of the ship
        delete the ship from self.ships and from the geometryManager
        Other stuff would be needed to restart 
        Don't need to change event handling as ship object will still be in the relevant attribute in game
        I should keep the same renderwidth, then I can inherit p etc from the ship blowing up, and just pass
        in a single point?  (but then it will be scaled incorrectly... bugger)
        '''
        crash_sound = pygame.mixer.Sound("Crash.wav")

        pygame.mixer.Sound.play(crash_sound)

        if gravity is None:
            gravity= self.gravity  # use default gravity if none specified
            
        Logd("In Explode shipid = %s"%shipId)
        s = self.ships[shipId]  # alittle circular I could just pass in the ship??
        shipCentre = Vec2d(s.p.x, s.p.y)
        bitsOfShip = []

        count = 0
        for ls in s.baseLSList:  # these things should already be Vec2dLineSegments?
            count += 1
            LS = drawableVec2dLineSegment(ls.p1, ls.p2)
            if LS.length  < FP_ERROR:
                # skip if line segment is of zero length
                Logd("Not adding wreckage for line segment: %s"%(LS))
                continue
            a = wreckageSprite(copyFrom = s,  lineSegment = LS,  id="Wreckage_%s.%s"%(s.id, count),  g= gravity, 
                               bornAt = self.gameTime)
            self.gm.addObject(a)

        # Do I need to worry about keeping a copy of the wreckage sprites?
        # other than in the gm?

        del self.ships[s.id]
        reinstateShip = self.delayedAction(self.gameTime+DEFAULT_RESPAWN_TIME,  self.initShips, ()) 
        self.delayedActions.append(reinstateShip)
        self.gm.delObject(s.id)

        Logd("Geometry manager now managing: \n%s"%list(self.gm.managedObjects.keys()))

        for k, s in list(self.gm.managedObjects.items()):
            Logd("Id: %s\nrenderR: %s\t Renderlist: %s"%(s.id, s.renderR, s.getRenderList))
        
    def killTheOld(self):
        for o in list(self.gm.managedObjects.values()):
            if not 'dieAt' in dir(o):
                continue
            if game.gameTime > o.dieAt:
                self.gm.delObject(o.id)
                if 'whatAmI' in dir(o):
                    if o.whatAmI == 'bullet':
                        self.bm.delBullet(o)

    def readOut(self):
        '''
        Readout is blitted to the actual game background so ships can fly in front of it
        Readout is blitted over by a special readoutBackground surface
        '''
        # Used to manage how fast the screen updates
        readOutFont = BasicVectorFont(None, READOUTFONTSIZE)

        readOutColour = DEFAULT_READOUT_COLOR  # maybe change this?
        ALIGN_RIGHT = 40
        dirtyList = []

        roX = self.screenWidth / 2 - READOUT_WIDTH / 2
        roY = 20
        readoutR = pygame.Rect(roX, roY, READOUT_WIDTH, READOUT_HEIGHT)



        s1 = readOutFont.render("%s :"%self.ship1.id, True, readOutColour,BACKGROUND_COLOUR)  # render the message
        s2 = readOutFont.render("%s :"%self.ship2.id, True, readOutColour,BACKGROUND_COLOUR)  # render the message
        s3 = readOutFont.render("%s."%self.noOfHits[self.ship2.id], True, readOutColour,BACKGROUND_COLOUR)  # render the message
        s4 = readOutFont.render("%s." % self.noOfHits[self.ship1.id], True, readOutColour,BACKGROUND_COLOUR)  # render the message

        # s5 = readOutFont.render("%s :" % output_string, True, readOutColour, BACKGROUND_COLOUR)  # render the message

        # the "." character is intended to be unprintable
        # just there to address a rendering bug for 3 and 8.

        width = max(s1.get_rect().right, s2.get_rect().right)
        s1x = roX + width - s1.get_rect().right
        s2x = roX + width - s2.get_rect().right
        offset = int(READOUTFONTSIZE*3.0*4.0/5.0)+4  # magic x offset for scores (right align)
        s3x = roX+width+offset - s3.get_rect().right
        s4x = roX+width+offset - s4.get_rect().right
        # s5x = roX + width - s5.get_rect().right

        self.background.blit(self.readoutBackground, (roX, roY))  # overwrite the message

        self.background.blit(s1, (s1x, roY))  # blit s to the background
        self.background.blit(s3, (s3x, roY))
        self.background.blit(s2, (s2x, roY+20))  # Next row of text
        self.background.blit(s4, (s4x, roY+20))
        # self.background.blit(s5, (s5x, roY + 40))

        self.screen.blit(self.background, (roX, roY),  readoutR)  # blit the background to the screen - need to blit an area, not whole thing
        pygame.display.update(readoutR)   # update the screen
        # wtf?
        # pygame.display.flip()

        

    def splashScreen(self,  interlinePause=800,   timeout = 800):
        '''Display a simple splash screen on program start for timeout milliseconds
        blocking pause - Game does not update in this time!
        '''
        splashFont = BasicVectorFont(None, SPLASHFONTSIZE)
        splashColour = DEFAULT_SPLASH_COLOR
        splashWidth = 300
        splashHeight = 300
        dirtyList = []
        splashBackground = pygame.Surface([splashWidth, splashHeight])
        splashBackground.fill(BACKGROUND_COLOUR)
        roX = 200
        roY = 100
        blitRect = pygame.Rect(roX, roY,  splashWidth, splashHeight)  
        splash1 = splashFont.render("Space", True,  splashColour,  BACKGROUND_COLOUR)
        s1x = roX
        r1 =self.screen.blit(splash1, (s1x, roY))  # blit s to the background

        pygame.display.update(r1)
        
        time.sleep(interlinePause/1000.0)
        
        splash2 = splashFont.render("War",  True,  splashColour,  BACKGROUND_COLOUR)
        s2x= roX+180
        r2= self.screen.blit(splash2, (s2x, roY+180))  # Next row of text
        pygame.display.update(r2)

        time.sleep(timeout/1000.0)
        
        for r in [r1, r2]:
                self.screen.blit(self.background, (r.left, r.top),  r)
        pygame.display.update([r1, r2])
        
    def message(self, msg,  timeout=5000):
        '''message area is the space in horizontal centre, 3/4 down 
        Blit a message to the message area
        and lodge a delayed action to blit over it after the timeout expires
        Need to check if there is already a message being displayed
        and, if so... 
        what? clear it?  delay this msg?
        if have set a delayed action to clear it, then it will clear the new mesg too early
        DONE: multiline text?
        '''
        
        messageColour = DEFAULT_MESSAGE_COLOR 
        msgList = msg.split('\n')
        msgSurfs = []
        height = 0
        width = 0
        lineSpacing = 1.5
        for line in msgList:
            msgSurfs.append(self.messageFont.render(line, True, messageColour,BACKGROUND_COLOUR))
            r = msgSurfs[-1].get_rect()
            height += r.bottom*lineSpacing
            width = max(width, r.right)
        
        msgCentrex = self.screenWidth/2.0  #float division, will need to round later for pixel
        msgCentrey = self.screenHeight*3.0/4.0
        msgx = msgCentrex-width/2.0
        msgy = msgCentrey-height/2.0   
        
        self.messageCorner=(msgx, msgy)
        
        if self.msgRects is not  None:
            self.clearMsg()
 #TODO maybe lodge this as a delayed action, shorten timeout for existing delayed action?
    
    
        # now render each line
        heightOffset = 0
        self.msgRects = []
        for i in range(len(msgList)):
            s = msgSurfs[i]
            blitCorner = (msgx, msgy+heightOffset)
            r = self.background.blit(s, blitCorner)
            self.screen.blit(self.background, blitCorner, r )
            self.msgRects.append(r)
            heightOffset += s.get_rect().bottom*lineSpacing
            
        ''' Now:
        set the msgRect
        blit the message 
        set a delayed action
        maybe set a rect to clean?'''
        
        pygame.display.update(self.msgRects)
        
        delayedActionExists = False
        for i in self.delayedActions:
            # requires a review of all delayed actions, but hopefully won't be many
            # and won't need to do it that often
            if i.runFunctionOnTrigger == self.clearMsg:
                i.triggerAtGameTime = self.gameTime+timeout
                delayedActionExists = True
        
        if not delayedActionExists:
            self.delayedActions.append(self.delayedAction(self.gameTime+timeout,  self.clearMsg, ()))
        
        
    def clearMsg(self):
        '''If self.msgRects is not None, 
        then fill the area of the screen with black to erase
        the existing message
        have to clear any delayed action as well??
        what if this is called from that delayed action?
        could turn it into a null?
        I would like something more sophisticated - eg a background which can be other than black, which 
        gets swapped in and out, but it seems like it will be too much trouble
        perhaps some other time...
        One day I'll do a fade out maybe '''
        
        if self.msgRects is not None:
            for r in self.msgRects:
                self.background.fill(BACKGROUND_COLOUR, r)
                self.screen.blit(self.background, (r.left, r.top),  r)
            pygame.display.update(self.msgRects)
            self.msgRects= None
      
    def checkDelayedActions(self):
        removeList = []
        for i in range(len(self.delayedActions)):
            spam = self.delayedActions[i]
            if spam.triggerAtGameTime < self.gameTime:
                spam.runFunctionOnTrigger(*spam.argTuple)
                removeList.append(i)
        removeList.reverse()
        for j in removeList:
            self.delayedActions.pop(j)




def gameLoop(game):
    clock = game.clock
    controls = Controls()

    pygame.mixer.music.load("Jazz.wav")
    pygame.mixer.music.play(-1)

    game.splashScreen()
    # game.showIntroMessage()
    game.paused = True
    game.initSettingsFromAttrs()
    game.settings.settingsShow()
    game.initAttrsFromSettings()
    game.paused = False

    start_ticks = pygame.time.get_ticks()  # starter
    frame_count = 0
    start_time = 120
    # game.readOut("Time: ", start_time)
    game.readOut()



    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    while game.MAINLOOP:

        # # game.readOut()
        # # game.readOut("Time: 00:00")
        # total_seconds = start_time - seconds  # calculate how many seconds
        # if total_seconds < 0:
        #     total_seconds = 0
        #
        # # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        #
        # # --- Timer going up ---
        # # Calculate total seconds
        # # total_seconds = frame_count // frame_rate
        #
        # # Divide by 60 to get total minutes
        # remain_minutes = total_seconds // 60
        #
        # # Use modulus (remainder) to get seconds
        # remain_seconds = total_seconds % 60
        # # Use python string formatting to format in leading zeros
        #
        # frame_count += 1
        # output_string = "Time: {0:02}:{1:02}".format(remain_minutes, remain_seconds)
        deltaTMillis = clock.tick(FPS)
        deltaT = deltaTMillis / (1000.0 * game.slowMo)
        game.loopCounter += 1
        # game.readOut(output_string)


        if not game.paused:

            seconds = (pygame.time.get_ticks() - start_ticks) / 1000

            game.gameTime += deltaTMillis / game.slowMo
            game.gm.update(deltaT)
            collisionDetection(game)
            game.checkDelayedActions()
            game.killTheOld()
            # total_seconds = start_time - seconds  # calculate how many seconds
            # if total_seconds < 0:
            #     total_seconds = 0
            #
            # # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
            #
            # # --- Timer going up ---
            # # Calculate total seconds
            # # total_seconds = frame_count // frame_rate
            #
            # # Divide by 60 to get total minutes
            # remain_minutes = total_seconds // 60
            #
            # # Use modulus (remainder) to get seconds
            # remain_seconds = total_seconds % 60
            # # Use python string formatting to format in leading zeros
            # output_string = "Time: {0:02}:{1:02}".format(remain_minutes, remain_seconds)
            # game.readOut(output_string)
            # # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
            # frame_count += 1
            # game.readOut()


            if seconds > 20:  # if more than 10 seconds pause the game
                game.paused = True
                if game.noOfHits[game.ship2.id] > game.noOfHits[game.ship1.id]:
                    i = '''HEX SHIP WON\n'''
                elif game.noOfHits[game.ship2.id] < game.noOfHits[game.ship1.id]:
                    i = '''TRIANGLE SHIP WON\n '''
                else:
                    i = '''TIE\n '''
                # game.screen.blit(game.background, (0, 0))
                # text_surface = game.font.render("Press space bar to play again", True, WHITE)
                # game.screen.blit(text_surface, (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 7 / 8))
                # pygame.display.flip()
                # # game.clock.tick(FPS)

                game.showIntroMessage(i)

                # game.noOfHits[s.id] = 0
                # break





            print(seconds)

            if game.loopCounter %100 == 0:
                game.readOut()
      
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                game.MAINLOOP = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.noOfHits[game.ship1.id] = 0
                    game.noOfHits[game.ship2.id] = 0
                    gameLoop(game)
                    # for k, s in list(game.ships.items()):

                    game.explode(game.ship1.id)
                    game.explode(game.ship2.id)
                    game.gm.delObject(game.ship1.id)
                    game.gm.delObject(game.ship2.id)
                    game.initShips(game.ship1, game.ship2)
                    # game.gm.delObject(game.ship1.id)
                    # game.gm.delObject(game.ship2.id)




                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    game.MAINLOOP= False

                if event.key == controls.p1Left:
                    Logd( "got a p1 left rotate")
                    game.ship1.rotating = -1.0
                    # this should be opposite sign, but 
                    # there is some bug somewhere, so I'm reversing it rather
                    # than track down the bug...
                if event.key == controls.p1Right:
                    Logd( "got a p1 right rotate")
                    game.ship1.rotating=1.0
                    # this should be opposite sign, but 
                    # there is some bug somewhere, so I'm reversing it rather
                    # than track down the bug...
                if event.key == controls.p1Thrust:
                    Logd( "got a p1 thrust")
                    game.ship1.setThrusterState(True)
                    
                if event.key == controls.p2Left:
                    Logd( "got a p2 left rotate")
                    game.ship2.rotating = -1.0
                    
                if event.key == controls.p2Right:
                    Logd( "got a p2 right rotate")
                    game.ship2.rotating = 1.0
                    
                if event.key == controls.p2Thrust:
                    Logd( "got a p2 thrust")
                    game.ship2.setThrusterState(True) 
                
                if event.key == controls.slowMo:
                    game.slowMo = 10

            elif event.type == pygame.KEYUP:
                if event.key == controls.p1Fire:
                    shoot_sound = pygame.mixer.Sound("shoot.wav")

                    pygame.mixer.Sound.play(shoot_sound)
                    Logd( "got p1 fire")
                    if game.ship1.id in game.ships:
                        game.bm.newBullet(game.ship1, 
                                game.gravity,
                                game.gameTime,  
                                game.gm , 
                                game.bulletSpeed, 
                                game.bulletLife)

                if event.key == controls.p2Fire:
                    shoot_sound = pygame.mixer.Sound("shoot.wav")

                    pygame.mixer.Sound.play(shoot_sound)
                    Logd( "got p2 fire")
                    if game.ship2.id in game.ships:
                        game.bm.newBullet(game.ship2, 
                                game.gravity,
                                game.gameTime,  
                                game.gm, 
                                game.bulletSpeed, 
                               game.bulletLife )
                
                if event.key == controls.p1Left:
                    Logd( "stop p1 left rotate")
                    game.ship1.rotating=0.0
                if event.key == controls.p2Left:
                    Logd( "stop p2 left rotate" )
                    game.ship2.rotating=0.0                    
                if event.key == controls.p1Right:
                    Logd( "stop p1 right rotate")
                    game.ship1.rotating=0.0
                if event.key == controls.p2Right:
                    Logd( "stop p2 right rotate")
                    game.ship2.rotating=0.0
                        
                if event.key == controls.pause:
                    if  game.paused: 
                        game.paused = False
                        pygame.mixer.music.unpause()

                    else:
                        game.paused = True
                        pygame.mixer.music.pause()

                if event.key == controls.dumpVals:
                    Logd( "Got a dump vals ")
                    for k, s in list(game.ships.items()):
                        s.dumpVals()
                
                if event.key == controls.restart:
                    Logd( "got a restart")
                    game.initShips(game.ship1,game.ship2)
                    # will this work??  
                    # Apparently it does, but 
                    # it is a blunt instrument and might be better to have 
                    # more finesse in restart 
                 
                if event.key == controls.slowMo:
                    game.slowMo = 1

                if event.key == controls.p1Thrust:
                    # stop thrusters
                    Logd( "got a p1 stop thruster"     )
                    game.ship1.setThrusterState(False)
                    
                if event.key == controls.p2Thrust:
                    # stop thrusters
                    game.ship2.setThrusterState(False) 
                    Logd( "got a p2 stop thruster"      )
                
                if event.key == controls.p1Explode:
                    # stop thrusters
                    Logd( "got a p1 stop thruster"  )   
                    game.explode(game.ship1.id)
                   
                if event.key == controls.p2Explode:
                    # stop thrusters
                    game.explode(game.ship2.id)
                    Logd( "got a p2 stop thruster"  )
                    
                if event.key == controls.settings:
                    # pause, load defaults, display settings, return dict
                    # reinitialise relevant variables
                    # unpause game
                    # ??? keep the paused state? or just unpause when done?
                    game.paused = True
                    game.initSettingsFromAttrs()
                    game.settings.settingsShow()
                    game.initAttrsFromSettings()
                     # probably didn't need to pause/unpause it as processing is suspended 
                if event.key == controls.introMsg:
                    game.showIntroMessage()
                
                if event.key == controls.debugKey:
                    game.message("This is a message\nIt has two lines")

                if event.key == controls.debugKey2:
                    game.message("This is another message")




if __name__ == "__main__":
    game = Game(SCREEN_WIDTH,  SCREEN_HEIGHT)
    gameLoop(game)
    
