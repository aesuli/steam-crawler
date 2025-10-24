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

from lingua import LanguageDetectorBuilder
import csv
import sys
from tqdm import tqdm

if __name__=="__main__":
    detector = LanguageDetectorBuilder.from_all_languages().build()

    csv.field_size_limit(sys.maxsize)

    with open('./data/reviews.csv', 'r', encoding='utf-8') as infile, \
        open('./data/reviews_language.csv', 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile, lineterminator='\n')
        writer.writerow(['review_id', 'language'])
        
        for row in tqdm(reader):
            review_text = row['review_text']
            language = detector.detect_language_of(review_text)
            language_code = language.iso_code_639_1.name.lower() if language else 'unknown'
            writer.writerow([row['review_id'], language_code])
