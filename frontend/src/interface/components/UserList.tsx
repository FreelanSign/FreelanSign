import React from 'react';
import type { User } from '../../domain/user';

interface Props {
  users: User[];
}

export default function UserList({ users }: Props) {
  return (
    <ul>
      {users.map((u) => (
        <li key={u.id}>
          {u.full_name} — {u.email} {u.phone && `(${u.phone})`}
        </li>
      ))}
    </ul>
  );
}
