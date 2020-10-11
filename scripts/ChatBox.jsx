import * as React from 'react';
import { Socket } from './Socket';


export function ChatBox() {
    
    const [timestamp, settimestamp] = React.useState(0);
    const [messages, setmessages] = React.useState([]);
    
    function getNewMessages() {
        React.useEffect( () => {
            Socket.on('chat log channel', updateMessages);
            return () => {
                Socket.off('chat log channel', updateMessages);
            };
        });

    }
    
    function updateMessages(data) {
        console.log("Recieved messages from server: ");
        
        let chatlog = data['chat_log'];
        
        chatlog.map( (item) => {
            console.log(item);
            
        });
        
        console.log("End of recieved messaes.");
        
        setmessages( messages => messages.concat( data['chatlog'] ));
        
        console.log("updated log: ", messages);
    }
    
    getNewMessages();

    return (
        <ul>
                { messages.map( (message,index) => 
                    <li key={index}> 
                    {message.userid} <br />
                    {message.message} <br />
                    {message.timestamp}
                    </li>
                )}
            
            </ul>
        
    );
}