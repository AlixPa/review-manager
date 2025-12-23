import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProfilePage from './pages/ProfilePage';
import ReviewsToDoPage from './pages/ReviewsToDoPage';
import ManageRequestsPage from './pages/ManageRequestsPage';
import CreateRequestPage from './pages/CreateRequestPage';
import RewardsPage from './pages/RewardsPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/todo" replace />} />
          <Route path="/todo" element={<ReviewsToDoPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/create" element={<CreateRequestPage />} />
          <Route path="/manage" element={<ManageRequestsPage />} />
          <Route path="/rewards" element={<RewardsPage />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

