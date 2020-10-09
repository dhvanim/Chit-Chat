import * as React from 'react';

import { Socket } from './Socket';
import { Users } from './Users';


export function Content() {
    
    function sendChat(event) {
        let mssg = document.getElementById("typeinput");
        Socket.emit('send message channel', {'user':username, 'mssg':mssg.value});
        console.log('message sent to server');
        
        event.preventDefault();
        mssg.value = "";
    }
        
    // get username from socket
    const [username, setUsername] = React.useState([""]);
    function getUsername() {
        React.useEffect(() => {
                Socket.on('get username channel', (data) => {
                    console.log("Received username from server: " + data['username']);
                    setUsername(data['username']);
                });
            });
    }
    getUsername();
    
    
    return (
        <div>

            <div class="header">
                <h1> chat room tehe </h1>
                
                <Users />
            </div>
            
            <div id="chatbox">
                <p> user name: { username } </p>
                <p> 
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent eu tristique tellus. Praesent vitae dignissim nibh. Integer ex turpis, hendrerit et lacus a, congue venenatis nisi. Nunc tempus quis massa ornare aliquet. Vivamus nec ultricies libero. Vestibulum laoreet tincidunt diam at viverra. Etiam est lorem, ullamcorper ac laoreet in, vestibulum at mi. Vestibulum hendrerit odio eget tortor finibus, feugiat gravida sem imperdiet. Fusce tristique justo id metus molestie rhoncus. Aenean consectetur lorem et ante imperdiet, ac ultricies elit pretium. Sed euismod nibh at tellus elementum malesuada. Aenean convallis, sem a luctus eleifend, est tortor semper ante, eu maximus urna libero eu sem. Proin ut quam sit amet leo accumsan imperdiet. Aliquam lacinia malesuada sem, eu tempor est hendrerit sed. Nulla eget pretium arcu. Donec maximus erat nisi, ut viverra metus imperdiet a.
                <br />
                Mauris at congue magna. Fusce id dapibus erat, at tempor ligula. Pellentesque eleifend, felis vel pharetra ultrices, dui enim scelerisque ligula, et interdum metus mauris eget augue. Donec viverra lacus quam, a hendrerit dui facilisis ac. Nunc suscipit pharetra lobortis. Nullam pharetra posuere eros in venenatis. Curabitur vitae pretium diam. Nullam facilisis, urna quis malesuada imperdiet, nulla est egestas leo, non consequat ligula justo ut mi. Aliquam commodo pulvinar tempus. Pellentesque nec ex in erat egestas suscipit. Morbi nec dui scelerisque, semper ante scelerisque, imperdiet orci. Cras convallis lobortis metus, vitae sodales augue eleifend non. Nulla quis consectetur nulla. Nullam non eros id dui dapibus consequat. Donec pretium nunc ut diam tincidunt, a tempus massa cursus.
                <br />
                Duis at egestas libero, eu vulputate sapien. Ut vehicula justo vel libero consectetur, at cursus dui aliquet. Ut convallis luctus pellentesque. Maecenas congue tristique magna, sed tincidunt velit lobortis ac. Nulla purus sapien, dignissim id mi eu, lobortis tristique odio. Aenean hendrerit eros lectus. Etiam est est, rutrum ut finibus a, accumsan nec purus. Proin bibendum, risus eget lacinia facilisis, mi nibh blandit libero, id auctor turpis diam id ligula. 
                <br />
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent eu tristique tellus. Praesent vitae dignissim nibh. Integer ex turpis, hendrerit et lacus a, congue venenatis nisi. Nunc tempus quis massa ornare aliquet. Vivamus nec ultricies libero. Vestibulum laoreet tincidunt diam at viverra. Etiam est lorem, ullamcorper ac laoreet in, vestibulum at mi. Vestibulum hendrerit odio eget tortor finibus, feugiat gravida sem imperdiet. Fusce tristique justo id metus molestie rhoncus. Aenean consectetur lorem et ante imperdiet, ac ultricies elit pretium. Sed euismod nibh at tellus elementum malesuada. Aenean convallis, sem a luctus eleifend, est tortor semper ante, eu maximus urna libero eu sem. Proin ut quam sit amet leo accumsan imperdiet. Aliquam lacinia malesuada sem, eu tempor est hendrerit sed. Nulla eget pretium arcu. Donec maximus erat nisi, ut viverra metus imperdiet a.
                </p>
            </div>
            
            <div class="form">
                <form onSubmit={sendChat}>
                    <input id="typeinput" type="text" placeholder="Type a message here..."></input>
                    <input id="submit" type="submit"></input>
                </form>
            </div>
            
        </div>
    );
}