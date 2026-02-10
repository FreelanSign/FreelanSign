import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { BetaWarningDialog } from '@/components/common/BetaWarningDialog';
import { FeedbackButton } from '@/components/feedback/FeedbackButton';
import { useAccountStore } from '../../infrastructure/account/accountStore';
import { useUIStore } from '../../infrastructure/ui/uiStore';
import Footer from '../components/footer/Footer';
import Navbar from '../components/navbar/Navbar';
import Sidebar from '../components/sidebar/Sidebar';

export default function MainLayout() {
  const { fetchAccounts, accounts, activeAccountId } = useAccountStore();
  const { isSidebarCollapsed, isDismissed, dismissModal } = useUIStore();
  const [showBetaWarning, setShowBetaWarning] = useState(false);

  const activeAccount = accounts.find((a) => a.id === activeAccountId);
  const BETA_WARNING_MODAL_ID = 'beta-warning';

  // Fetch accounts on mount to sync with backend state
  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  // Show beta warning if applicable
  useEffect(() => {
    if (
      activeAccount &&
      activeAccount.plan === 'beta' &&
      !isDismissed(BETA_WARNING_MODAL_ID)
    ) {
      const timer = setTimeout(() => {
        setShowBetaWarning(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [activeAccount, isDismissed]);

  const handleDismissForever = () => {
    dismissModal(BETA_WARNING_MODAL_ID);
    setShowBetaWarning(false);
  };

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

      <BetaWarningDialog
        open={showBetaWarning}
        onClose={() => setShowBetaWarning(false)}
        onDismissForever={handleDismissForever}
      />
      <FeedbackButton />
    </div>
  );
}
