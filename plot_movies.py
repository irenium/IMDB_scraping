import csv
import jinja2
import json
import numpy as np
import pandas as pd

from bokeh.core.templates import JS_RESOURCES
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource, Plot, Circle, Range1d,
    LinearAxis, HoverTool, Text, HoverTool,
    SingleIntervalTicker, Slider, CustomJS)
from bokeh.palettes import Spectral7
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import CDN


def process_data_teams():
    """Process movie teams and return organized dataframes"""

    with open('movies_6feb2017.json','rb') as infile:
        movie_dicts = json.load(infile)
    
    # Create a dictionary with release year as key, and
    # mapped to a list of movies released that year:
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

    # Find the maximum # of movies released in a given year:
    num_rows = 0
    for year, movie_list in movies_by_year.iteritems():
        num_rows = max(num_rows, len(movie_list))
    num_rows = num_rows*7
    num_cols = len(movies_by_year)

    allcrew_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    title_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = object)
    num_ratings_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    ratings_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    gross_array =  np.full(shape = (num_rows, num_cols), fill_value=None, dtype = float)
    teams_array = np.full(shape = (num_rows, num_cols), fill_value=None, dtype = object)

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
            if movie["gross"]:
                movie["gross"] = float(movie["gross"].strip().replace(',','').replace('$',''))
            elif movie["gross"] is None:
                movie["gross"] = 0
                
            # Scale bubble size for plotting:
            scale_factor = 1
            circle_size = np.sqrt(movie["gross"] / (100000 * np.pi)) / scale_factor
            min_size = 3

            for dummy_idx in range(7):
                title_array[row*7+dummy_idx, col] = movie["title"].strip().replace('\n', ' ')             
                num_ratings_array[row*7+dummy_idx, col] = movie["num_ratings"]              
                ratings_array[row*7+dummy_idx, col] = movie["rating"]               
                gross_array[row*7+dummy_idx, col] = max(circle_size, min_size)

            credits_by_teams = movie["credits_by_teams"]
            allcrew_array[row*7, col] = len(get_team_members(credits_by_teams, 
                                            "Animation Department"))
            teams_array[row*7, col] = Spectral7[0] 
            allcrew_array[row*7+1, col] = len(get_team_members(credits_by_teams, 
                                            "Visual Effects by"))
            teams_array[row*7+1, col] = Spectral7[1] 
            allcrew_array[row*7+2, col] = len(get_team_members(credits_by_teams, 
                                            "Music Department"))
            teams_array[row*7+2, col] = Spectral7[2] 
            allcrew_array[row*7+3, col] = len(get_team_members(credits_by_teams, 
                                            "Art Department"))
            teams_array[row*7+3, col] = Spectral7[3] 
            allcrew_array[row*7+4, col] = len(get_team_members(credits_by_teams, 
                                            "Writing Credits"))
            teams_array[row*7+4, col] = Spectral7[4] 
            allcrew_array[row*7+5, col] = len(get_team_members(credits_by_teams, 
                                            "Produced by")) 
            teams_array[row*7+5, col] = Spectral7[5] 
            allcrew_array[row*7+6, col] = len(movie["full_credits"])
            teams_array[row*7+6, col] = Spectral7[6] 

    teams = ["Animation Dept", "Visual Effects Dept", 
                "Music Dept", "Art Dept", "Writers", 
                "Producers", "Total Crew"]

    return (pd.DataFrame(data = ratings_array, columns = year_list),
            pd.DataFrame(data = allcrew_array, columns = year_list),
            pd.DataFrame(data = gross_array, columns = year_list),
            pd.DataFrame(data = teams_array, columns = year_list),
            pd.DataFrame(data = title_array, columns = year_list),
            year_list,
            teams)

def process_data():
    """Process movie data and return organized dataframes"""

    # Cross-check JSON movie titles w/CSV file scraped from wikipedia:
    wiki_movie_titles  = []
    for row in csv.reader(open("movie_list.csv", "rb")):
        wiki_movie_titles.append(row[0].decode('utf-8'))
    with open('movies_6feb2017.json','rb') as infile:
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


