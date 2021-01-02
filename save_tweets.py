import html
import json
import textwrap

def main():
    with open('Cache/7b02ee57e98a14732cefac8930b3f1d4') as f:
        j = json.load(f)

    url, headers, content = j
    j2 = json.loads(content)

    g = j2['globalObjects']
    #tweets = g['tweets']

    for instruction in j2['timeline']['instructions']:
        add_entries = instruction['addEntries']['entries']

    tweet_ids = [e['entryId'] for e in add_entries]
    output = []

    for tweet_id in tweet_ids:
        if not tweet_id.startswith('tweet-'):
            # cursors?
            continue
        id = tweet_id[6:]
        for text in display_tweet(g, id):
            print(text)
            output.append(text)

    with open('Documents/twitter-likes.txt', 'w') as f:
        f.write('\n'.join(output))

def display_tweet(g, id, indent=0):
    tweet = g['tweets'][id]
    user_id = tweet['user_id_str']
    user = g['users'][user_id]
    c = tweet['created_at'].split()
    date = f'{c[-1]} {c[1]} {c[2]}  {c[3]}'
    text = html.unescape(tweet['full_text'])
    lines = text.split('\n')
    width = 78 - indent
    lines = [textwrap.fill(line, width) for line in lines]
    filled_text = '\n'.join(lines)
    url = f'https://twitter.com/{user["screen_name"]}/status/{id}'

    #print(tweet)

    text = f'''\
{user['name']}  @{user['screen_name']}  {date}
{url}

{filled_text}

← {tweet['reply_count']}  \
⟳ {tweet['retweet_count']}  \
♥ {tweet['favorite_count']}
'''

    yield textwrap.indent(text, ' ' * indent)

    if tweet.get('is_quote_status'):
        quoted_id = tweet['quoted_status_id_str']
        if quoted_id in g['tweets']:
            yield from display_tweet(g, quoted_id, indent + 4)

    #print(tweet.keys())

if __name__ == '__main__':
    main()
