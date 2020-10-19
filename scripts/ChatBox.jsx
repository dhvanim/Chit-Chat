import * as React from 'react';
import { Socket } from './Socket';


export function ChatBox() {
    
    const [timestamp, settimestamp] = React.useState(0);
    const [messages, setmessages] = React.useState([]);
    const [username, setusername] = React.useState("");
    
    /* turns on socket channel for chat log and calls updatemessages */
    function getNewMessages() {
        React.useEffect( () => {
            Socket.on('chat log channel', updateMessages);
            return () => {
                Socket.off('chat log channel', updateMessages);
            };
        });
    }
    
    /* updates chat log */
    function updateMessages(data) {
        
        let chatlog = data['chat_log'];
        let newtimestamp = data['timestamp'];
        console.log("Recieved messages from server: ", Object.keys(chatlog).length);
        
        console.log("Timestamp on file: ", timestamp);
        console.log("Recieved timestamp: ", newtimestamp);
        
        /* user status or error message*/
        if (newtimestamp == "") {
            let item = chatlog;
            console.log(item);
            setmessages( messages => messages.concat(item) );
            return null;
        }
        
        /* only updates if the timestamp recieved is later */
        if (timestamp == newtimestamp || timestamp > newtimestamp) {
            return null;
        }
        
        /* iterates through recieved chatlog and appends to message state */
        chatlog.map( (item) => {
            console.log(item);
            setmessages( messages => messages.concat(item));
        });
        
        /* updates timestamp */
        settimestamp( newtimestamp );
        
        console.log("End of recieved messages.");
    }
    
    function getUsername() {
        React.useEffect( () => {
            Socket.on('username channel', updateUsername);
            return () => {
                Socket.off('username channel', updateUsername);
            };
        });
    }
    
    /* saves only first username recieved (its own) */
    function updateUsername(data) {
        console.log("Recieved username from server: ", data['username']);
        if (username == "") {
            setusername( data['username'] );
        }
    }
    
    /* scroll bar */
    const messagesEndRef = React.useRef(null);
    
    function scroll() {
        const scrollToBottom = () => {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        };
        React.useEffect(scrollToBottom, [messages]);
    }
    
    getNewMessages();
    getUsername();
    scroll();
    
    function getLIClass(id) {
        if (id == "chit-chat-bot") {
            return "botuser";
        }
        if (id == username) {
            return "thisuser";
        }
        if (id == "") {
            return "entereduser";
        }
        return "user";
    }
    
    
    /* loops through messages and displays in ul */
    return (
        <ul>
                { messages.map( (message,index) => 
                    <li key={index} class={ getLIClass(message.username) }> 
                        
                        { message.username == "" ? <span class="message"> <br /> {message.message} <br/> </span> :
                        
                        <span>
                        <span class="userid">{message.username} <span class="auth">via {message.auth}</span></span> <br />
                        <span class="message">{message.message}</span> <br />
                        <span class="timestamp">{message.timestamp}</span>
                        </span>
                        }
                    </li>
                )}
                
                <div ref={messagesEndRef}></div>
        </ul>
        
    );
}