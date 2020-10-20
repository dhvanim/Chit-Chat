# Chat Room #

## 0. Clone this repo and cd into it
```$ git clone https://github.com/NJIT-CS490/project2-m1-dmm77```
<br />

## 1. Install required dependencies, packages, etc <br />
``` $ nvm install 7 ``` <br />
``` $ npm install ```  <br />
``` $ npm install -g webpack ```  <br />
``` $ npm install --save-dev webpack ```  <br />
``` $ npm install socket.io-client --save ```  <br />
``` $ pip install flask-socketio ```  <br />
``` $ pip install eventlet ``` 
<br  />

*\*If you see any error messages, try using `sudo pip` or `sudo npm`. If 'pip cannot be found' run `which pip` and use `sudo [path from which pip]`*
<br />

*\*If installing webpack does not work, restart your terminal; and if it still doesn't work run: `$ npm install -g yarn` and `$ yarn upgrade`, and restart your terminal* 
<br />


## 2. Create a Spotify Developer's account and get your client codes.
1. Navigate to https://developer.spotify.com/dashboard/login and sign up or login <br />
2. Go to your dashboard and create a project (any appropriate title/description is fine) <br />
3. Click on the project to see your Client ID and Client Secret <br />
4. Under your main directory create a file called `spotify.env` and populate it as follows:
```
SPOTIFY_CLIENT_ID={your client id here}
SPOTIFY_CLIENT_SECRET={your client secret here}
```
*\*note the lack of quotes*
<br />



## 3. Set up Google Authorization
1. Install the following to easily use Google Auth with React <br / >
``` $ npm install react-google-login ``` <br />

2. Create a Google developer's account and head to https://console.developers.google.com/

3. On the left hand side, click <i>Credentials</i>, then click <i>Create Credentials</i>, then <i>OAuthClient ID</i>

4. The application type should be <i>Web Application</i>; the name can be anything, and paste the url of your website under <i> Authorized Javascript origins</i>

5. Copy your Client ID (NOT Client Secret), and paste it in <i>GoogleButton.jsx</i>, where it said `clientId="{Client ID here}"`



## 4. Set up PSQL
1. Update and install the following:  <br />
``` $ sudo yum update ```  <br />
``` $ sudo pip install upgrade pip ```  <br />
``` $ sudo pip install psycopg2-binary ```  <br />
``` $ sudo pip install Flask-SQLAlchemy==2.1 ```  <br />
``` $ sudo yum install postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs ```  <br />
*\*enter yes to all prompts* 

2. Initialize PSQL database <br />
``` sudo service postgresql initdb ``` 

3. Create a new superuser <br />
``` sudo -u postgres createuser --superuser $USER ```  <br />
*\*If it says "could not change directory", that's fine and it worked!* 

4. Make a new database <br />
```sudo -u postgres createdb $USER ```  <br />
*\*If it says "could not change directory", that's fine and it worked!* 

5. In PSQL <br />
a.) Enter PSQL `psql` <br />
b.) Enter `\du` and `\l` and make sure your user shows up <br />
c.) Make a new user
``` create user [your username here] superuser password '[your password here]' ```  <br />
*\*Repeat step b to make sure your user appears.* <br />
d.) Quit PSQL ` \q ` 

6. Under your main directory, create a file called `sql.env` and populate as follows
```
SQL_USER={your user here} 
SQL_PASSWORD={your password here}
```
*\*note the lack of quotes*


## 5. Enable read/write from SQLAlchemy
*There is a file you need to enable your db admin password to work* <br />
1. Run this command to open the file in vim `sudo vim /var/lib/pgsql9/data/pg_hba.conf` <br />
*\*If that doesn't work try this:* `sudo vim $(psql -c "show hba_file;" | grep pg_hba.conf)` 

2. Replace all values of `ident` with `md5` using this command: `:%s/ident/md5/g`; (quit vim `:wq`)

3. Run the following `sudo service postgresql restart`
<br />

## 6. Create a .gitignore file under your main directory
Run these commands to create it and add the following files to it. This is if you plan on publically deploying your app to keep your files secure. <br />
``` $ touch .gitignore ```  <br />
``` $ echo "node_modules/" >> .gitignore ```  <br />
``` $ echo "static/script.js" >> .gitignore ```  <br />
``` $ echo "package-lock.json" >> .gitignore ``` <br />
``` $ echo "spotify.env" >> .gitignore ```  <br />
``` $ echo "sql.env" >> .gitignore```  <br />

## 7. Run your app!!
1. Run this command and leave it running in your terminal <br />
```$ npm run watch```  <br />
*\*If asked to install webpack-cli, say yes*

2. In a new terminal, start PSQL <br />
``` sudo service postgresql start ```  

3. Finally, start your app! <br />
``` python main.py ```  <br />

*\*If you make changes to your code, you will need to do a hard refresh (Ctrl+Shift+R) to see the changes* 


# Resources #

### Spotify API
* How to set up the API: https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow
* Information on its type of requests: https://developer.spotify.com/documentation/web-api/reference/

### Funtranslations API
* https://funtranslations.com/api/ <br />
*\*I made requests without signing up or using an API key (and it worked for all my tested messages)

