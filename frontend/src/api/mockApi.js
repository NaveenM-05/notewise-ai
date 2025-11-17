// This file simulates a real backend API for frontend-first development.

// --- USER AUTHENTICATION ---
export const login_FAKE = async (email, password) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  if (email === "user@test.com" && password === "password") {
    return { token: "fake-jwt-token", user: { name: "Test User" } };
  }
  throw new Error("Invalid credentials");
};

// --- STUDY SETS ---
const MOCK_STUDY_SETS = [
    { id: '1', title: 'Biology Chapter 4', cardCount: 25 },
    { id: '2', title: 'Economics Supply & Demand', cardCount: 15 },
    { id: '3', title: 'Intro to Python OOP', cardCount: 30 },
];

export const getStudySets_FAKE = async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return [];
};

// --- GENERATION ---
export const generateFlashcards_FAKE = async (file) => {
    await new Promise(resolve => setTimeout(resolve, 2500));
    console.log("Simulating generation for file:", file.name);
    return {
        flashcards: [
            { id: 'f1', question: "What is Drag and Drop?", answer: "An intuitive way for users to select files." },
            { id: 'f2', question: "What is a Mock API?", answer: "A fake API that mimics a real backend, allowing the frontend to be developed independently." },
            { id: 'f3', question: "Why is frontend-first useful?", answer: "It allows for rapid prototyping and user feedback before backend development." },
        ]
    };
};

// --- STUDY SESSION ---
const MOCK_FLASHCARDS_FOR_SET = [
    { id: 'c1', question: "What is Mitochondria?", answer: "The powerhouse of the cell." },
    { id: 'c2', question: "What is Photosynthesis?", answer: "The process by which plants use sunlight to synthesize foods from carbon dioxide and water." },
    { id: 'c3', question: "What is DNA?", answer: "Deoxyribonucleic acid, a self-replicating material present in nearly all living organisms as the main constituent of chromosomes." },
];

export const getFlashcardsForSet_FAKE = async (setId) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    console.log("Fetching cards for set ID:", setId);
    return MOCK_FLASHCARDS_FOR_SET;
};

// --- APPLICATION ARENA ---
export const getArenaChallenge_FAKE = async (setId) => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    console.log("Generating challenge for set ID:", setId);
    return {
        challenge: "A new toxin is discovered that specifically disables the enzyme responsible for Step 3 of the Krebs cycle. Based on your notes, what immediate metabolic consequences would you predict for a cell, and why?",
        idealAnswer: "The immediate consequence would be the accumulation of the substrate for the disabled enzyme (isocitrate) and a deficit of all subsequent products, including α-ketoglutarate, NADH, and ATP. This would halt the Krebs cycle, drastically reducing the cell's energy production capacity."
    };
};
export const getTodaysReview_FAKE = async () => {
  // Simulate a network call
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Return a mock list of items due today
  return [
    { setId: '1', title: 'Biology Chapter 4', dueCardCount: 8 },
    { setId: '3', title: 'Intro to Python OOP', dueCardCount: 12 },
  ];
};
export const saveReview_FAKE = async (cardId, difficulty) => {
  // Simulate the time it takes to save to the database
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // In a real app, the backend would use this to update the card's next review date
  console.log(`Saved review for card ${cardId} with difficulty: ${difficulty}`);
  return { success: true };
};

// ... (at the end of the file) ...

export const getQuizData_FAKE = async (setId) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  console.log("Fetching quiz for set ID:", setId);
  return [
    {
      question: "What is the primary function of Mitochondria?",
      options: ["Photosynthesis", "Cellular Respiration", "Protein Synthesis", "Cell Division"],
      correctAnswer: "Cellular Respiration"
    },
    {
      question: "What is the main output of the Krebs cycle?",
      options: ["NADH and FADH2", "Oxygen", "Glucose", "Water"],
      correctAnswer: "NADH and FADH2"
    },
    {
      question: "Where does Glycolysis take place in the cell?",
      options: ["Nucleus", "Mitochondrial Matrix", "Cytoplasm", "Endoplasmic Reticulum"],
      correctAnswer: "Cytoplasm"
    }
  ];
};