# STEAM crawler

This set of scripts crawls STEAM website to download game reviews.

These scripts are aimed at students that want to experiment with text mining on review data.

The script have an order of execution.

  * _steam-game-crawler.py_ download pages that lists games into ./data/games/

  * _steam-game-extractor.py_ extracts games ids from the downloaded pages, saving them into ./data/games.csv
  
  * _steam-review-crawler.py_ uses the above list to download game reviews pages into ./data/reviews
  This process can take a long time (it's a lot of data and the script sleeps between requests to be fair with the server).
  When the script is stopped and restarted it will skip games for which all reviews have been downloaded on the previous run (it does not downloads new reviews for such games).
  
  * _steam-review-extractor.py_ extracts reviews and other info from the downloaded pages, saving them into ./data/reviews.csv 

Column in the reviews.csv file:
  * game id
  * number of people that found the review to be useful
  * number of people that found the review to be funny
  * username of the reviewer
  * number of games owned by the reviewer
  * number of reviews written by the reviewer
  * 1=recommended, -1=not recommended
  * hours played by the reviewer on the game
  * date of creation of the review
  * text of the review
  
The last script _steam-reviews-stats.py_ is a sample script that processes the review.csv file and outputs some basic info and stats in json files:

  * _./data/games.json_ number of reviews and played hours for every game.
  
  * _./data/users.json_ number of game owned (as reported by user's badge on STEAM) and number of played hours.
  
  * _./data/summary.json_ number of reviews, number of played hours, number of users, number of games.
  
On March 15, 2018 those last statistics are:

```
reviews        6614765
played hours 554702535
users          2720777
games            26677
```
  
