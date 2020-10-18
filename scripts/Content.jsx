import * as React from 'react';

import { Socket } from './Socket';
import { Users } from './Users';
import { ChatBox } from './ChatBox';
import { GoogleButton } from './GoogleButton';

export function Content() {
    
    /* sends chat message to server */
    function sendChat(event) {
        
        let mssg = document.getElementById("typeinput");
        Socket.emit('message channel', {'mssg':mssg.value});
        
        console.log('message sent to server');
        
        event.preventDefault();
        mssg.value = "";
        
    }
    
    const [status, setstatus] = React.useState(false);
    
    return (
        <div>
            
          
            <div class="header">
                <Users />
            </div>
            
            { status == false ? <GoogleButton /> :  
            
            <div>
             
            <div class="chatbox">
            
                <ChatBox />
                
            </div>
            
            <div class="form">
                <form onSubmit={sendChat}>
                    <input id="typeinput" type="text" placeholder="Type a message here..."></input>
                    <input id="submit" type="submit"></input>
                </form>
            </div>
            
            </div>
            
            }
            
        </div>
    );
}