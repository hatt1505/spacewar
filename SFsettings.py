''' Settings for space war'''

import pygame
import logging
Logd = logging.debug
from vectorLibrary import BasicVectorFont

''' 
This file should contain:
a class to store each of the settings; and
a class for displaying the settings on the screen to change them. 
Ideally I would like to use a vector font for all of this. 

Settings could include....
bullet speed
gravity strength
ship speed
ship rotation speed
geometry
bullet speed independent of ship speed?
screen size

each setting should be able to be displayed on the screen
should, I guess, specify a widget for each setting
setting types will be...
range from x to y as float
range from x to y as int (this is really just the same as set values
set values (0n/off) or set of possible values 
key value

May want to update a description to accompany chosen setting value
1.0 = normal 1.5 = Strong, 2.0 A bit much 3.0 Are you kidding? 4.0 Ridiculous (etc)
[setting name]  [chooser widget]  [description]

The question is, how does this get integrated with the game class in the game 
how can it be imported without a lot of hoohah in the definition of the game class?
I guess Game could inherit from Settings?

'''

# Widget types
FLOATWIDGET = "floatWidget"  # floating point range
LISTWIDGET = "listWidget"        # list of values, may include an integer range or On/Off
CHARWIDGET = "charWidget"   # key press values
ORIGIN = (0, 0)

WIDGETWIDTH = {
               FLOATWIDGET:100, 
               LISTWIDGET:100, 
               CHARWIDGET:20
               }

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DEFAULT_FONTSIZE =12


def renderFont():
    pass
    
def calcCentredRect(r1, r2):
    '''Calculate an offset to centre rectangle r1 within a larger rectangle r2
    Assumes both x and y dimensions of r2 are larger than those of r1
    Return a rectangle of width and height the same as r1, but centered at the centre of r2'''
    w1 = r1.width/2
    w2 = r2.width/2
    h1 = r1.height/2
    h2 = r2.height/2
    offset = (w2-w1,  h2-h1)
    s = r2.topleft
    return pygame.Rect(s[0]+offset[0], s[1]+offset[1],  r1.width, r2.height)
    

class individualSetting(object):
    ''' so far as possible, the id of an individualSetting should be the same as the name of an attribute of the game class'''
    def __init__(self,  label = "An Empty Setting",  id = None,  widgetType = FLOATWIDGET,  
                rangeStart= None,  rangeEnd= None,  
                valueList = [],  # possible values that  this setting can take
                descriptionList = [],   #  text descriptions corresponding to values in valueList
                fpDescriptionList=[],   
                # (value,text) tuples?  So that if fp value > fpDescription value, then display that description.
                # highest first so that lowest which satisfies greater than will be displayed.
                defaultValue = None, 
                fgColour = WHITE,  bgColour = BLACK 
                 ):
                     
