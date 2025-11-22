import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MenuBar from './components/MenuBar';
import ProtectedRoute from './components/ProtectedRoute';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import GeneratePage from './pages/GeneratePage';
import StudyPage from './pages/StudyPage';
import ApplicationArenaPage from './pages/ApplicationArenaPage';
import LoginPage from './pages/LoginPage';
import QuizPage from './pages/QuizPage';
import './App.css'; // <-- CRITICAL IMPORT

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App"> {/* <-- CRITICAL CLASSNAME */}
          <MenuBar />
          <main className="content"> {/* <-- CRITICAL CLASSNAME */}
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path="/generate" element={<ProtectedRoute><GeneratePage /></ProtectedRoute>} />
              <Route path="/study/:setId" element={<ProtectedRoute><StudyPage /></ProtectedRoute>} />
              <Route path="/arena/:setId" element={<ProtectedRoute><ApplicationArenaPage /></ProtectedRoute>} />
              <Route path="/quiz/:setId" element={<ProtectedRoute><QuizPage /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;