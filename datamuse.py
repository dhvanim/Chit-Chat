import requests

usernames = []

def generate_names():
    global usernames
    
    url = "https://api.datamuse.com/words"
    query = {'ml':'flowers'}
    
    # requests (default max 100) for words related to flowers
    response = requests.get(url, params=query)
    data = response.json()
    
    for item in data:
        name = item['word']
        name = name.replace(" ", "_")
        usernames.append(name)