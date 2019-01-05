#!/usr/local/bin/python3

# rooms: http://jswremakes.emuunlim.com/Mmt/Manic%20Miner%20Room%20Format.htm
# -8 -8 -6 -6 -4 -4 -2 -2 0 0 2 2 4 4 6 6 8 8
# https://www.gamejournal.it/the-sound-of-1-bit-technical-constraint-as-a-driver-for-musical-creativity-on-the-48k-sinclair-zx-spectrum/z
# D=8*(1+ABS(J-8));

# TODO:
#  hitting bricks doesn't work correctly
#  landing on a conveyor while walking in the opposite direction to the conveyor direction allows him to walk that way
#  dying should lower the music key
#  jump sounds slightly too loud
#  fix up the graphics so they don't need scaling
#  air supply and lives and score display need displaying
#  level transitions
#  "game over" graphic
#  further levels
#  cheat mode
#  consider pyglet for faster performance

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
            "restart": False,
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
                if e.key == pygame.K_r:
                    self.keysPressed["restart"] = True
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
                if e.key == pygame.K_r:
                    self.keysPressed["restart"] = False
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
    RGB = {
        "black":   (0, 0, 0),
        "white":   (255, 255, 255),
        "yellow":  (189,189,0),
        "magenta": (189,0,189),
        "cyan":    (0,189,189),
        "green":   (0,189,0),
        "red":     (189,0,0),
        "blue":    (0,0,189)
    }

    def __init__(self, x, y, backgroundColor="black"):
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
        # define some boundary values
        self.xboundary_left = 5
        self.xboundary_right = self.max_x - 50 # willyImgWidth*2
        self.yboundary_top = 5
        self.yboundary_bottom = self.max_y - 50 # willyImgHeight*2
        self.collisionCount = 0
        self.cellWidth = self.max_x / 32
        self.cellHeight = self.max_y / 16
        self.alpha = 255
        self.backgroundColor = backgroundColor

    def cellToCoords(self, x, y):
        coord_x = x * self.cellWidth
        coord_y = y * self.cellHeight
        return (coord_x,coord_y)
    
    def setBackgroundColor(self, color):
        self.DISPLAYSURF.fill(self.RGB[color])

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

        collisionWatchList = ["brick-0-15"]
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
                if willy_left <= object_right and willy_left >= object_left - 5:
                    horizontal = True
                if willy_bottom >= object_top and willy_bottom <= object_bottom:
                    # give a little more tolerance on guardians
                    if isinstance(object, Guardian):
                        if willy_bottom >= object_top + 5:
                            vertical = True
                    else:
                        vertical = True
                if willy_top <= object_bottom and willy_top >= object_top:
                    # give a little more tolerance on guardians
                    if isinstance(object, Guardian):
                        if willy_bottom >= object_bottom - 5:
                            vertical = True
                    else:
                        vertical = True
                if horizontal == True and vertical == True:
                    collision = True
                if collision == True:
                    self.collisionCount += 1
                    if isinstance(object, SolidStandableObject):
                        if willy_left <= object_right and willy_right >= object_right and willy_bottom >= object_top + 10:
                            collisions.append(Collision(object, "blockedleft"))
                            continue
                    if isinstance(object, SolidStandableObject):
                        if willy_right >= object_left and willy_left <= object_left and willy_bottom >= object_top + 10:
                            collisions.append(Collision(object, "blockedright"))
                            continue
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

    @staticmethod
    def colorImage(image, color):
        if color == "none":
            return image
        print("setting to " + color)
        imageCopy = image.copy()
        clear = (255, 255, 255, 0)
        rgb = Screen.RGB[color] + (0,)
        imageCopy.fill(clear, None, pygame.BLEND_RGBA_SUB)
        imageCopy.fill(rgb, None, pygame.BLEND_RGBA_ADD)
        return imageCopy

class Object:
    def __init__(self, start_x, start_y, name="NoName", color="none"):
        # print("Creating Object: ", name)
        self.xpos = start_x
        self.ypos = start_y
        self.startxpos = start_x
        self.startypos = start_y
        self.type = "Object"
        self.name = name
        self.collidable = False
        self.image = pygame.image.load('empty.png')
        self.color = color

    def move(self, screen):
        pass

    def restart(self):
        self.xpos = self.startxpos
        self.ypos = self.startypos

    def setColor(self, color):
        print("setColor ", self.name, color)
        self.image = Screen.colorImage(self.image, color)
        return

    def display(self, screen):
        pass
    
