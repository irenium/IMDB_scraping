import json
import csv
import sys
import movie_scrapers

# Make a list of movie dictionaries:

movie_dicts = []
movie_urls  = []
for row in csv.reader(open("imdb_url_list.csv", "rb")):
    movie_urls.append(row[0])
current_idx = 0
m = len(movie_urls)

for url in movie_urls:
    movie_object = movie_scrapers.Movie(url)
    movie_dicts.append(movie_object.to_dict())
    
    if (current_idx % 10) == 0:
        progress = 100.0 * current_idx / m
        sys.stdout.write('\r progress {} / {} ({:6.2f}%)'.format(current_idx, m, progress))
        sys.stdout.flush()
    current_idx += 1
        
print len(movie_dicts)    

# Write list of movie dictionaries to a json file:

with open('movies_6feb2017.json','wb') as outfile:
    json.dump(movie_dicts, outfile, indent = 2, separators = (',',': '))