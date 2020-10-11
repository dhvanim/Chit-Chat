import * as React from 'react';
import { Socket } from './Socket';

/* TODO: 
fix: when new page opens, all pages get full chat history again. 
update: style.css for chat
*/

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
            setmessages( messages => messages.concat(item));
        });
        
        console.log("End of recieved messaes.");
        
        
        
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