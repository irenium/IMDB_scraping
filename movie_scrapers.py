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
    main_table = soup.findAll('table','wikitable',limit=1)[0]
    
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
            if type(a_tag)==bs4.element.Tag:
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
        
    def __init__(self, url_key):
        
        # Get movie metrics by scraping the main IMDB movie page:
        imdb_url = "http://www.imdb.com"+url_key
    
        response = requests.get(imdb_url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        title = soup.findAll("div","title_block")[0]
        rating = title.find("strong").get_text()
        num_ratings = title.find("div","imdbRating").a.get_text()
        release_year = title.find("div","title_wrapper").a.get_text()
        run_time = title.find("time").get_text()
        movie_title = title.find("h1")
    	movie_span = movie_title.span.decompose()
    	movie_title = movie_title.get_text()

    	find_bottom_pg_data = soup.findAll("h4","inline")
        for data in find_bottom_pg_data:
            if data.get_text() == "Production Co:":
                production_co = data.find_next_sibling().get_text()
            if data.get_text() == "Budget:":
                budget = data.nextSibling
            if data.get_text() == "Gross:":
                gross = data.nextSibling
        
        # Get full cast and crew by scraping the IMDB movie credits page:
        imdb_credits_url = "http://www.imdb.com"+url_key+"fullcredits?ref_=tt_cl_sm#cast"
    
        response_credits = requests.get(imdb_credits_url)
        credits_soup = bs4.BeautifulSoup(response_credits.text, "html.parser")
        credits_data = credits_soup.findAll("div","header")[0]
        
        # Store movie credits in a list of tuples of the form (name,role):
        full_credits = []

        # Store movie credits in a list of tuples of the form (name, team):
        credits_by_teams = []
        teamnames = []

        find_teamnames = credits_data.findAll("h4","dataHeaderWithBorder")
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
                
                if row.findAll("td","credit"):
                    role = row.findAll("td","credit",limit=1)[0].get_text()
        
                    full_credits.append((name,role))
                    credits_by_teams.append((name, teamnames[idx]))
                  
        self.rating = rating
        self.num_ratings = num_ratings
        self.release_year = release_year
        self.run_time = run_time
        self.full_credits = full_credits
        self.credits_by_teams = credits_by_teams
        self.movie_title = movie_title
        self.budget = budget
        self.gross = gross
        self.production_co = production_co

    def get_team_members(self, teamname):
        """
        Retrieves member names for a given team.
        (e.g., "Writing Credits" team) 
        """
        return [name for name,teamnames in self.credits_by_teams if teamname in teamnames]