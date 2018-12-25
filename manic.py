#!/usr/local/bin/python3

# rooms: http://jswremakes.emuunlim.com/Mmt/Manic%20Miner%20Room%20Format.htm
# -8 -8 -6 -6 -4 -4 -2 -2 0 0 2 2 4 4 6 6 8 8

import os, sys, math, re, logging
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
            "test": False,
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
                    pygame.quit()
                    sys.exit()
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
            elif e.type == QUIT:
                    print("Manic Miner quit")
                    pygame.quit()
                    sys.exit()
        
class Screen:
    def __init__(self):
        pygame.init()
        self.FPS = 30 # frames per second setting
        self.fpsClock = pygame.time.Clock()
        # set up the window
        self.max_x = 640
        self.max_y = 480
        # DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), 0, 32)
        # DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), pygame.FULLSCREEN)
        self.DISPLAYSURF = pygame.display.set_mode((self.max_x, self.max_y), pygame.RESIZABLE)
        pygame.display.set_caption('Manic Miner')
        pygame.key.set_repeat(1,10)
        self.BLACK = (0, 0, 0)
        # define some boundary values
        self.xboundary_left = 5
        self.xboundary_right = self.max_x - 50 # willyImgWidth*2
        self.yboundary_top = 5
        self.yboundary_bottom = self.max_y - 50 # willyImgHeight*2

    def displayBackground(self):
        self.DISPLAYSURF.fill(self.BLACK)

class Guardian:
    def __init__(self, start_x, start_y):
        self.xpos = start_x
        self.ypos = start_y
        self.image = pygame.image.load('cat.png')
        (self.width, self.height) = self.image.get_rect().size

    def display(self, screen):
        screen.DISPLAYSURF.blit(self.image, (screen.xboundary_right - self.width, screen.yboundary_bottom - self.height))
        
