import bs4
import nltk
import requests
import sys
import time


def scrape_movie_lists(url):
    """
    Scrapes wikipedia page showing animated movie
    lists by year. Takes a url (string) as input,
    and returns a list of movie titles.
    """

    # Get web page
    response = requests.get(url)

    # Create soup object from page content
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    main_table = soup.findAll('table', 'wikitable', limit=1)[0]

    # Get table rows
    table_rows = main_table.findAll("tr")

    list_of_movies = []

    # Get movie titles
    for row in table_rows:
        cols = row.findAll('td', limit=1)

        for td in cols:

            # Filter by i tag since "small" tag is foreign movie title
            a_tag = td.i.a
            if type(a_tag) == bs4.element.Tag:
                list_of_movies.append(a_tag.get_text())
            else:
                pass

    return list_of_movies


def get_imdb_links(title, year):
    """
    Scrapes IMDB site and returns the unique IMDB url key
    for movie of interest. Takes the movie title (unicode)
    and release year (unicode) as input, and returns a url key.
    """

    # Convert input title into an IMDB search:
    tokenized_title = ""
    for token in nltk.word_tokenize(title):
        tokenized_title += token + "+"
    imdb_search = "http://www.imdb.com/find?ref_=nv_sr_fn&q=" + \
        tokenized_title + "&s=tt"

    # Get web page, and create Soup object:
    response = requests.get(imdb_search)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    # Return None if there are 0 search results for the movie:
    if len(soup.findAll('table', "findList", limit=1)) == 0:
        return None

    # Save URL w/movie key by finding the matching title and year:
    else:
        main_table = soup.findAll('table', "findList", limit=1)[0]
        table_rows = main_table.findAll("tr", limit=1)

        for row in table_rows:
            cols = row.findAll('td', "result_text", limit=1)

            for td in cols:
                store_movie_key = td.a.get('href')[0:17]
                movie_name = td.a.get_text()                
                strip_title = td.a.decompose()
                search_result_year = td.get_text()[3:7]
                
                if movie_name == title and search_result_year == year:
                    movie_key = store_movie_key
                else:
                    return None
                                
    return movie_key


def persistent_get(url):
    """Takes a url as input and continues to fetch the url
        if a ConnectionError is received"""

    for try_num in range(0, 100): # pylint: disable=unused-variable
        try:
            return requests.get(url)
        except requests.ConnectionError:
            time.sleep(0.5)
    sys.stderr.write("WARNING: failed to fetch {}.\n".format(url))
    return None


class Movie:
    """Collection of information about a single movie."""

    def __init__(self, url_key):

        self.movie_title = None
        self.budget = None
        self.gross = None
        self.production_co = None
        self.rating = None
        self.num_ratings = None
        self.release_year = None
        self.run_time = None

        imdb_url = "http://www.imdb.com" + url_key
        self.set_movie_metrics(imdb_url)

        self.full_credits = None
        self.credits_by_teams = None

        imdb_credits_url = "http://www.imdb.com" + \
            url_key + "fullcredits?ref_=tt_cl_sm#cast"
        self.set_credits_info(imdb_credits_url)

    def set_movie_metrics(self, url):
        """Get movie metrics by scraping the main IMDB page."""

        response = persistent_get(url)
        if response is None:
            return
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        bottom_pg_data = soup.findAll("h4", "inline")
        for data in bottom_pg_data:
            if data.get_text() == "Production Co:":
                self.production_co = data.find_next_sibling().get_text()
            elif data.get_text() == "Budget:":
                self.budget = data.nextSibling
            elif data.get_text() == "Gross:":
                self.gross = data.nextSibling

        title = soup.findAll("div", "title_block")[0]

        rating_tag = title.find("strong")
        if rating_tag:
            self.rating = rating_tag.get_text()
        num_ratings_tag = title.find("div", "imdbRating")
        if num_ratings_tag and num_ratings_tag.a:
            self.num_ratings = num_ratings_tag.a.get_text()
        release_year_tag = title.find("div", "title_wrapper")
        if release_year_tag and release_year_tag.a:
            self.release_year = release_year_tag.a.get_text()
        run_time_tag = title.find("time")
        if run_time_tag:
            self.run_time = run_time_tag.get_text()

        movie_title = title.find("h1")
        if movie_title and movie_title.span:
            movie_span = movie_title.span.decompose()
            self.movie_title = movie_title.get_text()

    def set_credits_info(self, url):
        """Get full cast and crew by scraping IMDB credits page."""

        response_credits = persistent_get(url)
        if response_credits is None:
            return
        credits_soup = bs4.BeautifulSoup(response_credits.text, "html.parser")
        credits_data = credits_soup.findAll("div", "header")[0]

        # Store movie credits in a list of tuples of the form (name,role):
        self.full_credits = []

        # Store movie credits in a list of tuples of the form (name, team):
        self.credits_by_teams = []
        teamnames = []

        teamnames_list = credits_data.findAll("h4", "dataHeaderWithBorder")
        for teamname in teamnames_list:
            teamnames.append(teamname.get_text())

        team_tables = credits_data.findAll("table")

        for idx, table in enumerate(team_tables):
            crew_byrow = table.findAll("tr")

            for row in crew_byrow:
                tds = row.findAll('td')

                for td in tds:
                    if td.a:
                        name = td.a.get_text()

                if row.findAll("td", "credit"):
                    role = row.findAll("td", "credit", limit=1)[0].get_text()

                    self.full_credits.append((name, role))
                    self.credits_by_teams.append((name, teamnames[idx]))

    def get_team_members(self, teamname):
        """Takes a teamname as input (in string representation),
        and returns a list of names for people on that team
        (e.g., "Writing Credits" team)"""

        return [name for name, teamnames in self.credits_by_teams if teamname in teamnames]

    def to_dict(self):
        """Returns a dictionary representation of the movie data"""

        return {"title": self.movie_title,
                "budget": self.budget,
                "gross": self.gross,
                "production_co": self.production_co,
                "rating": self.rating,
                "num_ratings": self.num_ratings,
                "release_year": self.release_year,
                "run_time": self.run_time,
                "full_credits": self.full_credits,
                "credits_by_teams": self.credits_by_teams}
