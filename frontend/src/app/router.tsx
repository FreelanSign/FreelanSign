import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import LoginPage from '../interface/pages/LoginPage';
import RegisterPage from '../interface/pages/RegisterPage';
import DashboardPage from '../interface/pages/DashboardPage';
import { useAuth } from './providers/AuthProvider';
import ProfilePage from '../interface/pages/ProfilePage';
import ProfileEditPage from '../interface/pages/ProfileEditPage';

/** Route protégée très simple */
function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div>Chargement…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/dashboard" replace /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/profile', element: <Protected><ProfilePage /></Protected>}, // route protégée pour le profil
  { path: '/profile/edit', element: <Protected><ProfileEditPage /></Protected>},
  {
    path: '/dashboard',
    element: (
      <Protected>
        <DashboardPage />
      </Protected>
    ),
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
