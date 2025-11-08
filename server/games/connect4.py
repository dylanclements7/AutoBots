"""
Connect 4 Game Module
Each game module must implement:
- MIN_PLAYERS: int
- create_initial_board() -> board
- get_player_symbol(player_index: int) -> str
- validate_move(board, move, symbol) -> (bool, str)
- apply_move(board, move, symbol) -> None
- check_winner(board) -> Optional[str]
"""

MIN_PLAYERS = 2
ROWS = 6
COLS = 7


def create_initial_board():
    """Create empty Connect 4 board"""
    return [[" " for _ in range(COLS)] for _ in range(ROWS)]


def get_player_symbol(player_index: int) -> str:
    """Get symbol for player at given index"""
    return "X" if player_index == 0 else "O"


def validate_move(board, move, symbol) -> tuple[bool, str]:
    """
    Validate a Connect 4 move
    Move format: column number (0-6)
    Returns: (is_valid, error_message)
    """
    # Check move is an integer
    if not isinstance(move, int):
        return False, f"Move must be integer, got {type(move)}"
    
    # Check column in range
    if move < 0 or move >= COLS:
        return False, f"Column must be 0-{COLS-1}, got {move}"
    
    # Check column not full
    if board[0][move] != " ":
        return False, f"Column {move} is full"
    
    return True, ""


def apply_move(board, move, symbol):
    """
    Apply a move to the board (mutates board)
    Move format: column number
    """
    col = move
    
    # Drop piece to lowest available row
    for row in reversed(board):
        if row[col] == " ":
            row[col] = symbol
            break


def check_winner(board) -> str | None:
    """
    Check for winner in Connect 4
    Returns: 'X', 'O', 'draw', or None
    """
    # Check horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] != " " and all(board[r][c+i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] != " " and all(board[r+i][c] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check diagonal (down-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] != " " and all(board[r+i][c+i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check diagonal (down-left)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if board[r][c] != " " and all(board[r+i][c-i] == board[r][c] for i in range(4)):
                return board[r][c]
    
    # Check for draw (top row full)
    if all(board[0][c] != " " for c in range(COLS)):
        return "draw"
    
    return None