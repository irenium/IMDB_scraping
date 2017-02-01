import json
import numpy as np
import pandas as pd
from bokeh.palettes import Spectral6


def process_data():

    with open('movies.json','rb') as infile:
        movie_dicts = json.load(infile)

    movies_by_year = {}
    for movie in movie_dicts:
        try:
            year = int(movie["release_year"])
        except ValueError:
            continue

        if year < 1980:
            continue
        if year not in movies_by_year:
            movies_by_year[year] = []
        movies_by_year[year].append(movie)

    num_rows = 0
    for year, movie_list in movies_by_year.iteritems():
        num_rows = max(num_rows, len(movie_list))

    num_cols = len(movies_by_year)

    visual_fx_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    animators_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    studio_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = object)
    num_ratings_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)

    year_list = sorted(movies_by_year.keys())
    for col, year in enumerate(year_list):
        movie_list = movies_by_year[year]

        for row, movie in enumerate(movie_list):
            if movie["num_ratings"]:
                movie["num_ratings"] = int(movie["num_ratings"].replace(',',''))
            elif movie["num_ratings"] is None:
                movie["num_ratings"]=0
            credits_by_teams = movie["credits_by_teams"]
            visual_fx_array[row, col] = len(get_team_members(credits_by_teams, 
                                            "Visual Effects by"))
            animators_array[row, col] = len(get_team_members(credits_by_teams, 
                                            "Animation Department"))


            scale_factor = 10
            circle_size = np.sqrt(movie["num_ratings"] / np.pi) / scale_factor
            min_size = 3
            num_ratings_array[row, col] = max(circle_size, min_size)

            if movie["production_co"]:
                movie["production_co"] = movie["production_co"].replace('\n','')
                
            if movie["production_co"] == "Pixar Animation Studios":
                studio_array[row, col] = Spectral6[0]
            elif movie["production_co"] == "Walt Disney Pictures":
                studio_array[row, col] = Spectral6[1]
            elif movie["production_co"] == "DreamWorks Animation":
                studio_array[row, col] = Spectral6[2]
            elif movie["production_co"] == "Toei Animation":
                studio_array[row, col] = Spectral6[3]
            elif movie["production_co"] == "Madhouse":
                studio_array[row, col] = Spectral6[4]
            else:
                studio_array[row, col] = Spectral6[5]
    studios = ["Pixar Animation Studios", "Walt Disney Pictures", 
                "DreamWorks Animation", "Toei Animation", "Madhouse", 
                "Other"]

    return (pd.DataFrame(data = animators_array, columns = year_list),
            pd.DataFrame(data = visual_fx_array, columns = year_list),
            pd.DataFrame(data = num_ratings_array, columns = year_list),
            pd.DataFrame(data = studio_array, columns = year_list),
            year_list,
            studios)


def get_team_members(credits_by_teams, teamname):
    return [name for name, teamnames in credits_by_teams if teamname in teamnames]