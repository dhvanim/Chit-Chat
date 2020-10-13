import * as React from 'react';
import { Socket } from './Socket';


export function Users() {
    
    const [users, setUsers] = React.useState([0]);
    
    function getActiveUsers() {
        React.useEffect( () => {
            Socket.on('active users channel', updateActiveUsers);
            return () => {
                Socket.off('active users channel', updateActiveUsers);
            }; 
        });
    }
    
    function updateActiveUsers(data) {
        console.log("recieved active users from server: ", data['users']);
        setUsers( data['users'] );
    }
    
    getActiveUsers();
    
    return (
        
        <p> Room CS-490&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;<span class="title">CHAT BOX</span>&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;{ users } Users Active </p>
        
    );

}