from datetime import datetime
import os
from os.path import join, dirname
import random
from dotenv import load_dotenv
import requests


# set up spotify keys
dotenv_path = join(dirname(__file__), 'spotify.env')
load_dotenv(dotenv_path)

spotify_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_secret = os.environ['SPOTIFY_CLIENT_SECRET']


# about mssg
def bot_about():
    return "Hi guys! My name is chit-chat-bot and I'm here " + \
        "to help! Type '!! help' to learn more :-))"


# help mssg
def bot_help(bot_commands):
    help_message = "Here are a list of commands you can ask me: "

    for command in bot_commands:
        help_message += " " + command + " "

    return help_message


# requests funtranslate to translate to morse code
def bot_translate(string):

    if string == "":
        return "Please enter text to be translated! :8"

    url = 'https://api.funtranslations.com/translate/morse.json'
    paramaters = {"text":string}

    response = requests.get(url, params=paramaters).json()

    # if could not translate
    if response['success']['total'] != 1:
        return "Sorry! Could not translate :-("

    translated_text = response['contents']['translated']

    return translated_text


# set up spotify auth and ges access token to make requests
def spotify_get_access_token():

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_body_params = {
        'grant_type':'client_credentials',
        'client_id':spotify_id,
        'client_secret':spotify_secret,
    }
    auth_response = requests.post(auth_url, data=auth_body_params)
    auth_data = auth_response.json()

    access_token = auth_data['access_token']
    return access_token


# returns a spotify top track
def bot_spotify(artist):

    if artist == "":
        return "Please enter an artist! :8"

    access_token = spotify_get_access_token()

    header = { 'Authorization': 'Bearer {token}'.format(token=access_token) }

    # search for artist to get id
    search_url = 'https://api.spotify.com/v1/search'
    search_body_params = { 'q':artist, 'type':'artist', 'limit':1 }
    search_response = requests.get(search_url, headers=header, params=search_body_params)

    # if api response error
    if search_response.status_code != 200:
        return "Sorry! Connection error :-("

    search_data = search_response.json()

    # if no artist was found
    if search_data['artists']['total'] == 0:
        return "Sorry! No artist found :-("

    # get artist id and name
    artist_id = search_data['artists']['items'][0]['id']
    artist_name = search_data['artists']['items'][0]['name']

    # search for top track
    tracks_url = 'https://api.spotify.com/v1/artists/' + artist_id + '/top-tracks'
    tracks_body_params = {'country':'US'}
    tracks_response = requests.get(tracks_url, headers=header, params=tracks_body_params)

    # if api response error
    if search_response.status_code != 200:
        return "Sorry! Connection error :-("

    # gets track data and randomly picks song
    tracks_data = tracks_response.json()
    rand = random.randint(0, len(tracks_data['tracks']) - 1)
    track_title = tracks_data['tracks'][rand]['name']

    bot_response = "You should listen to the song " + track_title + \
        " by " + artist_name + "!! It's one of my favorites :D"
    return bot_response


# returns time elapsed string
def bot_time(entered):

    current = datetime.now()

    hrs, minutes, sec, ms = bot_time_math(entered, current)

    bot_response = "You have been online for approximately "
    if hrs!=0:
        bot_response += str(hrs) + " hours, "
    if minutes!=0:
        bot_response += str(minutes) + " minutes, "
    if sec!=0:
        bot_response += str(sec) + " seconds and "

    bot_response += str(ms) + " microseconds :o"

    return bot_response

def bot_time_math(entered, current):

    elapsed = current - entered
    elapsed_sec = elapsed.total_seconds()

    # convert to hrs/min/sec
    hrs = int ( elapsed_sec // 3600 )
    minutes = int( ( elapsed_sec - (hrs*3600) ) // 60 )
    sec = int ( elapsed_sec - (hrs*3600) - (minutes*60) )

    return hrs, minutes, sec, elapsed.microseconds

# unknown command
def bot_unknown(command):
    return "( !!  " + command + " ) Command unknown. Type '!! help' for a list of commands :p"
