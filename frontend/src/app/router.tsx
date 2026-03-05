import React from 'react';
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from 'react-router-dom';
import MainLayout from '../interface/layout/MainLayout';
import RequestPasswordResetPage from '../interface/pages/Auth/request-password-reset';
import ResetPasswordPage from '../interface/pages/Auth/reset-password';
import VerifyEmailPage from '../interface/pages/Auth/VerifyEmailPage';
import ThemesCreatePage from '../interface/pages/Branding/ThemesCreatePage';
import ThemesEditPage from '../interface/pages/Branding/ThemesEditPage';
import ThemesListPage from '../interface/pages/Branding/ThemesListPage';
import ClientsListPage from '../interface/pages/Client/ClientsListPage';
import ClientDetailPage from '../interface/pages/Client/ClientDetailPage';
import ClientEditPage from '../interface/pages/Client/ClientEditPage';
import DashboardPage from '../interface/pages/DashboardPage';
import LoginPage from '../interface/pages/Login/LoginPage';
import ProfileEditPage from '../interface/pages/Profile/ProfileEditPage';
import ProfilePage from '../interface/pages/Profile/ProfilePage';
import QuoteCreatePage from '../interface/pages/Quote/QuoteCreatePage';
import QuoteDetailPage from '../interface/pages/Quote/QuoteDetailPage';
import QuoteEditPage from '../interface/pages/Quote/QuoteEditPage';
import QuotesListPage from '../interface/pages/Quote/QuoteListPage';
import RegisterPage from '../interface/pages/Register/RegisterPage';
import AccountOnboardingPage from '../interface/pages/Account/AccountOnboardingPage';
import LegalTermsPage from '../interface/pages/LegalTerms/LegalTermsPage';
import TermsOfServicePage from '../interface/pages/Legal/TermsOfServicePage';
import PrivacyPolicyPage from '../interface/pages/Legal/PrivacyPolicyPage';
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
  { path: '/cgu', element: <TermsOfServicePage /> },
  { path: '/confidentialite', element: <PrivacyPolicyPage /> },
  {
    element: (
      <Protected>
        <MainLayout />
      </Protected>
    ),
    children: [
      { path: '/profile', element: <ProfilePage /> },
      { path: '/profile/edit', element: <ProfileEditPage /> },
      { path: '/onboarding-account', element: <AccountOnboardingPage /> },
      { path: '/dashboard', element: <DashboardPage /> },
      { path: '/quotes/new', element: <QuoteCreatePage /> },
      { path: 'quotes', element: <QuotesListPage /> },
      { path: '/quotes/:id', element: <QuoteDetailPage /> },
      { path: '/quotes/:id/edit/', element: <QuoteEditPage /> },
      { path: '/clients', element: <ClientsListPage /> },
      { path: '/clients/:id', element: <ClientDetailPage /> },
      { path: '/clients/:id/edit', element: <ClientEditPage /> },
      { path: '/branding/themes', element: <ThemesListPage /> },
      { path: '/branding/themes/new', element: <ThemesCreatePage /> },
      { path: '/branding/themes/:id/edit', element: <ThemesEditPage /> },
      { path: '/legal-terms', element: <LegalTermsPage /> },
    ],
  },
  {
    path: '/auth/request-password-reset',
    element: <RequestPasswordResetPage />,
  },
  //{ path: '/reset-password', element: <ResetPasswordPage /> },
  { path: '/auth/reset-password', element: <ResetPasswordPage /> },
  { path: '/verify-email', element: <VerifyEmailPage /> },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
