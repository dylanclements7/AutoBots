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

interface GameSummary {
  title: string;
  difficulty: string;
  game_summary: string;
  objective: string;
  player_symbols: string[];
}

interface ApiResponse {
  games: GameSummary[];
  gameData: any[];
}

export const getGames = async (
  setData: (data: ApiResponse) => void,
  setLoading: (loading: boolean) => void
) => {
  try {
    const response = await apiFetch('/api/games');
    console.log('API response:', response);

    // Ensure we have both arrays
    const data: ApiResponse = {
      games: response.games || [],
      gameData: response.gameData || []
    };

    setData(data);
  } catch (err) {
    console.error('Error fetching games:', err);
  } finally {
    setLoading(false);
  }
};

export const getQueue = async (gameName: string, setQueue: (queue: string[]) => void, setLoading: (loading: boolean) => void) => {
    const queue = await apiFetch(`/api/lobby/${gameName}/status`);
    console.log('queue', queue);
    setQueue(queue?.players)
    setLoading(false)
}