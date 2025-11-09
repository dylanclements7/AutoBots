const boardDiv = document.getElementById('board');

// Initialize empty board
const board = Array.from({ length: 3 }, () => Array(3).fill(null));

function createBoard() {
  Array.from({ length: 3 })
    .flatMap((_, r) => Array.from({ length: 3 }).map((_, c) => ({ r, c })))
    .forEach(({ r, c }) => {
      const cell = document.createElement('div');
      cell.classList.add('cell');
      cell.dataset.row = r;
      cell.dataset.col = c;
      boardDiv.appendChild(cell);
    });
}

function renderBoard() {
  document.querySelectorAll('.cell').forEach(cell => {
    const r = parseInt(cell.dataset.row);
    const c = parseInt(cell.dataset.col);
    cell.textContent = board[r][c] || '';
  });
}


// Connect to server WebSocket
const ws = new WebSocket("ws://localhost:8000/ws/connect4/Alice");

ws.onopen = () => {
  console.log("Connected to WebSocket");
};

const handleServerMessage = async (data) => {
  if (data.type === 'board_update') {
    const newState = data.gameState;
    // Update local board state
    newState.forEach((row, r) => {
        row.forEach((cell, c) => {
            board[r][c] = cell === 1 ? 'X' : cell === 2 ? 'O' : null;
        });
    });
    renderBoard();
  }
}

// Initialize board in DOM
createBoard();