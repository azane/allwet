#!/usr/local/bin/pythonw2.7-32
#Copyright 2015-2016 Andrew Eric Zane

import pygame
import sys
import math
from random import randrange

##Create iterable metaclass
class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class Segment(object):
    def __init__(self, window, color, pressure, thickness, segNum, xStart, yStart, xEnd, yEnd):
        
        
        ##ARGS
        self.window = window
        self.color = color
        self.pressure = pressure
        self.rnge = self.pressure
        self.segNum = segNum
        self.xStart = xStart
        self.yStart = yStart
        self.xEnd = xEnd
        self.yEnd = yEnd
        self.thickness = thickness
        ##/ARGS
        
        ##INITS
        self.forming = True
        self.finished = False
            ##Theta for collision detection
        self.theta = math.atan2((self.yEnd-self.yStart), (self.xEnd-self.xStart))
        ##All of the below additionally used by collision detection
        self.Px, self.Py, self.xLen, self.yLen = self.get_Pxy()
        self.Pl = self.get_Pl()
        self.allowedLen = self.get_allowedLen()
            ##Init drawing coords
        self.xCurStart = self.xStart
        self.yCurStart = self.yStart
        self.xCurEnd = self.xStart
        self.yCurEnd = self.yStart
        self.curLen = 0
        self.traveledLen = 0
        self.actualLen = 0
        ##/INITS
        
        
    def get_Pxy(self, xStart = None, yStart = None, xEnd = None, yEnd = None, rnge = None):
        
        ##ARGS
        if xStart is None:
            xStart = self.xStart
        if yStart is None:
            yStart = self.yStart
        if xEnd is None:
            xEnd = self.xEnd
        if yEnd is None:
            yEnd = self.yEnd
        if rnge is None:
            rnge = self.rnge
        ##/ARGS
        
        xLen = xEnd-xStart
        yLen = yEnd-yStart
        
        ##This results in the traveling of a segment by a magnitude of 1*pressure per frame
        ##Also, P* MUST be normalized to a magnitude of 1 in order that collision detection works
        
        ##So, because of the origin of rnge, this function needs to be called every time the pressure changes
        
        Px = xLen/rnge
        Py = yLen/rnge
        
        return Px, Py, xLen, yLen
        
    def get_allowedLen(self, segNum = None, pressure = None):
        ##ARGS
        if segNum is None:
            segNum = self.segNum
        if pressure is None:
            pressure = self.pressure
        ##/ARGS
        
        return pressure/segNum
    def increment_seg(self):
        """Returns the proportional length additive-at-increment"""
        
        ##If we wanted dynamic pressure change, we could check allowedLen here
        
        ##print "Length traveled: " + str(self.traveledLen)
        ##print "Current endpoint: " + str(self.xCurEnd) + ", " + str(self.yCurEnd)
        
        if self.traveledLen < self.rnge:
            self.xCurEnd = self.xCurEnd + self.Px
            self.yCurEnd = self.yCurEnd + self.Py
            self.actualLen = self.actualLen + self.Pl
        ##Don't subtract from curLen when we stop incrementing *curEnd. 
        ##  curLen is only accurate until this point, otherwise, the below
        ##  comparison would break, the *CurStart would not increment
        ##  curLen must represent MAX segment length after formed.
        ##  even when the segment length ceases to be added to.
            
        ##Inc traveledLen even after not adding for self.finished check
        self.traveledLen = self.traveledLen + self.Pl
            
        if self.curLen < self.allowedLen:
            self.curLen = self.curLen + self.Pl
            ##Leave self.*CurStart as self.*Start
        else:
            self.xCurStart = self.xCurStart + self.Px
            self.yCurStart = self.yCurStart + self.Py
            self.actualLen = self.actualLen - self.Pl
            ##No longer forming, so head knows to start new segment
            if self.forming:
                self.forming = False
            
        ##Check finished, when 
        if (self.traveledLen - self.curLen) > self.rnge:
            self.finished = True
            
        return not self.finished
            
    def get_Pl(self, Px = None, Py = None):
        
        ##ARGS
        if Px is None:
            Px = self.Px
        if Py is None:
            Py = self.Py
        ##/ARGS
        
        return math.sqrt((Px**2)+(Py**2))
        
    def reDraw(self):
        
        ##self.increment_segment is true if not finished
        if self.increment_seg():
            pygame.draw.line(self.window, self.color, (self.xCurStart, self.yCurStart), (self.xCurEnd, self.yCurEnd), self.thickness)
        
    def runner_Xmove(self, distance):
        self.xCurStart = self.xCurStart + distance
        self.xCurEnd = self.xCurEnd + distance
        ##I don't think we need to increment anything beyond the current x's
        
        self.xEnd = self.xEnd + distance
