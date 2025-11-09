from typing import Optional

# Initial game state (3x3)
starting_game_state = [[" " for _ in range(3)] for _ in range(3)]

# Player symbols
player_symbols = ['X', 'O']


def is_valid_move(board, pos: int) -> bool:
    """
    Check if a move is valid.
    For Tic Tac Toe, pos is 0-8 representing cells left→right, top→bottom.
    """
    if pos < 0 or pos > 8:
        return False
    
    row, col = divmod(pos, 3)
    return board[row][col] == " "


def make_move(board, pos: int, symbol: str) -> bool:
    """Place the symbol if the move is valid. Return True if move made."""
    if not is_valid_move(board, pos):
        return False
    
    row, col = divmod(pos, 3)
    board[row][col] = symbol
    return True


def check_winner(board) -> Optional[str]:
    """Check for a winner. Returns 'X', 'O', 'draw', or None"""
    lines = []

    # Rows & Columns
    for i in range(3):
        lines.append(board[i])                      # row i
        lines.append([board[0][i], board[1][i], board[2][i]])  # col i

    # Diagonals
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    # Check winners
    for line in lines:
        if line[0] != " " and line.count(line[0]) == 3:
            return line[0]

    # Check for draw (all cells filled)
    if all(board[r][c] != " " for r in range(3) for c in range(3)):
        return "draw"

    return None