class MovingObject(Object):
    def __init__(self, start_x, start_y, name="MovingObject"):
        # print("Creating MovingObject: ", name)
        Object.__init__(self, start_x, start_y, name)
        self.type = "MovingObject"

    def restart(self):
        Object.restart(self)
        self.direction = "right"

class StationaryObject(Object):
    def __init__(self, x, y, name="StationaryObject", color="none"):
        # print("Creating StationaryObject: ", name)
        Object.__init__(self, x, y, name, color)
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
    def __init__(self, x, y, name="StandableObject", color="none"):
        StationaryObject.__init__(self, x, y, name, color)
        self.standable = True

class Floor(StandableObject):
    def __init__(self, x, y, scale, name="Floor", color="none"):
        print("Creating Floor: ", name)
        StandableObject.__init__(self, x, y, name, color)
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
            picture = Screen.colorImage(picture, color)
            self.floorImg[count] = picture
            (floorImgWidth,floorImgHeight) = self.floorImg[count].get_rect().size
            newHeight = int(floorImgHeight * scale)
            newWidth = int(floorImgWidth * scale)
            picture = pygame.transform.scale(self.floorImg[count], (newWidth,newHeight))
            picture = Screen.colorImage(picture, color)
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

class Conveyor(StandableObject):
    def __init__(self, x, y, scale, name="Conveyor", color="none"):
        StandableObject.__init__(self, x, y, name, color)
        print("x: ", x, ", y: ", y, ", scale: ", scale, ", name: ", name)
        self.conveyorDirection = "none"
        self.conveyorPosition = 0
        # sprite
        self.conveyorImg = [
            pygame.image.load('conveyor_1.png'),
            pygame.image.load('conveyor_2.png'),
            pygame.image.load('conveyor_3.png'),
            pygame.image.load('conveyor_4.png'),
            pygame.image.load('conveyor_5.png'),
            pygame.image.load('conveyor_6.png'),
            pygame.image.load('conveyor_7.png'),
            pygame.image.load('conveyor_8.png'),
        ]
        # scale the sprites up to larger
        numImages = len(self.conveyorImg)
        for count in range(0, numImages):
            (conveyorImgWidth, conveyorImgHeight) = self.conveyorImg[count].get_rect().size
            newHeight = int(conveyorImgHeight * scale)
            newWidth = int(conveyorImgWidth * scale)
            picture = pygame.transform.scale(self.conveyorImg[count], (newWidth, newHeight))
            picture = Screen.colorImage(picture, color)
            self.conveyorImg[count] = picture
            self.width = newWidth
            self.height = newHeight
            # print("Conveyor Width: ", self.width)
            # print("Conveyor Height: ", self.height)
        self.image = self.conveyorImg[0]

    def restart(self):
        pass

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))
        
class LeftConveyor(Conveyor):
    def __init__(self, x, y, scale, name="Conveyor", color="none"):
        print("Creating LeftConveyor: ", name)
        Conveyor.__init__(self, x, y, scale, name, color)
        self.type = "LeftConveyor"
        self.conveyorDirection = "left"

    def move(self, screen):
        self.conveyorPosition += 1
        if self.conveyorPosition == len(self.conveyorImg):
            self.conveyorPosition = 0
        self.image = self.conveyorImg[self.conveyorPosition]

class RightConveyor(Conveyor):
    def __init__(self, x, y, scale, name="Conveyor", color="none"):
        print("Creating RightConveyor: ", name)
        Conveyor.__init__(self, x, y, scale, name, color)
        self.type = "LeftConveyor"
        self.conveyorDirection = "right"

    def move(self, screen):
        self.conveyorPosition -= 1
        if self.conveyorPosition < 0:
            self.conveyorPosition = len(self.conveyorImg)
        self.image = self.conveyorImg[self.conveyorPosition]

