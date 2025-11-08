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

// Authentication API calls
export const authAPI = {
  // Login user
  login: async (email: string, password: string) => {
    // TODO: Replace with actual API call
    // return apiFetch('/auth/login', {
    //   method: 'POST',
    //   body: JSON.stringify({ email, password }),
    // });

    // Placeholder: simulate API delay
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password) {
          resolve({
            user: {
              id: '1',
              email: email,
              name: 'Test User',
            },
            token: 'fake-jwt-token-' + Date.now(),
          });
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 500);
    });
  },

  // Register new user
  signup: async (email: string, password: string, name: string) => {
    // TODO: Replace with actual API call
    // return apiFetch('/auth/signup', {
    //   method: 'POST',
    //   body: JSON.stringify({ email, password, name }),
    // });

    // Placeholder: simulate API delay
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password && name) {
          resolve({
            user: {
              id: '1',
              email: email,
              name: name,
            },
            token: 'fake-jwt-token-' + Date.now(),
          });
        } else {
          reject(new Error('Invalid signup data'));
        }
      }, 500);
    });
  },

  // Logout user
  logout: async () => {
    // TODO: Replace with actual API call
    // return apiFetch('/auth/logout', { method: 'POST' });

    // Placeholder
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 200);
    });
  },
};


  export const getGames =  async (setGames: (games: Game[]) => void) => {

    const games = await apiFetch('/api/games');
    setGames(games);
  }

