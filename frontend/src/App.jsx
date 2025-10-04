import { useState } from 'react';
import './App.css';

// This is a temporary function that mimics the real backend
const generateFlashcards_FAKE = async (formData) => {
  console.log("Sending data to fake API...");
  
  // Simulate a network delay of 2 seconds
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Return fake data that matches the API contract
  return {
    flashcards: [
      { question: "What is a fake API?", answer: "A function that mimics a real backend response for frontend development." },
      { question: "Why is it useful?", answer: "It allows the frontend to be built without waiting for the backend to be ready." }
    ]
  };
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null); // For the PDF file
  const [flashcards, setFlashcards] = useState([]); // For the results
  const [isLoading, setIsLoading] = useState(false); // For the loading message

  const handleGenerate = async () => {
    // Simplified check: only looks for a file
    if (!selectedFile) {
      alert("Please upload a PDF file to continue.");
      return;
    }
    
    setIsLoading(true);
    setFlashcards([]); // Clear previous results

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // Call the FAKE function for now. Later, you'll swap this with the real 'fetch' call.
      const data = await generateFlashcards_FAKE(formData);
      setFlashcards(data.flashcards);
    } catch (error) {
      console.error("Error generating flashcards:", error);
      alert("There was an error generating your flashcards.");
    }

    setIsLoading(false);
  };

  return (
    <div className="App">
      <h1>NoteWise AI 🧠</h1>
      <p>Upload your PDF notes to generate flashcards instantly.</p>

      {/* Simplified input container */}
      <div className="input-container">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => {
            setSelectedFile(e.target.files[0]);
          }}
          disabled={isLoading}
        />
      </div>

      <button onClick={handleGenerate} disabled={isLoading}>
        {isLoading ? 'Generating...' : 'Generate Flashcards'}
      </button>

      <div className="results-container">
        {isLoading && <p className="loading-text">AI is thinking...</p>}
        {flashcards.length > 0 && !isLoading && (
          <div className="flashcards-grid">
            {flashcards.map((card, index) => (
              <div className="flashcard" key={index}>
                <h4>{card.question}</h4>
                <p>{card.answer}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;