class CrumblingFloor(StandableObject):
    def __init__(self, x, y, scale, name="CrumblingFloor", color="none"):
        print("Creating CrumblingFloor: ", name)
        StandableObject.__init__(self, x, y, name, color)
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
            picture = Screen.colorImage(picture, color)
            self.floorImg[count] = picture
            (floorImgWidth,floorImgHeight) = self.floorImg[count].get_rect().size
            newHeight = int(floorImgHeight * scale)
            newWidth = int(floorImgWidth * scale)
            picture = pygame.transform.scale(self.floorImg[count], (newWidth,newHeight))
            picture = Screen.colorImage(picture, color)
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

class SolidStandableObject(StandableObject):
    def __init__(self, x, y, scale, name="SolidStandable", color="none"):
        StandableObject.__init__(self, x, y, name, color)
        
class Brick(SolidStandableObject):
    def __init__(self, x, y, scale, name="Brick", color="none"):
        print("Creating Brick: ", name)
        SolidStandableObject.__init__(self, x, y, scale, name, color)
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
            picture = Screen.colorImage(picture, color)
            self.brickImg[count] = picture
            (brickImgWidth,brickImgHeight) = self.brickImg[count].get_rect().size
            newHeight = int(brickImgHeight * scale)
            newWidth = int(brickImgWidth * scale)
            picture = pygame.transform.scale(self.brickImg[count], (newWidth,newHeight))
            picture = Screen.colorImage(picture, color)
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
        self.conveyorDirection = "none"
        self.blocked = {
            "left": False,
            "right": False,
            "above": False,
        }

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
            if self.direction == "right" and self.walking and self.walking and self.blocked["right"] == False:
                if (self.xpos < screen.xboundary_right): # don't go off the screen to the right
                    self.xpos += self.xdistance
                    self.willyWalk += 1
            elif self.direction == "left" and self.walking and self.blocked["left"] == False:
                if (self.xpos > screen.xboundary_left): # don't go off the screen to the right
                    self.xpos -= self.xdistance
                    self.willyWalk += 1
        else: # falling
            if (self.ypos < screen.yboundary_bottom): # don't go off the bottom of the screen
                jumpPos = (self.willyJumpDistance - self.willyJump)
                toJump = self.getJumpHeight(jumpPos, self.willyJumpDistance, self.willyJumpHeight)
                self.ypos += toJump
            if self.direction == "right" and self.walking and self.walking and self.blocked["right"] == False:
                if (self.xpos < screen.xboundary_right): # don't go off the screen to the right
                    self.xpos += self.xdistance
                    self.willyWalk += 1
            elif self.direction == "left" and self.walking and self.blocked["left"] == False:
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

    def walk(self, walkDirection, screen, distance=-1):
        if distance == -1:
            distance = self.xdistance
        if walkDirection == "left" and self.blocked["left"] == False:
            # print("*** walk left")
            self.direction = "left"
            if self.xpos > screen.xboundary_left:
                self.xpos -= distance
                self.willyWalk += 1            
                if self.willyWalk == len(self.willyImgLeft):
                    self.willyWalk = 0
        elif walkDirection == "right" and self.blocked["right"] == False:
            self.direction = "right"
            if self.xpos < screen.xboundary_right:
                # print("walking right")
                self.xpos += distance
                self.willyWalk += 1
                if self.willyWalk == len(self.willyImgRight):
                    self.willyWalk = 0
        self.blocked["left"] = False
        self.blocked["right"] = False
        self.blocked["above"] = False

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
        if (events.keysPressed["left"] and self.conveyorDirection == "none") \
           or (events.keysPressed["jump"] and self.conveyorDirection == "left"):
            if events.keysPressed["jump"]:
                # print("*** jump left")
                sound.playJumpFallSound()
                self.willyJump = self.willyJumpDistance;
                self.direction = "left"
                self.walking = True
            elif self.conveyorDirection == "none":
                # print("*** walk left")
                self.walk("left", screen)
        elif (events.keysPressed["right"] and self.conveyorDirection == "none") \
             or (events.keysPressed["jump"] and self.conveyorDirection == "right"):
            # print("*** handling right key")
            if events.keysPressed["jump"]:
                # print("*** jump right")
                sound.playJumpFallSound()
                self.willyJump = self.willyJumpDistance;
                self.direction = "right"
                self.walking = True
            elif self.conveyorDirection == "none":
                # print("*** walk right")
                self.walk("right", screen)
        elif events.keysPressed["jump"]:
            # print("*** jump in place")
            sound.playJumpFallSound()
            self.willyJump = self.willyJumpDistance;
            self.walking = False
        else:
            self.walking = False
        self.animateWalk()

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

