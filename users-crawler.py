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
import socket
import time
import urllib.request
import urllib.error
import urllib.parse
import zipfile
from contextlib import closing

import pandas as pd
from tqdm import tqdm


def download_page(url, maxretries, timeout, pause, user_agent="Mozilla/5.0"):
    tries = 0
    while tries < maxretries:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with closing(urllib.request.urlopen(req, timeout=timeout)) as f:
                data = f.read()
            time.sleep(pause)
            return data
        except (urllib.error.URLError, socket.timeout, socket.error):
            tries += 1
            time.sleep(pause)
    return None


def sanitize_filename(name):
    # simple sanitization to avoid problematic characters in filenames
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in str(name))


def process_users(users_file, out_base, timeout, maxretries, pause, force):
    df = pd.read_csv(users_file, dtype=str).fillna("")
    # expected columns: username, profile_or_id
    if 'username' not in df.columns:
        raise SystemExit("users.csv must contain a 'username' column")
    if 'profile_or_id' not in df.columns:
        # fallback: try to infer column name
        raise SystemExit("users.csv must contain a 'profile_or_id' column (values 'profiles' or 'id')")

    base_pages = os.path.join(out_base, "pages", "users")

    total_users = len(df)
    print(f"Processing {total_users} users from {users_file}")

    for _, row in tqdm(df.iterrows(), total=total_users, desc="users", unit="user"):
        username = str(row['username']).strip()
        profile_or_id = str(row['profile_or_id']).strip()

        if username == "":
            # skip empty entries but advance progress
            continue

        # separate users identified by profile from those by id.
        # use the last three letters (numbers) of profile to distribute profile-users
        # use the first two letters of id to distribute id-users
        if profile_or_id.lower() == 'profiles':
            suffix = username[-3:] if len(username) >= 3 else username
            user_dir = os.path.join(base_pages,"profile", suffix)
            os.makedirs(user_dir, exist_ok=True)
        elif profile_or_id.lower() == 'id':
            suffix = username[:2] if len(username) >= 2 else username
            user_dir = os.path.join(base_pages,"id", suffix)
            os.makedirs(user_dir, exist_ok=True)
        else:
            suffix = username[:2] if len(username) >= 2 else username
            user_dir = os.path.join(base_pages,"unknown", suffix)
            os.makedirs(user_dir, exist_ok=True)

        safe_username = sanitize_filename(username)
        zipname = f"{safe_username}.zip"
        zip_path = os.path.join(user_dir, zipname)

        if os.path.exists(zip_path) and not force:
            print(f"   skipping existing {zip_path}")
            continue

        # build URLs
        url_base = f"https://steamcommunity.com/{profile_or_id}/{urllib.parse.quote(username)}"
        urls = {
            "profile.html": url_base,
            "games.html": f"{url_base}/games/?tab=all",
            "friends.html": f"{url_base}/friends/"
        }

        contents = {}
        error = False

        for fname, url in tqdm(list(urls.items()), desc=f"   downloading {username}", leave=False, unit="file"):
            data = download_page(url, maxretries, timeout, pause)
            if data is None:
                print(f"   error downloading {url} -> skipping user {username}")
                error = True
                break
            contents[fname] = data

        if error:
            continue

        try:
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
                for fname, data in contents.items():
                    z.writestr(fname, data)
        except Exception as e:
            print(f"   failed writing zip for {username}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Crawler of Steam user pages")
    parser.add_argument(
        '-i', '--input', help='CSV file with users (columns: username, profile_or_id)', default='./data/users.csv')
    parser.add_argument(
        '-o', '--out', help='Output base path', default='data')
    parser.add_argument(
        '-t', '--timeout', help='Timeout in seconds for http connections. Default: 60', type=int, default=60)
    parser.add_argument(
        '-r', '--maxretries', help='Max retries to download a file. Default: 3', type=int, default=3)
    parser.add_argument(
        '-p', '--pause', help='Seconds to wait between http requests. Default: 1', type=float, default=1)
    parser.add_argument(
        '-f', '--force', help='Force download even if zip already exists', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out, exist_ok=True)

    process_users(args.input, args.out, args.timeout, args.maxretries, args.pause, args.force)


if __name__ == '__main__':
    main()
