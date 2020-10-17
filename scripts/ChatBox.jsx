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
            console.log( chatlog );
            setmessages( messages => messages.concat(chatlog) );
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
    
    
    /* uses this class to format message (alignment/color) */
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
    
    /* format based on text/images/links */
    function message_type(mssg, mssg_type) {
        if (mssg_type == "link") {
            return <span class="message"><a class="message_link" target="_blank" href={mssg}>{mssg}</a></span>;
        }
        else if (mssg_type == "image") {
            return <span class="message"><img class ="message_image" src={mssg} alt="Error: Image could not be displayed"/></span>;
        }
        else {
            return <span class="message">{mssg}</span>;
        }
    }
    
    getNewMessages();
    getUsername();
    scroll();
    
    /* loops through messages and displays in ul */
    return (
        <ul>
            { messages.map( (message,index) => 
                <li key={index} class={ getLIClass(message.userid) }> 
                    <span class="userid">{message.userid}</span> <br />
                    { message_type( message.message, message.message_type ) } <br />
                    <span class="timestamp">{message.timestamp}</span>
                </li>
            )}
                
            <div ref={messagesEndRef}></div>
        </ul>
        
    );
}