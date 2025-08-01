#!/usr/bin/env python3
#
# Snag tweets and some of their replies.

import argparse
import random
import sys
from functools import wraps
from pathlib import Path
from time import sleep
from urllib.parse import urlencode
from urllib.request import urlopen
from waybackpy import WaybackMachineCDXServerAPI
from waybackpy.exceptions import NoCDXRecordFound

USER_AGENT = 'Brandon Personal Archive'

def main(argv):
    parser = argparse.ArgumentParser(description='Get some tweets')
    # parser.add_argument('input_file', help='path to input file')
    args = parser.parse_args(argv)

    # id = '1174624170854047744'
    # url = wayback_url_for_tweet(id)
    # print(url)

    #curl -X GET "https://archive.org/wayback/available?url=<url>"

    #path = args.input_file
    path = 'Manifests/tw-shire-reckoning'
    with open(path) as f:
        import csv
        rows = list(csv.reader(f))

    #id = '1679598319893463041'
    #id = '1310647211903066114'

    random.shuffle(rows)

    for tag, when, id in rows:
        url = wayback_url_for_tweet(id)
        print(url)

        # if id != '1310647211903066114':
        #     continue

        # from pathlib import Path
        # #output_path = Path(f'Cache/tw-wayback-{id}.json')
        # output_path = Path(f'Cache/tw-wayback-available-{id}.json')
        # if output_path.exists():
        #     continue
        # url = f'https://twitter.com/ShireReckoning/status/{id}'
        # #print(urlencode({'url', url}))
        # archive_url = (
        #     'https://archive.org/wayback/available?'
        #     + urlencode({'url': url})
        # )

        # print(url)

        # u = urlopen(archive_url)
        # data = u.read()

        # print('response:')
        # print(data)
        # print()

        # with output_path.open('wb') as f:
        #     f.write(data)

        # sleep(3)
        #archive_url = 'http://web.archive.org/web/20221228235314/https://twitter.com/ShireReckoning/status/1310647211903066114'

        # u = urlopen(archive_url)
        # data = u.read()
        # with output_path.open('wb') as f:
        #     f.write(data)

def cache_at(path_pattern):
    def wrap(func):
        @wraps(func)
        def wrapper(*args):
            cache_path = Path(path_pattern.format(*args))
            if cache_path.exists():
                print('  (cached)')
                return cache_path.open().read().strip()
            result = func(*args)
            with cache_path.open('w') as f:
                f.write(result)
                f.write('\n')
            return result
        return wrapper
    return wrap

def url_for_tweet(id):
    return f'https://twitter.com/ShireReckoning/status/{id}'

@cache_at('Cache/tw-wayback-available-{}.json')
def wayback_url_for_tweet(id):
    url = url_for_tweet(id)
    cdx = WaybackMachineCDXServerAPI(url, USER_AGENT)
    print(f'Asking for newest {id}')
    sleep(20)
    try:
        newest = cdx.newest()
    except NoCDXRecordFound:
        return ''
    return newest.archive_url

if __name__ == '__main__':
    main(sys.argv[1:])