#        self.font = pygame.font.Font(None, DEFAULT_FONTSIZE)   # can substitute a vector font later if I want
        self.font = BasicVectorFont(None, DEFAULT_FONTSIZE)

        self.fgColour = fgColour
        self.bgColour = bgColour
        self.padding = 5
        self.fpDescriptionList = fpDescriptionList
    
        self.label = label
        self.widgetType = widgetType
        self.rangeStart = rangeStart
        self.rangeEnd = rangeEnd
        self.range = abs(rangeEnd-rangeStart)
        self.valueList = valueList
        self.rect = None   # initialised in makeImage 
        if id is None:
            self.id = label
        else:
            self.id = id
        if defaultValue is None:
            initDefaultValue()
        else:
            self.defaultValue = defaultValue
        self.value = self.defaultValue  # now init to default

        # Set label stuff
        self.layoutWeights = {
                                "label":1.0, 
                                "widget":1.0, 
                                "increment":0.1,
                                "decrement" :0.1, 
                                "reset":0.1, 
                                "description":1.0}
        self.totalWeight = sum([x for x in self.layoutWeights.values()])
        logging.debug("totalWeight = %s"%self.totalWeight)
        self.layoutWidths = {}
        self.rects={}
        
        self.mouseDown = False
        
    def initLabel(self):
        self.labelSurface = self.font.render(self.label,  True, self.fgColour, self.bgColour)
        w = self.labelSurface.get_rect().width
        h = self.labelSurface.get_rect().height
        x = self.labelRightAlign - w
        y = self.rects['label'].centery -(h/2)
        self.rects['label'].left   = x 
        
        self.rects['labelSurface']= pygame.Rect(x, y, w, h)


    def renderLabel(self):
        self.image.blit(self.labelSurface, self.rects['labelSurface'].topleft)  # blit it at x in order to right align ?? allowance for padding??
    
    def initIncDec(self):
        self.decSurface = self.font.render("-", True,  self.fgColour, self.bgColour)
        self.incSurface = self.font.render("+", True,  self.fgColour, self.bgColour)
        self.resetSurface = self.font.render("*", True,  self.fgColour, self.bgColour)

        # draw a rectangle around each of them
        pygame.draw.rect(self.image,  self.fgColour, self.rects['increment'], 1)
        pygame.draw.rect(self.image,  self.fgColour, self.rects['decrement'], 1)
        pygame.draw.rect(self.image,  self.fgColour, self.rects['reset'], 1)

        # locate + and - in centre of rectangles that have been rendered
        # want centre of intSurface to == centre of incRect etc 
        incSurfRect = self.incSurface.get_rect()
        w1 = incSurfRect.width/2
        w2 = self.rects['increment'].width/2
        h1 = incSurfRect.height/2
        h2 =  self.rects['increment'].height/2
        offset = (w2-w1,  h2-h1)
        s = self.rects['increment'].topleft  # ie the entire box, rather than just the character to be rendered 
        self.rects['incSurface']= pygame.Rect(s[0]+offset[0], s[1]+offset[1],  incSurfRect.width, incSurfRect.height)
        
        self.image.blit(self.incSurface, self.rects['incSurface'].topleft)
        
        # repeat for decrement button
        decSurfRect = self.decSurface.get_rect()
        w1 = decSurfRect.width/2
        w2 = self.rects['decrement'].width/2
        h1 = decSurfRect.height/2
        h2 = self.rects['decrement'].height/2
        offset = (w2-w1,  h2-h1)
        s = self.rects['decrement'].topleft  # ie the entire box, rather than just the character to be rendered 
        self.rects['decSurface']= pygame.Rect(s[0]+offset[0], s[1]+offset[1],  decSurfRect.width, decSurfRect.height)
        self.image.blit(self.decSurface, self.rects['decSurface'].topleft)
        
        # repeat for reset button
        resetSurfRect = self.resetSurface.get_rect()
        w1 = resetSurfRect.width/2
        w2 = self.rects['reset'].width/2
        h1 = resetSurfRect.height/2
        h2 = self.rects['reset'].height/2
        offset = (w2-w1,  h2-h1)
        s = self.rects['reset'].topleft  # ie the entire box, rather than just the character to be rendered 
        self.rects['resetSurface']= pygame.Rect(s[0]+offset[0], s[1]+offset[1],  resetSurfRect.width, resetSurfRect.height)
        self.image.blit(self.resetSurface, self.rects['resetSurface'].topleft)

        
    
    def initDefaultValue(self):
        if self.widgetType == FLOATWIDGET:
            self.defaultValue = (self.rangeStart+self.rangeEnd)/2.0  # use median value
        if self.widgetType == LISTWIDGET:
            self.defaultValue = len(self.valueList)/2   # use middle value in list
        if self.widgetType == CHARWIDGET:
            self.defaultValue = "A"  
            # no easy way of guessing what a char should default to so just make it arbitrary
            # char widgets could be dealt with in the Settings class so that they are all unique.
            
    def makeImage(self, imageRect,  renderTopLeft):
        self.image = pygame.Surface((imageRect.width, imageRect.height)).convert()
        self.renderTopLeft = renderTopLeft  #  topleft of this setting when rendered on the screen. 
        # now we know how big the image for this settings entry is, we can 
        # calculate other stuff about it
        w = imageRect.width
        h = imageRect.height
        T = self.totalWeight
        self.settingRect = imageRect
        self.settingRect.topleft = renderTopLeft
        #print "is: %s, self.rect : %s"%(self.id, self.settingRect)
        for k in self.layoutWeights.keys():
            self.layoutWidths[k] = self.layoutWeights[k]*w/T
        
        self.rects['label']= pygame.Rect(0, self.padding,  self.layoutWidths['label'], h -2*self.padding)
        self.rects['widget']= pygame.Rect(self.layoutWidths['label'], self.padding,  self.layoutWidths['widget'], h -2*self.padding)
        self.rects['increment']=  pygame.Rect (self.rects['widget'].right, self.padding, self.layoutWidths['increment'],  h -2*self.padding)
        self.rects['decrement']=  pygame.Rect (self.rects['increment'].right, self.padding, self.layoutWidths['decrement'],  h -2*self.padding)
        self.rects['reset']=  pygame.Rect (self.rects['decrement'].right, self.padding, self.layoutWidths['reset'],  h -2*self.padding)
        self.rects['description']=  pygame.Rect (self.rects['reset'].right, self.padding, self.layoutWidths['description'],  h -2*self.padding)
        
        self.labelRightAlign = self.layoutWidths['label']  # maybe subtract some padding?
        
        # initialise the various components 
        self.initLabel()
        self.initIncDec()
        self.initWidget()
        self.updateDescription()

    def initWidget(self):
        if self.widgetType ==  FLOATWIDGET:
            self.updateFloatSlider()
            return
        # other widget types to follow
        

    def updateFloatSlider(self):
        # widget is a float slider so draw this into the widget rectangle
        
        # horizontal bar
        self.image.fill(BLACK, self.rects['widget'],  0)
        
        w = self.rects['widget'].width - 2*self.padding
        h = 2                               # height of horiz slider 
        c = self.rects['widget'].centery
        self.rects['sliderHoriz'] = pygame.Rect(self.rects['widget'].left+self.padding,  c+(h/2),  w,  h)
        pygame.draw.rect(self.image,  self.fgColour,  self.rects['sliderHoriz'],  0 )  # fill the rect
        
        # vertical bar
        vh = 20
        sliderVert = pygame.Rect(0, 0,  2, vh)
        play = self.rects['widget'].width -(2*self.padding) -2 # 2 being the width of the vertical bar...
        Logd(" rendering vertical part, self value = %s"%(self.value))
        offset = play * ((self.value-self.rangeStart)/self.range)
        sliderVert.left = self.rects['sliderHoriz'].left+offset
