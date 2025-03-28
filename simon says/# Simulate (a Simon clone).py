import random, sys, time, pygame
from pygame.locals import *
import os

# Game Constants
FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 500  # in milliseconds
FLASHDELAY = 200  # in milliseconds
BUTTONSIZE = 200
BUTTONGAPSIZE = 20
TIMEOUT = 6  # seconds before game over if no button is pushed.

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHTRED = (255, 0, 0)
RED = (155, 0, 0)
BRIGHTGREEN = (0, 255, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 0, 255)
BLUE = (0, 0, 155)
BRIGHTYELLOW = (255, 255, 0)
YELLOW = (155, 155, 0)
DARKGRAY = (40, 40, 40)

bgColor = BLACK

# Button Placement
XMARGIN = (WINDOWWIDTH - (2 * BUTTONSIZE) - BUTTONGAPSIZE) // 2
YMARGIN = (WINDOWHEIGHT - (2 * BUTTONSIZE) - BUTTONGAPSIZE) // 2

YELLOWRECT = pygame.Rect(XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
BLUERECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
REDRECT = pygame.Rect(XMARGIN, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)
GREENRECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)

def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()

def terminate():
    pygame.quit()
    sys.exit()

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Simulate')

    BASICFONT = pygame.font.Font('freesansbold.ttf', 14)  # Reduced font size for better fit
    infoSurf = BASICFONT.render('Match the pattern by clicking buttons.', True, DARKGRAY)
    infoRect = infoSurf.get_rect(topleft=(10, WINDOWHEIGHT - 25))

    # Set sound file path
    sound_path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "Python", "sounds")
    
    try:
        BEEP1 = pygame.mixer.Sound(os.path.join(sound_path, 'beep1.ogg'))
        BEEP2 = pygame.mixer.Sound(os.path.join(sound_path, 'beep2.ogg'))
        BEEP3 = pygame.mixer.Sound(os.path.join(sound_path, 'beep3.ogg'))
        BEEP4 = pygame.mixer.Sound(os.path.join(sound_path, 'beep4.ogg'))
    except pygame.error:
        BEEP1 = BEEP2 = BEEP3 = BEEP4 = None
        print("Error: Sound files missing!")

    # Game Variables
    pattern = []
    currentStep = 0
    lastClickTime = time.time()
    score = 0
    highScore = 0  # Track high score
    waitingForInput = False

    while True:
        clickedButton = None
        DISPLAYSURF.fill(bgColor)  # Always set the background color to black
        drawButtons()

        # Display score
        scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
        scoreRect = scoreSurf.get_rect(topleft=(WINDOWWIDTH - 110, 10))

        # Display high score below the regular score
        highScoreSurf = BASICFONT.render(f'High Score: {highScore}', True, WHITE)
        highScoreRect = highScoreSurf.get_rect(topleft=(WINDOWWIDTH - 110, 30))  # Adjusted position

        DISPLAYSURF.blit(scoreSurf, scoreRect)
        DISPLAYSURF.blit(highScoreSurf, highScoreRect)
        DISPLAYSURF.blit(infoSurf, infoRect)

        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                clickedButton = getButtonClicked(event.pos[0], event.pos[1])

        if not waitingForInput:
            pygame.display.update()
            pygame.time.wait(1000)  # Give time for the player to watch the pattern
            pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))
            for button in pattern:
                flashButtonAnimation(button)
                pygame.time.wait(FLASHDELAY)
            pygame.time.wait(500)  # Add an extra wait here so the player has time to react before input
            waitingForInput = True
            currentStep = 0
        else:
            if clickedButton and clickedButton == pattern[currentStep]:
                flashButtonAnimation(clickedButton)
                currentStep += 1
                lastClickTime = time.time()
                if currentStep == len(pattern):
                    score += 1
                    highScore = max(highScore, score)
                    waitingForInput = False
            elif (clickedButton and clickedButton != pattern[currentStep]) or (time.time() - lastClickTime > TIMEOUT):
                displayGameOverMessage()
                gameOverAnimation()
                pattern = []
                score = 0
                waitingForInput = False
                pygame.time.wait(1000)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def flashButtonAnimation(color, animationSpeed=50):
    sound = {YELLOW: BEEP1, BLUE: BEEP2, RED: BEEP3, GREEN: BEEP4}[color]
    flashColor = {YELLOW: BRIGHTYELLOW, BLUE: BRIGHTBLUE, RED: BRIGHTRED, GREEN: BRIGHTGREEN}[color]
    rectangle = {YELLOW: YELLOWRECT, BLUE: BLUERECT, RED: REDRECT, GREEN: GREENRECT}[color]

    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface((BUTTONSIZE, BUTTONSIZE)).convert_alpha()
    r, g, b = flashColor
    if sound:
        sound.play()
    
    for alpha in range(0, 255, animationSpeed):
        checkForQuit()
        DISPLAYSURF.blit(origSurf, (0, 0))
        flashSurf.fill((r, g, b, alpha))
        DISPLAYSURF.blit(flashSurf, rectangle.topleft)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

    DISPLAYSURF.blit(origSurf, (0, 0))

def drawButtons():
    pygame.draw.rect(DISPLAYSURF, YELLOW, YELLOWRECT)
    pygame.draw.rect(DISPLAYSURF, BLUE, BLUERECT)
    pygame.draw.rect(DISPLAYSURF, RED, REDRECT)
    pygame.draw.rect(DISPLAYSURF, GREEN, GREENRECT)

def changeBackgroundAnimation():
    global bgColor
    newBgColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    bgColor = newBgColor

def gameOverAnimation():
    pygame.time.wait(500)

def displayGameOverMessage():
    font = pygame.font.Font('freesansbold.ttf', 32)
    textSurf = font.render('Game Over!', True, WHITE)
    textRect = textSurf.get_rect(center=(WINDOWWIDTH // 2, WINDOWHEIGHT // 2))
    DISPLAYSURF.blit(textSurf, textRect)
    pygame.display.update()
    pygame.time.wait(2000)

def getButtonClicked(x, y):
    return next((b for b, r in zip([YELLOW, BLUE, RED, GREEN], [YELLOWRECT, BLUERECT, REDRECT, GREENRECT]) if r.collidepoint((x, y))), None)

if __name__ == '__main__':
    main()
