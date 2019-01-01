#!/usr/local/bin/python3

# rooms: http://jswremakes.emuunlim.com/Mmt/Manic%20Miner%20Room%20Format.htm
# -8 -8 -6 -6 -4 -4 -2 -2 0 0 2 2 4 4 6 6 8 8
# https://www.gamejournal.it/the-sound-of-1-bit-technical-constraint-as-a-driver-for-musical-creativity-on-the-48k-sinclair-zx-spectrum/z
# D=8*(1+ABS(J-8));

# TODO:
#  bring in code for Brick as a SolidStandable object again
#  when hitting the brick try just setting willyJump to the mid-way point and willyWalk or whatever to False
#  fix up the weird jump lands
#  conveyors need implenting
#  fix up the graphics so they don't need scaling

import os, sys, math, re, logging, pdb, time
# load pygame without getting its hello message
with open(os.devnull, 'w') as f:
    # disable stdout
    oldstdout = sys.stdout
    sys.stdout = f
    # do imports
    import pygame
    from pygame.locals import *;
    from pygame import key;
    # enable stdout
    sys.stdout = oldstdout

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Test:
    def __init__(self):
        # self.testString1 = "R5,RJ1,R"
        self.testString2 = "R20, R10,L10,J,J,R5,L5"
        self.testString1 = "R5, RJ, J2, R5, RJ, J2, L5, LJ, J, L5, LJ, J, L5, R20, L15, R15, L15, R15"

        self.testMoves = []

        shortmoves = {
            "L": ["left"],
            "R": ["right"],
            "LJ": ["left", "jump"],
            "RJ": ["right", "jump"],
            "J": ["jump"],
        }

        moves = self.testString1.split(",")
        # print("moves: ", moves)
        for move in moves:
            # print("move: ", move)
            # read the number of iterations
            iters = re.findall('[0-9]+', move)
            if len(iters) == 0:
                iters = 1
            else:
                iters = int(iters[0])
            # print("iters: ", iters)
            # read the direction
            dir = re.findall('[A-Z]+', move)[0]
            # print("dir: ", dir)
            self.testMoves.append((iters, shortmoves[dir]))
        # print(self.testMoves)
        # for i in range(0,len(self.testMoves)):
        #     print("Loading test... ", self.testMoves[i])
        self.moveNumber = 0    

    def getNextMove(self):
        # print("moveNumber: ", self.moveNumber)
        if self.moveNumber < len(self.testMoves):
            (repetitions, keys) = self.testMoves[self.moveNumber]
            # print("Playing test: ", repetitions, keys)
            repetitions -= 1
            self.testMoves[self.moveNumber] = (repetitions, keys)
            if repetitions == 0:
                self.moveNumber += 1
            return keys
        else:
            return ["none"]

class Events:
    def __init__(self):
        # print("ctor")
        self.eventCount = 0
        self.keysPressed = {
            "left": False,
            "right": False,
            "jump": False,
            "dev1": False,
            "dev2": False,
            "dev3": False,
            "test": False,
            "music": False,
        }

    def check(self):
        self.eventCount += 1
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == pygame.K_t:
                    # print("test mode")
                    self.keysPressed["test"] = True
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_q:
                    print("Manic Miner quit")
                    return False
                if e.key == pygame.K_SPACE or e.key == pygame.K_UP:
                    # print("up pressed")
                    self.keysPressed["jump"] = True
                if e.key == pygame.K_o or e.key == pygame.K_LEFT:
                    # print("left pressed")
                    self.keysPressed["left"] = True
                    self.keysPressed["right"] = False
                elif e.key == pygame.K_p or e.key == pygame.K_RIGHT:
                    # print("right pressed")
                    self.keysPressed["right"] = True
                    self.keysPressed["left"] = False
                if e.key == pygame.K_j:
                    self.keysPressed["dev1"] = True
                if e.key == pygame.K_k:
                    self.keysPressed["dev2"] = True
                if e.key == pygame.K_l:
                    self.keysPressed["dev3"] = True
                if e.key == pygame.K_m:
                    self.keysPressed["music"] = True
            elif e.type == KEYUP:
                if e.key == pygame.K_t:
                    # print("test released")
                    self.keysPressed["test"] = False
                if e.key == pygame.K_SPACE or e.key == pygame.K_UP:
                    # print("up released")
                    self.keysPressed["jump"] = False
                if e.key == pygame.K_o or e.key == pygame.K_LEFT:
                    # print("left released")
                    self.keysPressed["left"] = False
                elif e.key == pygame.K_p or e.key == pygame.K_RIGHT:
                    # print("right released")
                    self.keysPressed["right"] = False
                if e.key == pygame.K_j:
                    # print("dev1 released")
                    self.keysPressed["dev1"] = False
                if e.key == pygame.K_k:
                    # print("dev2 released")
                    self.keysPressed["dev2"] = False
                if e.key == pygame.K_l:
                    # print("dev3 released")
                    self.keysPressed["dev3"] = False
                if e.key == pygame.K_m:
                    self.keysPressed["music"] = False
            elif e.type == QUIT:
                    print("Manic Miner quit")
                    return False
        return True

