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
import datetime
import json
import os
import re
import sys

from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


def extract_reviews(basepath, outputfile_name, games_df, title_pattern):
    helpfulre = re.compile(r'([0-9]+) [a-z]+? found this review helpful')
    funnyre = re.compile(r'([0-9]+) [a-z]+? found this review funny')
    ownedre = re.compile(r'([0-9]+) product')
    revre = re.compile(r'([0-9]+) review')
    timere = re.compile(r'([0-9.]+) hrs on record')
    postedre = re.compile(r'Posted: (.+)')
    idre = re.compile(r'app-([0-9]+)$')
    yearre = re.compile(r'.* [0-9][0-9][0-9][0-9]$')
    userre = re.compile(r'/(profiles|id)/(.+?)/')
    title_re = re.compile(title_pattern) if title_pattern else None
    with open(outputfile_name, mode="w", encoding="utf-8", newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(['game_id','game_title', 'review_helpful', 'review_funny', 'username', 'games_owned', 'reviews_written', 'recommended', 'time_played', 'review_date', 'review_text'])
        for root, _, files in tqdm(list(os.walk(basepath))):
            m = idre.search(root)
            if m:
                game_id = m.group(1)
                game_title = games_df[(games_df['game_id'] == int(game_id)) & (games_df['package_type']=='app')]['game_title'].values[0]
                if title_re and not title_re.search(str(game_title)):
                    print('skipping not matching game %s %s' % (game_id, game_title))
                    continue
            else:
                print('skipping non-game path ', root, file=sys.stderr)
                continue
            for file in tqdm(files, leave=False):
                fullpath = os.path.join(root, file)
                with open(fullpath, encoding='utf8') as f:
                    try:
                        soup = BeautifulSoup(json.loads(f.read())['html'], "html.parser")
                    except ValueError:
                        continue
                    for reviewdiv in soup.find_all('div', attrs={'class': 'review_box'}):
                        helpful = 0
                        funny = 0
                        elem = reviewdiv.find('div', attrs={'class': 'vote_info'})
                        if elem:
                            m = helpfulre.search(elem.text)
                            if m:
                                helpful = m.group(1)
                            m = funnyre.search(elem.text)
                            if m:
                                funny = m.group(1)
                        username = '__anon__'
                        elem = reviewdiv.find('div', attrs={'class': 'persona_name'})
                        if elem:
                            m = userre.search(str(elem.contents))
                            if m:
                                username = m.group(2)
                        owned = 0
                        elem = reviewdiv.find('div', attrs={'class': 'num_owned_games'})
                        if elem:
                            m = ownedre.search(elem.text)
                            if m:
                                owned = m.group(1)
                        numrev = 0
                        elem = reviewdiv.find('div', attrs={'class': 'num_reviews'})
                        if elem:
                            m = revre.search(elem.text)
                            if m:
                                numrev = m.group(1)
                        recco = 0
                        elem = reviewdiv.find('div', attrs={'class': 'title ellipsis'})
                        if elem:
                            if elem.text == 'Recommended':
                                recco = 1
                            else:
                                recco = -1
                        time = 0
                        elem = reviewdiv.find('div', attrs={'class': 'hours ellipsis'})
                        if elem:
                            m = timere.search(elem.text)
                            if m:
                                time = m.group(1)
                        posted = 0
                        elem = reviewdiv.find('div', attrs={'class': 'postedDate'})
                        if elem:
                            m = postedre.search(elem.text)
                            if m:
                                posted = m.group(1).strip()
                                if not yearre.match(posted):
                                    posted = posted + ", %s" % datetime.date.today().year
                        content = ''
                        elem = reviewdiv.find('div', attrs={'class': 'content'})
                        if elem:
                            content = elem.text.strip()
                        writer.writerow(
                            (game_id, game_title, helpful, funny, username, owned, numrev, recco, time, posted, content))

def main():
    parser = argparse.ArgumentParser(description='Extractor of Steam reviews')
    parser.add_argument(
        '-i', '--input', help='Input file or path (all files in subpath are processed)', default="./data/pages/reviews",
        required=False)
    parser.add_argument(
        '-g', '--games', help='Games file', default='./data/games.csv', required=False)
    parser.add_argument(
        '-o', '--output', help='Output file', default='./data/reviews.csv', required=False)
    parser.add_argument(
        '-t', '--title', help='Process only games whose title matches the given regular expression', required=False)
    args = parser.parse_args()

    games_df = pd.read_csv(args.games)
    extract_reviews(args.input, args.output, games_df, args.title)

if __name__ == '__main__':
    main()
