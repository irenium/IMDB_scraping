import csv
import json
import numpy as np
import pandas as pd
from bokeh.palettes import Spectral7


def process_data():
    """Process movie data and return organized dataframes"""

    # Cross-check JSON movie titles w/CSV file scraped from wikipedia:
    wiki_movie_titles  = []
    for row in csv.reader(open("movie_list.csv", "rb")):
        wiki_movie_titles.append(row[0].decode('utf-8'))
    with open('movies.json','rb') as infile:
        movie_dicts = json.load(infile)
    valid_movie_dicts = []
    wiki_set = set(wiki_movie_titles)

    for movie in movie_dicts:
        movie_name = movie.get("title", None)
        if movie_name and movie_name.strip() in wiki_set:
            valid_movie_dicts.append(movie)

    # Create a dictionary with release year as key, and
    # mapped to a list of movies released that year:
    movies_by_year = {}
    for movie in valid_movie_dicts:
        try:
            year = int(movie["release_year"])
        except ValueError:
            continue
        if year < 1980:
            continue
        if year not in movies_by_year:
            movies_by_year[year] = []
        movies_by_year[year].append(movie)

    # Find the maximum # of movies released in a given year:
    num_rows = 0
    for year, movie_list in movies_by_year.iteritems():
        num_rows = max(num_rows, len(movie_list))
    num_cols = len(movies_by_year)

    # Initialize empty arrays (of equal dimensions) to store data:
    visual_fx_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    animators_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    studio_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = object)
    title_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = object)
    num_ratings_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    ratings_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    allcrew_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)

    # Fill in the empty arrays with data:
    year_list = sorted(movies_by_year.keys())
    for col, year in enumerate(year_list):
        movie_list = movies_by_year[year]

        for row, movie in enumerate(movie_list):
            if movie["num_ratings"]:
                movie["num_ratings"] = int(movie["num_ratings"].replace(',',''))
            elif movie["num_ratings"] is None:
                movie["num_ratings"] = 0
            if movie["rating"]:
                movie["rating"] = float(movie["rating"])
            elif movie["rating"] is None:
                movie["rating"] = 0
            ratings_array[row, col] = movie["rating"]

            credits_by_teams = movie["credits_by_teams"]
            allcrew_array[row, col] = len(movie["full_credits"])
            visual_fx_array[row, col] = len(get_team_members(credits_by_teams, 
                                            "Visual Effects by"))
            animators_array[row, col] = len(get_team_members(credits_by_teams, 
                                            "Animation Department"))

            title_array[row, col] = movie["title"].strip().replace('\n', ' ')

            # Scale bubble size for plotting:
            scale_factor = 10
            circle_size = np.sqrt(movie["num_ratings"] / np.pi) / scale_factor
            min_size = 3
            num_ratings_array[row, col] = max(circle_size, min_size)

            if movie["production_co"]:
                movie["production_co"] = movie["production_co"].replace('\n','')
            
            # Select which studios to highlight on the plot:
            if movie["production_co"] == "Pixar Animation Studios":
                studio_array[row, col] = Spectral7[0]
            elif movie["production_co"] == "Walt Disney Pictures":
                studio_array[row, col] = Spectral7[1]
            elif movie["production_co"] == "DreamWorks Animation":
                studio_array[row, col] = Spectral7[2]
            elif movie["production_co"] == "Toei Animation":
                studio_array[row, col] = Spectral7[3]
            elif movie["production_co"] == "Warner Bros.":
                studio_array[row, col] = Spectral7[4]
            elif movie["production_co"] == "Bandai Visual Company":
                studio_array[row, col] = Spectral7[5]
            else:
                studio_array[row, col] = Spectral7[6]

    studios = ["Pixar Animation Studios", "Walt Disney Pictures", 
                "DreamWorks Animation", "Toei Animation", "Warner Bros.", 
                "Bandai Visual Company", "Other"]

    return (pd.DataFrame(data = animators_array, columns = year_list),
            pd.DataFrame(data = visual_fx_array, columns = year_list),
    #return (pd.DataFrame(data = ratings_array, columns = year_list),
    #        pd.DataFrame(data = allcrew_array, columns = year_list),
            pd.DataFrame(data = num_ratings_array, columns = year_list),
            pd.DataFrame(data = studio_array, columns = year_list),
            pd.DataFrame(data = title_array, columns = year_list),
            year_list,
            studios)


def get_team_members(credits_by_teams, teamname):
    """Takes a teamname as input (in string representation),
    and returns a list of names for people on that team
    (e.g., "Writing Credits" team)"""

    return [name for name, teamnames in credits_by_teams if teamname in teamnames]