def make_interactive_plot():
    """Copied from bokeh tutorials, and modified to make movie interactive plot"""

    x_axis_df, y_axis_df, bubble_df, colors_df, labels_df, years, teams = process_data_teams()
    
    sources = {}

    for year in years:
        team_color = colors_df[year]
        team_color.name = 'team_color'
        
        x_variable = x_axis_df[year]
        x_variable.name = 'x_variable'
        y_variable = y_axis_df[year]
        y_variable.name = 'y_variable'
        bubble_variable = bubble_df[year]
        bubble_variable.name = 'bubble_variable'
        labels = labels_df[year]
        labels.name = 'labels'
        new_df = pd.concat([x_variable, y_variable, bubble_variable, team_color, labels], axis=1)
        sources['_' + str(year)] = ColumnDataSource(new_df)

    dictionary_of_sources = dict(zip([x for x in years], ['_%s' % x for x in years]))
    js_source_array = str(dictionary_of_sources).replace("'", "")

    xdr = Range1d(1, 10)
    ydr = Range1d(-50, 1200)
    plot = Plot(
        x_range=xdr,
        y_range=ydr,
        plot_width=800,
        plot_height=400,
        outline_line_color=None,
        toolbar_location=None,
        sizing_mode="scale_width",
    )
    AXIS_FORMATS = dict(
        minor_tick_in=None,
        minor_tick_out=None,
        major_tick_in=None,
        major_label_text_font_size="12pt",
        major_label_text_font_style="normal",
        axis_label_text_font_size="12pt",

        axis_line_color='#AAAAAA',
        major_tick_line_color='#AAAAAA',
        major_label_text_color='#666666',

        major_tick_line_cap="round",
        axis_line_cap="round",
        axis_line_width=1,
        major_tick_line_width=1,
    )

    xaxis = LinearAxis(ticker=SingleIntervalTicker(interval=1), axis_label="IMDb Rating", **AXIS_FORMATS)
    yaxis = LinearAxis(ticker=SingleIntervalTicker(interval=100), axis_label="Team Size", **AXIS_FORMATS)
    plot.add_layout(xaxis, 'below')
    plot.add_layout(yaxis, 'left')

    # ### Add the background year text
    # We add this first so it is below all the other glyphs
    text_source = ColumnDataSource({'year': ['%s' % years[0]]})
    text = Text(x=2, y=35, text='year', text_font_size='150pt', text_color='#EEEEEE')
    #plot.add_glyph(text_source, text)

    # Add the circle
    renderer_source = sources['_%s' % years[0]]
    circle_glyph = Circle(
        x='x_variable', y='y_variable', size='bubble_variable',
        fill_color='team_color', fill_alpha=0.8,
        line_color='#7c7e71', line_width=0.5, line_alpha=0.5)
    circle_renderer = plot.add_glyph(renderer_source, circle_glyph)

    # Add the hover (only against the circle and not other plot elements)
    tooltips = "@labels"
    plot.add_tools(HoverTool(tooltips=tooltips, renderers=[circle_renderer]))

    # Add the legend
    text_x = 2
    text_y = 1150
    for i, team in enumerate(teams):
        plot.add_glyph(Text(x=text_x, y=text_y, text=[team], text_font_size='10pt', text_color='#666666'))
        plot.add_glyph(Circle(x=text_x - 0.1, y=text_y + 25, fill_color=Spectral7[i], size=10, line_color=None, fill_alpha=0.8))
        text_y = text_y - 50

    # Add the slider
    code = """
        var year = slider.get('value'),
            sources = %s,
            new_source_data = sources[year].get('data');
        renderer_source.set('data', new_source_data);
        text_source.set('data', {'year': [String(year)]});
    """ % js_source_array

    callback = CustomJS(args=sources, code=code)
    slider = Slider(start=years[0], end=years[-1], value=1, step=1, title="Year", callback=callback, name='testy')
    callback.args["renderer_source"] = renderer_source
    callback.args["slider"] = slider
    callback.args["text_source"] = text_source

    # Lay it out
    return column(plot, slider)

HTML_TEMPLATE ="""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{{ title if title else "Bokeh Plot" }}</title>
        <link href="assets/gapminder_styles.css" type="text/css" rel="stylesheet" />
    </head>
    <body>
        {{ plot_div|indent(8) }}
        {{ bokeh_js|indent(8) }}
        {{ plot_script|indent(8) }}
    </body>
</html>
"""


def write_plot_html():
    """Saves interactive plot as html (copied from bokeh tutorials)"""

    layout = make_interactive_plot()
    template = jinja2.Template(HTML_TEMPLATE)
    script, div = components(layout)
    html = template.render(
        title="Resource Allocation in Animated Movies",
        bokeh_js=JS_RESOURCES.render(js_raw=CDN.js_raw, js_files=CDN.js_files),
        plot_script=script,
        plot_div=div,
    )
    with open('interactive_plot_for_web2.html', 'wb') as outfile:
        outfile.write(html)
