# connect4.py

def check_win(board):
    """
    Given a Connect 4 board as a list of lists with:
        0 = empty
        1 = Player 1
        2 = Player 2
    Return:
        1 if Player 1 wins
        2 if Player 2 wins
        0 if no win
    """
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    
    # Directions to check: (row_step, col_step)
    directions = [
        (0, 1),   # Horizontal →
        (1, 0),   # Vertical ↓
        (1, 1),   # Diagonal down-right ↘
        (1, -1)   # Diagonal down-left ↙
    ]
    
    for r in range(rows):
        for c in range(cols):
            player = board[r][c]
            if player == 0:
                continue  # Only check from a player's piece
            
            for dr, dc in directions:
                count = 0
                for i in range(4):  # Check 4 spots in this direction
                    nr, nc = r + dr*i, c + dc*i
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player:
                        count += 1
                    else:
                        break
                
                if count == 4:
                    return player  # 1 or 2
    
    return 0  # No winner


if __name__ == "__main__":
    # Example board for quick test
    sample_board = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0],
        [0, 0, 1, 2, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1],
        [2, 2, 2, 1, 0, 0, 0],
    ]
    
    winner = check_win(sample_board)
    print("Winner:", winner)  # Expected: Winner: 2 (horizontal bottom row)