class Sound:
    def __init__(self):
        self.playMusic = True
        self.mainMusic = pygame.mixer.music.load('maingame.ogg')
        self.death = pygame.mixer.Sound('death.ogg')
        self.titleTune = pygame.mixer.Sound('titletune.ogg')
        self.jumpFall = pygame.mixer.Sound('jumpfall.ogg')
        self.fall = pygame.mixer.Sound('fall.ogg')
        self.gameOver = pygame.mixer.Sound('gameover.ogg')

    def toggleMainMusic(self):
        print("self.playMusic before: ", self.playMusic)
        self.playMusic = not self.playMusic
        print("self.playMusic after: ", self.playMusic)
        if self.playMusic == False:
            self.pauseMainMusic()
        else:
            self.playMainMusic()
        
    def startMainMusic(self):
        if (self.playMusic):
            pygame.mixer.music.play(-1, 0.15)

    def playMainMusic(self):
        if (self.playMusic):
            pygame.mixer.music.unpause()

    def waitUntilFinished(self):
        while pygame.mixer.get_busy():
            pass

    def pauseMainMusic(self):
        pygame.mixer.music.pause()

    def playDeathSound(self):
        self.death.play()

    def playJumpFallSound(self):
        self.jumpFall.play()

    def stopJumpFallSound(self):
        self.jumpFall.stop()

    def playFallSound(self):
        self.fall.play()

    def stopFallSound(self):
        self.fall.stop()

    def playGameOver(self):
        self.gameOver.play()
        self.waitUntilFinished()

    def playTitleTune(self):
        self.titleTune.play()
        self.waitUntilFinished()

    def stopAll(self):
        self.titleTune.stop()
        self.jumpFall.stop()
        self.fall.stop()
        pygame.mixer.music.stop()

class Collision:
    def __init__(self, object, event):
        self.collidingObject = object
        self.event = event

class Screen:
    def __init__(self, x, y):
        pygame.init()
        self.FPS = 15 # frames per second setting
        self.fpsClock = pygame.time.Clock()
        # set up the window
        self.max_x = x
        self.max_y = y
        self.scale = 2.4           # how much to scale the loaded sprites
        # DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), 0, 32)
        # DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), pygame.FULLSCREEN)
        self.DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), pygame.RESIZABLE)
        pygame.display.set_caption('Manic Miner')
        pygame.key.set_repeat(1,10)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        # define some boundary values
        self.xboundary_left = 5
        self.xboundary_right = self.max_x - 50 # willyImgWidth*2
        self.yboundary_top = 5
        self.yboundary_bottom = self.max_y - 50 # willyImgHeight*2
        self.collisionCount = 0
        self.cellWidth = self.max_x / 32
        self.cellHeight = self.max_y / 16
        self.alpha = 255
        self.RGB = {
            "yellow":  (189,189,0),
            "magenta": (189,0,189),
            "cyan":    (0,189,189),
            "green":   (0,189,0),
            "red":     (189,0,0),
        }

    def cellToCoords(self, x, y):
        coord_x = x * self.cellWidth
        coord_y = y * self.cellHeight
        return (coord_x,coord_y)
    
    # given coordinates (x,y), return the corresponding 
    # def getScreenLoc(self, x, y):
        
    def displayBackground(self):
        self.DISPLAYSURF.fill(self.BLACK)

    def flashBackground(self):
        self.DISPLAYSURF.fill(self.WHITE)

    def displayBlocks(self):
        return

    def displayConveyors(self):
        return

    #def load(self, roomData):
        # roomData is a 2D array, 32 wide by 16 tall, each block corresponding to a wall, floor, guardian, key, etc.
        # print("start of map")
        #for row in range (0,15): # each row
            # print("row: ", row)
            # for col in range (0,31): # each column
                # print("col: ", col)
                # print(roomData[row][col],end=', ')
            # print()
        ## print("end of map")
    
    def checkCollisions(self, willy, objects, willyx=-1, willyy=-1):
        # use either willy's current (x,y) by default, or a hypothetical (x,y) to see what would happen
        if (willyx == -1):
            willyx = willy.xpos
        if (willyy == -1):
            willyy = willy.ypos
        willy_left = willyx
        willy_right = willyx + willy.width
        willy_top = willyy
        willy_bottom = willyy + willy.height
        # print("willy x,y: (", willy.xpos, ",", willy.ypos, ")")
        # print("willy bounds: (", willy_left, ",", willy_top, ") to (", willy_right, ",", willy_bottom, ")")

        collisionWatchList = ["floor-10-11", "floor-11-11", "floor-12-11", "floor-2-9"]
        collisions = []

        for object in objects:
            if object.collidable == True:
                object_left = object.xpos
                object_right = object.xpos + object.width
                object_top = object.ypos
                object_bottom = object.ypos + object.height
                horizontal = False
                vertical = False
                collision = False
                # print("object: ", object.name, ": (", object.xpos, ",", object.ypos, ")")
                # print("          (", object_left, ",", object_top, ") to (", object_right, ",", object_bottom, ")")
                if willy_right - 1 >= object_left and willy_right <= object_right:
                    horizontal = True
                if willy_left <= object_right and willy_left >= object_left:
                    horizontal = True
                if willy_bottom >= object_top and willy_bottom <= object_bottom:
                    vertical = True
                if willy_top <= object_bottom and willy_top >= object_top:
                    vertical = True
                if horizontal == True and vertical == True:
                    collision = True
                if collision == True:
                    self.collisionCount += 1
                    if isinstance(object, StandableObject) and object.standable == True:
                        if object.name in collisionWatchList:
                            print("willy  (L,R,T,B): ", willy_left, willy_right, willy_top, willy_bottom)
                            print("object (L,R,T,B): ", object_left, object_right, object_top, object_bottom)
                            print("WB (", willy_bottom, ") needs to be in range ", object_top - 5, " to ", object_top + 5)
                        if (willy.falling or willy.willyJump <= willy.willyJumpDistance / 2) \
                           and willy_bottom >= object_top and willy_bottom <= object_top + 10:
                            willy.ypos = object_top - willy.height
                            collisions.append(Collision(object, "landed"))
                            continue
                    collisions.append(Collision(object, "collision"))
        return collisions

    def colorImage(self, image, color):
        print("setting to " + color)
        imageCopy = image.copy()
        clear = (255, 255, 255, 0)
        rgb = self.RGB[color] + (0,)
        imageCopy.fill(clear, None, pygame.BLEND_RGBA_SUB)
        imageCopy.fill(rgb, None, pygame.BLEND_RGBA_ADD)
        return imageCopy

