#!/usr/local/bin/python3

'''
  manic.py - A retro platform game engine
  Copyright (C) 2018 Miner48k

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

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
#  enlarging window makes performance poor
#   - consider only updating the cells with moving pieces
#     e.g. blanking the sprite square then drawing the spite
#     and not redrawing unchanged components anyway
#   - consider pyglet for faster performance

import os, sys, math, re, logging, pdb, time, textwrap, re
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
        self.textMove = "None"
        rows, columns = os.popen('stty size', 'r').read().split()
        self.terminalWidth = int(columns)
        self.infocomMode = False
        self.infocomRepeatCount = 0

    def check(self, willy):
        self.eventCount += 1

        if self.infocomMode == True:
            self.keysPressed["left"] = False
            self.keysPressed["right"] = False
            self.keysPressed["jump"] = False
            self.keysPressed["restart"] = False
            print("repeat count:", self.infocomRepeatCount, "event count:", self.eventCount)
            if self.eventCount % 18 == 0:
                if self.infocomRepeatCount > 0:
                    self.infocomRepeatCount -= 1
                else:
                    roomDesc = "You are standing in a large mine with a variety of platforms and shafts around you."
                    textwrap.wrap(roomDesc, self.terminalWidth)
                    print(roomDesc)
                    print()
                    self.textMove = input("> ")
                    match = re.search(r'\d', self.textMove)
                    if match:
                        self.infocomRepeatCount = int(match.group(0)) - 1
            elif willy.isJumping() == False:
                for word in ["right", "east", "e", "r"]:
                    if word in self.textMove:
                        self.keysPressed["right"] = True
                        self.keysPressed["left"] = False
                for word in ["left", "west", "w", "l"]:
                    if word in self.textMove:
                        self.keysPressed["right"] = False
                        self.keysPressed["left"] = True
                for word in ["up", "jump", "u"]:
                    if word in self.textMove:
                        self.keysPressed["jump"] = True
                        self.infocomRepeatCount *= 4
                for word in ["restart", "die"]:
                    if word in self.textMove:
                        self.keysPressed["restart"] = True
            
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

    def __init__(self, game_x, game_y, backgroundColor="black"):
        pygame.init()
        self.FPS = 15 # frames per second setting
        self.fpsClock = pygame.time.Clock()
        # set up the window
        self.max_x = game_x
        self.max_y = game_y
        self.scale = 2.4           # how much to scale the loaded sprites
        # DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), 0, 32)
        # DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), pygame.FULLSCREEN)
        self.DISPLAYSURF = pygame.display.set_mode((game_x, game_y), pygame.RESIZABLE)
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

    def getScale(self, width):
        return self.cellWidth / width
    
    def setBackgroundColor(self, color):
        # print("setting background color to ", color, self.RGB[color])
        self.DISPLAYSURF.fill(self.RGB[color])
        self.backgroundColor = color

    def flash(self):
        print("flashing")
        bgColor = self.backgroundColor
        self.setBackgroundColor("white")
        pygame.display.update()
        self.backgroundColor = bgColor

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
        print("willy x,y: (", willy.xpos, ",", willy.ypos, ")")
        # print("willy bounds: (", willy_left, ",", willy_top, ") to (", willy_right, ",", willy_bottom, ")")

        collisionWatchList = [""]
        collisions = []

        for object in objects:
            if object.collidable == True:
                # print("getting next object: ", object.name)
                object_left = object.xpos
                object_right = object.xpos + object.width
                object_top = object.ypos
                object_bottom = object.ypos + object.height
                horizontal = False
                vertical = False
                collision = False
                # print("willy: (", willy.xpos, ",", willy.ypos, ")")
                # print("object: ", object.name, ": (", object.xpos, ",", object.ypos, ")")
                # print("willy  (L,R,T,B): ", willy_left, willy_right, willy_top, willy_bottom)
                # print("object (L,R,T,B): ", object_left, object_right, object_top, object_bottom)
                if willy_right - 1 >= object_left and willy_right <= object_right:
                    horizontal = True
                    # print("horizontal: true")
                if willy_left <= object_right and willy_left >= object_left - 5:
                    horizontal = True
                    # print("horizontal: true")
                if willy_bottom >= object_top and willy_bottom <= object_bottom:
                    # give a little more tolerance on guardians
                    if isinstance(object, Guardian):
                        if willy_bottom >= object_top + 5:
                            vertical = True
                            # print("vertical: true")
                    else:
                        vertical = True
                        # print("vertical: true")
                if willy_top <= object_bottom and willy_top >= object_top:
                    # give a little more tolerance on guardians
                    if isinstance(object, Guardian):
                        if willy_bottom >= object_bottom - 5:
                            vertical = True
                            # print("vertical: true")
                    else:
                        vertical = True
                        # print("vertical: true")
                # if horizontal:
                #     print("horizontal collision with", object.name)
                # if vertical:
                #     print("vertical collision with", object.name)
                if horizontal == True and vertical == True:
                    collision = True
                    # print("collision: true")
                if collision == True:
                    # print("collision with object")
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
                        if object.name in collisionWatchList or collisionWatchList[0] == "*":
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
        # print("setting to " + color)
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
        self.images = [  
            pygame.image.load('empty.png'),
        ]
        self.image = self.images[0]
        self.color = color
        self.setColor(color)
        self.width = 0
        self.height = 0

    def move(self, screen):
        pass

    def restart(self):
        self.xpos = self.startxpos
        self.ypos = self.startypos

    def setColor(self, color):
        # print("setColor(", color, ") called on", self.name)
        for n in range(0,len(self.images)):
            self.images[n] = Screen.colorImage(self.images[n], color)

    def scaleUp(self, scaleFactor):
        # scale our graphics up to larger
        numImages = len(self.images)
        for count in range(0, numImages):
            (portalImgWidth, portalImgHeight) = self.images[count].get_rect().size
            newHeight = int(portalImgHeight * scaleFactor)
            newWidth = int(portalImgWidth * scaleFactor)
            picture = pygame.transform.scale(self.images[count], (newWidth, newHeight))
            self.images[count] = picture
            self.width = newWidth
            self.height = newHeight

    def getWidth(self):
        (width, height) = self.images[0].get_rect().size
        return width

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.images[0], (self.xpos,self.ypos))
    
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
        
        self.images = [
            pygame.image.load('portal_start.png'),
            pygame.image.load('portal_end.png'),
        ]
        self.scaleUp(scale)
        self.displayCount = 0
        self.imageNum = 0
        self.image = self.images[self.imageNum]
        self.open = False
        self.collidable = True

    def move(self, screen):
        if self.open:
            self.displayCount += 1
            if self.displayCount <= 5:
                self.imageNum = 0
            else:
                self.imageNum = 1
            self.image = self.images[self.imageNum]
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
        # print("Creating Floor: ", name)
        StandableObject.__init__(self, x, y, name, color)
        self.type = "Floor"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.images = [
            pygame.image.load('floor_1.png'), # red
        ]
        self.scaleUp(scale)
        self.image = self.images[0]

    def restart(self):
        pass

class Conveyor(StandableObject):
    def __init__(self, x, y, scale, name="Conveyor", color="none"):
        StandableObject.__init__(self, x, y, name, color)
        # print("x: ", x, ", y: ", y, ", scale: ", scale, ", name: ", name)
        self.conveyorDirection = "none"
        self.conveyorPosition = 0
        self.images = [
            pygame.image.load('conveyor_1.png'),
            pygame.image.load('conveyor_2.png'),
            pygame.image.load('conveyor_3.png'),
            pygame.image.load('conveyor_4.png'),
            pygame.image.load('conveyor_5.png'),
            pygame.image.load('conveyor_6.png'),
            pygame.image.load('conveyor_7.png'),
            pygame.image.load('conveyor_8.png'),
        ]
        self.scaleUp(scale)

    def restart(self):
        pass

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.images[0], (self.xpos,self.ypos))
        
class LeftConveyor(Conveyor):
    def __init__(self, x, y, scale, name="Conveyor", color="none"):
        # print("Creating LeftConveyor: ", name)
        Conveyor.__init__(self, x, y, scale, name, color)
        self.type = "LeftConveyor"
        self.conveyorDirection = "left"

    def move(self, screen):
        self.conveyorPosition += 1
        if self.conveyorPosition == len(self.images):
            self.conveyorPosition = 0
        self.image = self.images[self.conveyorPosition]

class RightConveyor(Conveyor):
    def __init__(self, x, y, scale, name="Conveyor", color="none"):
        # print("Creating RightConveyor: ", name)
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
        # print("Creating CrumblingFloor: ", name)
        StandableObject.__init__(self, x, y, name, color)
        self.type = "CrumblingFloor"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.images = [
            pygame.image.load('crumble_1.png'),
            pygame.image.load('crumble_2.png'),
            pygame.image.load('crumble_3.png'),
            pygame.image.load('crumble_4.png'),
            pygame.image.load('crumble_5.png'),
            pygame.image.load('crumble_6.png'),
            pygame.image.load('crumble_7.png'),
            pygame.image.load('crumble_8.png'),
        ]
        self.scaleUp(scale)
        self.crumbleLevel = 0
        self.image = self.images[self.crumbleLevel]

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
            image = self.images[self.crumbleLevel]
            screen.DISPLAYSURF.blit(image, (self.xpos,self.ypos))
        # otherwise just don't show anything

class Ice(StationaryObject):
    def __init__(self, x, y, scale, name="Ice"):
        # print("Creating Ice: ", name)
        StationaryObject.__init__(self, x, y, name)
        self.type = "Ice"
        # sprite
        self.images = [
            pygame.image.load('icicle.png'),
        ]
        self.scaleUp(scale)

class SolidStandableObject(StandableObject):
    def __init__(self, x, y, scale, name="SolidStandable", color="none"):
        StandableObject.__init__(self, x, y, name, color)
        
class Brick(SolidStandableObject):
    def __init__(self, x, y, scale, name="Brick", color="none"):
        # print("Creating Brick: ", name)
        SolidStandableObject.__init__(self, x, y, scale, name, color)
        self.type = "Floor"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.images = [
            pygame.image.load('brick_1.png'),
        ]
        self.scaleUp(scale)
        self.image = self.images[0]

class Plant(StationaryObject):
    def __init__(self, x, y, scale, name="Plant"):
        # print("Creating Plant: ", name)
        StationaryObject.__init__(self, x, y, name)
        self.type = "Plant"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.images = [
            pygame.image.load('plant_1.png'),
        ]
        self.scaleUp(scale)
        self.image = self.images[0]

class SpiderLine(StationaryObject):
    def __init__(self, x, y, scale, name="SpiderLine"):
        # print("Creating SpiderLine: ", name)
        StationaryObject.__init__(self, x, y, name)
        self.type = "SpiderLine"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.images = [
            pygame.image.load('spiderline.png'),
        ]
        self.scaleUp(scale)
        self.image = self.images[0]

class Spider(StationaryObject):
    def __init__(self, x, y, scale, name="Spider"):
        # print("Creating Spider: ", name)
        StationaryObject.__init__(self, x, y, name)
        self.type = "Spider"
        # print("x,y = ", self.xpos, ",", self.ypos)
        # sprite
        self.images = [
            pygame.image.load('spider.png'),
        ]
        self.scaleUp(scale)

class Key(StationaryObject):
    def __init__(self, start_x, start_y, scale, name="Key"):
        StationaryObject.__init__(self, start_x, start_y, name)
        # print("Creating Key: ", name)
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
        self.imagesLeft = []
        self.imagesRight = []
        MovingObject.__init__(self, start_x, start_y, name)
        self.type = "Guardian"
        self.xpos = start_x
        self.ypos = start_y
        self.startxpos = start_x
        self.startypos = start_y
        (self.width, self.height) = self.image.get_rect().size
        self.direction = "right"
        self.collidable = True

    def scaleUp(self, scale):
        # scale the sprites up to larger
        numImages = len(self.imagesRight)
        for count in range(0, numImages):
            (imgWidth, imgHeight) = self.imagesRight[count].get_rect().size
            newHeight = int(imgHeight * scale)
            newWidth = int(imgWidth * scale)
            picture = pygame.transform.scale(self.imagesRight[count], (newWidth, newHeight))            
            self.imagesRight[count] = picture
            (imgWidth,imgHeight) = self.imagesLeft[count].get_rect().size
            newHeight = int(imgHeight * scale)
            newWidth = int(imgWidth * scale)
            picture = pygame.transform.scale(self.imagesLeft[count], (newWidth,newHeight))
            self.imagesLeft[count] = picture
            self.width = newWidth
            self.height = newHeight

    def setColor(self, color):
        # print("setColor(", color, ") called on", self.name)
        for n in range(0,len(self.imagesLeft)):
            self.imagesLeft[n] = Screen.colorImage(self.imagesLeft[n], color)
        for n in range(0,len(self.imagesRight)):
            self.imagesRight[n] = Screen.colorImage(self.imagesRight[n], color)

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

    def setEndPos(self, screenx, screeny):
        print("Updating", self.name, "endPosX")
        self.endPosX = screenx
        
    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (self.xpos,self.ypos))
        return

class TrumpetNose(Guardian):
    def __init__(self, start_x, start_y, scale, name="TrumpetNose"):
        Guardian.__init__(self, start_x, start_y, name)
        self.subtype = "TrumpetNose"
        # print("Creating TrumpetNose: ", name)
        # moving left animation sprites
        self.imagesLeft = [
            pygame.image.load('trumpetnose_left_1.png'),
            pygame.image.load('trumpetnose_left_2.png'),
            pygame.image.load('trumpetnose_left_3.png'),    
            pygame.image.load('trumpetnose_left_4.png')
        ]

        # moving right animation sprites
        self.imagesRight = [
            pygame.image.load('trumpetnose_right_1.png'),
            pygame.image.load('trumpetnose_right_2.png'),
            pygame.image.load('trumpetnose_right_3.png'),    
            pygame.image.load('trumpetnose_right_4.png')
        ]
        self.scaleUp(scale)
        self.walkPos = 0
        self.direction = "right"
        self.endPosX = start_x + 100
        self.endPosY = start_y

    def move(self, screen):
        if self.direction == "left":
            self.image = self.imagesLeft[self.walkPos]
            self.xpos -= 4
        else: # direction == "right"
            self.image = self.imagesRight[self.walkPos]
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

class Ostrich(Guardian):
    def __init__(self, start_x, start_y, scale, name="Ostrich"):
        Guardian.__init__(self, start_x, start_y, name)
        self.subtype = "Ostrich"
        # moving left animation sprites
        self.imagesLeft = [
            pygame.image.load('ostrich_left_1.png'),
            pygame.image.load('ostrich_left_2.png'),
            pygame.image.load('ostrich_left_3.png'),    
            pygame.image.load('ostrich_left_4.png')
        ]

        # moving right animation sprites
        self.imagesRight = [
            pygame.image.load('ostrich_right_1.png'),
            pygame.image.load('ostrich_right_2.png'),
            pygame.image.load('ostrich_right_3.png'),    
            pygame.image.load('ostrich_right_4.png')
        ]
        self.scaleUp(scale)
        self.walkPos = 0
        self.direction = "right"
        self.endPosX = start_x + 100
        self.endPosY = start_y

    def move(self, screen):
        if self.direction == "left":
            self.image = self.imagesLeft[self.walkPos]
            self.xpos -= 4
        else: # direction == "right"
            self.image = self.imagesRight[self.walkPos]
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
        # print("Creating Willy at ", start_x, start_y)
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

    def isJumping(self):
        return self.willyJump > 0
            
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
    screen.flash()
    # play death sound
    sound.playMainMusic()
        
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
    if events.keysPressed["dev1"]:
        print("dev1 - skip level")
        return "levelComplete"
    if events.keysPressed["restart"]:
        print("restart")
        player.lives = 3
        print("Lives:", player.lives)
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
                return "levelComplete"
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
K = 0x0B # key
L = 0x0C # spider line
N = 0x0E # Ostrich end location
O = 0x0F # Ostrich start location
P = 0x10 # plant
S = 0x13 # spider
T = 0x14 # TrumpetNose start location
U = 0x15 # TrumpetNose end location
V = 0x16 # left conveyor
W = 0x17 # willy start location
X = 0x18 # right conveyor
Y = 0x19 # combination of U and Z
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
            [B,T,0,0,0,0,0,0,0,0,U,0,0,0,0,0,0,0,0,U,0,C,C,C,F,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,B,C,C,B,0,0,B],
            [B,F,C,C,C,C,C,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,K,0,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,0,K,0,0,0,0,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,C,C,C,C,0,0,0,B,C,C,B,0,0,B],
            [B,0,V,V,V,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,0,0,K,0,0,0,0,0,B,C,C,B,0,0,B],
            [B,0,W,0,0,0,0,C,C,C,C,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,U,Z,Y,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,B],
            [B,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,B],
        ],
        "blue",    # background
        "magenta", # floors
        "yellow",  # conveyors
    ],
    "theMenagerie": [
        [
            [B,0,0,0,0,K,0,0,0,S,0,0,0,K,0,0,L,0,0,0,S,0,0,0,K,0,0,0,S,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,S,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,O,0,0,0,0,0,0,0,0,0,0,0,0,0,N,0,O,0,0,0,0,0,0,0,0,0,0,0,0,N,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,F,F,F,F,F,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,C,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,F,F,F,F,F,F,F,F,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,F,B],
            [B,L,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,L,0,0,0,0,0,V,V,V,V,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,L,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,F,F,F,B],
            [B,S,0,0,0,0,0,0,0,0,0,0,0,F,F,F,F,F,0,0,0,0,0,0,0,0,0,0,0,Z,Z,B],
            [B,0,0,0,0,F,F,F,F,F,F,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,B],
            [B,0,W,0,0,0,0,0,0,0,0,O,0,0,0,0,0,0,K,N,F,F,F,F,F,F,F,F,F,F,F,B],
            [B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,B],
            [B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B,B],
        ],
        "black",   # background
        "cyan",    # floors
        "red",     # conveyors
    ],
    "centralCavernTest": [
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
    "testCavern": [
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

guardians = []
keys = []
floors = []
obstacles = []
portal = [] # actually made of 4 portal objects

def loadCavern(cavern, screen):
    global willy
    global portal
    global obstacles
    global floors
    global keys
    global guardians

    portal = []
    obstacles = []
    floors = []
    keys = []
    guardians = []
    
    # cavern data
    cavernMap = cavern[0]
    bgColor = cavern[1]
    floorColor = cavern[2]
    conveyorColor = cavern[3]
    colorSequenceNum = 0
    colorSequence = ["magenta", "red", "green", "blue", "yellow"]

    for celly in range(0,16):
        for cellx in range(0,32):
            cellContents = cavernMap[celly][cellx]
            # print("handling map: ", cellx, celly, " = ", cellContents)
            (screenx,screeny) = screen.cellToCoords(cellx, celly)
            if cellContents == B:
                cellName = "brick-" + str(cellx) + "-" + str(celly)
                newbrick = Brick(screenx, screeny, screen.scale * 1.1, cellName)
                # newbrick.setColor(floorColor)
                floors.append(newbrick)
            elif cellContents == F:
                cellName = "floor-" + str(cellx) + "-" + str(celly)
                newfloor = Floor(screenx, screeny, screen.scale * 1.1, cellName, floorColor)
                newfloor.setColor(floorColor)
                floors.append(newfloor)
            elif cellContents == I:
                cellName = "ice-" + str(cellx) + "-" + str(celly)
                obstacles.append(Ice(screenx, screeny, screen.scale, cellName))
            elif cellContents == O:
                cellName = "ostrich-" + str(cellx) + "-" + str(celly)
                newOstrich = Ostrich(screenx, screeny, screen.scale, cellName)
                newOstrich.setColor(colorSequence[colorSequenceNum % len(colorSequence)])
                colorSequenceNum += 1
                guardians.append(newOstrich)
            elif cellContents == N:
                lastOstrich = None
                for guardian in guardians:
                    print("Looking for Ostrich: ", guardian.name)
                    if guardian.subtype == "Ostrich":
                        lastOstrich = guardian
                print("last guardian found was", lastOstrich, "named", lastOstrich.name)
                if lastOstrich != None:
                    print("setting", lastOstrich.name, " end position to: (", cellx, ",", celly, ")")
                    lastOstrich.setEndPos(screenx, screeny)
            elif cellContents == P:
                cellName = "plant-" + str(cellx) + "-" + str(celly)
                obstacles.append(Plant(screenx, screeny, screen.scale, cellName))
            elif cellContents == L:
                cellName = "spiderline-" + str(cellx) + "-" + str(celly)
                obstacles.append(SpiderLine(screenx, screeny, screen.scale, cellName))
            elif cellContents == S:
                cellName = "spider-" + str(cellx) + "-" + str(celly)
                obstacles.append(Spider(screenx, screeny, screen.scale, cellName))
            elif cellContents == V:
                cellName = "leftconveyor-" + str(cellx) + "-" + str(celly)
                newconveyor = LeftConveyor(screenx, screeny, screen.scale * 1.1, cellName, conveyorColor)
                newconveyor.setColor(conveyorColor)
                floors.append(newconveyor)
            elif cellContents == X:
                cellName = "rightconveyor-" + str(cellx) + "-" + str(celly)
                newconveyor = RightConveyor(screenx, screeny, screen.scale * 1.1, cellName, conveyorColor)
                newconveyor.setColor(conveyorColor)
                floors.append(newconveyor)
            elif cellContents == C:
                cellName = "crumble-" + str(cellx) + "-" + str(celly)
                newcrumble = CrumblingFloor(screenx, screeny, screen.scale, cellName, floorColor)
                newcrumble.setColor(floorColor)
                floors.append(newcrumble)
            elif cellContents == W:
                cellName = "willy-" + str(cellx) + "-" + str(celly)
                screeny -= 10
                willy = Willy(screenx, screeny, screen.scale)
            elif cellContents == T:
                cellName = "trumpetnose-" + str(cellx) + "-" + str(celly)
                newTrumpetNose = TrumpetNose(screenx, screeny, screen.scale, cellName)
                guardians.append(newTrumpetNose)
            elif cellContents == U:
                lastTrumpetNose = None
                for guardian in guardians:
                    print("Looking for TN: ", guardian.name)
                    if guardian.subtype == "TrumpetNose":
                        lastTrumpetNose = guardian
                print("last guardian found was", lastTrumpetNose, "named", lastTrumpetNose.name)
                if lastTrumpetNose != None:
                    print("setting", lastTrumpetNose.name, " end position to: (", cellx, ",", celly, ")")
                    lastTrumpetNose.setEndPos(screenx, screeny)
            elif cellContents == K:
                cellName = "key" + "-" + str(cellx) + "-" + str(celly)
                keys.append(Key(screenx, screeny, screen.scale, cellName))
            elif cellContents == Z or cellContents == Y:
                cellName = "portal" + "-" + str(cellx) + "-" + str(celly)
                portal.append(Portal(screenx, screeny, screen.scale * 1.1, cellName))
                if cellContents == Y:
                    # we also set the guardian end
                    lastGuardian = guardians[len(guardians)-1]
                    if lastGuardian != None:
                        lastGuardian.setEndPos(screenx, screeny)
    screen.setBackgroundColor(bgColor)

def processCmdLineArgs(events):
    cavernFound = False
    for arg in sys.argv[1:]:
        if arg[0:2] == "--":
            if arg[2:] == "infocom":
                events.infocomMode = True
        else:
            return arg

def main():
    # screen (h x w): 6.802 x 9.071 (25% larger height and width than inner game area)
    # inner game area (h x w): 5.419 x 7.255
    # top/bottom border height: 0.672 (10% of screen height)
    # left/right border width: 0.902 (10% of screen width)
    # game area height: 3.611
    # cavern name height: 0.218
    # air supply height: 0.213
    # high score, lives height: 1.352
    
    events = Events()
    game = ["centralCavern", "coldRoom", "theMenagerie"]
    levelNumber = 0
    # load the specified cavern or the default, falling back to default if specified but not found
    defaultCavern = "centralCavern"
    userCavern = processCmdLineArgs(events)
    if userCavern not in caverns.keys():
        print("Cavern", userCavern, " is not known")
        cavern = caverns[game[levelNumber]]
    else:
        print("Loading", userCavern)
        cavern = caverns[userCavern]

    screen = Screen(640, 320, cavern[1])
    loadCavern(cavern, screen)
    player = Player()
    sound = Sound()
    scale = 0.7
    clock = pygame.time.Clock()
    sound.startMainMusic()

    print("Manic Miner is running")
    running = True

    # show title screen and play title music
    # sound.playTitleTune()

    while running and player.lives > 0:
        running = events.check(willy)
        if update(clock, player, events, keys, guardians, willy, screen, sound, floors, obstacles, portal):
            # player just completed a level
            levelNumber += 1
            if levelNumber >= len(game):
                win()
            loadCavern(caverns[game[levelNumber]], screen)
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
