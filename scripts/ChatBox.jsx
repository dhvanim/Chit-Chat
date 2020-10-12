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
        console.log("Recieved messages from server: ");
        
        let chatlog = data['chat_log'];
        let newtimestamp = data['timestamp'];
        console.log("prev ", timestamp);
        console.log("new ", newtimestamp);
        
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
        
        console.log("End of recieved messaes.");
        console.log("updated log: ", messages);
    }
    
    function getUsername() {
        React.useEffect( () => {
            Socket.on('username channel', updateUsername);
            return () => {
                Socket.off('username channel', updateUsername);
            };
        });
    }
    
    function updateUsername(data) {
        console.log("Recieved username from server: ", data['userid']);
        if (username == "") {
            setusername( data['userid'] );
        }
    }
    
    
    getNewMessages();
    getUsername();
    
    /* scroll bar */
    
    const messagesEndRef = React.useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }

    React.useEffect(scrollToBottom, [messages]);
    
    

    /* loops through messages and displays in ul */
    return (
        <ul>
                { messages.map( (message,index) => 
                    <li key={index} class={ message.userid == "chit-chat-bot" ? "botuser" : ( message.userid == username ? "thisuser" : "user") }> 
                        <span class="userid">{message.userid}</span> <br />
                        <span class="message">{message.message}</span> <br />
                        <span class="timestamp">{message.timestamp}</span>
                    </li>
                )}
                
                <div ref={messagesEndRef}></div>
        </ul>
        
    );
}