class Object:
    def __init__(self, start_x, start_y, name="NoName"):
        # print("Creating Object: ", name)
        self.xpos = start_x
        self.ypos = start_y
        self.startxpos = start_x
        self.startypos = start_y
        self.type = "Object"
        self.name = name
        self.collidable = False
        self.image = pygame.image.load('empty.png')

    def restart(self):
        self.xpos = self.startxpos
        self.ypos = self.startypos

    def setColor(self, screen, color):
        print("setColor ", self.name, color)
        self.image = screen.colorImage(self.image, color)
        return

class MovingObject(Object):
    def __init__(self, start_x, start_y, name="MovingObject"):
        # print("Creating MovingObject: ", name)
        Object.__init__(self, start_x, start_y, name)
        self.type = "MovingObject"

    def restart(self):
        Object.restart(self)
        self.direction = "right"

class StationaryObject(Object):
    def __init__(self, x, y, name="StationaryObject"):
        # print("Creating StationaryObject: ", name)
        Object.__init__(self, x, y, name)
        self.type = "StationaryObject"
        self.collidable = True

class Portal(StationaryObject):
    def __init__(self, x, y, scale, name="Portal"):
        StationaryObject.__init__(self, x, y, name)
        self.type = "Portal"
        
        self.portalImg = [
            pygame.image.load('portal_start.png'),
            pygame.image.load('portal_end.png'),
        ]
        # scale the sprites up to larger
        numImages = len(self.portalImg)
        for count in range(0, numImages):
            (portalImgWidth, portalImgHeight) = self.portalImg[count].get_rect().size
            newHeight = int(portalImgHeight * scale)
            newWidth = int(portalImgWidth * scale)
            picture = pygame.transform.scale(self.portalImg[count], (newWidth, newHeight))
            self.portalImg[count] = picture
            (portalImgWidth,portalImgHeight) = self.portalImg[count].get_rect().size
            newHeight = int(portalImgHeight * scale)
            newWidth = int(portalImgWidth * scale)
            picture = pygame.transform.scale(self.portalImg[count], (newWidth,newHeight))
            self.portalImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Portal Width: ", self.width)
            # print("Portal Height: ", self.height)
        self.displayCount = 0
        self.imageNum = 0
        self.image = self.portalImg[self.imageNum]
        self.open = False
        self.collidable = True

    def move(self, screen):
        if self.open:
            self.displayCount += 1
            if self.displayCount <= 5:
                self.imageNum = 0
            else:
                self.imageNum = 1
            self.image = self.portalImg[self.imageNum]
            if self.displayCount == 10:
                self.displayCount = 0

    def restart(self):
        self.open = False

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))
        
class StandableObject(StationaryObject):
    def __init__(self, x, y, name="StandableObject"):
        StationaryObject.__init__(self, x, y, name)
        self.standable = True

class Floor(StandableObject):
    def __init__(self, x, y, scale, name="Floor"):
        print("Creating Floor: ", name)
        StandableObject.__init__(self, x, y, name)
        self.type = "Floor"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.floorImg = [
            pygame.image.load('floor_1.png'), # red
        ]
        # scale the sprites up to larger
        numImages = len(self.floorImg)
        for count in range(0, numImages):
            (floorImgWidth, floorImgHeight) = self.floorImg[count].get_rect().size
            newHeight = int(floorImgHeight * scale)
            newWidth = int(floorImgWidth * scale)
            picture = pygame.transform.scale(self.floorImg[count], (newWidth, newHeight))
            self.floorImg[count] = picture
            (floorImgWidth,floorImgHeight) = self.floorImg[count].get_rect().size
            newHeight = int(floorImgHeight * scale)
            newWidth = int(floorImgWidth * scale)
            picture = pygame.transform.scale(self.floorImg[count], (newWidth,newHeight))
            self.floorImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Floor Width: ", self.width)
            # print("Floor Height: ", self.height)
        self.image = self.floorImg[0]

    def restart(self):
        pass

    def display(self, screen):
        image = self.floorImg[0]
        screen.DISPLAYSURF.blit(image, (self.xpos,self.ypos))

