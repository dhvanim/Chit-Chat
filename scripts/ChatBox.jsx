import * as React from 'react';
import { Socket } from './Socket';

export function ChatBox() {
  const [messages, setmessages] = React.useState([]);
  const [username, setusername] = React.useState('');

  /* turns on socket channel for chat log and calls updatemessages */
  function getNewMessages() {
    React.useEffect(() => {
      Socket.on('chat log channel', updateMessages);
      return () => {
        Socket.off('chat log channel', updateMessages);
      };
    });
  }

  /* updates chat log */
  function updateMessages(data) {
    const chatlog = data.chat_log;
    const { timestamp } = data;
    console.log('Recieved messages from server: ', Object.keys(chatlog).length);
    console.log('Recieved timestamp: ', timestamp);

    /* user status or error message */
    if (timestamp == '') {
      console.log(chatlog);
      setmessages((messages) => messages.concat(chatlog));
      return null;
    }

    /* iterates through recieved chatlog and appends to message state */
    chatlog.map((item) => {
      console.log(item);
      setmessages((messages) => messages.concat(item));
    });

    console.log('End of recieved messages.');
  }

  function getUsername() {
    React.useEffect(() => {
      Socket.on('username channel', updateUsername);
      return () => {
        Socket.off('username channel', updateUsername);
      };
    });
  }

  /* saves only first username recieved (its own) */
  function updateUsername(data) {
    console.log('Recieved username from server: ', data.username);
    if (username == '') {
      setusername(data.username);
    }
  }

  /* scroll bar */
  const messagesEndRef = React.useRef(null);

  function scroll() {
    const scrollToBottom = () => {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    };
    React.useEffect(scrollToBottom, [messages]);
  }

  /* uses this class to format message (alignment/color) */
  function getLIClass(id) {
    if (id == 'chit-chat-bot') {
      return 'botuser';
    }
    if (id == username) {
      return 'thisuser';
    }
    if (id == '') {
      return 'entereduser';
    }
    return 'user';
  }

  /* format based on text/images/links */
  function message_type(mssg, mssg_type) {
    if (mssg_type == 'link') {
      return <span className="message"><a className="message_link" target="_blank" href={mssg}>{mssg}</a></span>;
    } if (mssg_type == 'image') {
      return <span className="message"><img className="message_image" src={mssg} alt="Error: Image could not be displayed" /></span>;
    }
    return <span className="message">{mssg}</span>;
  }

  getNewMessages();
  getUsername();
  scroll();

  /* loops through messages and displays in ul */
  return (

    <ul>
      { messages.map((message, index) => (
        <li key={index} className={getLIClass(message.username)}>

          { message.username == '' ? (
            <span className="message">
              {' '}
              <br />
              {' '}
              {message.message}
              {' '}
              <br />
              {' '}
            </span>
          )

            : (
              <span>
                <img className="usericon" src={message.icon} />
                <span className="userid">
                  {message.username}
                  {' '}
                  <span className="auth">
                    via{message.auth}
                  </span>
                </span>
                {' '}
                <br />
                { message_type(message.message, message.message_type) }
                {' '}
                <br />
                <span className="timestamp">{message.timestamp}</span>
              </span>
            )}

        </li>
      ))}

      <div ref={messagesEndRef} />
    </ul>

  );
}
