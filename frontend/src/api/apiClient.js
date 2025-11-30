const API_BASE_URL = 'http://127.0.0.1:8000';

const getToken = () => localStorage.getItem('jwt_token');

const request = async (endpoint, method, body = null) => {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config = { method, headers };
  if (body) config.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An API error occurred');
  }
  const text = await response.text();
  return text ? JSON.parse(text) : {};
};

// --- AUTH ---
export const apiLogin = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email); 
  formData.append('password', password);
  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });
  if (!response.ok) throw new Error('Login failed');
  return response.json();
};

export const apiRegister = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error('Registration failed');
  return response.json();
};

// --- DASHBOARD ---
export const apiGetStudySets = () => request('/api/study-sets', 'GET');
export const apiGetTodaysReview = () => request('/api/reviews/today', 'GET');
export const apiDeleteStudySet = (setId) => request(`/api/study-sets/${setId}`, 'DELETE');

// --- GENERATION ---
export const apiGenerateStudySet = (formData) => {
  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return fetch(`${API_BASE_URL}/api/generate`, { method: 'POST', headers, body: formData })
    .then(async res => {
      if (!res.ok) throw new Error('Generation failed');
      return res.json();
    });
};

// --- STUDY & REVIEW ---
export const apiGetFlashcards = (setId, mode = "all") => request(`/api/study-set/${setId}/flashcards?mode=${mode}`, 'GET');
export const apiSaveReview = (cardId, difficulty) => request('/api/flashcards/review', 'POST', { card_id: cardId, difficulty });

// --- QUIZ ---
export const apiGetQuiz = (setId) => request(`/api/quiz/${setId}`, 'GET');
export const apiSubmitQuiz = (setId, answers) => request('/api/quiz/complete', 'POST', { set_id: setId, answers });
// NEW: Regenerate Quiz
export const apiRegenerateQuiz = (setId) => request(`/api/quiz/regenerate/${setId}`, 'POST');

// --- ARENA ---
export const apiGetArenaChallenge = (setId) => request(`/api/arena/${setId}`, 'GET');
// UPDATED: Sends user_response text
export const apiSubmitArena = (setId, challengeId, userResponse) => {
    return request('/api/arena/submit', 'POST', { 
        set_id: setId, 
        challenge_id: challengeId, 
        user_response: userResponse 
    });
};

// Add this near the other Arena functions
export const apiRegenerateArena = (setId) => {
    return request(`/api/arena/regenerate/${setId}`, 'POST');
};