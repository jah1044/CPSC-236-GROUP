#-----> NEW CODE <-------

import random, copy, sys, pygame
from pygame.locals import *

# Create the game board size and color 
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

gameMode = 'pvc'
popMode = False

POP_LEFT_RECT = pygame.Rect(20, 20, 60, 30)
POP_RIGHT_RECT = pygame.Rect(WINDOWWIDTH - 80, 20, 60, 30)

def displayMenu():
    """Displays a menu for the user to choose whether to play a computer or a player"""
    font = pygame.font.SysFont(None, 48)
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        title = font.render("Choose Game Mode", True, WHITE)
        pvp = font.render("1 - Player vs Player", True, WHITE)
        pvc = font.render("2 - Player vs Computer", True, WHITE)
        DISPLAYSURF.blit(title, (WINDOWWIDTH // 2 - title.get_width() // 2, 100))
        DISPLAYSURF.blit(pvp, (100, 200))
        DISPLAYSURF.blit(pvc, (100, 300))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_1:
                    return 'pvp'
                elif event.key == K_2:
                    return 'pvc'
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        FPSCLOCK.tick()

def runGame(isFirstGame):
    """Runs a single game loop, alternating turns between players, handling moves and checking for win/tie."""
    global turn
    global gameMode, popMode
    if isFirstGame:
        turn = RED
        showHelp = True
    else:
        turn = RED if random.randint(0, 1) == 0 else BLACK
        showHelp = False

    board = getNewBoard()
    winnerImg = None

    while True:
        if turn == RED:
            result = getHumanMove(board, showHelp, RED)
            showHelp = False
            if result == 'pop':
                popOutPiece(board, RED)
                turn = BLACK
                continue
            elif isinstance(result, int):
                if isWinner(board, RED):
                    winnerImg = HUMANWINNERIMG
                    break
                turn = BLACK
                continue

        elif turn == BLACK:
            if gameMode == 'pvc':
                column = getComputerMove(board)
                animateDroppingToken(board, column, BLACK)
                board[column][getLowestEmptySpace(board, column)] = BLACK
                if isWinner(board, BLACK):
                    winnerImg = COMPUTERWINNERIMG
                    break
                turn = RED
                continue
            else:
                result = getHumanMove(board, showHelp, BLACK)
                if result == 'pop':
                    popOutPiece(board, BLACK)
                    turn = RED
                    continue
                elif isinstance(result, int):
                    if isWinner(board, BLACK):
                        winnerImg = HUMANWINNERIMG
                        break
                    turn = RED
                    continue

        if isBoardFull(board):
            winnerImg = TIEWINNERIMG
            break

    while True:
        drawBoard(board)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return
        FPSCLOCK.tick()

def main():
    """Creates the game environment by implementing the pictures saved in the file to represent the black and red pieces
    and handles top-level game state and loop."""
    global FPSCLOCK, DISPLAYSURF, REDTOKENIMG, BLACKTOKENIMG, BOARDIMG, HUMANWINNERIMG
    global COMPUTERWINNERIMG, TIEWINNERIMG, WINNERRECT, REDPILERECT, BLACKPILERECT, ARROWIMG, ARROWRECT, gameMode

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

    gameMode = displayMenu()
    isFirstGame = True

    while True:
        runGame(isFirstGame)
        isFirstGame = False

def getNewBoard():
    """This function is what generates the game board at the beginning of play"""
    return [[EMPTY] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

def drawBoard(board, extraToken=None):
    """Draws the current state of the game board and any token being dragged."""
    DISPLAYSURF.fill(BGCOLOR)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect = pygame.Rect(XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE), SPACESIZE, SPACESIZE)
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)
            DISPLAYSURF.blit(BOARDIMG, spaceRect)
    if extraToken is not None:
        DISPLAYSURF.blit(REDTOKENIMG if extraToken['color'] == RED else BLACKTOKENIMG,
                         (extraToken['x'], extraToken['y']))
    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT)
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT)
    pygame.draw.rect(DISPLAYSURF, WHITE, POP_LEFT_RECT, 2)
    pygame.draw.rect(DISPLAYSURF, WHITE, POP_RIGHT_RECT, 2)
    font = pygame.font.SysFont(None, 24)
    popText = font.render("POP", True, WHITE)
    DISPLAYSURF.blit(popText, (POP_LEFT_RECT.x + 10, POP_LEFT_RECT.y + 5))
    DISPLAYSURF.blit(popText, (POP_RIGHT_RECT.x + 10, POP_RIGHT_RECT.y + 5))

