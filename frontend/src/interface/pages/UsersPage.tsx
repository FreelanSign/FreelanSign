import { useEffect, useState } from 'react';
import type { User } from '../../domain/user';
import { fetchUsers } from '../../services/userService';
import UserList from '../components/UserList';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers()
      .then(setUsers)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Chargement…</p>;
  return (
    <div>
      <h1>Liste des utilisateurs</h1>
      <UserList users={users} />
    </div>
  );
}