#        sliderVert.left = self.rects['widget'].left+offset+self.padding
        sliderVert.top = c-1- (vh/2)
        
        pygame.draw.rect(self.image,  self.fgColour,  sliderVert,  0)
        
    def updateDescription(self):
        ''' blank the current description area 
        determine description based on value
        write description'''
        
        Logd("In update Description")
        self.image.fill(BLACK,  self.rects['description'], 0)
        description = "###Error"
        for d in self.fpDescriptionList:
            if self.value > d[0]:
                description = d[1]
        
        self.descriptionSurface = self.font.render(description,  True,  self.fgColour,  self.bgColour)  
        self.rects['descriptionSurface'] = self.descriptionSurface.get_rect()
        w =self.rects['descriptionSurface'].width
        h = self.rects['descriptionSurface'].height
        x = self.rects['description'].left+self.padding
        y = self.rects['description'].centery -(h/2)
        
        self.rects['descriptionSurface'].left = x
        self.rects['descriptionSurface'].top = y
        
        self.image.blit(self.descriptionSurface, self.rects['descriptionSurface'].topleft)

    def eventHandler(self,  e):
        '''handle events received from the main settings page
        will come in with an absolute screen location
        First convert to an offset to this setting
        Then handle as appropriate - mainly clicks on increment/decrement/reset and widget'''
        
        
        Logd( "Handler for %s, rect: %s, got event: %s"%(self.id, self.settingRect, e) )
        relPos =  (e.pos[0] -self.settingRect.left ,  e.pos[1] - self.settingRect.top)
        Logd("Relative position = %s,%s"%(relPos[0], relPos[1]))
        
        ''' determine if it collides with widget, increment, decrement or reset
        widget takes mouse motion, mouse down and mouse up
        others just take... mouse up?'''
        
        collision = None
        for k in ['widget',  'increment', 'decrement', 'reset']:
            if self.rects[k].collidepoint(relPos):
                collision = k
                break
        
        if collision is None:
            return
        
        if (e.type == pygame.MOUSEBUTTONDOWN or e.type== pygame.MOUSEMOTION):
            if  k != 'widget':
                Logd("Event a down or motion and not over widget, dropping")
                # can ignore if these events are not over  the widget
                return
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.mouseDown = True
                return
                
            if e.type == pygame.MOUSEMOTION and self.mouseDown:
                if self.widgetType == FLOATWIDGET:
                    Logd("Got mouseMotion")
                    x = max(0,  relPos[0]  - self.rects['sliderHoriz'].left)
                    if x > self.rects['sliderHoriz'].width:
                        x = self.rects['sliderHoriz'].width
                    self.value = self.rangeStart+ (self.range *x /self.rects['sliderHoriz'].width)
                    Logd("#############setting value. x = %s, width = %s value = %s"%(x, self.rects['sliderHoriz'].width,  self.value))
                    self.updateWidget()
                    # handle other widgets differently
                

        if e.type == pygame.MOUSEBUTTONUP:  
            # actually, maybe these should be mouseDown events and should continue to increment/decrement 
            # until mouse up.
            if k  == 'increment':
                Logd("Got a button up increment")
                pass #TODO
            if k  == 'decrement':
                Logd("Got a button up decrement")
                pass #TODO
            if k  == 'reset':
                Logd("Got a button up reset")
                self.value = self.defaultValue
                self.updateWidget()