class CrumblingFloor(StandableObject):
    def __init__(self, x, y, scale, name="CrumblingFloor"):
        print("Creating CrumblingFloor: ", name)
        StandableObject.__init__(self, x, y, name)
        self.type = "CrumblingFloor"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.floorImg = [
            pygame.image.load('crumble_1.png'),
            pygame.image.load('crumble_2.png'),
            pygame.image.load('crumble_3.png'),
            pygame.image.load('crumble_4.png'),
            pygame.image.load('crumble_5.png'),
            pygame.image.load('crumble_6.png'),
            pygame.image.load('crumble_7.png'),
            pygame.image.load('crumble_8.png'),
        ]
        # scale the sprites up to larger
        numImages = len(self.floorImg)
        for count in range(0, numImages):
            (floorImgWidth, floorImgHeight) = self.floorImg[count].get_rect().size
            newHeight = int(floorImgHeight * scale)
            newWidth = int(floorImgWidth * scale)
            picture = pygame.transform.scale(self.floorImg[count], (newWidth, newHeight))
            self.floorImg[count] = picture
            (floorImgWidth,floorImgHeight) = self.floorImg[count].get_rect().size
            newHeight = int(floorImgHeight * scale)
            newWidth = int(floorImgWidth * scale)
            picture = pygame.transform.scale(self.floorImg[count], (newWidth,newHeight))
            self.floorImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Floor Width: ", self.width)
            # print("Floor Height: ", self.height)
        self.crumbleLevel = 0
        self.image = self.floorImg[self.crumbleLevel]

    def crumble(self):
        if self.crumbleLevel == 0:
            self.crumbleLevel += 2
        else:
            self.crumbleLevel += 1
        if self.crumbleLevel == 8:
            self.standable = False

    def restart(self):
        self.crumbleLevel = 0
        self.standable = True

    def display(self, screen):
        if self.crumbleLevel < 8:
            image = self.floorImg[self.crumbleLevel]
            screen.DISPLAYSURF.blit(image, (self.xpos,self.ypos))
        # otherwise just don't show anything

class Ice(StationaryObject):
    def __init__(self, x, y, scale, name="Ice"):
        print("Creating Ice: ", name)
        StationaryObject.__init__(self, x, y, name)
        self.type = "Ice"
        # sprite
        self.image = pygame.image.load('icicle.png')
        # scale the sprites up to larger
        (iceImgWidth, iceImgHeight) = self.image.get_rect().size
        newHeight = int(iceImgHeight * scale)
        newWidth = int(iceImgWidth * scale)
        picture = pygame.transform.scale(self.image, (newWidth, newHeight))
        self.image = picture
        self.width = newWidth
        self.height = newHeight
        # print("Ice Width: ", self.width)
        # print("Ice Height: ", self.height)

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))

class Brick(StandableObject):
    def __init__(self, x, y, scale, name="Brick"):
        print("Creating Brick: ", name)
        StandableObject.__init__(self, x, y, name)
        self.type = "Floor"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.brickImg = [
            pygame.image.load('brick_1.png'),
        ]
        # scale the sprites up to larger
        numImages = len(self.brickImg)
        for count in range(0, numImages):
            (brickImgWidth, brickImgHeight) = self.brickImg[count].get_rect().size
            newHeight = int(brickImgHeight * scale)
            newWidth = int(brickImgWidth * scale)
            picture = pygame.transform.scale(self.brickImg[count], (newWidth, newHeight))
            self.brickImg[count] = picture
            (brickImgWidth,brickImgHeight) = self.brickImg[count].get_rect().size
            newHeight = int(brickImgHeight * scale)
            newWidth = int(brickImgWidth * scale)
            picture = pygame.transform.scale(self.brickImg[count], (newWidth,newHeight))
            self.brickImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Brick Width: ", self.width)
            # print("Brick Height: ", self.height)
        self.image = self.brickImg[0]

    def display(self, screen):
        image = self.brickImg[0]
        screen.DISPLAYSURF.blit(image, (self.xpos,self.ypos))

class Plant(StationaryObject):
    def __init__(self, x, y, scale, name="Floor"):
        print("Creating Plant: ", name)
        StationaryObject.__init__(self, x, y, name)
        self.type = "Plant"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.plantImg = [
            pygame.image.load('plant_1.png'),
        ]
        # scale the sprites up to larger
        numImages = len(self.plantImg)
        for count in range(0, numImages):
            (plantImgWidth, plantImgHeight) = self.plantImg[count].get_rect().size
            newHeight = int(plantImgHeight * scale)
            newWidth = int(plantImgWidth * scale)
            picture = pygame.transform.scale(self.plantImg[count], (newWidth, newHeight))
            self.plantImg[count] = picture
            (plantImgWidth,plantImgHeight) = self.plantImg[count].get_rect().size
            newHeight = int(plantImgHeight * scale)
            newWidth = int(plantImgWidth * scale)
            picture = pygame.transform.scale(self.plantImg[count], (newWidth,newHeight))
            self.plantImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Plant Width: ", self.width)
            # print("Plant Height: ", self.height)
        self.image = self.plantImg[0]

    def display(self, screen):
        image = self.plantImg[0]
        screen.DISPLAYSURF.blit(image, (self.xpos,self.ypos))

