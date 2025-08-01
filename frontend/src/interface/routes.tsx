import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import UsersPage from './pages/UsersPage';

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/users" element={<UsersPage />} />
        <Route path="*" element={<Navigate to="/users" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
