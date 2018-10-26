
import pygame
import pytmx
import sys
from pytmx.util_pygame import load_pygame

TILE_WIDTH  = 16
TILE_HEIGHT = 16
MOVE_WIDTH  = TILE_WIDTH
MOVE_HEIGHT = TILE_HEIGHT

def toTiled(x):
    return x // TILE_HEIGHT;

pygame.init()
size = width,height = 640,480
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

background = pygame.Surface((25*32, 25*32))
    
def getFile(tag):
    resourceFolder = "./resources"
    resourceLookup = { "player" : (resourceFolder + "/player.png"),
                       "level"  : (resourceFolder + "/level.tmx"),
                       "grass"  : (resourceFolder + "/grass.png")}
    return resourceLookup[tag]
resources = dict()
def getResource(tag):
    if not tag in resources:
        image = pygame.image.load(getFile(tag))
        resources[tag] = image
    return resources[tag]

#Extend this to add unified debugging 
class DebugMeta:
    _debugTxt = ""
    def __init__(self,dTxt=None):
        if not dTxt:
            dTxt = self.__class__.__name__
        self._debugTxt = dTxt
    def debugTxt(self):
        return "<" + self._debugTxt + ">"

class Transform:
    x,y = (0,0)
    def __init__(self):
        print(str(self.x) + ", " + str(self.y))
    def translate(x,y):
        self.x += x
        self.y += y
class HasImage(DebugMeta):
    imageTag = ""
    imageFileFn = None
    def __init__(self,imageTag,imageFileFn=getFile):
        self.imageTag = imageTag
        self.imageFileFn = imageFileFn
        DebugMeta.__init__(self,"imageTag: " + self.imageTag + ", imageFile: " + self.imageFile())
    def imageFile(self):
        return self.imageFileFn(self.imageTag)
    def surface(self):
        return getResource(self.imageTag)

def defaultLevelUp(self):
    self.maxLevel += self.levelGainRate
    self.level = maxLevel
    
    self.maxXp *= self.maxXpMultiplier
    
class Stat:
    name = ""
    level = 0
    maxLevel = 0
    xp = 0
    maxXp = 0
    levelGainRate = 1
    maxXpMultiplier = 1.2
    def __init__(self,name,level=1,maxLevel=1,xp=0,maxXp=80,levelUp=None):
        if not levelUp:
            levelUp = defaultLevelUp
        self.name = name

        self.level = level
        self.maxLevel = maxLevel

        self.xp = xp
        self.maxXp = maxXp
        
        self.levelUp = levelUp

def defaultOnDie(self):
    self.refresh()
class DrainableStat(Stat):
    def __init__(self,name,level=1,maxLevel=1,xp=0,maxXp=80,onDie=None):
        Stat.__init__(self,name,level,maxLevel,xp,maxXp)
        if not onDie:
            onDie = defaultOnDie
        self.onDie = onDie
    def refresh(self):
        self.level = self.maxLevel
    @property
    def level(self):
        return self.__level
    @level.setter
    def level(self,x):
        if(x <= 0):
            self.__level = 0
            self.die()
        else:
            self.__level = x
    def die(self):
        self.onDie(self)
class HasStats:
    stats = dict()
    def getStat(self,stat):
        return self.stats[stat]
    def setStat(self,stat,val):
        self.stats[stat] = val

    def getStatLevel(self,stat):
        return self.getStat(stat).level
    def getStatMaxLevel(stat):
        return self.getStat(stat).maxLevel
    # setDStat = setDrainableStat;  will create a DrainableStat and set it
    def setDStat(self,name,val,maxVal,onDie=None):
        dStat = DrainableStat(name,val,maxVal,onDie)
        self.setStat(name,dStat)
    # setSStat = setStatStat; will create a generic Stat and set stat to it
    def setSStat(self,stat,val,maxVal,onLevelup=None):
        dStat = Stat(name,val,maxVal,onLevelup)
        self.setStat(name,dStat)
class BattleBody(HasStats):
    def __init__(self,onDie=None):
        if not onDie:
            onDie = defaultOnDie
        self.setDStat("health",10,10)

        self.setDStat("strength",1,1)
        self.setDStat("defense",1,1)

        self.onDie = onDie
    def recieveImpact(self,impact):
        myDefense = self.getStatLevel("defense")
        damage = impact - myDefense
        if(damage <= 0):
            damage = 0
        accuracy = random.random()
        damage *= accuracy

        self.health -= damage
        
class Actor(Transform,HasImage,DebugMeta):
    density = 1
    def __init__(self,imageTag):
        HasImage.__init__(self,imageTag)
        DebugMeta.__init__(self,"actor " + self._debugTxt)
class BattleActor(Actor,BattleBody):
    def __init__(self,imageTag):
        Actor.__init__(self,imageTag)
        BattleBody.__init__(self)
    
class Player(BattleActor):
    pass
 
class Game:
    width,height = width,height
    tileWidth,tileHeight = width // TILE_WIDTH, height // TILE_HEIGHT
    def handleEvents(self):
        events = pygame.event.get()
        for event in events:
            #Keydown events
            if event.type == pygame.KEYDOWN:
                # Left arrow 
                if event.key == pygame.K_LEFT:
                    if(toTiled(self.mainPlayer.x) > 0):
                        self.mainPlayer.x -= MOVE_WIDTH
                # Right arrow
                if event.key == pygame.K_RIGHT:
                    if(toTiled(self.mainPlayer.x) < self.tileWidth):
                        self.mainPlayer.x += MOVE_WIDTH
                # Up arrow
                if event.key == pygame.K_UP:
                    if(toTiled(self.mainPlayer.y) > 0):
                        self.mainPlayer.y -= MOVE_HEIGHT
                # Down arrow
                if event.key == pygame.K_DOWN:
                    if(toTiled(self.mainPlayer.y) < self.tileHeight):
                        self.mainPlayer.y += MOVE_HEIGHT
    def draw(self):
        layerIndex = 0
        for layer in self.worldMap.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x in range(0, self.tileWidth):
                    for y in range(0, self.tileHeight):
                        #How far to shift camera on map
                        xDisplace = toTiled(self.mainPlayer.x)
                        yDisplace = toTiled(self.mainPlayer.y)
                        
                        image = self.worldMap.get_tile_image(xDisplace+x, yDisplace+y, layerIndex)

                        if image != None:
                            image.set_alpha(255)
                            background.blit(
                                image,
                                (TILE_WIDTH*x,
                                 TILE_HEIGHT*y))
            layerIndex += 1
        
    def update(self):
        pass
    def start(self):
        self.gameLoop()
    def gameLoop(self):
        while True:
            self.handleEvents()
            self.update()
            self.draw()
        
            screen.blit(background, (0,0))
            screen.blit(self.mainPlayer.surface(),(0,0))
            clock.tick(60)
            pygame.display.flip()

    def __init__(self):
        self.mainPlayer = Player("player")
        self.worldMap = load_pygame(getFile("level"))

        self.start()
        
a = Game()
