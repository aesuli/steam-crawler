#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andrea Esuli (andrea@esuli.it)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import csv
import os
import re
import socket
import string
import urllib
import urllib.request
import urllib.parse
import json
from contextlib import closing
from time import sleep


def download_page(url, maxretries, timeout, pause):
    tries = 0
    htmlpage = None
    while tries < maxretries and htmlpage is None:
        try:
            with closing(urllib.request.urlopen(url, timeout=timeout)) as f:
                htmlpage = f.read()
                sleep(pause)
        except (urllib.error.URLError, socket.timeout, socket.error):
            tries += 1
    return htmlpage


def getgameids(filename):
    ids = set()
    with open(filename, encoding='utf8') as f:
        reader = csv.reader(f)
        for row in reader:
            dir = row[0]
            id_ = row[1]
            name = row[2]
            ids.add((dir, id_, name))
    return ids


def getgamereviews(ids, timeout, maxretries, pause, out):
    urltemplate = string.Template(
        'http://store.steampowered.com//appreviews/$id?cursor=$cursor&filter=recent&language=english')
    endre = re.compile(r'({"success":2})|(no_more_reviews)')

    for (dir, id_, name) in ids:
        if dir == 'sub':
            print('skipping sub %s %s' % (id_, name))
            continue

        gamedir = os.path.join(out, 'pages', 'reviews', '-'.join((dir, id_)))

        donefilename = os.path.join(gamedir, 'reviews-done.txt')
        if not os.path.exists(gamedir):
            os.makedirs(gamedir)
        elif os.path.exists(donefilename):
            print('skipping app %s %s' % (id_, name))
            continue

        print(dir, id_, name)

        cursor = '*'
        offset = 0
        page = 1
        maxError = 10
        errorCount = 0
        while True:
            url = urltemplate.substitute({'id': id_, 'cursor': cursor})
            print(offset, url)
            htmlpage = download_page(url, maxretries, timeout, pause)

            if htmlpage is None:
                print('Error downloading the URL: ' + url)
                sleep(pause * 3)
                errorCount += 1
                if errorCount >= maxError:
                    print('Max error!')
                    break
            else:
                with open(os.path.join(gamedir, 'reviews-%s.html' % page), 'w', encoding='utf-8') as f:
                    htmlpage = htmlpage.decode()
                    if endre.search(htmlpage):
                        break
                    f.write(htmlpage)
                    page = page + 1
                    parsed_json = (json.loads(htmlpage))
                    cursor = urllib.parse.quote(parsed_json['cursor'])

        with open(donefilename, 'w', encoding='utf-8') as f:
            pass


def main():
    parser = argparse.ArgumentParser(description='Crawler of Steam reviews')
    parser.add_argument('-f', '--force', help='Force download even if already successfully downloaded', required=False,
                        action='store_true')
    parser.add_argument(
        '-t', '--timeout', help='Timeout in seconds for http connections. Default: 180',
        required=False, type=int, default=180)
    parser.add_argument(
        '-r', '--maxretries', help='Max retries to download a file. Default: 5',
        required=False, type=int, default=3)
    parser.add_argument(
        '-p', '--pause', help='Seconds to wait between http requests. Default: 0.5', required=False, default=0.5,
        type=float)
    parser.add_argument(
        '-m', '--maxreviews', help='Maximum number of reviews per item to download. Default:unlimited', required=False,
        type=int, default=-1)
    parser.add_argument(
        '-o', '--out', help='Output base path', required=False, default='data')
    parser.add_argument(
        '-i', '--ids', help='File with game ids', required=False, default='./data/games.csv')
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    ids = getgameids(args.ids)

    print('%s games' % len(ids))

    getgamereviews(ids, args.timeout, args.maxretries, args.pause, args.out)


if __name__ == '__main__':
    main()