#                pass #TODO
            if k =='widget':
                Logd("Got a button up widget")
                self.mouseDown = False

    def update(self):
        self.renderLabel()
        self.updateWidget()  
        self.renderIncrementDecrement()
        self.renderReset()
        self.renderDescription()
    
    def updateWidget(self):
        if self.widgetType ==  FLOATWIDGET:
            self.updateFloatSlider()
            self.updateDescription()
            return

    
    def renderIncrementDecrement(self):
        pass
        
    def renderReset(self):
        pass
        
    def renderDescription(self):
        pass
        
        
class Settings(object):
    def __init__(self,  header = "",  footer ="",  settingsList = [],  
                 fgColour=WHITE,  bgColour=BLACK, 
                 columnWidth = 800 , columnHeight=600  # assuming an 800x600 display
                 ):
                     
#        self.font = pygame.font.Font(None, DEFAULT_FONTSIZE)   # can substitute a vector font later if I want
        self.font = BasicVectorFont(None, DEFAULT_FONTSIZE)

        self.fgColour = fgColour
        self.bgColour = bgColour
        self.padding = 20

        self.settingsList = settingsList
        self.columnWidth =columnWidth  # width of column including padding.
        self.columnHeight = columnHeight  # height of column, including padding, headers, footers
        self.rowHeight = 50  # to be reset once we know how many settings/columns there are. 
        self.padLeft = 20
        self.padRight = 20
        self.padTop = 20
        self.padBottom = 20
        self.headerSpace = 50
        self.footerSpace = 50
        self.header = header
        self.footer = footer
        ### work out rect for individual setting
    
        self.settingsInitRect()
        self.settingsGenerateLayout()
        
        self.rects={
                    'header': pygame.Rect(0, 0, self.columnWidth, self.headerSpace), 
                    'footer': pygame.Rect(0, self.columnHeight-self.footerSpace, self.columnWidth, self.footerSpace),  
                    'headerText':pygame.Rect(0, 0, 1, 1),  # random rect
                    'footerText':pygame.Rect(0, 0, 1, 1)
                    }
        
        self.buttonKeys = ['okButton',  'resetAllButton',  'cancelButton']  # for event handling

    def initFromDict(self, d):
        ''' where d is a dictionary with keys as setting ids and values as the default value of the setting with that id
        As this sets default values, settings will return these values on cancel.  Load them with current values from the game
        and then it will return those values on a cancel'''
        for k, v in d.items():
            for s in self.settingsList:
                if s.id == k:  # there is probably a neater way of doing this.
                    s.defaultValue = v

    def settingsInitRect(self):
        ax = self.columnWidth - (self.padLeft+ self.padRight)
        ay = self.columnHeight-(self.padBottom+self.padTop + self.headerSpace + self.footerSpace)
        self.settingsRect = pygame.Rect(0, 0, ax, self.rowHeight)
    
    
    def settingsGenerateLayout(self):
        ''' In this function we need to run through all settings, determine rectangles for each of the items
        and use these rectangles to (eg) align labels, values, descriptions etc.
        render all possible options for each setting.  Take largest rectangle from these renderings, create an image surface for that setting
        create subsurfaces within the image for label, widget, reset, description
        for each setting assign a value for topleft in the screen surface
        '''
        
        # maybe I just have a fixed layout???
        x = self.padRight
        yBase = self.padTop+self.headerSpace # always leave header space
        y = yBase
        column = 0
        
        for i in self.settingsList:
            spamRect = self.settingsRect.copy()
