import pygame as p
import ChessEngine
import sys
from tkinter import *


BOARD_WIDTH = BOARD_HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH ,BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    color = (0, 0, 0)
    smallfont = p.font.SysFont('Corbel', 35)
    text = smallfont.render('START', True, color)
    color_light = (170, 170, 170)
    color_dark = (100, 100, 100)

    while True:
        for ev in p.event.get():
            if ev.type == p.QUIT:
                p.quit()
            if ev.type == p.MOUSEBUTTONDOWN:
                mouse = p.mouse.get_pos()
                if BOARD_WIDTH / 2 <= mouse[0] <= BOARD_WIDTH / 2 + 140 and BOARD_HEIGHT / 2 <= mouse[1] <= BOARD_HEIGHT / 2 + 40:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    move_made = False
                    loadImages()
                    running = True
                    square_selected = ()
                    player_clicks = []
                    game_over = False

                    while running:
                        for e in p.event.get():
                            if e.type == p.QUIT:
                                p.quit()
                                sys.exit()
                            # mouse handler
                            elif e.type == p.MOUSEBUTTONDOWN:
                                if not game_over:
                                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                                    col = location[0] // SQUARE_SIZE
                                    row = location[1] // SQUARE_SIZE
                                    if square_selected == (row, col) or col >= 8:  # user clicked the same square twice
                                        square_selected = ()  # deselect
                                        player_clicks = []  # clear clicks
                                    else:
                                        square_selected = (row, col)
                                        player_clicks.append(square_selected)  # append for both 1st and 2nd click
                                    if len(player_clicks) == 2:  # after 2nd click
                                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                                        for i in range(len(valid_moves)):
                                            if move == valid_moves[i]:
                                                game_state.makeMove(valid_moves[i])
                                                move_made = True
                                                square_selected = ()  # reset user clicks
                                                player_clicks = []
                                        if not move_made:
                                            player_clicks = [square_selected]

                            elif e.type == p.KEYDOWN:
                                if e.key == p.K_z:  # undo when 'z' is pressed
                                    game_state.undoMove()
                                    move_made = True
                                    game_over = False

                                if e.key == p.K_r:  # reset the game when 'r' is pressed
                                    game_state = ChessEngine.GameState()
                                    valid_moves = game_state.getValidMoves()
                                    square_selected = ()
                                    player_clicks = []
                                    move_made = False
                                    game_over = False

                        if move_made:
                            valid_moves = game_state.getValidMoves()
                            move_made = False

                        drawGameState(screen, game_state, valid_moves, square_selected)

                        if game_state.checkmate:
                            game_over = True
                            if game_state.white_to_move:
                                drawEndGameText(screen, "Black wins by checkmate")
                            else:
                                drawEndGameText(screen, "White wins by checkmate")

                        elif game_state.stalemate:
                            game_over = True
                            drawEndGameText(screen, "Stalemate")

                        clock.tick(MAX_FPS)
                        p.display.flip()
        mouse = p.mouse.get_pos()
        if BOARD_WIDTH / 2 <= mouse[0] <= BOARD_WIDTH / 2 + 140 and BOARD_HEIGHT / 2 <= mouse[
            1] <= BOARD_HEIGHT / 2 + 40:
            p.draw.rect(screen, color_light, [BOARD_WIDTH / 2, BOARD_HEIGHT / 2, 140, 40])

        else:
            p.draw.rect(screen, color_dark, [BOARD_WIDTH / 2, BOARD_HEIGHT / 2, 140, 40])

            # superimposing the text onto our button
        screen.blit(text, (BOARD_WIDTH / 2 + 20, BOARD_HEIGHT / 2))

        # updates the frames of the game
        p.display.update()

def drawGameState(screen, game_state, valid_moves, square_selected):
    drawBoard(screen)
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("dark green")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlightSquares(screen, game_state, valid_moves, square_selected):
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):  # square_selected is a piece that can be moved
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))



def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


main()