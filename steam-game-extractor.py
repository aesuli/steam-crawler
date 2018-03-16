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
import urllib
import urllib.request
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


def extract_games(basepath, outputfile_name):
    gameidre = re.compile(r'/(app|sub)/([0-9]+)/')
    gamenamere = re.compile(r'<span class="title">(.*?)</span>')
    games = dict()
    for root, _, files in os.walk(basepath):
        for file in files:
            fullpath = os.path.join(root, file)
            with open(fullpath, encoding='utf8') as f:
                htmlpage = f.read()

                gameids = list(gameidre.findall(htmlpage))
                gamenames = list(gamenamere.findall(htmlpage))
                for app, id_, name in zip([app for (app, _) in gameids], [id_ for (_, id_) in gameids], gamenames):
                    games[(app, id_)] = name
    with open(outputfile_name, mode='w', encoding='utf-8', newline='') as outputfile:
        writer = csv.writer(outputfile)
        for app, id_ in games:
            writer.writerow([app, id_, games[(app, id_)]])


def main():
    parser = argparse.ArgumentParser(description='Crawler of Steam game ids and names')
    parser.add_argument(
        '-i', '--input', help='Input file or path (all files in subpath are processed)', default='./data/pages/games',
        required=False)
    parser.add_argument(
        '-o', '--output', help='Output file', default='./data/games.csv', required=False)
    args = parser.parse_args()

    extract_games(args.input, args.output)


if __name__ == '__main__':
    main()
