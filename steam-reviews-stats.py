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
import json
from collections import defaultdict

import pandas as pd
from tqdm import tqdm


def process_reviews(inputfile_name, output_dir):
    with open(inputfile_name, mode="r", encoding="utf-8") as inputfile:
        input_df = pd.read_csv(inputfile)
        totalreviews = len(input_df)
        totalhours = input_df['time_played'].astype(float).sum()
        users = defaultdict(lambda: defaultdict(float))
        games = defaultdict(lambda: defaultdict(float))
        for _, row in tqdm(input_df.iterrows(), total=totalreviews):
            username = row['username']
            game_id = row['game_id']
            time = float(row['time_played'])
            users[username]['games'] += 1
            users[username]['time_played'] += time
            games[game_id]['users'] += 1
            games[game_id]['title'] = row['game_title']
            games[game_id]['reviews'] += 1
            if row['recommended'] == 1:
                games[game_id]['recommended'] += 1
            else:
                games[game_id]['not_recommended'] += 1
            games[game_id]['time_played'] += time

        summary = {'reviews': totalreviews,
                   'hours': totalhours,
                   'users': len(users),
                   'games': len(games)}
        with open(output_dir + '/summary.json', mode='w', encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
        with open(output_dir + '/users.json', mode='w', encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        with open(output_dir + '/games.json', mode='w', encoding="utf-8") as f:
            json.dump(games, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Stats from Steam reviews')
    parser.add_argument(
        '-i', '--input', help='Input file of reviews', required=False, default="./data/reviews.csv")
    parser.add_argument(
        '-o', '--output', help='Output dir for stats', required=False, default="./data/")
    args = parser.parse_args()

    process_reviews(args.input, args.output)


if __name__ == '__main__':
    main()
