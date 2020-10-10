import * as React from 'react';

import { Socket } from './Socket';
import { Users } from './Users';
import { ChatBox } from './ChatBox';


export function Content() {
    
    function sendChat(event) {
        
        let mssg = document.getElementById("typeinput");
        Socket.emit('send message channel', {'mssg':mssg.value});
        console.log('message sent to server');
        
        event.preventDefault();
        mssg.value = "";
    }
        
    /*    
     // get username from socket
    const [username, setUsername] = React.useState([""]);
    function getUsername() {
        
        Socket.on('get username channel', (data) => {
            console.log("Received username from server: " + data['username']);
            setUsername(data['username']);
        });
           
    }
    
    */
    
    return (
        <div>

            <div class="header">
                <h1> chat room tehe </h1>
                <Users />
            </div>
            
            <ChatBox />
            
            <div class="form">
                <form onSubmit={sendChat}>
                    <input id="typeinput" type="text" placeholder="Type a message here..."></input>
                    <input id="submit" type="submit"></input>
                </form>
            </div>
            
        </div>
    );
}