def restartLevel(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal):
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
    # flash screen
    # play death sound
    sound.playMainMusic()
    screen.setBackgroundColor(screen.backgroundColor)
        
def loseLifeAndRestart(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal):
    player.lives -= 1
    restartLevel(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal)

def win():
    print("You have won!")
    sys.exit(0)

def update(clock, player, events, keys, guardians, willy, screen, sound, floors, obstacles, portal):
    if events.keysPressed["music"]:
        print("toggle music")
        sound.toggleMainMusic()
    if events.keysPressed["restart"]:
        print("restart")
        restartLevel(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal)
    screen.setBackgroundColor(screen.backgroundColor)
    for floor in floors:
        floor.move(screen)
        floor.display(screen)
    for obstacle in obstacles:
        obstacle.display(screen)
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
        objectHit = collision.collidingObject
        # print("Collision with ", objectHit.type)
        if objectHit.type == "Guardian" or objectHit.type == "Plant":
            loseLifeAndRestart(clock, screen, events, player, keys, floors, obstacles, guardians, willy, sound, portal)
        elif objectHit.type == "Key":
            print("collided with ", objectHit.name)
            objectHit.disappear()
            player.score += key.scorevalue
        # object can be stood on,
        # and Willy landed on top of that object,
        # and Willy is on the descent part of a jump or falling
        elif isinstance(objectHit, StandableObject) \
             and collision.event == "landed" \
             and willy.willyJump <= willy.willyJumpDistance / 2:
            floor = objectHit
            if isinstance(floor, CrumblingFloor): # it's a crumbling floor...
                print("touching crumble")
                floor.crumble()
                if floor.standable == True:
                    print("floor is standable")
                    reallyLanded = True           # ...and is still at least partially intact
                else:
                    print("floor is not standable")
                    reallyLanded = False          # ...but has fully crumbled so can no longer be landed on
                willy.conveyorDirection = "none"
            elif isinstance(objectHit, Conveyor):
                print("conveyor")
                willy.walkDirection = "left"
                willy.conveyorDirection = objectHit.conveyorDirection
                willy.walk(objectHit.conveyorDirection, screen, willy.xdistance / 2)
                reallyLanded = True
            else:
                # print("landed on floor")
                reallyLanded = True               # generic, non-crumbling floor - we can land on this
                willy.conveyorDirection = "none"
        elif isinstance(objectHit, Portal): # handle walking into the portal
            portal_piece = objectHit
            if portal_piece.open:
                win()
        elif isinstance(objectHit, SolidStandableObject) and collision.event[0:7] == "blocked":
            bumpDirection = collision.event[7:]
            print("bump on", bumpDirection)
            willy.blocked[bumpDirection] = True
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
V = 0x16 # left conveyor
W = 0x17 # willy start location
X = 0x18 # right conveyor
Z = 0x1A # portal

caverns = {
    "centralCavern": [
        [
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
        ],
        "black", # background
        "red",   # floors
        "green", # conveyors
    ],
    "coldRoom": [
        [
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,B,B,B,B,B,B,B,B,B,B,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,K,0,0,0,I,B],
            [B,0,0,0,0,0,K,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,T,0,0,0,0,0,U,0,0,0,0,0,0,0,0,0,0,C,C,C,F,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,B,C,C,B,0,0,B],
            [B,F,C,C,C,C,C,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,K,0,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,0,K,0,0,0,0,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,C,C,C,C,0,0,0,B,C,C,B,0,0,B],
            [B,0,V,V,V,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,0,0,K,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,W,0,0,0,0,C,C,C,C,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,U,Z,Z,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,B],
            [B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B],
        ],
        "blue",    # background
        "magenta", # floors
        "yellow",  # conveyors
    ],
    "testCavern1": [
        [
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
        ],
        "black", # background
        "red",   # floors
        "green", # conveyors
    ],
    "testCavern2": [
        [
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
        ],
        "black", # background
        "red",   # floors
        "green", # conveyors
    ],
    "emptyCavern": [
        [
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,W,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B],
        ],
        "black", # background
        "red",   # floors
        "green", # conveyors
    ],
    "brickTests": [
        [
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,W,0,0,0,0,B,B,B,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,B,B,B,B,B,0,0,0,0,0,0,0,B],
            [B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B],
        ],
        "black", # background
        "red",   # floors
        "green", # conveyors
    ],
}

