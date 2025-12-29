import { cn } from '@/lib/utils';
import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useAccountStore } from '../../infrastructure/account/accountStore';
import { useUIStore } from '../../infrastructure/ui/uiStore';
import Footer from '../components/footer/Footer';
import Navbar from '../components/navbar/Navbar';
import Sidebar from '../components/sidebar/Sidebar';

export default function MainLayout() {
  const { fetchAccounts } = useAccountStore();
  const { isSidebarCollapsed } = useUIStore();

  // Fetch accounts on mount to sync with backend state
  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  return (
    <div className="flex min-h-screen bg-gray-50/80">
      {/* Sidebar - Fixe à gauche sur desktop */}
      <Sidebar />

      {/* Main Content Area */}
      <div
        className={cn(
          'flex-1 flex flex-col min-h-screen transition-all duration-300',
          isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64',
        )}
      >
        <Navbar />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        <Footer />
      </div>
    </div>
  );
}
