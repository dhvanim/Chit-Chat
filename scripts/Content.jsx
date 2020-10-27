import * as React from 'react';
import ChatBox from './ChatBox';
import { Socket } from './Socket';
import Users from './Users';

import { GoogleButton } from './GoogleButton';

export default function Content() {
  /* sends chat message to server */
  function sendChat(event) {
    const mssg = document.getElementById('typeinput');
    Socket.emit('message channel', { mssg: mssg.value });

    event.preventDefault();
    mssg.value = '';
  }

  const [status, setstatus] = React.useState(false);

  function updateStatus() {
    React.useEffect(() => {
      Socket.on('user auth channel', (data) => {
        setstatus(data.auth);
      });
      return () => {
        Socket.off('user auth channel');
      };
    });
  }

  updateStatus();

  return (
    <div>

      <div className="header">
        <Users />
      </div>

      { status === false ? <GoogleButton />

        : (
          <div>

            <div className="chatbox">

              <ChatBox />

            </div>

            <div className="form">
              <form onSubmit={sendChat}>
                <input id="typeinput" type="text" placeholder="Type a message here..." maxLength="280" />
                <input id="submit" type="submit" />
              </form>
            </div>

          </div>
        )}

    </div>
  );
}