class Key(StationaryObject):
    def __init__(self, start_x, start_y, scale, name="Key"):
        StationaryObject.__init__(self, start_x, start_y, name)
        print("Creating Key: ", name)
        self.type = "Key"
        self.appears = True
        self.scorevalue = 100
        # animation sprites
        self.keyImg = [
            pygame.image.load('key_1.png'), # magenta
            pygame.image.load('key_2.png'), # yellow
            pygame.image.load('key_3.png'), # cyan
            pygame.image.load('key_4.png')  # green
        ]
        # scale the sprites up to larger
        numImages = len(self.keyImg)
        for count in range(0, numImages):
            (keyImgWidth, keyImgHeight) = self.keyImg[count].get_rect().size
            newHeight = int(keyImgHeight * scale)
            newWidth = int(keyImgWidth * scale)
            picture = pygame.transform.scale(self.keyImg[count], (newWidth, newHeight))
            self.keyImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Key Width: ", self.width)
            # print("Key Height: ", self.height)
        self.animPos = 0

    def disappear(self):
        self.appears = False
        self.collidable = False

    def move(self, screen):
        # this object doesn't move, but
        # the item's ink-colour cycles from magenta to yellow to cyan to green
        self.image = self.keyImg[self.animPos]
        self.animPos += 1
        if self.animPos == 4:
            self.animPos = 0

    def display(self, screen):
        if self.appears == True:
            screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))
        return

    def restart(self):
        StationaryObject.restart(self)
        self.appears = True
        self.collidable = True

class Escalator(StationaryObject):
    def __init__(self, start_x, start_y, scale, name = "Escalator"):
        StationaryObject.__init__(self, start_x, start_y, name)
        self.type = "Escalator"
        
class Guardian(MovingObject):
    def __init__(self, start_x, start_y, name = "Guardian"):
        MovingObject.__init__(self, start_x, start_y, name)
        self.type = "Guardian"
        self.xpos = start_x
        self.ypos = start_y
        self.startxpos = start_x
        self.startypos = start_y
        (self.width, self.height) = self.image.get_rect().size
        self.direction = "right"
        self.collidable = True

    def move(self, screen):
        print("self.xpos: ", self.xpos, " vs ", screen.xboundary_left)
        if self.xpos >= screen.xboundary_right:
            self.direction = "left"
        if self.xpos <= screen.xboundary_left:
            self.direction = "right"
        if self.direction == "right":
            self.xpos += 10
        elif self.direction == "left":
            self.xpos -= 10

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))
        return

class TrumpetNose(Guardian):
    def __init__(self, start_x, start_y, willyScale, name="TrumpetNose"):
        Guardian.__init__(self, start_x, start_y, name)
        self.subtype = "TrumpetNose"
        print("Creating TrumpetNose: ", name)
        # moving left animation sprites
        self.trumpetNoseImgLeft = [
            pygame.image.load('trumpetnose_left_1.png'),
            pygame.image.load('trumpetnose_left_2.png'),
            pygame.image.load('trumpetnose_left_3.png'),    
            pygame.image.load('trumpetnose_left_4.png')
        ]

        # moving right animation sprites
        self.trumpetNoseImgRight = [
            pygame.image.load('trumpetnose_right_1.png'),
            pygame.image.load('trumpetnose_right_2.png'),
            pygame.image.load('trumpetnose_right_3.png'),    
            pygame.image.load('trumpetnose_right_4.png')
        ]

        # scale the sprites up to larger
        numImages = len(self.trumpetNoseImgRight)
        for count in range(0, numImages):
            (trumpetNoseImgWidth, trumpetNoseImgHeight) = self.trumpetNoseImgRight[count].get_rect().size
            newHeight = int(trumpetNoseImgHeight * willyScale)
            newWidth = int(trumpetNoseImgWidth * willyScale)
            picture = pygame.transform.scale(self.trumpetNoseImgRight[count], (newWidth, newHeight))            
            self.trumpetNoseImgRight[count] = picture
            (trumpetNoseImgWidth,trumpetNoseImgHeight) = self.trumpetNoseImgLeft[count].get_rect().size
            newHeight = int(trumpetNoseImgHeight * willyScale)
            newWidth = int(trumpetNoseImgWidth * willyScale)
            picture = pygame.transform.scale(self.trumpetNoseImgLeft[count], (newWidth,newHeight))
            self.trumpetNoseImgLeft[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("TrumpetNose Width: ", self.width)
            # print("TrumpetNose Height: ", self.height)
        self.walkPos = 0
        self.direction = "right"
        self.endPosX = start_x + 100
        self.endPosY = start_y

    def setEndPos(self, screenx, screeny):
        print("Updating TrumpetNose endPosX")
        self.endPosX = screenx
        
    def move(self, screen):
        if self.direction == "left":
            self.image = self.trumpetNoseImgLeft[self.walkPos]
            self.xpos -= 4
        else: # direction == "right"
            self.image = self.trumpetNoseImgRight[self.walkPos]
            self.xpos += 4
        self.walkPos += 1 # for animation
        if self.walkPos == 4:
            self.walkPos = 0
        if self.xpos <= self.startxpos or self.xpos >= self.endPosX:
            if self.direction == "left":
                self.direction = "right"
            else:
                self.direction = "left"
        return

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))       

class Player:
    def __init__(self):
        self.score = 0
        self.lives = 3
        
