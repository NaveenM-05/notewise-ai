// frontend/src/api/apiClient.js

// This is the base URL of your partner's backend server
const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * A private helper function to make API requests.
 * It automatically adds the JWT token to the headers.
 */
const request = async (endpoint, method, body = null) => {
  // 1. Get the token from the browser's memory
  const token = localStorage.getItem('jwt_token'); 

  const headers = {
    'Content-Type': 'application/json',
  };

  // 2. If the token exists, add it to the Authorization header
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

  // 3. Make the actual request
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // 4. Handle errors
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An API error occurred');
  }

  // 5. Return the JSON data if the request was successful
  // Use .text() first to handle potentially empty responses
  const responseText = await response.text();
  return responseText ? JSON.parse(responseText) : {};
};

/**
 * ----------------------------------------------------
 * API FUNCTIONS
 * ----------------------------------------------------
 */

// --- AUTH ---

export const apiLogin = async (email, password) => {
  // 1. Create URLSearchParams to send data as 'application/x-www-form-urlencoded'
  const formData = new URLSearchParams();
  
  // 2. CRITICAL: FastAPI's OAuth2PasswordRequestForm expects 'username', not 'email'
  formData.append('username', email); 
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: 'POST',
    headers: { 
        // 3. Explicitly set the content type for Form Data
        'Content-Type': 'application/x-www-form-urlencoded' 
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    // Handle FastAPI validation errors (which can be arrays) or simple detail strings
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

// --- GENERATION ---
export const apiGenerateStudySet = (formData) => {
  // FormData requests are special and don't use the JSON helper
  // We need to manually get the token here
  const token = localStorage.getItem('jwt_token');
  
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  // NOTE: Do NOT set 'Content-Type' for FormData, the browser does it automatically with the boundary

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