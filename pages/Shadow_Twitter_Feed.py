from twikit import Client
import json

# Setup the ghost client
client = Client('en-US')

async def get_curated_tweets():
    # Only login once; thereafter use cookies.json
    # client.login(auth_info_1='user', password='pw', email='email')
    # client.save_cookies('cookies.json')
    client.load_cookies('cookies.json')
    
    # Target verified financial "cashtags"
    query = "$NVDA OR $BTC OR $OIL filter:verified"
    tweets = await client.search_tweet(query, 'Latest', count=20)
    
    return [{"user": t.user.name, "text": t.text} for t in tweets]