class Willy(MovingObject):
    def __init__(self, start_x, start_y, scale):
        print("Creating Willy at ", start_x, start_y)
        MovingObject.__init__(self, start_x, start_y, "Willy")
        # motion distances
        self.xdistance = 4              # how far left and right motion moves Willy
        self.ydistance = 5              # how far jumping motion moves Willy on the y axis
        self.willyJumpDistance = 36     # how far to jump horizontally
        self.willyJumpHeight = 18       # peak of a jump relative to zero
        # starting position
        self.willystartx = start_x
        self.willystarty = start_y
        self.xpos = start_x           # willy's x location; start at left of screen
        self.ypos = start_y           # willy's y location; start at bottom of screen
        self.direction = "right";       # start willy off facing right
        self.walking = False            # is willy walking or standing still?

        self.willyWalk = 0              # where willy is at in his walking animation
        self.willyJump = 0              # where willy is at in his jump
        self.willyJumpFactor = 1.2
        self.testMode = False
        self.test = Test()
        self.falling = False
        self.fallDistance = 0

        # moving left animation sprites
        self.willyImgLeft = [
            pygame.image.load('willy_left_1.png'),
            pygame.image.load('willy_left_2.png'),
            pygame.image.load('willy_left_1.png'),    
            pygame.image.load('willy_left_3.png')
        ]

        # moving right animation sprites
        self.willyImgRight = [
            pygame.image.load('willy_right_1.png'),
            pygame.image.load('willy_right_2.png'),
            pygame.image.load('willy_right_1.png'),    
            pygame.image.load('willy_right_3.png')
        ]

        # scale the sprites up to larger
        numImages = len(self.willyImgRight)
        for count in range(0, numImages):
            (willyImgWidth,willyImgHeight) = self.willyImgRight[count].get_rect().size
            # print("dimensions: ", willyImgWidth, willyImgHeight)
            newHeight = int(willyImgHeight * scale)
            newWidth = int(willyImgWidth * scale)
            picture = pygame.transform.scale(self.willyImgRight[count], (newWidth, newHeight))
            self.willyImgRight[count] = picture
            (willyImgWidth,willyImgHeight) = self.willyImgLeft[count].get_rect().size
            # print("dimensions: ", willyImgWidth, willyImgHeight)
            newHeight = int(willyImgHeight * scale)
            newWidth = int(willyImgWidth * scale)
            picture = pygame.transform.scale(self.willyImgLeft[count], (newWidth, newHeight))
            self.willyImgLeft[count] = picture
            self.width = newWidth
            self.height = newHeight
            print("Willy Width: ", self.width)
            print("Willy Height: ", self.height)


    def getJumpHeight(self, jumpPosition, jumpDistance, jumpHeight):
        jumpPosition //= 2
        # print("  jumpPosition: ", jumpPosition)
        heights = [8, 8, 6, 6, 4, 4, 2, 2, 0, 0, 2, 2, 4, 4, 6, 6, 8, 8]
        heightToAdd = heights[jumpPosition]
        # print("  heightToAdd:  ", heightToAdd)
        return heightToAdd * self.willyJumpFactor

    def jump(self, screen, sound):
        if self.willyJump > (self.willyJumpDistance / 2): # rising
            if self.ypos > screen.yboundary_top: # don't go off the top of the screen
                jumpPos = (self.willyJumpDistance - self.willyJump)
                toJump = self.getJumpHeight(jumpPos, self.willyJumpDistance, self.willyJumpHeight)
                self.ypos -= toJump
            if self.direction == "right" and self.walking:
                if (self.xpos < screen.xboundary_right): # don't go off the screen to the right
                    self.xpos += self.xdistance
                    self.willyWalk += 1
            elif self.direction == "left" and self.walking:
                if (self.xpos > screen.xboundary_left): # don't go off the screen to the right
                    self.xpos -= self.xdistance
                    self.willyWalk += 1
        else: # falling
            if (self.ypos < screen.yboundary_bottom): # don't go off the bottom of the screen
                jumpPos = (self.willyJumpDistance - self.willyJump)
                toJump = self.getJumpHeight(jumpPos, self.willyJumpDistance, self.willyJumpHeight)
                self.ypos += toJump
            if self.direction == "right" and self.walking:
                if (self.xpos < screen.xboundary_right): # don't go off the screen to the right
                    self.xpos += self.xdistance
                    self.willyWalk += 1
            elif self.direction == "left" and self.walking:
                if (self.xpos > screen.xboundary_left): # don't go off the screen to the right
                    self.xpos -= self.xdistance
                    self.willyWalk += 1
        if self.willyWalk == len(self.willyImgRight):
            self.willyWalk = 0
        self.willyJump -= 1
        if self.willyJump == 1:
            self.stopJumping(sound)
        return self.willyJump

    def stopJumping(self, sound):
        self.walking = False
        self.willyJump = 0
        if not self.falling:
            sound.stopJumpFallSound()

    def stopFalling(self, sound):
        sound.stopFallSound()

    def move(self, events, screen, sound):
        if events.keysPressed["dev1"]:
            self.xpos = self.willystartx
            self.ypos = self.willystarty
        
        if events.keysPressed["dev2"]:
            self.xpos += 200
            self.ypos = self.willystarty
        
        if events.keysPressed["dev3"]:
            print("Willy location: (", self.xpos, ",", self.ypos, ")")
        
        # are we already jumping?
        if self.willyJump > 0:
            # already jumping
            self.jump(screen, sound)
            self.willyJump -= 1
            self.animateWalk()
            # don't handle any more keys
            return

        # are we falling?
        if self.falling == True:
            # pdb.set_trace()
            if (self.fallDistance == 0):
                sound.stopJumpFallSound()
                sound.playFallSound()
            self.fallDistance += 1
            print("falling: ", self.fallDistance)
            self.ypos += 8
            self.animateWalk()
            # don't handle any more keyboard entries
            return

        # play the next test move
        if events.keysPressed["test"]:
            self.testMode = True

        if self.testMode:
            moves = self.test.getNextMove()
            for move in moves:
                # print(move, ", ", end='', flush=True)
                if move != "none":
                    events.keysPressed[move] = True

        # move in response to direction
        if events.keysPressed["left"]:
            if events.keysPressed["jump"]:
                # print("*** jump left")
                sound.playJumpFallSound()
                self.willyJump = self.willyJumpDistance;
                self.direction = "left"
                self.walking = True
            else:
                # print("*** walk left")
                self.direction = "left"
                if self.xpos > screen.xboundary_left:
                    self.xpos -= self.xdistance
                    self.willyWalk += 1            
                    if self.willyWalk == len(self.willyImgLeft):
                        self.willyWalk = 0
        elif events.keysPressed["right"]:
            # print("*** handling right key")
            if events.keysPressed["jump"]:
                # print("*** jump right")
                sound.playJumpFallSound()
                self.willyJump = self.willyJumpDistance;
                self.direction = "right"
                self.walking = True
            else:
                # print("*** walk right")
                self.direction = "right"
                if self.xpos < screen.xboundary_right:
                    # print("walking right")
                    self.xpos += self.xdistance
                    self.willyWalk += 1
                    if self.willyWalk == len(self.willyImgRight):
                        self.willyWalk = 0
        elif events.keysPressed["jump"]:
            # print("*** jump in place")
            sound.playJumpFallSound()
            self.willyJump = self.willyJumpDistance;
            self.walking = False
        else:
            self.walking = False
        self.animateWalk()
        # if self.direction == "left":
        #     self.image = self.willyImgLeft[self.willyWalk]
        # else:
        #     self.image = self.willyImgRight[self.willyWalk]
        # return

    def animateWalk(self):
        if self.direction == "left":
            self.image = self.willyImgLeft[self.willyWalk]
        else:
            self.image = self.willyImgRight[self.willyWalk]

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos, self.ypos))

    def restart(self):
        self.willyJump = 0
        self.xpos = self.willystartx
        self.ypos = self.willystarty

