"""
Tic-Tac-Toe Game Module
"""

MIN_PLAYERS = 2


def create_initial_board():
    """Create empty 3x3 board"""
    return [[" " for _ in range(3)] for _ in range(3)]


def get_player_symbol(player_index: int) -> str:
    """Get symbol for player at given index"""
    return "X" if player_index == 0 else "O"


def validate_move(board, move, symbol) -> tuple[bool, str]:
    """
    Validate a Tic-Tac-Toe move
    Move format: {"row": 0-2, "col": 0-2} or [row, col]
    """
    # Handle dict format
    if isinstance(move, dict):
        row = move.get("row")
        col = move.get("col")
    # Handle list/tuple format
    elif isinstance(move, (list, tuple)) and len(move) == 2:
        row, col = move
    else:
        return False, "Move must be {row, col} or [row, col]"
    
    # Validate coordinates
    if not isinstance(row, int) or not isinstance(col, int):
        return False, "Row and col must be integers"
    
    if row < 0 or row > 2 or col < 0 or col > 2:
        return False, "Row and col must be 0-2"
    
    # Check if cell is empty
    if board[row][col] != " ":
        return False, f"Cell ({row}, {col}) is already occupied"
    
    return True, ""


def apply_move(board, move, symbol):
    """Apply move to board"""
    if isinstance(move, dict):
        row = move["row"]
        col = move["col"]
    else:
        row, col = move
    
    board[row][col] = symbol


def check_winner(board) -> str | None:
    """
    Check for winner in Tic-Tac-Toe
    Returns: 'X', 'O', 'draw', or None
    """
    # Check rows
    for row in board:
        if row[0] != " " and row[0] == row[1] == row[2]:
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] != " " and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] != " " and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    
    if board[0][2] != " " and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    # Check for draw (no empty cells)
    if all(cell != " " for row in board for cell in row):
        return "draw"
    
    return None