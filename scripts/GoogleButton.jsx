import * as React from 'react';
import { Socket } from './Socket';
import ReactDOM from 'react-dom';
import { GoogleLogin } from 'react-google-login';

export function GoogleButton() {
    
    const responseGoogle = (response) => {
      console.log(response);
      let name = response['profileObj']['name'];
      let email = response['profileObj']['email'];
      console.log(name, email);
      
      Socket.emit('new google user', {'name':name, 'email':email});
    };
    
    
    return (

            <div class="googlelogin">
            
            <p> Login below to join Room CS-490 </p>
            
                <GoogleLogin
                    clientId="407466096960-jiq3qed5a96hfgab7v804rm705mb8vsk.apps.googleusercontent.com"
                    buttonText="Google"
                    onSuccess={responseGoogle}
                    onFailure={responseGoogle}
                    cookiePolicy={'single_host_origin'}
                />
            
            </div>
   
    );
}