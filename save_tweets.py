#!/usr/bin/env python3

import argparse
import html
import json
import sys
import textwrap

def main(argv):
    parser = argparse.ArgumentParser(description='Format tweets for search')
    parser.add_argument('cache_paths', nargs='+',
                        help='paths to the Cache/ entries to process')
    args = parser.parse_args(argv)

    with open(args.cache_paths[0]) as f:
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

    text = tweet['full_text']

    url_map = {}

    entities = tweet.get('entities')
    if entities:
        media = entities.get('media', ())
        for item in media:
            expanded_url = item.get('expanded_url')
            if not expanded_url:
                continue
            i, j = item['indices']
            text = text[:i] + expanded_url + text[j:]

        urls = entities.get('urls', ())
        for item in urls:
            expanded_url = item.get('expanded_url')
            if not expanded_url:
                continue
            url = item['url']
            url_map[url] = expanded_url
            i, j = item['indices']
            text = text[:i] + expanded_url + text[j:]

    text = html.unescape(text)
    lines = text.split('\n')
    width = 78 - indent
    lines = [textwrap.fill(line, width, break_long_words=False)
             for line in lines]

    card = tweet.get('card')
    if card is not None:
        bv = card['binding_values']
        text = bv["title"]["string_value"]
        description = bv.get("description")
        if description:
            text += '\n\n'
            text += description["string_value"]
        more_lines = []
        for line in text.splitlines():
            more_lines.extend(textwrap.fill(line, width, break_long_words=False)
                              .splitlines())
        url = card['url']
        url = url_map.get(url, url)
        more_lines.append(url)
        more_lines = ['> ' + line if line else '>' for line in more_lines]
        lines.append('')
        lines.extend(more_lines)
        # print(lines)
        # print(textwrap.fill(text, width, break_long_words=False))

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
    main(sys.argv[1:])