### react-google-login
* Information on set up, how to use, and more: https://www.npmjs.com/package/react-google-login


# MILESTONE 2: Problems I Encountered #
1. One of the issues I was having was that my sockets always emitted to every client: so if two clients, not yet authorized, had the page open and then 1 of them logged in, the other would automatically be logged in as the other person. To solve this I googled ways to emit messages to only certain clients. I then found the use of socket rooms, so the emitted auth and username would only send to the right client. I also applied this to emitted chat log messages. The following source was really helpful: https://stackoverflow.com/questions/39423646/flask-socketio-emit-to-specific-user
2. Another issue I struggled with was the order of items emitted to the client after their log in is authorized. Just by running my code multiple times and using print/console.log statements, I found out that if I emitted their username immediately after I emit the status True for its auth, sometimes the client would never recieve the username and the messages would not display correctly. 

# MILESTONE 2: Improvements #
1. A huge improvement would be allowing users to send images, links, and text in the same message. I tried implementing this by parsing my message on the client side, but despite what I did my values kept returning as [Object object]. One possible solution would be to just research more and find a better way to parse and build the HTML element for message. Another would be to break up the recieved message between text/link/image so even though it may display as different speech bubbles, the user would be able to send it at once. 
2. Another improvement would be saving the user state if the user refreshes the page. Currently, on refresh it prompts the user to log in again and this could get annoying. To achieve this, the react state for user logged in status would have to be persistent. Also, the server database would have to know if the user is active, either through a log out UI or there could be more information in the flask socketio docs.

# MILESTONE 1: Problems I Encountered #
1. The biggest issue I had was getting my messages to update properly. At first, when sending a message or when a new user entered the chat, I would recieve the same messages dozens of times. I had already used useEffect, which only renders on change so I was confused as to why. After researching how React rendering and SocketIO work together, I realized I had multiple listeners opening everytime the page rendered. It would save the previous message instances and append duplicated message chains. I then added code that would close the socket. This was a helpful source: https://www.reddit.com/r/reactjs/comments/cgp50p/best_approach_using_react_hooks_socketio/ 
2. Getting the client to accept the correct messages was also an issue. When a new user would enter, all the already active users would recieve the entire chat log again. To fix this problem, I added two checks for timestamps, one stored in the client and one in the server. Since the server emits the same message to all clients with that channel, the clients have to ensure only what is needed is saved. 
3. When a user would send a message, and another would reply, the chat log would duplicate the initial user's message(s). To figure out this issue I set up multiple print statements detailing each user's last timestamp, messages emitted, etc. I realized this was happening because I was only updating one of the user's timestamps even though all of them were recieving that chat log. To resolve, I added a code to update all of the current user's timestamps.
4. I had an issue formatting the chatbox messages. I made it so the user sending messages would see their messages on the right side and everything on the left. I naturally thought to just float those elements right and left, respectively. However, the elements displayed stacked next to each other side by side. I researched online to better understand float. I learned that by floating elements, you are taking them out of the page's natural flow, so the following elements will do what they can to fill up the previous space. I simply cleared the float property for the messages not by the user. This website was really helpful: https://css-tricks.com/almanac/properties/f/float/
5. Another issue I faced was a circular import issue in python. My main python file (app.py) imported a python file that set up my databases, and that file imported something from my app.py. Because of this, my databases simply weren't getting created and I could not access anything from the database file. A temporary solution I made was to paste the database creation code into my app.py, although it makes my code not as organized, it was a simple solution so I could work on the bulk of my application. 

# MILESTONE 1: Improvements #
1. A really important improvement to my application would be implementing proper usernames picked by the user. I tried implementing a pop-up form to get this input when first opening the app, but I could not figure out the front-end details. This would add a lot to my application and could provide for user data persistence (same user each time) and security (could set up a password with it). I could add this feature by researching more about React Components and how to toggle the display of certain components. Back-end wise, the user information would be stored in a database table similar to how the messages are being sent. My current username set up merely provides aesthetics for the user.
2. A purely visual improvement would be better formatting of the bot responses. They are all in plain text, with no new line and tab characters or any styling to individual words within the chat. This can be resolved by looking into how to send different encoding types, files, or data via flask's socketio or a different module. Also, the messages would have to retain its styling when displaying it using React so that is important to check for too. 
3. A really cool improvement would be implementing different chat rooms. This way multiple groups of people can retain their privacy and talk within different rooms. Flask has a way to create differnt rooms, so researching how its room funtionality works would help me create this feature. This would also cause the need for a different database build: it would have to either keep track of the room id or have a different table per room.
4. Allowing users to send images would be a cool feature. To do this user's would either have to input the link or file of an image. If a link, there would need to be some way for the server to know it is an image file and to tell the client to embed it as such (maybe a bot command). If it was a file, there would need to be a different way of transferring data between sockets, one that allows files. The latter way requires more research into how sockets with different data. 
5. A simple, yet fun feature would be allowing private messages to be sent within the public chat room (similar to WebEx and Zoom). This could be sent up via a bot command with the recieving user's id and the message. There would have to be another attribute to all messages labelling them as for the public or only viewable to certain users. Although not the best approach, the client may have to sort through and display only the messages meant for that client user. This would also tie into privacy/security and would work best if proper usernames were established. 