import * as React from 'react';

import { Socket } from './Socket';
import { Users } from './Users';
import { ChatBox } from './ChatBox';
import { GoogleButton } from './GoogleButton';

export function Content() {
    
    /* sends chat message to server */
    function sendChat(event) {
        let username = ChatBox.username;
        let mssg = document.getElementById("typeinput");
        Socket.emit('message channel', {'mssg':mssg.value, 'username':username});
        
        console.log('message sent to server');
        
        event.preventDefault();
        mssg.value = "";
        
    }
    
    const [status, setstatus] = React.useState(false);
    
    function updateStatus() {
        React.useEffect( () => {
            Socket.on('user auth channel', data => {
                setstatus(data['auth']);
                console.log("status data", data['auth']);
            });
            return () => {
                Socket.off('user auth channel');
            };
        });
        
        console.log("status", status);
    }
    
    updateStatus();
    
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