class Runner(object):
    
    ##FIXME
    ## Needs value error and type error exception handling
    ##/FIXME
    
    ##Class Elements
    
    __diagMove = 0.707
    
    ##Link to metaclass, define registry
    __metaclass__ = IterRegistry
    _registry = []
    
    def __init__(self, window, arrows, top, speed, image):
        """Speed is distance moved per frame
        Image is a path here, note comment in reDraw()"""
        
        ##Append instance to class registry
        self._registry.append(self)
        
        self.window = window
        self.top = top
        
        self.defSpeed = speed
        
        ##Get x, y and dist = 0 from start
        ##self.speed declared here
        self.x, self.y, self.distance = self.start()
        
        ##Init lastPlaced distance
        self.lastPlaced = 0
                
        ##self.arrows is a bool true:arrow keys, false:wasd
        self.arrows = arrows
        ##Convert image parameter into a pygame image, store as instance variable
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (15, 20))
    
    def start(self, window=None, top=None):
        if window is None:
            window = self.window
        if top is None:
            top = self.top
            
        ##Tell sprinkler appender that we're ready to restart
        self.reInit = True
        
        x, y = window.get_size()
        
        ##Center vertically
        ##y = y/2
        
        ##OPPOSITE SIDES
        ##if top:
            ##Put at the left 25th of the screen
            ##x = x/25
        ##else:
            ##Put at the right 25th of the screen
            ##x = x - (x/25)
            
        if top:
            y=(y/2) - 15
        else:
            y=(y/2) + 15    
        x = x/3
                  
        self.speed = self.defSpeed
        
        ##Reset distance traveled
        dist = 0
        
        ##Put cursor on guy for mouse control
        pygame.mouse.set_pos([x, y])
        
        return x, y, dist
    
    ##<KEY CONTROL>
    def moveY(self, YPositive):
        
        if not YPositive:
            dirSpeed = self.speed * (-1)
        else:
            dirSpeed = self.speed
        
        self.y = self.y + dirSpeed
    
    def moveX(self, XPositive):
        
        if not XPositive:
            dirSpeed = self.speed * (-1)
        else:
            dirSpeed = self.speed
        
        self.x = self.x + dirSpeed
        
    def moveXSprink(self, XPositive):
        
        if not XPositive:
            dirSpeed = self.speed
        else:
            dirSpeed = self.speed * (-1)
        
        for sprinkler in Rotator:
            sprinkler.runner_Xmove(dirSpeed)
        
        self.distance = self.distance - dirSpeed
        
    def moveDiagonal(self, XPositive, YPositive):
        #FIXME 192hgk2u59 key controls are not normalized for diagonal movement.
        diagSpeed = (self.speed*self.__diagMove)
        
        if XPositive:
            self.x = self.x + diagSpeed
        else:
            self.x = self.x - diagSpeed
            
        if YPositive:
            self.y = self.y + diagSpeed
        else:
            self.y = self.y - diagSpeed
    
    def moveDiagonalSprink(self, XPositive, YPositive):
        #FIXME 192hgk2u59 key controls are not normalized for diagonal movement.
        diagSpeed = (self.speed*self.__diagMove)
        
        if XPositive:
            ##Has to be out of below for loop...
            self.distance = self.distance + diagSpeed
            for sprinkler in Rotator:
                sprinkler.xHead = sprinkler.xHead - diagSpeed
        else:
            ##Same thing hahaha
            self.distance = self.distance - diagSpeed
            for sprinkler in Rotator:
                sprinkler.xHead = sprinkler.xHead + diagSpeed
            
        if YPositive:
            self.y = self.y + diagSpeed
        else:
            self.y = self.y - diagSpeed
    ##</KEY CONTROL>
    def mouse_control(self, xMouse, yMouse):
        
        ##Get the xy change
        xChange = xMouse - self.x
        yChange = yMouse - self.y
        
        ##Get the distance between the guy and cursor
        totChange = math.sqrt((xChange**2) + (yChange**2))
        
        ##Abort if no change, avoid /0
        if totChange == 0:
            return
        
        ##Get proportional x,y to distance = 1
        ##totChange will always be positive
        xInc = xChange/totChange
        yInc = yChange/totChange
        
        ##Get greatest wind size for dist-speed
        (windWidth, windHeight) = self.window.get_size()
        if windWidth > windHeight:
            windSize = windWidth
        else:
            windSize = windHeight
        
        ##25% of screen size away from guy is max speed
        if totChange >= (windSize/4):
            speedPerc = 1
        else:
            ##Get percentile of distance between guy and 25% of screen size
            speedPerc = totChange/(windSize/4)
        
        ##Multiply incs by speed, and that by speedPerc to get final inc
        increment = self.speed*xInc*speedPerc
        
        self.distance = self.distance + increment
        
        ##Do the opposite for the sprinklers
        for sprink in Rotator:
            ##sprink.xHead = sprink.xHead - increment
            sprink.runner_Xmove((increment*-1))
        
        self.y = self.y + (self.speed*yInc*speedPerc)
        
        
    def getMove(self, keys):
        """keys is a pygame.key.get_pressed() object
        This method also uses self.arrows"""
        ##define control methods
        
        #FIXME the sprinkler movement is incorrect when both mouse and key controls are used simultaneously.
        #FIXME simultaneous key and mouse controls give additive speed.
        #FIXME 192hgk2u59 key controls are not normalized for diagonal movement.
        if self.arrows:
            left = keys[pygame.K_LEFT]
            right = keys[pygame.K_RIGHT]
            down = keys[pygame.K_DOWN]
            up = keys[pygame.K_UP]
            restart = keys[pygame.K_RSHIFT]
        else:
            left = keys[pygame.K_a]
            right = keys[pygame.K_d]
            down = keys[pygame.K_s]
            up = keys[pygame.K_w]
            restart = keys[pygame.K_LSHIFT]
            
        if restart:
            self.x, self.y, self.distance = self.start()
        
        if left:
            if up:
                self.moveDiagonalSprink(False, False)
            elif down:
                self.moveDiagonalSprink(False, True)
            else:
                self.moveXSprink(False)           
        elif right:
            if up:
                self.moveDiagonalSprink(True, False)
            elif down:
                self.moveDiagonalSprink(True, True)
            else:
                self.moveXSprink(True)
        elif up:
            self.moveY(False)
        elif down:
            self.moveY(True)
        
            
    def reDraw(self, window=None, x=None, y=None, image=None):
        """In this method, image is a pygame image object"""
        
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if window is None:
            window = self.window
        if image is None:
            image = self.image
            
        window.blit(image, (self.x, self.y))
        
    def check_dist_add(self, sprinklerList):
        
        ##print self.distance
        ##If the dude was recently re
        if (self.distance == 0) and (self.reInit):
            
            ##We've restarted! Don't do it again
            self.reInit = False
            
            ##ReInit lastPlaced distance
            self.lastPlaced = 0
            
            ##Clear iterable registry
            Rotator._registry = []
            
            sprinklerList = []
            sprinklerList = [Rotator(screen, True, teal, randrange(500, 900), randrange(3, 6), randrange(0, WIDTH), randrange(0, HEIGHT), randrange(0, 6), randrange(25, 70), randrange(5, 10)) for name in range(3)]
            
        ##Place if we've traveled the travel dist since the last x-coord we placed
        elif (self.lastPlaced + 200 < self.distance):
            
            ##Track distance last placed
            self.lastPlaced = self.distance
            
            sprinklerList.append(Rotator(screen, True, teal, randrange(500, 900), randrange(3, 6), (WIDTH + randrange(100, 400)), randrange(-50, (HEIGHT+50)), randrange(0, 6), randrange(25, 70), randrange(5, 10)))

        return sprinklerList
            
