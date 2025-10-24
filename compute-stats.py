#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2025 Andrea Esuli (andrea@esuli.it)
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
import os

import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar


def process_reviews(inputfile_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Reading reviews CSV with dask: {inputfile_name}")
    df = dd.read_csv(inputfile_name, assume_missing=True, dtype=str)

    print("Ensuring expected columns exist")
    for col, default in [('time_played', 0.0), ('recommended', 0), ('profile_or_id', "")]:
        if col not in df.columns:
            print(f" - Column '{col}' missing, adding default")
            df[col] = default

    print("Converting numeric columns (dask, lazy)")
    df['time_played'] = dd.to_numeric(df['time_played'], errors='coerce').fillna(0.0)
    df['recommended'] = dd.to_numeric(df['recommended'], errors='coerce').fillna(0).astype(int)

    print("Building indicator columns")
    df['rec_is1'] = (df['recommended'] == 1).astype(int)
    df['not_rec'] = (df['recommended'] != 1).astype(int)

    print("Computing totals (this will run dask computations)")
    with ProgressBar():
        totalreviews = int(df.map_partitions(len).sum().compute())
    print(f" - total reviews: {totalreviews}")
    with ProgressBar():
        totalhours = float(df['time_played'].sum().compute())
    print(f" - total hours played: {totalhours:.2f}")

    print("Aggregating per-user stats (groupby username)")
    print(" - counting reviews per user")
    with ProgressBar():
        users_count = df.groupby('username').size().compute().rename('games')
    print(" - summing time_played per user")
    with ProgressBar():
        users_time = df.groupby('username')['time_played'].sum().compute().rename('time_played')
    print(" - taking first profile_or_id per user")
    with ProgressBar():
        users_profile = df.groupby('username')['profile_or_id'].first().compute().rename('profile_or_id')
    users_df = pd.concat([users_count, users_time, users_profile], axis=1)
    # ensure sensible defaults
    users_df['profile_or_id'] = users_df['profile_or_id'].fillna('').astype(str)
    users_df['games'] = users_df['games'].fillna(0).astype(int)
    users_df['time_played'] = users_df['time_played'].fillna(0.0).astype(float)
    print(f" - unique users: {len(users_df)}")

    # write users to CSV (username included as column)
    users_out = os.path.join(output_dir, "users.csv")
    print(f"Writing users CSV: {users_out}")
    users_df_reset = users_df.reset_index().rename(columns={users_df.index.name or 'index': 'username'})
    users_df_reset = users_df_reset[['username', 'profile_or_id', 'games', 'time_played']]
    users_df_reset.to_csv(users_out, index=False)
 
    print("Aggregating per-game stats (groupby game_id)")
    print(" - counting reviews per game")
    with ProgressBar():
        games_count = df.groupby('game_id').size().compute().rename('reviews')
    print(" - summing time_played per game")
    with ProgressBar():
        games_time = df.groupby('game_id')['time_played'].sum().compute().rename('time_played')
    print(" - taking first title per game")
    with ProgressBar():
        games_title = df.groupby('game_id')['game_title'].first().compute().rename('title')
    print(" - summing recommended / not_recommended per game")
    with ProgressBar():
        games_rec = df.groupby('game_id')['rec_is1'].sum().compute().rename('recommended')
    with ProgressBar():
        games_notrec = df.groupby('game_id')['not_rec'].sum().compute().rename('not_recommended')
 
    games_df = pd.concat([games_title, games_count, games_rec, games_notrec, games_time], axis=1).fillna(0)
    print(f" - unique games: {len(games_df)}")
 
    games_out = os.path.join(output_dir, "games_stats.csv")
    print(f"Writing games CSV: {games_out}")
    games_df = games_df.astype({
        'title': str,
        'reviews': int,
        'recommended': int,
        'not_recommended': int,
        'time_played': float
    }, errors='ignore')
    games_df_reset = games_df.reset_index().rename(columns={games_df.index.name or 'index': 'game_id'})
    games_df_reset = games_df_reset[['game_id', 'title', 'reviews', 'recommended', 'not_recommended', 'time_played']]
    games_df_reset.to_csv(games_out, index=False)
 
    summary = {
        'reviews': int(totalreviews),
        'hours': float(totalhours),
        'users': int(len(users_df)),
        'games': int(len(games_df))
    }
    summary_out = os.path.join(output_dir, "summary.csv")
    print(f"Writing summary CSV: {summary_out}")
    pd.DataFrame([summary]).to_csv(summary_out, index=False)
 
    print("Done.")


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
