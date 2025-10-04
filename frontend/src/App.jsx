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
  const [notes, setNotes] = useState(''); // For the textarea
  const [selectedFile, setSelectedFile] = useState(null); // For the PDF file
  const [flashcards, setFlashcards] = useState([]); // For the results
  const [isLoading, setIsLoading] = useState(false); // For the loading message

  // We will create the handleGenerate function next
  const handleGenerate = async () => {
  if (!notes && !selectedFile) {
    alert("Please enter some text or upload a PDF file.");
    return;
  }
  
  setIsLoading(true);
  setFlashcards([]); // Clear previous results

  const formData = new FormData();
  if (selectedFile) {
    formData.append("file", selectedFile);
  } else {
    formData.append("text", notes);
  }

  try {
    // Call the FAKE function for now
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
      <p>Upload your notes as text or a PDF to generate flashcards instantly.</p>

      <div className="input-container">
        <textarea
          value={notes}
          onChange={(e) => {
            setNotes(e.target.value);
            setSelectedFile(null); // Clear file if user types
          }}
          placeholder="Paste your notes here..."
          disabled={isLoading}
        />
        <span className="or-divider">OR</span>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => {
            setSelectedFile(e.target.files[0]);
            setNotes(''); // Clear text if user uploads file
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