class Rotator(object):
    
    ##FIXME
    ## Needs Value Error and Type Error exception handling for arguments    
    ##/FIXME
    
    ##Class elements
    
    ##Link to metaclass, define registry
    __metaclass__ = IterRegistry
    _registry = []
    
    ##Internal variables
    #FIXME just use math.pi
    __pi=3.14
    
    def __init__(self, window, placed, color, fluid, fAmps, xHead, yHead, theta, rotInc, segNum):
        """Speed is the # of frames it takes to go around a full circle
            Theta is the starting angle"""
        
        ##Append instance to class registry
        self._registry.append(self)
        
        ##Basic inits
        self.window = window
        self.color = color
        self.fluid = fluid
        self.fAmps = fAmps
        self.segNum = segNum
        
        ##Placed bool: this determines whether to draw the sprinkler
        self.placed = placed
        
        ##Move arguments to class members accessible by other class definitions        
        self.xHead = xHead
        self.yHead = yHead
        self.theta = theta
        self.speed = self.__pi/rotInc
        
        self.pressure = self.get_pressure()
        self.rnge = self.pressure
        
        self.init_segments()
        
    def init_segments(self):
        ##Must call this every time the sprinkler is replaced, otherwise there are "invisible segments"
        self.xEnd = self.getxEnd()
        self.yEnd = self.getyEnd()
        self.segments = [Segment(self.window, self.color, self.pressure, self.fAmps, self.segNum, self.xHead, self.yHead, self.xEnd, self.yEnd)]
    def get_pressure(self, fAmps = None, fluid = None):
        
        ##FIXME This might be divided by a constant? Or should the normal fAmps/fluid ratio just be such that in acts appropriately
        ##FIXME     a quick research of water pressure equations should reveal this.
        
        ##Args
        if fAmps is None:
            fAmps = self.fAmps
        if fluid is None:
            fluid = self.fluid
        ##/Args
        
        return (fluid/fAmps)
        
    def getxEnd(self, h=None, r=None, theta=None):
        """Either uses instance variables, or takes arguments.
            Returns the x coord end point"""
            
        ##Process optional parameters
        if h is None:
            h = self.xHead
        if r is None:
            r = self.rnge
        if theta is None:
            theta=self.theta
        ##/Process optoinal parameters 
        
        return(h + (r * math.cos(theta)))   
        
    def getyEnd(self, k=None, r=None, theta=None):
        """Either uses instance variables, or takes arguments.
            Retuns the y coord end point"""
            
        ##Process optional parameters
        if k is None:
            k=self.yHead
        if r is None:
            r=self.rnge
        if theta is None:
            theta=self.theta
        ##/Process optoinal parameters
        
        return(k + (r * math.sin(theta)))
    
    def IncrementTheta(self, theta=None, speed=None):
        """Either uses instance variables, or takes arguments."""
        
        ##Process optional parameters
        if theta is None:
            theta=self.theta
        if speed is None:
            speed=self.speed
        ##/Process optoinal parameters
        
        ##Some sprinklers do funky stuff when being reset to 0
        ##This needs to be relative to the sprinkler's initial theta...do something with that.
        
        if math.fabs(theta) < math.fabs(((2*self.__pi)-speed)):
            theta = theta + speed
        else:
            theta = 0
        
        ##Return theta
        return theta
        
    def reDraw(self, window=None, color=None):
        """Increments angle, updates endpoints.
            Uses class variables for points draw.
            And optional set arguments for window, color, and fluid"""
        
        if not self.segments[-1].forming:
            
            ##Process optional parameters
            if window is None:
                window=self.window
            if color is None:
                color=self.color
            ##/Process optoinal parameters
            
            ##Increment angle first!
            self.theta = self.IncrementTheta()
            
            ##Get endpoints second
            self.yEnd = self.getyEnd()
            self.xEnd = self.getxEnd()
            
            ##For dynamic pressure changes, only apply to new segments
            self.pressure = self.get_pressure()
            
            self.segments.append(Segment(window, color, self.pressure, self.fAmps, self.segNum, self.xHead, self.yHead, self.xEnd, self.yEnd))
            
            ##pygame.draw.line(window, color, (self.xHead, self.yHead), (self.xEnd, self.yEnd), self.fluid)
            
        ##Clean finished segments
        if self.segments[0].finished:
            del self.segments[0]
            
        for seg in self.segments:
            seg.reDraw()
            
    def collision(self, runner):
        
        ##FIXME this will probably be a param passed to the method eventually.
        ##FIXME but leave here now for understandings sake.
        ##FIXME should be replaced in favor of a collision box for the runner
        proxLeeway = 3.14/128
        
        ##INITS
        
        ##Get distance between runner and each segment
        runRelX = runner.x-self.xHead
        runRelY = runner.y-self.yHead
        
        ##/INITS
            
        ##RANGE
        ##Check if runner is in range
        ##Distance formula
        runnerDistance = math.sqrt(((runner.x - self.xHead)**2)+((runner.y - self.yHead)**2))
        
        furthestSegment = self.segments[0]
        if runnerDistance > (furthestSegment.traveledLen - (furthestSegment.allowedLen - furthestSegment.actualLen)):
            return False
        ##/RANGE
        
        if len(self.segments) > 1:
            ##SPAN
            ##Checking span before looping segments is actually better. Looping through 
            ##      every segment of every sprinkler in range takes a lot of power
            ##Get angle between the first segment and last segment, all water falls between.
            ##acos of normalized dot product.
            ##seg.P* is the normalized vector of the full length the segment will travel
            
            ##Newest segment to Oldest segment
            NOdpNorm = ((self.segments[-1].Px) * (self.segments[0].Px)) + ((self.segments[-1].Py) * (self.segments[0].Py))
            spanNO = math.acos(NOdpNorm)
            
            ##Newest segment to Runner
            NRdpNorm = ((self.segments[-1].Px) * (runRelX/runnerDistance)) + ((self.segments[-1].Py) * (runRelY/runnerDistance))
            spanNR = math.acos(NRdpNorm)
            
            ##Oldest segment to Runner
            ORdpNorm = ((self.segments[0].Px) * (runRelX/runnerDistance)) + ((self.segments[0].Py) * (runRelY/runnerDistance))
            spanOR = math.acos(ORdpNorm)
            
            ##Check if runner does not double overlap, if he does, he's in the larger angle between the old/new segments
            ##To detect positively, would check if spanNR <= spanNO >= spanOR, if so, he's between them.
            ##proxLeeway added in case on outside edge of spanNO
            ##FIXME if spanNO == pi, he will collide on both sides, but the sprinklers should never have a span of pi?
            if (spanNR > (spanNO + proxLeeway)) or (spanOR > (spanNO + proxLeeway)):
                return False
            ##FIXME tshoot span visualizer
            pygame.draw.line(self.window, (255, 255, 255), (self.xHead, self.yHead), (((self.segments[0].Px * self.segments[0].rnge) + self.xHead), ((self.segments[0].Py * self.segments[0].rnge) + self.yHead)), 2)
            pygame.draw.line(self.window, (255, 255, 255), (self.xHead, self.yHead), (((self.segments[-1].Px * self.segments[-1].rnge) + self.xHead), ((self.segments[-1].Py * self.segments[-1].rnge) + self.yHead)), 2)
            ##/SPAN
            
            
            ##SUBRANGE
            for i, seg in enumerate(self.segments):
                ##We already know he's in range of the furthest segment, so we can check seg.traveledLen from furthest seg from center
                ##  He's in range and between the newest and oldest segments.
                ##      even if all the segments have not been created, for some segment, runnerDistance < traveledLen.
                ##      that is, this will never break with i<1
                if runnerDistance < seg.traveledLen:
                    pass
                else:
                    break
            
            ##See note above, this will not wrongly read the newest segment, i will be > 0
            checkSeg = self.segments[i-1]
            
            ##/SUBRANGE
            
        ## else there is only 1 segment
        else:
            seg = self.segments[0]
            if runnerDistance > seg.traveledLen:
                ##if runner is outside of the first segment's range
                return False
            else:
                checkSeg = seg
        
        ##FIXME tshoot range visualizer
        checkRadius = int((checkSeg.traveledLen - (checkSeg.allowedLen - checkSeg.actualLen)))
        if checkRadius > 1:
            pygame.draw.circle(self.window, (0, 0, 0), (int(self.xHead), int(self.yHead)), checkRadius, 1)
        
        ##Get runner span from checkSeg to runner
        CRdpNorm = ((checkSeg.xLen/self.rnge) * (runRelX/runnerDistance)) + ((checkSeg.yLen/self.rnge) * (runRelY/runnerDistance))
        spanCR = math.acos(CRdpNorm)
        
        if spanCR < proxLeeway:
            pygame.draw.line(self.window, (0, 0, 0), (self.xHead, self.yHead), (runner.x, runner.y), 10)
            return True
        else:
            return False
        
        #FIXME use the warning module
        print "Weird exception in collision detection! Shouldn't have gotten this far."
        
    def runner_Xmove(self, distance):
        self.xHead = self.xHead + distance
        for seg in self.segments:
            seg.runner_Xmove(distance)
