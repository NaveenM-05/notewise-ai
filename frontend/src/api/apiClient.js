// This is the base URL of your partner's future backend server
const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * A private helper function to make API requests.
 * It automatically adds the JWT token to the headers.
 */
const request = async (endpoint, method, body = null) => {
  // 1. Get the token from the browser's memory (which we'll save on login)
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
  // Use .text() for responses that might be empty
  const responseText = await response.text();
  return responseText ? JSON.parse(responseText) : {};
};

/**
 * ----------------------------------------------------
 * Now, we define all our API functions for the app to use.
 * These will replace your "mockApi.js" functions.
 * ----------------------------------------------------
 */

// --- AUTH ---
export const apiLogin = (email, password) => {
  // Login is special, it doesn't send a token
  return fetch(`${API_BASE_URL}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, password: password }),
  }).then(async res => {
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      return res.json(); // This will return { access_token: "...", token_type: "bearer" }
  });
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
  const token = localStorage.getItem('jwt_token');
  
  return fetch(`${API_BASE_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}` 
      // Do NOT set 'Content-Type' for FormData, the browser does it
    },
    body: formData,
  }).then(res => res.json());
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