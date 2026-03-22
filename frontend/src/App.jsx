import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { NotificationsProvider } from './contexts/NotificationsContext';
import { ToastProvider } from './contexts/ToastContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Tournaments from './pages/Tournaments';
import Teams from './pages/Teams';
import MyTeams from './pages/MyTeams';
import CreateTeam from './pages/CreateTeam';
import TeamPublic from './pages/TeamPublic';
import ManageTeam from './pages/ManageTeam';
import Profile from './pages/Profile';
import ProfileEdit from './pages/ProfileEdit';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <ToastProvider>
          <NotificationsProvider>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/tournaments" element={<ProtectedRoute><Tournaments /></ProtectedRoute>} />
              <Route path="/teams" element={<ProtectedRoute><Teams /></ProtectedRoute>} />
              <Route path="/teams/my" element={<ProtectedRoute><MyTeams /></ProtectedRoute>} />
              <Route path="/teams/create" element={<ProtectedRoute><CreateTeam /></ProtectedRoute>} />
              <Route path="/teams/:slug/manage" element={<ProtectedRoute><ManageTeam /></ProtectedRoute>} />
              <Route path="/teams/:slug" element={<ProtectedRoute><TeamPublic /></ProtectedRoute>} />
              <Route path="/my-teams" element={<Navigate to="/teams/my" replace />} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/profile/edit" element={<ProtectedRoute><ProfileEdit /></ProtectedRoute>} />
              {/* Public profile route */}
              <Route path="/u/:username" element={<Profile />} />
            </Routes>
          </NotificationsProvider>
        </ToastProvider>
      </Router>
    </AuthProvider>
  );
}

export default App;
