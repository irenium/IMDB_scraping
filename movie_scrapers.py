import bs4
import requests
import nltk

def scrape_movie_lists(url):
    """
    Scrapes a wikipedia url and returns the
    movie titles for a given year (code is specific
    to wikipedia's animated movie lists by year).
    """
    
    # Get web page
    response = requests.get(url)

    # Create soup object from page content
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    main_table = soup.findAll('table', 'wikitable', limit=1)[0]
    
    # Get table rows
    trs = main_table.findAll("tr")

    list_of_movies = []
    list_of_techniques = [] # Currently not being used
    
    # Get movie titles
    for row in trs:        
        cols = row.findAll('td', limit=1)
        
        for td in cols:
            
            # Filter by the i tag since the "small" tag includes foreign languages
            i_tag = td.i
            a_tag = i_tag.a
            if type(a_tag) == bs4.element.Tag:
                list_of_movies.append(a_tag.get_text())  
            else: 
                pass
    
    return list_of_movies

def get_imdb_links(title):
    """
    Scrapes IMDB site and returns the IMDB main url
    for movie of interest. 
    """
     
    # Convert input title into an IMDB search:
    tokenized_title = ""
    for token in nltk.word_tokenize(title):
        tokenized_title += token+"%20"
    imdb_search = "http://www.imdb.com/find?q="+tokenized_title+"&s=tt&ttype=ft&ref_=fn_ft"
    
    # Get web page, and create Soup object:
    response = requests.get(imdb_search)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    # Return None if there are 0 search results for the movie:
    if len(soup.findAll('table', "findList", limit=1))==0:
        return None
    
    # Save URL w/movie key by finding the first result in the table:
    else:
        main_table = soup.findAll('table', "findList", limit=1)[0]
        trs = main_table.findAll("tr", limit=1)
    
        for row in trs:        
            cols = row.findAll('td', "result_text", limit=1)
        
            for td in cols:
                a_tag = td.a
                movie_key = a_tag.get('href')
        
    return movie_key

class Movie:
    """Collection of information about a single movie."""

    def set_movie_metrics(self, url):
        """Get movie metrics by scraping the main IMDB page."""

        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        find_bottom_pg_data = soup.findAll("h4", "inline")
        for data in find_bottom_pg_data:
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
        num_ratings_tag = title.find("div", "imdbRating").a
        if num_ratings_tag:
        	self.num_ratings = num_ratings_tag.get_text()
        release_year_tag = title.find("div", "title_wrapper").a
        if release_year_tag:
            self.release_year = release_year_tag.get_text()    
        run_time_tag = title.find("time")
        if run_time_tag:
            self.run_time = run_time_tag.get_text()

        movie_title = title.find("h1")
        movie_span = movie_title.span.decompose()
        self.movie_title = movie_title.get_text()

    def set_credits_info(self, url):
        """Get full cast and crew by scraping IMDB credits page."""

        response_credits = requests.get(url)
        credits_soup = bs4.BeautifulSoup(response_credits.text, "html.parser")
        credits_data = credits_soup.findAll("div", "header")[0]
        
        # Store movie credits in a list of tuples of the form (name,role):
        self.full_credits = []

        # Store movie credits in a list of tuples of the form (name, team):
        self.credits_by_teams = []
        teamnames = []

        find_teamnames = credits_data.findAll("h4", "dataHeaderWithBorder")
        for teamname in find_teamnames:
            teamnames.append(teamname.get_text())
        
        team_tables = credits_data.findAll("table")
    
        for idx,table in enumerate(team_tables):
            crew_byrow = table.findAll("tr")
        
            for row in crew_byrow:
                tds = row.findAll('td')
        
                for td in tds:
                    if td.a:
                        name = td.a.get_text()
                
                if row.findAll("td", "credit"):
                    role = row.findAll("td", "credit", limit=1)[0].get_text()
        
                    self.full_credits.append((name,role))
                    self.credits_by_teams.append((name, teamnames[idx]))
                      
    def __init__(self, url_key):
        
        self.budget = None
        self.gross = None
        self.production_co = None
        self.rating = None
        self.num_ratings = None
        self.release_year = None
        self.run_time = None
        self.movie_title = None  

        imdb_url = "http://www.imdb.com"+url_key
        self.set_movie_metrics(imdb_url)

        self.full_credits = None
        self.credits_by_teams = None

        imdb_credits_url = "http://www.imdb.com"+url_key+"fullcredits?ref_=tt_cl_sm#cast"
        self.set_credits_info(imdb_credits_url)

    def get_team_members(self, teamname):
        """
        Retrieves member names for a given team.
        (e.g., "Writing Credits" team) 
        """
        return [name for name, teamnames in self.credits_by_teams if teamname in teamnames]