class Willy:
    def __init__(self, start_x, start_y):
        # start bottom left
        self.willyScale = 2.4           # how much to scale the loaded sprites
        # motion distances
        self.xdistance = 4              # how far left and right motion moves Willy
        self.ydistance = 5              # how far jumping motion moves Willy on the y axis
        self.willyJumpDistance = 36     # how far to jump horizontally
        self.willyJumpHeight = 18       # peak of a jump relative to zero
        # starting position
        self.willystartx = start_x
        self.willystarty = start_y
        self.willyx = start_x           # willy's x location; start at left of screen
        self.willyy = start_y           # willy's y location; start at bottom of screen
        self.direction = "right";       # start willy off facing right
        self.walking = False            # is willy walking or standing still?

        self.willyWalk = 0              # where willy is at in his walking animation
        self.willyJump = 0              # where willy is at in his jump
        self.willyJumpFactor = 1.2
        self.testMode = False
        self.test = Test()

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
            (willyImgHeight,willyImgWidth) = self.willyImgRight[count].get_rect().size
            # print("dimensions: ", willyImgHeight, willyImgWidth)
            newHeight = int(willyImgHeight * self.willyScale)
            newWidth = int(willyImgWidth * self.willyScale)
            picture = pygame.transform.scale(self.willyImgRight[count], (newHeight, newWidth))
            self.willyImgRight[count] = picture
            (willyImgHeight,willyImgWidth) = self.willyImgLeft[count].get_rect().size
            # print("dimensions: ", willyImgHeight, willyImgWidth)
            newHeight = int(willyImgHeight * self.willyScale)
            newWidth = int(willyImgWidth * self.willyScale)
            picture = pygame.transform.scale(self.willyImgLeft[count], (newHeight, newWidth))
            self.willyImgLeft[count] = picture

    def getJumpHeight(self, jumpPosition, jumpDistance, jumpHeight):
        jumpPosition //= 2
        # print("  jumpPosition: ", jumpPosition)
        heights = [8, 8, 6, 6, 4, 4, 2, 2, 0, 0, 2, 2, 4, 4, 6, 6, 8, 8]
        heightToAdd = heights[jumpPosition]
        # print("  heightToAdd:  ", heightToAdd)
        return heightToAdd * self.willyJumpFactor

    def jump(self, screen):
        if self.willyJump > (self.willyJumpDistance / 2): # rising
            if self.willyy > screen.yboundary_top: # don't go off the top of the screen
                jumpPos = (self.willyJumpDistance - self.willyJump)
                toJump = self.getJumpHeight(jumpPos, self.willyJumpDistance, self.willyJumpHeight)
                self.willyy -= toJump
            if self.direction == "right" and self.walking:
                if (self.willyx < screen.xboundary_right): # don't go off the screen to the right
                    self.willyx += self.xdistance
                    self.willyWalk += 1
            elif self.direction == "left" and self.walking:
                if (self.willyx > screen.xboundary_left): # don't go off the screen to the right
                    self.willyx -= self.xdistance
                    self.willyWalk += 1
        else: # falling
            if (self.willyy < screen.yboundary_bottom): # don't go off the bottom of the screen
                jumpPos = (self.willyJumpDistance - self.willyJump)
                toJump = self.getJumpHeight(jumpPos, self.willyJumpDistance, self.willyJumpHeight)
                self.willyy += toJump
            if self.direction == "right" and self.walking:
                if (self.willyx < screen.xboundary_right): # don't go off the screen to the right
                    self.willyx += self.xdistance
                    self.willyWalk += 1
            elif self.direction == "left" and self.walking:
                if (self.willyx > screen.xboundary_left): # don't go off the screen to the right
                    self.willyx -= self.xdistance
                    self.willyWalk += 1
        if self.willyWalk == len(self.willyImgRight):
            self.willyWalk = 0
        self.willyJump -= 1
        if self.willyJump == 1:
            self.walking = False
        return self.willyJump

    def move(self, events, screen):
        # if events.keysPressed["left"] or events.keysPressed["right"] or events.keysPressed["jump"]:
        #     print("Keys: ", end='', flush=True)
        #     if events.keysPressed["left"]:
        #         print("L,",end='', flush=True)
        #     if events.keysPressed["right"]:
        #         print("R,",end='', flush=True)
        #     if events.keysPressed["jump"]:
        #         print("J",end='', flush=True)
        #     print()
        # else:
        #     print("No keys pressed")
        
        if events.keysPressed["dev1"]:
            self.willyx = self.willystartx
            self.willyy = self.willystarty
        
        # are we already jumping?
        if self.willyJump > 0:
            # already jumping
            self.jump(screen)
            self.willyJump -= 1
            # don't handle any more keys
            return

        # play the next test move
        if events.keysPressed["test"]:
            self.testMode = True

        if self.testMode:
            moves = self.test.getNextMove()
            # print("testKeys: ", end='')
            for move in moves:
                # print(move, ", ", end='', flush=True)
                if move != "none":
                    events.keysPressed[move] = True
            # print()

        # move in response to direction
        if events.keysPressed["left"]:
            if events.keysPressed["jump"]:
                # print("*** jump left")
                self.willyJump = self.willyJumpDistance;
                self.direction = "left"
                self.walking = True
            else:
                # print("*** walk left")
                self.direction = "left"
                if self.willyx > screen.xboundary_left:
                    self.willyx -= self.xdistance
                    self.willyWalk += 1            
                    if self.willyWalk == len(self.willyImgLeft):
                        self.willyWalk = 0
        elif events.keysPressed["right"]:
            # print("*** handling right key")
            if events.keysPressed["jump"]:
                # print("*** jump right")
                self.willyJump = self.willyJumpDistance;
                self.direction = "right"
                self.walking = True
            else:
                # print("*** walk right")
                self.direction = "right"
                if self.willyx < screen.xboundary_right:
                    # print("walking right")
                    self.willyx += self.xdistance
                    self.willyWalk += 1
                    if self.willyWalk == len(self.willyImgRight):
                        self.willyWalk = 0
        elif events.keysPressed["jump"]:
            # print("*** jump in place")
            self.willyJump = self.willyJumpDistance;
            self.walking = False
        else:
            self.walking = False
        return
    
    def display(self, screen):
        if self.direction == "left":
            screen.DISPLAYSURF.blit(self.willyImgLeft[self.willyWalk], (self.willyx, self.willyy))
        else:
            screen.DISPLAYSURF.blit(self.willyImgRight[self.willyWalk], (self.willyx, self.willyy))

def update(events, guardians, willy, screen):
    screen.displayBackground()
    guardians.display(screen)
    willy.move(events, screen)
    willy.display(screen)
    pygame.display.update()
    
def main():
    events = Events()
    screen = Screen()
    guardians = Guardian(200,200)
    # draw room
    # draw guardians
    
    startx = screen.xboundary_left
    starty = screen.yboundary_bottom
    willy = Willy(0, screen.yboundary_bottom)
    clock = pygame.time.Clock()

    print("Manic Miner is running")
    
    while True:
        events.check()
        update(events, guardians, willy, screen)
        clock.tick(screen.FPS)

main()
