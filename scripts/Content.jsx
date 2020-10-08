import * as React from 'react';

import { Socket } from './Socket';

function testSocket(event) {
    let mssg = document.getElementById("chat");
    Socket.emit('test socket', {'mssg':mssg.value});
    console.log('ayo sent');
    
    event.preventDefault();
}

export function Content() {
    
    
    return (
        <div>
            <form onSubmit={testSocket}>
                <input id="chat" type="text"></input>
                <input type="submit"></input>
            </form>
            <h1> Test tehe </h1>
            
        </div>
    );
}