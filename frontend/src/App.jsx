
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import HomePage from "./HomePage";
import AllQuizPage from './AllQuizPage.jsx';
import ThemePage from './ThemePage.jsx';
import SignIn from './SignIn.jsx';
import SignUp from './SignUp.jsx';
import NotFound from './NotFound.jsx';
import { AuthProvider } from './AuthContext';
import Navbar from './Navbar';
import ResetPassword from './ResetPassword.jsx';
import SetNewPassword from './SetNewPassword.jsx';
import Settings from './Settings.jsx';
import MyQuizzes from './MyQuizzes.jsx';
import MyFavorites from './MyFavorites.jsx';
import Ranking from './Ranking.jsx';
import MyScores from './MyScores.jsx';
import QuizStart from './QuizStart.jsx';
import CreateQuiz from './CreateQuiz.jsx';

function App() {

  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/all-quiz" element={<AllQuizPage />} />
          <Route path="/theme/:themeName" element={<ThemePage />} />
          <Route path="sign-in" element={<SignIn />} />
          <Route path="sign-up" element={<SignUp />} />
          <Route path="settings" element={<Settings />} />
          <Route path="reset-password" element={<ResetPassword />} />
          <Route path="/reset-password/:token" element={<SetNewPassword />} />
          <Route path="my-quizzes" element={<MyQuizzes />} />
          <Route path="/my-favorites" element={<MyFavorites />} />
          <Route path="/ranking" element={<Ranking />} />
          <Route path="/my-scores" element={<MyScores />} />
          <Route path="/quiz/:quiz_id" element={<QuizStart />} />
          <Route path="create-quiz" element={<CreateQuiz />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App