def main():
    # load the specified cavern or the default, falling back to default if specified but not found
    cavernFound = False
    defaultCavern = "centralCavern"
    if len(sys.argv) >= 2:
        if sys.argv[1] not in caverns.keys():
            print("Cavern", sys.argv[1], " is not known")
            cavernFound = False
        else:
            print("Loading", sys.argv[1])
            cavern = caverns[sys.argv[1]]
            cavernFound = True
    if cavernFound == False:
        # default to the classic central cavern
        cavern = caverns[defaultCavern]

    # cavern data
    cavernMap = cavern[0]
    backgrounColor = cavern[1]
    floorColor = cavern[2]
    conveyorColor = cavern[3]
    
    events = Events()
    screen = Screen(640,320, cavern[1])
    player = Player()
    sound = Sound()
    guardians = []
    keys = []
    floors = []
    obstacles = []
    portal = [] # actually made of 4 portal objects
    # screen.load(centralCavern)
    scale = 0.7
    
    for cellx in range(0,32):
        for celly in range(0,16):
            cellContents = cavernMap[celly][cellx]
            # print("handling map: ", cellx, celly, " = ", cellContents)
            (screenx,screeny) = screen.cellToCoords(cellx, celly)
            if cellContents == B:
                cellName = "brick" + "-" + str(cellx) + "-" + str(celly)
                newbrick = Brick(screenx, screeny, screen.scale * 0.7, cellName)
                newbrick.setColor(floorColor)
                floors.append(newbrick)
            elif cellContents == F:
                cellName = "floor" + "-" + str(cellx) + "-" + str(celly)
                newfloor = Floor(screenx, screeny, screen.scale * 0.7, cellName, floorColor)
                newfloor.setColor(floorColor)
                floors.append(newfloor)
            elif cellContents == I:
                cellName = "ice" + "-" + str(cellx) + "-" + str(celly)
                obstacles.append(Ice(screenx, screeny, screen.scale, cellName))
            elif cellContents == P:
                cellName = "plant" + "-" + str(cellx) + "-" + str(celly)
                obstacles.append(Plant(screenx, screeny, screen.scale * 0.7, cellName))
            elif cellContents == V:
                cellName = "leftconveyor" + "-" + str(cellx) + "-" + str(celly)
                newconveyor = LeftConveyor(screenx, screeny, screen.scale, cellName, conveyorColor)
                newconveyor.setColor(conveyorColor)
                floors.append(newconveyor)
            elif cellContents == X:
                cellName = "rightconveyor" + "-" + str(cellx) + "-" + str(celly)
                newconveyor = RightConveyor(screenx, screeny, screen.scale, cellName, conveyorColor)
                newconveyor.setColor(conveyorColor)
                floors.append(newconveyor)
            elif cellContents == C:
                cellName = "crumble" + "-" + str(cellx) + "-" + str(celly)
                newcrumble = CrumblingFloor(screenx, screeny, screen.scale * 0.7, cellName, floorColor)
                newcrumble.setColor(floorColor)
                floors.append(newcrumble)
            elif cellContents == W:
                cellName = "willy" + "-" + str(cellx) + "-" + str(celly)
                screeny -= 10
                willy = Willy(screenx, screeny, screen.scale)
            elif cellContents == T:
                cellName = "trumpetnose start" + "-" + str(cellx) + "-" + str(celly)
                newTrumpetNose = TrumpetNose(screenx, screeny, screen.scale, cellName)
                guardians.append(newTrumpetNose)
            elif cellContents == U:
                lastTrumpetNose = None
                for guardian in guardians:
                    print("Looking for TN: ", guardian.subtype)
                    if guardian.subtype == "TrumpetNose":
                        lastTrumpetNose = guardian
                if lastTrumpetNose != None:
                    cellName = "trumpetnose end" + "-" + str(cellx) + "-" + str(celly)
                    lastTrumpetNose.setEndPos(screenx, screeny)
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