#            print "now setting rect for id = %s"%(i.id)
            i.makeImage(spamRect,  (x, y))
            Logd("After setting rect.  id: %s, rect: %s"%(i.id, i.settingRect))
            y+= self.rowHeight
            if y > self.columnHeight - self.footerSpace:
                break 
                # single column for now
#                column += 1
#                if column > 1:
#                    # out of screen real estate, drop any further settings
#                    break
#                x += x+self.columnWidth
#                y = yBase
     
     
    
    def settingsShow(self):
        ''' show/edit available settings 
        At present limited to a single page of settings
        save screen
        save current settings
        display settings chooser 
        ok/cancel buttons
        save/discard changes 
        restore screen
        return
        
        '''
        self.screen = pygame.display.get_surface()  # current screen
        self.backupCopyOfScreen()
        screenRect = self.screen.get_rect()
        self.settingsDisplay = pygame.Surface((screenRect.width,screenRect.height))
        # one day I will make this a subsurface of a specific size or ratio
        
        self.settingsInitHeader()
        self.settingsInitFooter()  # I could actually do this at the same time as the header
        
        for s in self.settingsList:
            s.update()
            self.settingsRender(s)  # s should have its own rect by now. 
        
        pygame.display.flip()
        self.settingsEventLoop()  
        
        self.restoreCopyOfScreen()
        
    
    
    def settingsEventLoop(self):
        clock = pygame.time.Clock()
        FPS = 30 # can hard code this.  Slightly slower would probably also be acceptable
        loop = True
        mouseDown = False
        currentReceiver = None
        
        while loop:
            deltaTMillis = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        loop= False
                elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN  or event.type ==pygame.MOUSEMOTION:
                    '''So, logic is: if there is a mouse down, then all subsequent mouse events until mouse up should go to the same handler
                    if there is no mouse down, then can pass motion events to individual settings (may implement current selection using this at some time)'''
                    if mouseDown: 
                        Logd("Mouse down, sending event to %s"%currentReceiver.id)
                        currentReceiver.eventHandler(event)
                        self.screen.blit(currentReceiver.image, currentReceiver.settingRect)
                        pygame.display.update(currentReceiver.settingRect) 
                        # now clean up if its a button up
                        if event.type == pygame.MOUSEBUTTONUP:
                            Logd("Got a mouse up")
                            mouseDown = False
                            currentReceiver.mouseDown=False  # not sure if I need to do this here or in the individual class
                            currentReceiver = None
                            
                    else:  # no current button down being handled
                        p = event.pos
                        for s in self.settingsList:
                            if s.settingRect.collidepoint(p):
                                Logd("rect = %s"%(s.settingRect))
                                s.eventHandler(event)
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    currentReceiver = s
                                    mouseDown=True
                                    Logd("Got a mouseDown for id = %s"%currentReceiver.id)
                                
                                self.screen.blit(s.image, s.settingRect)
                                pygame.display.update(s.settingRect)
                                break  # don't try passing event to any other setting
                        if event.type != pygame.MOUSEBUTTONUP:
                            continue
                        if event.type == pygame.MOUSEBUTTONUP:
                            # and not handled earlier
                            for k in self.buttonKeys:
                                if self.rects[k].collidepoint(p):
                                    Logd("Got a collision with a footer button")
                                    if k == 'resetAllButton':
                                        for s in self.settingsList:
                                            s.value = s.defaultValue
                                            s.updateWidget()
                                            self.screen.blit(s.image, s.settingRect)
                                        pygame.display.flip()  # may as well update the whole thing 
                                        break
                                    if k == 'okButton':
                                        # game will have this settings object  as an attribute so can access settings values directly
                                        # no need to return a dictionary
                                        return
    
                                    if k =='cancelButton':
                                        # game will have this settings object  as an attribute so can access settings values directly
                                        # however cancelling, so must return values to original defaults before returning.
                                        for s in self.settingsList:
                                            s.value = s.defaultValue
                                        return
                                        
                                        
    def settingsInitHeader(self):
        self.headerText= self.font.render(self.header, True,  self.fgColour, self.bgColour)
        self.rects['headerText']= self.headerText.get_rect()
        c = self.rects['header'].center
        self.rects['headerText'].center = c
        
        self.screen.blit(self.headerText, self.rects['headerText'])
        pygame.display.update(self.rects['headerText'])
        
    
    def settingsInitFooter(self):
        ''' Need to create three buttons: ok, reset All and cancel '''
        buttonWidth = 180  # magic number
        ypadding = 5
        okText = self.font.render("OK", True,  self.fgColour, self.bgColour)
        resetText = self.font.render("RESET ALL", True,  self.fgColour, self.bgColour)
        cancelText = self.font.render("CANCEL", True,  self.fgColour, self.bgColour)
        self.rects['okText'] = okText.get_rect()
        self.rects['resetText']= resetText.get_rect()
        self.rects['cancelText']=cancelText.get_rect()
        
        baseButtonRect = pygame.Rect(0, 0, buttonWidth,  self.footerSpace- 2*ypadding)
        
        cx = self.rects['footer'].centerx
        cy = self.rects['footer'].centery
        
        self.rects['okButton'] = baseButtonRect.copy()
        self.rects['okButton'].right = cx - buttonWidth
        self.rects['okButton'].centery = cy
        self.rects['resetAllButton'] = baseButtonRect.copy()
        self.rects['resetAllButton'].centerx = cx
        self.rects['resetAllButton'].centery = cy
        self.rects['cancelButton'] = baseButtonRect.copy()
        self.rects['cancelButton'].left = cx +buttonWidth
        self.rects['cancelButton'].centery = cy

        for k in ['okButton', 'resetAllButton', 'cancelButton']:
            pygame.draw.rect(self.screen,  self.fgColour,  self.rects[k], 1)

        self.rects['okText'] = calcCentredRect(self.rects['okText'],  self.rects['okButton'])
        self.rects['resetText'] = calcCentredRect(self.rects['resetText'],  self.rects['resetAllButton'])
        self.rects['cancelText']= calcCentredRect(self.rects['cancelText'],  self.rects['cancelButton'])
        
        self.screen.blit(okText,  self.rects['okText'])
        self.screen.blit(resetText,  self.rects['resetText'])
        self.screen.blit(cancelText,  self.rects['cancelText'])
        
        pygame.display.update(self.rects['footer'])
    
    def settingsGetChanges(self):
        ''' Record interactions between user and settings screen
        Start with mouse interations but I guess sooner or later I could also add a kb interface
        need highlight on mouseover
        '''
    
    def settingsRender(self, s):
        ''' actually render the setting s, based on s
        each setting should have: label, value chooser, reset, description
        use a global self.nextTopLeft to record where the next rectangle should start. 
        lists and floats should have increment/decrement arrows on each side <-- -->'''
        
        self.screen.blit(s.image, s.renderTopLeft)
    
    def  backupCopyOfScreen(self):
        self.backupOfScreen = self.screen.copy()
        self.backupOfScreen.blit(self.screen, ORIGIN)
        
    def restoreCopyOfScreen(self):
        self.screen.blit(self.backupOfScreen, ORIGIN)
        pygame.display.flip()
 

    