##Main Inits

pygame.init() 
WIDTH = 480*2
HEIGHT = 320*2
screen = pygame.display.set_mode((WIDTH, HEIGHT),0, 32)

clock = pygame.time.Clock()
FPS = 40

forestGreen = (34, 139, 34)
darkRed = (139, 0, 0)
teal = (0, 128, 128)
red, green, blue = 90, 200, 60

i = 0

myfont = pygame.font.SysFont("monospace", 30)

##/Main Inits

##Object inits!

    ## = ( window, True:Arrows/False:WASD, True:Top of screen/False:Bottom of Screen, speed, image path)
    ##FIXME default speed not remembered, reset to 2 in start
runnerTop = Runner(screen, False, True, 5, 'Images/ShyGuyMSS.PNG')

##Sprinklers are created and added by the runner, per his distance see PROCESSES
##But need init.
sprinks = []

##/Object inits!

##Drawing Loooooop!
while True:
    
    ##PROCESSES
    
    ##Ask Runner if his distance warrants new sprinklers
    ##FIXME Using multiple runners...will make a gazillion sprinklers.
    for dude in Runner:
        ##Pass sprinks for append/delete
        sprinks = dude.check_dist_add(sprinks)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()         
    
    for sprinkler in Rotator:
        
        ##Sprinklers now start placed
        ##Check if not placed, place new sprinklers
        ##if not sprinkler.placed:
        ##    sprinkler.xHead = randrange(50, (WIDTH+300)) ##Spread out sprinklers
        ##    sprinkler.yHead = randrange(-50, (HEIGHT+50))
        ##    sprinkler.placed = True
        
        if not sprinkler.placed:
            print 'Woops!'
        
        ##Check if sprinkler is off the screen
        ##FIXME ought to be a method of the sprinkler itself.
        if sprinkler.xHead < (-150):
    
            ##Move sprinkler
            ##FIXME ought to be a method of the sprinkler itself.
            sprinkler.xHead = sprinkler.xHead + (WIDTH+(randrange(150, 500)))
            sprinkler.yHead = randrange(-50, (HEIGHT+50))
            sprinkler.init_segments()
    
            randomDir = randrange(1, 3)
            if randomDir % 2 == 0:
                sprinkler.speed = sprinkler.speed * (-1)
        
                
    ##/PROCESSES
    
    ##DRAW and UPDATE OBJECTS
    screen.fill((red, green, blue))
    
    #FIXME for performance, combine these two loops with the ones above? for readability, maybe not?
    
    for sprinkler in Rotator:
        ##Check if sprinkler has been placed before drawing
        if sprinkler.placed:
            sprinkler.reDraw()
            
            #NOTE TODO 20160520: this run time is O(num sprinkler * num runner), because we just have 1 or 2 runners, this is not a big deal
            #               BUT, if there were lots of runners, we'd probably want to use a sweep line.
            #               1. keep an ordered list of events, by x value, of sprinkler (position - radius) and (position + radius)
            #               2. and a stack of ordered runners
            #                    we'd probably use insertion sort to maintain both of these, as only small changes are needed to each on each frame
            #                    and we want constant retrieval time.
            #               3. if the event is a left side,
            #                   store the sprinkler in an a list ordered by left position
            #                   store the sprinkler by name in a dictionary/hash table, this will have an index to its list position
            #               3. if the event is a right side,
            #                   examine runners in the list until one is encountered past the sweep line
            #                   if the runner is left of the furthest retained left event, discard the runner
            #                   check collisions for each runner to this sprinkler.
            #                   then discard corresponding left event
            #               
            #               for each event then, only the runners in the window between the leftest left event and the sweep line will be checked against
            #                   each sprinkler. the best case scenario would be O 2(sprinklers), and would occur if no explorer was examined twice..
            #                   the worst case would be if there was a GIANT sprinkler whose left and right events encompassed all events and runners. 
            #                   in this case, all the runners would have to be examined for each event, so we'd have O 2(sprinklers)(runners)
            #               if we took advantage of the triangle in which all the collision exists, we could do two sweep lines
            #                   the first would have an x-ordered list of left and right events of collision triangles that were more narrow on x than y.
            #                   the second would have a y-ordered list of top and bottom events of collision triangles that were more narrow on y than x.
            #                   these lists would require similarly small changes, so insertion sort could be used.
            #                   sprinklers would switch lists very infrequently, so they could be placed in the other list in O logn average case using a quicksort.
            #               
            
            ##Check if a runner has collided!
            for oneRunner in Runner:
                if sprinkler.collision(oneRunner):
                    if oneRunner.speed > 0:
                        oneRunner.speed = oneRunner.speed - (oneRunner.defSpeed*0.10)
                    if red < 225:
                        red = red + 30
                    else: red = 0
                    
            
    for oneRunner in Runner:
        ##Keyboard
        keys = pygame.key.get_pressed()
        oneRunner.getMove(keys)
        
        ##Mouse Control
        mPos = pygame.mouse.get_pos()
        oneRunner.mouse_control(*mPos)
        
        oneRunner.reDraw()
    
    ##Display score for runnertop
    score = myfont.render(str(int(runnerTop.distance)), 1, (255,255,0))
    screen.blit(score, ((WIDTH-100), (HEIGHT-100)))
    
    pygame.display.flip()
    ##/DRAW and UPDATE OBJECTS
    
    clock.tick(FPS)
    
##/Drawing Loooop!
    