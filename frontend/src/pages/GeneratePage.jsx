import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Added for redirection
import { apiGenerateStudySet } from '../api/apiClient'; // Import REAL API
import LoadingSpinner from '../components/LoadingSpinner';
import './GeneratePage.css';

function GeneratePage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate(); // Hook to redirect user
  
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
    
    // Prepare the form data for the backend
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // 1. Call the Real Backend
      console.log("Sending PDF to AI...");
      const newStudySet = await apiGenerateStudySet(formData);
      
      console.log("AI Generation Complete:", newStudySet);
      
      // 2. Redirect to the dashboard to see the new set
      // (Or we could redirect straight to study mode: `/study/${newStudySet.id}`)
      navigate('/'); 
      
    } catch (error) {
      console.error("Error generating flashcards:", error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
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
        {isLoading ? "AI is processing (this may take 30s)..." : "Generate Flashcards"}
      </button>

      {isLoading && (
        <div className="loading-container">
            <LoadingSpinner />
            <p className="loading-text">Analyzing your PDF...</p>
            <p className="loading-subtext">Extracting topics, generating flashcards, and building quizzes.</p>
        </div>
      )}
    </div>
  );
}

export default GeneratePage;