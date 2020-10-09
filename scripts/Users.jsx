import * as React from 'react';
import { Socket } from './Socket';


export function Users() {
    
    const [users, updateUsers] = React.useState([0]);
    
    function getActiveUsers() {
        React.useEffect(() => {
                Socket.on('active users channel', (data) => {
                    console.log("Received users from server: " + data['users']);
                    updateUsers(data['users']);
                });
            });
    }
    
    getActiveUsers();
    
    return (
        
        <p> { users } Users Active </p>
        
    )

}