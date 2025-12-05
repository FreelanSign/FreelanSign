import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useAccountStore } from '../../infrastructure/account/accountStore';
import Footer from '../components/footer/Footer';
import Navbar from '../components/navbar/Navbar';
import Sidebar from '../components/sidebar/Sidebar';
import styles from './main-layout.module.css';

export default function MainLayout() {
  const { fetchAccounts } = useAccountStore();

  // Fetch accounts on mount to sync with backend state
  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.contentWrapper}>
        <Navbar />
        <main className={styles.main}>
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}
