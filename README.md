# Chat Room #

## 0. Clone this repo and *cd* into it
```$ git clone https://github.com/NJIT-CS490/project2-m1-dmm77```

## 1. Create a Spotify Developer's account and get your client codes.
i.    Navigate to https://developer.spotify.com/dashboard/login and sign up or login <br />
ii.   Go to your dashboard and create a project (any appropriate title/description is fine) <br />
iii.  Click on the project to see your Client ID and Client Secret <br />
iv.   Under your main directory create a file called `spotify.env` and populate it as follows: <br />
```
SPOTIFY_CLIENT_ID={your client id here}
SPOTIFY_CLIENT_SECRET={your client secret here}
``` 
<br />
*note the lack of quotes*
<br />

## 2. Install required dependencies, packages, etc
i.    ```$ nvm install 7``` <br />
ii.   ```$ npm install``` <br />
iii.  ```$ npm install -g webpack ``` <br />
      ```$ npm install --save-dev webpack ``` <br />
      *- If this does not work, restart your terminal. <br />
       - If it still doesn't work run: `$ npm install -g yarn` and `$ yarn upgrade`, and restart your terminal* <br />

iv.   ```$ npm install socket.io-client --save``` <br />
v.    ```$ pip install flask-socketio``` <br />
vi.   ```$ pip install eventlet``` <br  />
<br />
*If you see any error messages, try using ```sudo pip``` or ```sudo npm```. If 'pip cannot be found' run ```which pip``` and use ```sudo [path from which pip]```*
<br />

## 3. Set up PSQL
i.    Update and install the following: <br />
``` sudo yum update  
sudo pip install upgrade pip 
sudo pip install psycopg2-binary 
sudo pip install Flask-SQLAlchemy==2.1 
sudo yum install postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs 
``` 
<br />
*enter yes to all prompts* <br />

ii.   Initialize PSQL database <br />
``` sudo service postgresql initdb ``` <br />

iii.  Create a new superuser <br />
``` sudo -u postgres createuser --superuser $USER ``` <br />
*If it says "could not change directory, that's fine and it worked!* <br />

iv.   Make a new database <br />
```sudo -u postgres createdb $USER ``` <br />
*If it says "could not change directory, that's fine and it worked!* <br />

v.    Enter into psql <br />
  a.) ``` psql ``` <br />
  b.)   Make sure your created user shows up <br />
``` \du <br /> \l ``` <br/>
  c.)  Make a new user <br />
``` create user [your username here] superuser password '[your password here]' ``` <br />
*repeat step vi. to make sure your user appears.* <br />
  d.) Quit psql <br />
``` \q ``` <br />

vi.   Under your main directory, create a file called `sql.env` and populate as follows:
```
SQL_USER={your user here} 
SQL_PASSWORD={your password here}
```
<br />

## 4. Enable read/write from SQLAlchemy
*There is a file you need to enable your db admin password to work* <br />
i.    Run this command to open the file in vim <br />
``` sudo vim /var/lib/pgsql9/data/pg_hba.conf ``` <br>
*If that doesn't work try this:* ``` sudo vim $(psql -c "show hba_file;" | grep pg_hba.conf) ``` 
<br />

ii.   Replace all values of `ident` with `md5` by typing the following <br />
```:%s/ident/md5/g
:wq 
```
<br />

iii.  Run the following <br />
```sudo service postgresql restart```


## 5. Create a .gitignore file under your main directory
Run these commands to create it and add the following files to it. This is if you plan on publically deploying your app to keep your files secure.
```$ touch .gitignore``` <br />
```$ echo "node_modules/" >> .gitignore``` <br />
```$ echo "static/script.js" >> .gitignore``` <br />
```$ echo "package-lock.json" >> .gitignore``` <br />
```$ echo "spotify.env" >> .gitignore``` <br />
```$ echo "sql.env" >> .gitignore``` <br />


## 6. Run your app!!
i.    Run this command and leave it running in your terminal. <br />
```$ npm run watch``` <br />
*If asked to install webpack-cli, say yes*
<br />

ii.   In a new terminal, start PSQL <br />
``` sudo service postgresql start ``` <br />

iii.  Finally, start your app! <br />
``` python main.py ```

*If you make changes to your code, you will need to do a hard refresh (Ctrl+Shift+R) to see the changes*
