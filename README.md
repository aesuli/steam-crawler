# STEAM crawler

Collection of small scripts to crawl Steam pages and extract game and review data for text-mining experiments.

## Overview

Work flow:
1. Crawl Steam search pages to collect game ids (games-crawler.py).
2. Extract game ids and titles from the downloaded search pages (games-extractor.py) → produces `data/games.csv`.
3. Crawl reviews for each game found in `data/games.csv` (reviews-crawler.py) → stores per-game review pages as zipped html under `data/pages/reviews/<language>/app-<id>/reviews.zip`.
4. Extract reviews from the downloaded per-game zip files into a single CSV (reviews-extractor.py) → produces `data/reviews.csv`.
5. (Optional) Detect language of each review text (reviews_add_language.py) → produces `data/reviews_language.csv`.
6. Produce aggregated statistics from `data/reviews.csv` (compute-stats.py) → writes `users.csv`, `games_stats.csv` and `summary.csv` under the chosen output directory.
7. Crawl Steam user pages given a `users.csv` input (users-crawler.py) → stores per-user zips under `data/pages/users/...`.

## Scripts

- games-crawler.py  
  Crawl Steam search result pages and save HTML pages under `data/pages/games/`. Use `-o` to change output base directory and `-f` to force re-download.

- games-extractor.py  
  Walks the downloaded search pages and extracts (package_type, game_id, game_title) into a CSV (default `./data/games.csv`).

- reviews-crawler.py  
  Given `data/games.csv`, downloads review pages for each app and stores them under `data/pages/reviews/<language>/app-<id>/reviews.zip`. Skips bundles. Configure language, timeouts and pauses via CLI options.

- reviews-extractor.py  
  Reads `data/pages/reviews/.../*/reviews.zip` and writes a flattened `data/reviews.csv`. Can filter games by title regex.

- reviews_add_language.py  
  Uses the lingua language detector to write `data/reviews_language.csv` with two columns: `review_id,language`. Adjusts CSV field size to handle long reviews.

- compute-stats.py  
  Uses dask/pandas to aggregate per-user and per-game statistics from `data/reviews.csv` and writes:
  - `users.csv` (username, profile_or_id, games, time_played)
  - `games_stats.csv` (game_id, title, reviews, recommended, not_recommended, time_played)
  - `summary.csv` (reviews, hours, users, games)

- users-crawler.py  
  Given a `users.csv` (must contain `username` and `profile_or_id` columns), downloads profile, games and friends pages for each user and stores them as per-user zip files under `data/pages/users/...`.

## reviews.csv columns

The extractor writes these columns (header order):
- review_id
- game_id
- game_title
- review_helpful
- review_funny
- username
- profile_or_id
- games_owned
- reviews_written
- recommended        (1 recommended, -1 not recommended)
- time_played        (hours on record, numeric string)
- review_date        (textual date as extracted)
- review_text

## Outputs

Default output locations (can be overridden via CLI options):
- Crawled pages: `data/pages/...`
- Extracted games: `data/games.csv`
- Extracted reviews: `data/reviews.csv`
- Reviews language: `data/reviews_language.csv`
- Aggregated stats: `data/users.csv`, `data/games_stats.csv`, `data/summary.csv`

## Dependencies

Install required packages before running:
- pandas, tqdm, beautifulsoup4
- dask and dask[distributed] (for compute-stats.py)
- lingua (for reviews_add_language.py)

`pip install -r requirements.txt`

## Notes

- The crawlers are polite to the server by default (configurable pause between requests).
- The project stores large volumes of HTML/zip files; ensure sufficient disk space.
- Use `-f` / `--force` on crawlers to re-download existing content.

