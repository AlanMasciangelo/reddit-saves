#!/usr/bin/env python
# 
# Retrieve all saved posts for a user and optionally filter on subreddits.
#   Writes out to ./saved_posts.md since emojis will break stdout 🤷‍♂️
#
# Usage:
#  REDDIT_APP=<app> REDDIT_APP_SECRET=<app_secret> REDDIT_USER=<user> REDDIT_PASS=<pass> ./main.py
# 
# Create an app at https://www.reddit.com/prefs/apps to authenticate with
#   select script, redirect url can be anything.
#

import requests
import json
import os

# API credential stuff
app=os.environ['REDDIT_APP'] # Weird id from your personal use script app
secret=os.environ['REDDIT_APP_SECRET'] # App secret
username=os.environ['REDDIT_USER'] # Your reddit username
password=os.environ['REDDIT_PASS'] # Your reddit password, yes you need a secret token AND password 🤷‍♂️

# Subreddits to filter on. Leave empty to not filter anything
subreddits=['programming', 'kubernetes', 'devops', 'java']

# Get an access token for your account
auth = requests.auth.HTTPBasicAuth(app, secret)
headers = {'User-Agent': 'SavedPostsBot/0.0.1'}
data = {'grant_type': 'password',
        'username': username,
        'password': password}
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)
bearer_token = res.json()['access_token']

# Get your saved posts
headers = {**headers, **{'Authorization': f"bearer {bearer_token}"}}
params = {'limit':100}
res = requests.get(f"https://oauth.reddit.com/user/{username}/saved", headers=headers, params=params)
data = res.json()['data']

# pagination and filter
posts = []
first=True
while(data['after'] or first):
        first=False
        # t3 is saved posts, t1 is saved comments if you're into that.
        posts += list(filter(lambda child: child['kind'] == 't3' and ( not subreddits or child['data']['subreddit'] in subreddits ) , data['children']))
        params = {'limit':100, 'after': data['after'] }
        res = requests.get(f"https://oauth.reddit.com/user/{username}/saved", headers=headers, params=params)
        data = res.json()['data']        

with open('saved_posts.md','w',encoding='utf-8-sig') as f:
        f.write('## Saved Reddit posts\n')
        f.write('|subreddit|title|thread|link|\n')
        f.write('|-|-|-|-|\n')
       
        posts.sort(key=lambda p: p['data']['subreddit'])
        for post in posts:
                data=post['data']
                # permalink is always the url to the post after https://www.reddit.com
                # url can be the same link for self posts or the link to articles, pics, vids if a link post
                line=f"| {data['subreddit']} | {data.get('title', '')} | https://www.reddit.com{data['permalink']} | {data['url']} |"
                f.write(line + '\n')
