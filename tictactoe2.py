import pygame
import sys
from functools import lru_cache

# Initialize pygame
pygame.init()

# Colors and settings
WHITE = (255, 255, 255)
LINE_COLOR = (23, 85, 85)
CROSS_COLOR = (242, 85, 96)
CIRCLE_COLOR = (85, 170, 85)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tic Tac Toe')

BOARD_SIZE = 4


def board_to_tuple(board):
    return tuple(tuple(row) for row in board)


def draw_board():
    for row in range(1, BOARD_SIZE):
        pygame.draw.line(SCREEN, LINE_COLOR, (SCREEN_WIDTH / BOARD_SIZE * row, 0),
                         (SCREEN_WIDTH / BOARD_SIZE * row, SCREEN_HEIGHT), 7)
        pygame.draw.line(SCREEN, LINE_COLOR, (0, SCREEN_HEIGHT / BOARD_SIZE * row),
                         (SCREEN_WIDTH, SCREEN_HEIGHT / BOARD_SIZE * row), 7)


draw_board()

# Create the game board
board = [['' for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]


# def check_winner(board, player):
#     for i in range(BOARD_SIZE):
#         if board[i][0] == board[i][1] == board[i][2] == player:
#             return True
#         if board[0][i] == board[1][i] == board[2][i] == player:
#             return True
#     if board[0][0] == board[1][1] == board[2][2] == player:
#         return True
#     if board[0][2] == board[1][1] == board[2][0] == player:
#         return True
#     return False

def check_winner(board, player):
    BOARD_SIZE = 4
    WIN_COUNT = 3

    # Helper function to check for 3 in a row in a list
    def check_consecutive(lst, player):
        count = 0
        for item in lst:
            if item == player:
                count += 1
                if count == WIN_COUNT:
                    return True
            else:
                count = 0
        return False

    # Check rows and columns
    for i in range(BOARD_SIZE):
        if check_consecutive(board[i], player):  # Check rows
            return True
        if check_consecutive([board[j][i] for j in range(BOARD_SIZE)], player):  # Check columns
            return True

    # Check diagonals
    main_diag = [board[i][i] for i in range(BOARD_SIZE)]
    secondary_diag = [board[i][BOARD_SIZE - 1 - i] for i in range(BOARD_SIZE)]

    if check_consecutive(main_diag, player):  # Check main diagonal
        return True
    if check_consecutive(secondary_diag, player):  # Check secondary diagonal
        return True

    return False


def all_possible_lines(board):
    # Rows, columns, diagonals
    lines = [row for row in board] + [[board[i][j]
                                       for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)]
    lines.append([board[i][i] for i in range(BOARD_SIZE)])
    lines.append([board[i][BOARD_SIZE - 1 - i] for i in range(BOARD_SIZE)])
    return lines


def evaluate_board(board):
    score = 0

    # Check for lines of 3, 2, and 1
    for line in all_possible_lines(board):
        if line.count('O') == 3 and line.count('') == 1:
            score += 5
        elif line.count('X') == 3 and line.count('') == 1:
            score -= 10

        if line.count('O') == 2 and line.count('') == 2:
            score += 2
        elif line.count('X') == 2 and line.count('') == 2:
            score -= 5

        # New conditions for lines of 1
        if line.count('O') == 1 and line.count('') == 3:
            score += 1
        elif line.count('X') == 1 and line.count('') == 3:
            score -= 2  # prioritize blocking the player even when there's only one mark

    # Check center squares
    center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    for pos in center_positions:
        if board[pos[0]][pos[1]] == 'O':
            score += 2
        elif board[pos[0]][pos[1]] == 'X':
            score -= 3  # prioritize blocking the player a bit more for center squares

    return score


@lru_cache(maxsize=None)
def minimax(board_tuple, depth, is_maximizing, alpha, beta):
    board = [list(row) for row in board_tuple]

    score = evaluate_board(board)
    if score != 0:
        return score

    if check_winner(board, 'X'):
        return -10 + depth  # make the algorithm choose the quickest win
    if check_winner(board, 'O'):
        return 10 - depth  # make the algorithm delay the loss
    # if check_winner(board, 'X'):
    #     return -10
    # if check_winner(board, 'O'):
    #     return 10
    if all(cell != '' for row in board for cell in row):
        return 0

    if is_maximizing:
        max_eval = float('-inf')
        should_break = False
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == '':
                    board[i][j] = 'O'
                    eval = minimax(board_to_tuple(board),
                                   depth + 1, False, alpha, beta)
                    board[i][j] = ''
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        should_break = True
                        break
            if should_break:
                break
        return max_eval
    else:
        min_eval = float('inf')
        should_break = False
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == '':
                    board[i][j] = 'X'
                    eval = minimax(board_to_tuple(board),
                                   depth + 1, True, alpha, beta)
                    board[i][j] = ''
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        should_break = True
                        break
            if should_break:
                break
        return min_eval


def best_move(board):
    best_score = float('-inf')
    move = (-1, -1)
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == '':
                board[i][j] = 'O'
                score = minimax(board_to_tuple(board), 0, False,
                                float('-inf'), float('inf'))
                board[i][j] = ''
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move


def update_board(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 'X':
                pygame.draw.line(SCREEN, CROSS_COLOR,
                                 (int(col * 100 + 20), int(row * 100 + 20)),
                                 (int(col * 100 + 80), int(row * 100 + 80)), 40)
                pygame.draw.line(SCREEN, CROSS_COLOR,
                                 (int(col * 100 + 80), int(row * 100 + 20)),
                                 (int(col * 100 + 20), int(row * 100 + 80)), 40)
            elif board[row][col] == 'O':
                pygame.draw.circle(SCREEN, CIRCLE_COLOR,
                                   (int(col * 100 + 50), int(row * 100 + 50)), 40)
    pygame.display.update()


def board_full(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == '':
                return False
    return True


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            clicked_row = int(mouseY // 100)
            clicked_col = int(mouseX // 100)
            if board[clicked_row][clicked_col] == '':
                board[clicked_row][clicked_col] = 'X'
                if board_full(board):
                    print('Draw')
                    pygame.quit()
                    sys.exit()
                if not check_winner(board, 'X'):
                    ai_move = best_move(board)
                    board[ai_move[0]][ai_move[1]] = 'O'
                update_board(board)

                # You can add additional logic here to show who wins and to reset the game if needed
        if check_winner(board, 'X'):
            print('X wins')
            # save game board as an image
            pygame.image.save(SCREEN, 'tic_tac_toe.png')
            pygame.quit()
            sys.exit()

        if check_winner(board, 'O'):
            print('O wins')
            # save game board as an image
            pygame.image.save(SCREEN, 'tic_tac_toe.png')
            pygame.quit()
            sys.exit()

        if board_full(board):
            print('Draw')
            # save game board as an image
            pygame.image.save(SCREEN, 'tic_tac_toe.png')
            pygame.quit()
            sys.exit()

    pygame.display.update()
