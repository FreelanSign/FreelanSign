import React from 'react';
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from 'react-router-dom';
import LoginPage from '../interface/pages/Login/LoginPage';
import RegisterPage from '../interface/pages/Register/RegisterPage';
import DashboardPage from '../interface/pages/DashboardPage';
import { useAuth } from './providers/AuthProvider';
import ProfilePage from '../interface/pages/Profile/ProfilePage';
import ProfileEditPage from '../interface/pages/Profile/ProfileEditPage';
import QuoteCreatePage from '../interface/pages/Quote/QuoteCreatePage';
import QuotesListPage from '../interface/pages/Quote/QuoteListPage';
import QuoteDetailPage from '../interface/pages/Quote/QuoteDetailPage';
import QuoteEditPage from '../interface/pages/Quote/QuoteEditPage';
import ThemesListPage from '../interface/pages/Branding/ThemesListPage';
import ThemesCreatePage from '../interface/pages/Branding/ThemesCreatePage';
import ThemesEditPage from '../interface/pages/Branding/ThemesEditPage';

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
  {
    path: '/profile',
    element: (
      <Protected>
        <ProfilePage />
      </Protected>
    ),
  },
  {
    path: '/profile/edit',
    element: (
      <Protected>
        <ProfileEditPage />
      </Protected>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <Protected>
        <DashboardPage />
      </Protected>
    ),
  },
  {
    path: '/quotes/new',
    element: (
      <Protected>
        <QuoteCreatePage />
      </Protected>
    ),
  },
  {
    path: 'quotes',
    element: (
      <Protected>
        <QuotesListPage />
      </Protected>
    ),
  },
  {
    path: '/quotes/:id',
    element: <QuoteDetailPage />,
  },
  {
    path: '/quotes/:id/edit/',
    element: <QuoteEditPage />,
  },
  {
    path: '/branding/themes',
    element: (
      <Protected>
        <ThemesListPage />
      </Protected>
    ),
  },
  {
    path: '/branding/themes/new',
    element: (
      <Protected>
        <ThemesCreatePage />
      </Protected>
    ),
  },
  {
    path: '/branding/themes/:id/edit',
    element: (
      <Protected>
        <ThemesEditPage />
      </Protected>
    ),
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
