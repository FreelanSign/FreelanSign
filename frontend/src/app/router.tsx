import React from 'react';
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from 'react-router-dom';
import RequestPasswordResetPage from '../interface/pages/Auth/request-password-reset';
import ResetPasswordPage from '../interface/pages/Auth/reset-password';
import ThemesCreatePage from '../interface/pages/Branding/ThemesCreatePage';
import ThemesEditPage from '../interface/pages/Branding/ThemesEditPage';
import ThemesListPage from '../interface/pages/Branding/ThemesListPage';
import DashboardPage from '../interface/pages/DashboardPage';
import LoginPage from '../interface/pages/Login/LoginPage';
import ProfileEditPage from '../interface/pages/Profile/ProfileEditPage';
import ProfilePage from '../interface/pages/Profile/ProfilePage';
import QuoteCreatePage from '../interface/pages/Quote/QuoteCreatePage';
import QuoteDetailPage from '../interface/pages/Quote/QuoteDetailPage';
import QuoteEditPage from '../interface/pages/Quote/QuoteEditPage';
import QuotesListPage from '../interface/pages/Quote/QuoteListPage';
import RegisterPage from '../interface/pages/Register/RegisterPage';
import { useAuth } from './providers/AuthProvider';

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
  {
    path: '/auth/request-password-reset',
    element: <RequestPasswordResetPage />,
  },
  { path: '/auth/reset-password', element: <ResetPasswordPage /> },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
