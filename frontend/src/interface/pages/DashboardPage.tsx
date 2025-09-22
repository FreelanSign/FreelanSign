import { Link } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <p>Bienvenue {user?.profile?.first_name ?? user?.email} 👋</p>

      <div className="flex gap-3">
        <Link to="/profile" className="bg-blue-600 text-white rounded px-3 py-2">Mon profil</Link>
        <Link to="/quotes" className="bg-indigo-600 text-white rounded px-3 py-2">Mes devis</Link>
        <Link to="/quotes/new" className="bg-green-600 text-white rounded px-3 py-2">+ Créer un devis</Link>
        <button onClick={() => logout()} className="bg-gray-200 rounded p-2">Se déconnecter</button>
      </div>
    </main>
  );
}