if __name__ == "__main__":
    
    LOGFILE = "sfs.log"
    f = open(LOGFILE, 'w')
    f.close()
    logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)
    Logd= logging.debug
    Logd('This message should go to the log file')

    Logd = logging.debug
    SCREEN_WIDTH= 800
    SCREEN_HEIGHT=600
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH,  SCREEN_HEIGHT])
    background = pygame.Surface([SCREEN_WIDTH,  SCREEN_HEIGHT])
    background.fill(BLACK)
    screen.blit(background, (0, 0))
    
    pygame.display.update()
    clock = pygame.time.Clock()
    MAINLOOP = True
    FPS = 30
    
    gravityScale = individualSetting(
                label = "Gravity Strength",  
                id = "gravityScale",  
                widgetType = FLOATWIDGET,  
                rangeStart= 0.0,  rangeEnd= 10.0,  
                valueList = [],
                descriptionList = [], 
                fpDescriptionList=[(-1, "None"), (0.0, "Very Weak"), (0.5, "Weak"), (0.75, "Normal"), 
                                   (3.0, "Strong"), 
                                   (6.0, "Very Strong"),
                                 (8.0, "A bit much"), 
                                   (9.5, "Are You Insane?")], 
                defaultValue = 1.0
                )
    
    bulletSpeed = individualSetting(
                label = "Bullet Speed",  
                id = "bulletSpeed",  
                widgetType = FLOATWIDGET,  
                rangeStart= 0.1,  rangeEnd= 10.0,  
                valueList = [],
                descriptionList = [], 
                fpDescriptionList=[(-1, "Soporific"), (0.4, "Slooooowwww"), (0.7, "Slowish"), (0.99, "Normal"), 
                                   (3.0, "Fast"), (6.0, "Very Fast"),  
                                   (8.0,  "Steady on..."), 
                                   (9.5, "Are You Insane?")], 
                defaultValue = 1.0
                )
        
 
    thrusterPower= individualSetting(
                label = "Thruster Power",  
                id = "thrusterPower",  
                widgetType = FLOATWIDGET,  
                rangeStart= 0.1,  rangeEnd= 10.0,  
                valueList = [],
                descriptionList = [], 
                fpDescriptionList=[(-1, "Pathetic"), (0.4, "Very Weak"), (0.7, "Weak"), (0.99, "Normal"), 
                                   (3.0, "Strong"), (6.0, "Powerful"),  
                                   (8.0,  "Ridiculous"), 
                                   (9.5, "Are You Insane?")], 
                defaultValue = 1.0
                ) 
    
    
    
    settings = Settings(settingsList =[gravityScale, bulletSpeed, thrusterPower],  header ="Space War! Settings")
    valuesDict = settings.settingsShow()
    
    print "Got the following: \n%s"%valuesDict
