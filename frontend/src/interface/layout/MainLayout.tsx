import { Outlet } from 'react-router-dom';
import Footer from '../components/footer/Footer';
import Navbar from '../components/navbar/Navbar';
import Sidebar from '../components/sidebar/Sidebar';
import styles from './main-layout.module.css';

export default function MainLayout() {
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
