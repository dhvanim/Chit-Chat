import * as React from 'react';

import { GoogleLogin } from 'react-google-login';
import { Socket } from './Socket';

export default function GoogleButton() {
  const responseGoogle = (response) => {
    const { email } = response.profileObj;
    const image = response.profileObj.imageUrl;

    Socket.emit('new google user', { email, image });
  };

  return (

    <div className="googlelogin">

      <p> Login below to join Room CS-490 </p>

      <GoogleLogin
        clientId="407466096960-jiq3qed5a96hfgab7v804rm705mb8vsk.apps.googleusercontent.com"
        buttonText="Google"
        onSuccess={responseGoogle}
        onFailure={responseGoogle}
        cookiePolicy="single_host_origin"
      />

    </div>

  );
}
