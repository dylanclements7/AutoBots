// API base URL - replace with your actual API endpoint
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Generic fetch wrapper
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'API request failed');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}


  export const getGames =  async (setGames: (games: Game[]) => void, setLoading: (loading: boolean) => void) => {

    const games = await apiFetch('/api/games');
    console.log('games', games)
    setGames(games);
    setLoading(false)
    
  }

export const getQueue = async (gameName: string, setQueue: (queue: string[]) => void, setLoading: (loading: boolean) => void) => {
    const queue = await apiFetch(`/api/lobby/${gameName}/status`);
    console.log('queue', queue);
    setQueue(queue?.players)
    setLoading(false)
}

export interface GameData {
  title: string;
  objective: string;
  game_summary: string;
  win_condition: string;
  task: string;
  bot_input_format: string;
  bot_output_format: string;
  state_format: any;
  player_symbols: string[];
  difficulty: string;
  code: string;
  html: string;
}

export const addGameToDb = async (gameData: GameData) => {
  try {
    const response = await apiFetch('/add_game_to_db', {
      method: 'POST',
      body: JSON.stringify(gameData),
    });
    return response;
  } catch (error) {
    console.error('Error adding game to database:', error);
    throw error;
  }
}