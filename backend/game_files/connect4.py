from typing import Optional

# Initial game state
starting_game_state = [[" " for _ in range(7)] for _ in range(6)]

# Player symbols
player_symbols = ['X', 'O']


def is_valid_move(board, col: int) -> bool:
    """Check if a column has space"""
    if col < 0 or col >= 7:
        return False
    return board[0][col] == " "


def make_move(board, col: int, symbol: str):
    """Make a move and return success"""
    if not is_valid_move(board, col):
        return (True, board)
    
    # Drop piece
    for row in reversed(board):
        if row[col] == " ":
            row[col] = symbol
            break
    
    return (False, board)

def check_winner(board) -> Optional[str]:
    """Check for a winner in Connect 4. Returns 'X', 'O', 'draw', or None"""
    rows, cols = 6, 7
    
    # Check horizontal
    for r in range(rows):
        for c in range(cols - 3):
            if board[r][c] != " " and all(board[r][c+i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check vertical
    for r in range(rows - 3):
        for c in range(cols):
            if board[r][c] != " " and all(board[r+i][c] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check diagonal (down-right)
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] != " " and all(board[r+i][c+i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check diagonal (down-left)
    for r in range(rows - 3):
        for c in range(3, cols):
            if board[r][c] != " " and all(board[r+i][c-i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check for draw
    if all(board[0][c] != " " for c in range(cols)):
        return "draw"
    
    return None