def loseLifeAndRestart(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal):
    sound.pauseMainMusic()
    sound.playDeathSound()
    for guardian in guardians:
        guardian.restart()
    for floor in floors:
        floor.restart()
    for key in keys:
        key.restart()
    for portal_piece in portal:
        portal_piece.restart()
    willy.restart()
    sound.stopJumpFallSound()
    player.lives -= 1
    # flash screen
    # play death sound
    sound.playMainMusic()
    screen.flashBackground()

def win():
    print("You have won!")
    sys.exit(0)

def update(clock, player, events, keys, guardians, willy, screen, sound, floors, obstacles, portal):
    if events.keysPressed["music"]:
        print("toggle music")
        sound.toggleMainMusic()
    screen.displayBackground()
    for floor in floors:
        floor.display(screen)
    screen.displayBlocks()
    for obstacle in obstacles:
        obstacle.display(screen)
    screen.displayConveyors()
    for guardian in guardians:
        guardian.move(screen)
        guardian.display(screen)
    for key in keys:
        key.move(screen)
        key.display(screen)
    collisions = screen.checkCollisions(willy, keys + guardians + floors + obstacles + portal)
    freezeWilly = False
    reallyLanded = False # for now - to be determined below
    for collision in collisions:
        # print("Collision with ", collision.collidingObject.type)
        if collision.collidingObject.type == "Guardian" or collision.collidingObject.type == "Plant":
            loseLifeAndRestart(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal)
        elif collision.collidingObject.type == "Key":
            print("collided with ", collision.collidingObject.name)
            collision.collidingObject.disappear()
            player.score += key.scorevalue
        elif isinstance(collision.collidingObject, StandableObject) \
             and collision.event == "landed" \
             and willy.willyJump <= willy.willyJumpDistance / 2:
            floor = collision.collidingObject
            if isinstance(floor, CrumblingFloor):
                print("touching crumble")
                floor.crumble()
                if floor.standable == True:
                    print("floor is standable")
                    reallyLanded = True
                else:
                    print("floor is not standable")
                    reallyLanded = False
            else:
                # print("landed on floor")
                reallyLanded = True
        elif isinstance(collision.collidingObject, Portal):
            portal_piece = collision.collidingObject
            if portal_piece.open:
                win()
    if reallyLanded == True:
        willy.falling = False
        willy.stopJumping(sound)
        willy.stopFalling(sound)
        willy.falling = False
        if willy.fallDistance > 10:
            loseLifeAndRestart(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal)
        # either way, reset the fall distance
        willy.fallDistance = 0
    else:
       willy.falling = True
    willy.move(events, screen, sound)
    willy.display(screen)
    allKeysFound = True
    for key in keys:
        if key.appears:
            allKeysFound = False
    for portal_part in portal:
        if allKeysFound:
            portal_part.open = True
        portal_part.move(screen)
        portal_part.display(screen)
    pygame.display.update()

