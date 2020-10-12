# Chat Room #

## 0. Clone this repo and cd into it
```$ git clone https://github.com/NJIT-CS490/project2-m1-dmm77```
<br />


## 1. Create a Spotify Developer's account and get your client codes.
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


## 2. Install required dependencies, packages, etc <br />
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

*\*If install webpack does not work, restart your terminal; and if it still doesn't work run: `$ npm install -g yarn` and `$ yarn upgrade`, and restart your terminal* 
<br />


## 3. Set up PSQL
1. Update and install the following:  <br />
``` $ sudo yum update ```  <br />
``` $ sudo pip install upgrade pip ```  <br />
``` $ sudo pip install psycopg2-binary ```  <br />
``` $ sudo pip install Flask-SQLAlchemy==2.1 ```  <br />
``` $ sudo yum install postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs ```  <br />
*\*enter yes to all prompts* 
 <br />

2. Initialize PSQL database <br />
``` sudo service postgresql initdb ``` 
<br />

3. Create a new superuser <br />
``` sudo -u postgres createuser --superuser $USER ```  <br />
*\*If it says "could not change directory", that's fine and it worked!* 
<br />

4. Make a new database <br />
```sudo -u postgres createdb $USER ```  <br />
*\*If it says "could not change directory", that's fine and it worked!* 
<br />

5. In PSQL <br />
a.) Enter PSQL `psql` <br />
b.) Enter `\du` and `\l` and make sure your user shows up <br />
c.) Make a new user
``` create user [your username here] superuser password '[your password here]' ```  <br />
*\*Repeat step b to make sure your user appears.* <br />
d.) Quit PSQL ` \q ` 
<br />

6. Under your main directory, create a file called `sql.env` and populate as follows
```
SQL_USER={your user here} 
SQL_PASSWORD={your password here}
```
*\*note the lack of quotes*
<br />


## 4. Enable read/write from SQLAlchemy
*There is a file you need to enable your db admin password to work* <br />
1. Run this command to open the file in vim `sudo vim /var/lib/pgsql9/data/pg_hba.conf` <br />
*\*If that doesn't work try this:* `sudo vim $(psql -c "show hba_file;" | grep pg_hba.conf)` 
<br />

2. Replace all values of `ident` with `md5` using this command: `:%s/ident/md5/g`; quit vim `:wq`
<br />

3. Run the following `sudo service postgresql restart`
<br />


## 5. Create a .gitignore file under your main directory
Run these commands to create it and add the following files to it. This is if you plan on publically deploying your app to keep your files secure.
``` $ touch .gitignore ```  <br />
``` $ echo "node_modules/" >> .gitignore ```  <br />
``` $ echo "static/script.js" >> .gitignore ```  <br />
``` $ echo "package-lock.json" >> .gitignore ``` <br />
``` $ echo "spotify.env" >> .gitignore ```  <br />
``` $ echo "sql.env" >> .gitignore```  <br />
<br />


## 6. Run your app!!
1. Run this command and leave it running in your terminal <br />
```$ npm run watch```  <br />
*\*If asked to install webpack-cli, say yes*
<br />

2. In a new terminal, start PSQL <br />
``` sudo service postgresql start ```  

3. Finally, start your app! <br />
``` python main.py ```  <br />

*\*If you make changes to your code, you will need to do a hard refresh (Ctrl+Shift+R) to see the changes*
