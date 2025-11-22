// frontend/src/api/apiClient.js

const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Helper to get token safely
 */
const getToken = () => {
  const token = localStorage.getItem('jwt_token');
  if (!token) {
    console.warn("Warning: No JWT token found in localStorage!");
  }
  return token;
};

/**
 * General request helper for JSON APIs
 */
const request = async (endpoint, method, body = null) => {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method: method,
    headers: headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An API error occurred');
  }

  const responseText = await response.text();
  return responseText ? JSON.parse(responseText) : {};
};

// --- AUTH ---

export const apiLogin = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email); 
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/x-www-form-urlencoded' 
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    const errorMessage = typeof errorData.detail === 'string' 
      ? errorData.detail 
      : 'Validation Error: Check input format';
    throw new Error(errorMessage);
  }

  return response.json();
};

export const apiRegister = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/register`, {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/json' 
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Registration failed');
  }

  return response.json();
};

// --- DASHBOARD ---
export const apiGetStudySets = () => {
  return request('/api/study-sets', 'GET');
};

export const apiGetTodaysReview = () => {
  return request('/api/reviews/today', 'GET');
};

// --- GENERATION (The Fix is Here) ---
export const apiGenerateStudySet = (formData) => {
  const token = getToken();
  
  // Debugging Log
  console.log("Generating Study Set with Token:", token ? "Token Exists" : "TOKEN MISSING");

  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else {
    // If we have no token, the backend will definitely reject this. 
    // We throw an error early to make debugging easier.
    return Promise.reject(new Error("No authentication token found. Please log in again."));
  }

  return fetch(`${API_BASE_URL}/api/generate`, {
    method: 'POST',
    headers: headers,
    body: formData,
  }).then(async res => {
      if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'Generation failed');
      }
      return res.json();
  });
};

// --- STUDY & QUIZ & ARENA ---
export const apiGetFlashcards = (setId) => {
  return request(`/api/study-set/${setId}/flashcards`, 'GET');
};

export const apiSaveReview = (cardId, difficulty) => {
  return request('/api/flashcards/review', 'POST', { card_id: cardId, difficulty: difficulty });
};

export const apiGetQuiz = (setId) => {
    return request(`/api/quiz/${setId}`, 'GET');
};

export const apiSubmitQuiz = (setId, score) => {
    return request('/api/quiz/complete', 'POST', { set_id: setId, score: score });
};

export const apiGetArenaChallenge = (setId) => {
    return request(`/api/arena/${setId}`, 'GET');
};

export const apiSubmitArena = (setId, challengeId, assessmentScore) => {
    return request('/api/arena/submit', 'POST', { set_id: setId, challenge_id: challengeId, self_score: assessmentScore });
};

export const apiLogTime = (setId, timeSpentMs) => {
    return request('/api/study/log-time', 'POST', { set_id: setId, time_spent_ms: timeSpentMs });
};