B = 0x02 # brick
C = 0x03 # crumbling floor
F = 0x06 # floor
I = 0x09 # ice
K = 0x0A # key
P = 0x10 # plant
T = 0x14 # TrumpetNose start location
U = 0x15 # TrumpetNose end location
V = 0x16 # conveyor
W = 0x17 # willy start location
Z = 0x18 # portal

centralCavern = [
    [B,0,0,0,0,0,0,0,0,0,K,0,I,0,0,0,0,I,0,0,0,0,0,0,0,0,0,0,0,K,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,K,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,P,K,0,0,P,0,0,B],
    [B,F,F,F,F,F,F,F,F,F,F,F,F,F,C,C,C,C,F,C,C,C,C,F,F,F,F,F,F,F,F,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,K,B],
    [B,F,F,F,0,0,0,0,T,0,0,0,0,0,0,0,U,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,B,B,0,P,0,0,0,0,0,0,0,0,0,B],
    [B,F,F,F,F,0,0,0,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,F,F,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,P,0,0,0,0,0,0,0,B,B,B,C,C,C,C,C,F,F,F,B],
    [B,0,W,0,0,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,0,Z,Z,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,B],
    [B,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,B],
    ]

testCavern1 = [
    [B,0,0,0,0,0,0,0,0,0,0,0,I,0,0,0,0,I,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,P,0,0,0,P,0,0,B],
    [B,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,F,F,F,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,B,B,0,P,0,0,0,0,0,0,0,0,0,B],
    [B,F,F,F,F,0,0,0,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,V,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,F,F,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,W,0,0,K,0,0,0,0,0,0,P,0,0,0,0,0,0,0,B,B,B,C,C,C,C,C,F,F,F,B],
    [B,0,0,0,0,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,0,Z,Z,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,B],
    [B,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,B],
    ]
testCavern2 = [
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,W,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,F,F,0,0,0,F,F,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,F,F,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,F,F,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,B,B,B,B,B,B,B,B,B,F,F,F,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
    ]

def main():
    events = Events()
    screen = Screen(640,320)
    player = Player()
    sound = Sound()
    guardians = []
    keys = []
    floors = []
    obstacles = []
    portal = [] # actually made of 4 portal objects
    # screen.load(centralCavern)
    scale = 0.7
    # cavern = testCavern1
    # cavern = testCavern2
    cavern = centralCavern
    for cellx in range(0,32):
        for celly in range(0,16):
            cellContents = cavern[celly][cellx]
            # print("handling map: ", cellx, celly, " = ", cellContents)
            (screenx,screeny) = screen.cellToCoords(cellx, celly)
            if cellContents == B:
                cellName = "brick" + "-" + str(cellx) + "-" + str(celly)
                floors.append(Brick(screenx, screeny, screen.scale * 0.7, cellName))
            elif cellContents == F:
                cellName = "floor" + "-" + str(cellx) + "-" + str(celly)
                floors.append(Floor(screenx, screeny, screen.scale * 0.7, cellName))
            elif cellContents == I:
                cellName = "ice" + "-" + str(cellx) + "-" + str(celly)
                obstacles.append(Ice(screenx, screeny, screen.scale, cellName))
            elif cellContents == P:
                cellName = "plant" + "-" + str(cellx) + "-" + str(celly)
                obstacles.append(Plant(screenx, screeny, screen.scale * 0.7, cellName))
            elif cellContents == V:
                cellName = "conveyor" + "-" + str(cellx) + "-" + str(celly)
                floors.append(Floor(screenx, screeny, screen.scale * 0.7, cellName))
            elif cellContents == C:
                cellName = "crumble" + "-" + str(cellx) + "-" + str(celly)
                floors.append(CrumblingFloor(screenx, screeny, screen.scale * 0.7, cellName))
            elif cellContents == W:
                cellName = "willy" + "-" + str(cellx) + "-" + str(celly)
                screeny -= 10
                willy = Willy(screenx, screeny, screen.scale)
            elif cellContents == T:
                cellName = "trumpetnose start" + "-" + str(cellx) + "-" + str(celly)
                guardians.append(TrumpetNose(screenx, screeny, screen.scale, cellName))
            elif cellContents == U:
                for guardian in guardians:
                    print("Looking for TN: ", guardian.subtype)
                    if guardian.subtype == "TrumpetNose":
                        cellName = "trumpetnose end" + "-" + str(cellx) + "-" + str(celly)
                        guardian.setEndPos(screenx, screeny)
            elif cellContents == K:
                cellName = "key" + "-" + str(cellx) + "-" + str(celly)
                keys.append(Key(screenx, screeny, screen.scale, cellName))
            elif cellContents == Z:
                cellName = "portal" + "-" + str(cellx) + "-" + str(celly)
                portal.append(Portal(screenx, screeny, screen.scale * 0.7, cellName))

    clock = pygame.time.Clock()
    sound.startMainMusic()

    print("Manic Miner is running")
    running = True

    # show title screen and play title music
    # sound.playTitleTune()

    while running and player.lives > 0:
        running = events.check()
        update(clock, player, events, keys, guardians, willy, screen, sound, floors, obstacles, portal)
        clock.tick(screen.FPS)
    if player.lives == 0:
        sound.stopAll()
        print("Game Over!")
        sound.playGameOver()
    else:
        print("Game quit - lives remaining: ", player.lives)
    print("Final score: ", player.score)
    pygame.quit()
    return

main()