def getLowestEmptySpace(board, column):
    """To make the rule variant more effective for the POP, I want the piece to drop out of the bottom
    because if they were out of the top they could just replace the piece that was missing
    by dropping it out of the bottom it alters he board and strategy to win"""
    for y in range(BOARDHEIGHT - 1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1

def isValidMove(board, column):
    """Returns True if the move is valid (column not full), False otherwise."""
    return 0 <= column < BOARDWIDTH and board[column][0] == EMPTY

def isBoardFull(board):
    """Checks if the board is full and returns True if it is."""
    return all(board[x][0] != EMPTY for x in range(BOARDWIDTH))

def isWinner(board, tile):
    """Checks after the piece is in placee whether there is 4 in a row in all directions"""
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

def getComputerMove(board):
    """Randomly selects and returns a valid move for the computer."""
    validMoves = [i for i in range(BOARDWIDTH) if isValidMove(board, i)]
    return random.choice(validMoves)

def animateDroppingToken(board, column, color):
    """Animation of the players token falling into the selected column"""
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
    """animation of computer's token sliding into position."""
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    while y > YMARGIN - SPACESIZE:
        y -= 2
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    animateDroppingToken(board, column, BLACK)

def popOutPiece(board, color):
    """The Pop function randomly deletes the oppenents piece if pop function is selected
    to alter the game strategy and then moves the pieces down accordingly """
    opponent = RED if color == BLACK else BLACK
    bottom_row_pieces = [(x, BOARDHEIGHT - 1) for x in range(BOARDWIDTH) if board[x][BOARDHEIGHT - 1] == opponent]

    if bottom_row_pieces:
        col, row = random.choice(bottom_row_pieces)
        for y in range(row, 0, -1):
            board[col][y] = board[col][y - 1]
        board[col][0] = EMPTY

def getHumanMove(board, isFirstMove, color=RED):
    """This function controls the token being moved above the board to drop it in or being taken out with the pop function"""
    global turn
    dragging = False
    tokenx = tokeny = None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if ((color == RED and REDPILERECT.collidepoint(event.pos) and turn == RED) or
                    (color == BLACK and BLACKPILERECT.collidepoint(event.pos) and turn == BLACK)):
                    dragging = True
                    tokenx, tokeny = event.pos
                elif (color == RED and POP_LEFT_RECT.collidepoint(event.pos) and turn == RED) or (color == BLACK and POP_RIGHT_RECT.collidepoint(event.pos) and turn == BLACK):
                    return 'pop'
            elif event.type == MOUSEMOTION and dragging:
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and dragging:
                if tokeny < YMARGIN and XMARGIN <= tokenx < WINDOWWIDTH - XMARGIN:
                    col = int((tokenx - XMARGIN) / SPACESIZE)
                    if isValidMove(board, col):
                        animateDroppingToken(board, col, color)
                        board[col][getLowestEmptySpace(board, col)] = color
                        return col
                dragging = False
                tokenx = tokeny = None

        drawBoard(board, {'x': tokenx - SPACESIZE // 2, 'y': tokeny - SPACESIZE // 2, 'color': color} if dragging else None)
        if isFirstMove:
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT)
            isFirstMove = False
        pygame.display.update()
        FPSCLOCK.tick()

if __name__ == '__main__':
    main()  
