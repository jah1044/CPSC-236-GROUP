# Four-In-A-Row (a Connect Four clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license



#---> ORIGINAL CODE <-----




import random, copy, sys, pygame
from pygame.locals import *

BOARDWIDTH = 7
BOARDHEIGHT = 6
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

DIFFICULTY = 2

SPACESIZE = 50
FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

BRIGHTBLUE = (0, 50, 255)
WHITE = (255, 255, 255)

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'

def main():
    global FPSCLOCK, DISPLAYSURF, REDTOKENIMG, BLACKTOKENIMG, BOARDIMG, HUMANWINNERIMG
    global COMPUTERWINNERIMG, TIEWINNERIMG, WINNERRECT, REDPILERECT, BLACKPILERECT, ARROWIMG, ARROWRECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Four in a Row')

    REDTOKENIMG = pygame.image.load('4row_red.png')
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    BLACKTOKENIMG = pygame.image.load('4row_black.png')
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    BOARDIMG = pygame.image.load('4row_board.png')
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

    HUMANWINNERIMG = pygame.image.load('4row_humanwinner.png')
    COMPUTERWINNERIMG = pygame.image.load('4row_computerwinner.png')
    TIEWINNERIMG = pygame.image.load('4row_tie.png')
    WINNERRECT = HUMANWINNERIMG.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)

    ARROWIMG = pygame.image.load('4row_arrow.png')
    ARROWRECT = ARROWIMG.get_rect()
    ARROWRECT.left = REDPILERECT.right + 10
    ARROWRECT.centery = REDPILERECT.centery

    isFirstGame = True

    while True:
        runGame(isFirstGame)
        isFirstGame = False

def runGame(isFirstGame):
    if isFirstGame:
        turn = COMPUTER
        showHelp = True
    else:
        turn = HUMAN if random.randint(0, 1) == 0 else COMPUTER
        showHelp = False

    board = getNewBoard()

    while True:
        if turn == HUMAN:
            getHumanMove(board, showHelp)
            if showHelp:
                showHelp = False
            if isWinner(board, RED):
                winnerImg = HUMANWINNERIMG
                break
            turn = COMPUTER
        else:
            column = getComputerMove(board)
            animateComputerMoving(board, column)
            makeMove(board, BLACK, column)
            if isWinner(board, BLACK):
                winnerImg = COMPUTERWINNERIMG
                break
            turn = HUMAN

        if isBoardFull(board):
            winnerImg = TIEWINNERIMG
            break

    while True:
        drawBoard(board)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()
        FPSCLOCK.tick()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return

def getNewBoard():
    return [[EMPTY] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

def drawBoard(board, extraToken=None):
    DISPLAYSURF.fill(BGCOLOR)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect = pygame.Rect(XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE), SPACESIZE, SPACESIZE)
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)
            DISPLAYSURF.blit(BOARDIMG, spaceRect)
    if extraToken != None:
        if extraToken['color'] == RED:
            DISPLAYSURF.blit(REDTOKENIMG, (extraToken['x'], extraToken['y']))
        elif extraToken['color'] == BLACK:
            DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y']))
    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT)
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT)

def getHumanMove(board, isFirstMove):
    draggingToken = False
    tokenx, tokeny = None, None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
                draggingToken = True
                tokenx, tokeny = event.pos
            elif event.type == MOUSEMOTION and draggingToken:
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and draggingToken:
                if tokeny < YMARGIN and XMARGIN <= tokenx < WINDOWWIDTH - XMARGIN:
                    column = int((tokenx - XMARGIN) / SPACESIZE)
                    if isValidMove(board, column):
                        animateDroppingToken(board, column, RED)
                        board[column][getLowestEmptySpace(board, column)] = RED
                        return
                tokenx, tokeny = None, None
                draggingToken = False
        if tokenx is not None and tokeny is not None:
            drawBoard(board, {'x': tokenx - int(SPACESIZE / 2), 'y': tokeny - int(SPACESIZE / 2), 'color': RED})
        else:
            drawBoard(board)
        if isFirstMove:
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT)
        pygame.display.update()
        FPSCLOCK.tick()

def makeMove(board, player, column):
    row = getLowestEmptySpace(board, column)
    if row != -1:
        board[column][row] = player

def getLowestEmptySpace(board, column):
    for y in range(BOARDHEIGHT - 1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1

def isValidMove(board, column):
    return 0 <= column < BOARDWIDTH and board[column][0] == EMPTY

def isBoardFull(board):
    return all(board[x][0] != EMPTY for x in range(BOARDWIDTH))

def isWinner(board, tile):
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT):
            if all(board[x + i][y] == tile for i in range(4)):
                return True
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 3):
            if all(board[x][y + i] == tile for i in range(4)):
                return True
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT - 3):
            if all(board[x + i][y + i] == tile for i in range(4)):
                return True
    for x in range(BOARDWIDTH - 3):
        for y in range(3, BOARDHEIGHT):
            if all(board[x + i][y - i] == tile for i in range(4)):
                return True
    return False

def animateDroppingToken(board, column, color):
    x = XMARGIN + column * SPACESIZE
    y = YMARGIN - SPACESIZE
    targetY = YMARGIN + getLowestEmptySpace(board, column) * SPACESIZE
    speed = 1.0
    while y < targetY:
        y += int(speed)
        speed += 0.5
        drawBoard(board, {'x': x, 'y': y, 'color': color})
        pygame.display.update()
        FPSCLOCK.tick()

def animateComputerMoving(board, column):
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    while y > YMARGIN - SPACESIZE:
        y -= 2
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    y = YMARGIN - SPACESIZE
    while x > XMARGIN + column * SPACESIZE:
        x -= 2
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    animateDroppingToken(board, column, BLACK)

def getComputerMove(board):
    possibleMoves = [i for i in range(BOARDWIDTH) if isValidMove(board, i)]
    return random.choice(possibleMoves)

if __name__ == '__main__':
    main()
