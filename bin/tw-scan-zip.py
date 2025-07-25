#!/usr/bin/env python3

import argparse
import csv
import datetime as dt
import json
import sys
from zipfile import ZipFile

def main(argv):
    parser = argparse.ArgumentParser(description='Scan Twitter zip file')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')
    args = parser.parse_args(argv)
    #print(args.accumulate(args.integers))

    path = (
        '/home/brandon/Downloads/'
        'twitter-2023-07-31-'
        'f13908f8c8f57a2dfbbcb270697faea4bac469e39888cfac2855ef645e95e266.zip'
    )

    with open(path, 'rb') as zf:
        z = ZipFile(zf)
        #print(z.namelist())
        f = z.open('data/tweets.js')
        s = f.read()
        s = s[s.index(b'['):]
        j = json.loads(s)

    rows = []
    for tweet in j:
        #print(j[0])
        dstr = tweet['tweet']['created_at']
        d = dt.datetime.strptime(dstr, '%a %b %d %H:%M:%S +0000 %Y')
        id = j[0]['tweet']['id']
        rows.append(['tweet', d.strftime('%Y-%m-%d %H:%M:%S'), id])

    rows.sort()

    with open('Manifests/tw-shire-reckoning', 'w') as f:
        #f = sys.stdout
        w = csv.writer(f)
        w.writerows(rows)
        #[manifest, f, indent=1]

if __name__ == '__main__':
    main(sys.argv[1:])
