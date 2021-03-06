#!/usr/bin/env python3

import argparse
import html
import json
import sys
import textwrap
from pprint import pprint
from sys import stderr

tw = textwrap.TextWrapper(break_long_words=False, break_on_hyphens=False)

def main(argv):
    parser = argparse.ArgumentParser(description='Format tweets for search')
    parser.add_argument('cache_paths', nargs='+',
                        help='paths to the Cache/ entries to process')
    args = parser.parse_args(argv)

    for cache_path in args.cache_paths:
        #print(cache_path, file=stderr)
        with open(cache_path) as f:
            j = json.load(f)
        output_tweets(j)

def output_tweets(j):
    url, headers, content = j
    j2 = json.loads(content)

    g = j2['globalObjects']
    #tweets = g['tweets']

    #print(json.dumps(j2, indent=2))
    #print(json.dumps(j2['timeline']['instructions'], indent=2))

    for instruction in j2['timeline']['instructions']:
        if 'addEntries' not in instruction:  # for example, "pinEntry"
            continue
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

    # TODO: why are we both saving output in `output` but also printing?

def display_tweet(g, id, indent=0):
    tweet = g['tweets'].get(id)
    if not tweet:
        yield f'MISSING TWEET {id}'
        return
    user_id = tweet['user_id_str']
    user = g['users'][user_id]
    c = tweet['created_at'].split()
    date = f'{c[-1]} {c[1]} {c[2]}  {c[3]}'

    text = tweet['full_text']

    url_map = {}

    replacements = []  # (i,j,text)

    entities = tweet.get('entities')
    if entities:
        media = entities.get('media', ())
        for item in media:
            expanded_url = item.get('expanded_url')
            if not expanded_url:
                continue
            i, j = item['indices']
            replacements.append((i, j, expanded_url))

        urls = entities.get('urls', ())
        for item in urls:
            expanded_url = item.get('expanded_url')
            if not expanded_url:
                continue
            url = item['url']
            url_map[url] = expanded_url
            i, j = item['indices']
            replacements.append((i, j, expanded_url))

    replacements.sort(reverse=True)
    for i, j, replacement in replacements:
        text = text[:i] + replacement + text[j:]

    text = html.unescape(text)
    lines = text.split('\n')
    tw.width = 78 - indent
    lines = [tw.fill(line) for line in lines]

    card = tweet.get('card')
    if card is not None:
        bv = card['binding_values']
        if 'title' not in bv:
            title = 'MISSING TITLE'
        else:
            text = bv["title"]["string_value"]
        description = bv.get("description")
        if description:
            text += '\n\n'
            text += description["string_value"]
        more_lines = []
        for line in text.splitlines():
            more_lines.extend(tw.fill(line).splitlines())
        url = card['url']
        url = url_map.get(url, url)
        more_lines.append(url)
        more_lines = ['> ' + line if line else '>' for line in more_lines]
        lines.append('')
        lines.extend(more_lines)
        # print(lines)
        # print(tw.fill(text))

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
        quoted_id = tweet.get('quoted_status_id_str')
        # TODO: examine when quoted id is missing
        if quoted_id and quoted_id in g['tweets']:
            yield from display_tweet(g, quoted_id, indent + 4)

    #print(tweet.keys())

if __name__ == '__main__':
    main(sys.argv[1:])

