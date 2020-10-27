import * as React from 'react';
import { Socket } from './Socket';

export default function Users() {
  const [users, setUsers] = React.useState([0]);

  function updateActiveUsers(data) {
    setUsers(data.users);
  }

  function getActiveUsers() {
    React.useEffect(() => {
      Socket.on('active users channel', updateActiveUsers);
      return () => {
        Socket.off('active users channel', updateActiveUsers);
      };
    });
  }

  getActiveUsers();

  return (

    <p>
      {' '}
      Room CS-490&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
      <span className="title">CHAT BOX</span>
&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
      { users }
      {' '}
      Users Active
      {' '}
    </p>

  );
}
