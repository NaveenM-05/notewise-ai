import React, { useState } from 'react';
import Flashcard from '../components/Flashcard';
import { generateFlashcards_FAKE } from '../api/mockApi';
import './GeneratePage.css';

function GeneratePage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [flashcards, setFlashcards] = useState([]);
  
  const handleFileSelect = (file) => {
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
      if (file) alert("Please select a PDF file.");
    }
  };
  
  const handleDragEvents = (e, isOver) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(isOver);
  };

  const handleDrop = (e) => {
    handleDragEvents(e, false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };
  
  const handleGenerate = async () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }
    setIsLoading(true);
    setFlashcards([]);
    const data = await generateFlashcards_FAKE(selectedFile);
    setFlashcards(data.flashcards);
    setIsLoading(false);
  };

  return (
    <div className="generate-page">
      <h1>Generate New Study Set</h1>
      <p>Drop your PDF notes into the zone below to get started.</p>

      <div 
        className={`drop-zone ${isDragOver ? 'drag-over' : ''}`}
        onClick={() => document.getElementById('fileInput').click()}
        onDragOver={(e) => handleDragEvents(e, true)}
        onDragLeave={(e) => handleDragEvents(e, false)}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          id="fileInput" 
          accept=".pdf" 
          hidden 
          onChange={(e) => handleFileSelect(e.target.files[0])}
        />
        {selectedFile ? <p>{selectedFile.name}</p> : <p>Drag & Drop PDF Here, or Click to Select</p>}
      </div>
      
      <button onClick={handleGenerate} disabled={isLoading || !selectedFile}>
        {isLoading ? "Generating..." : "Generate Flashcards"}
      </button>

      <div className="results-container">
        {isLoading && <p className="loading-text">AI is thinking...</p>}
        {flashcards.length > 0 && (
          <div className="flashcards-grid">
            {flashcards.map((card, index) => (
              <Flashcard key={index} question={card.question} answer={card.answer} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default GeneratePage;
