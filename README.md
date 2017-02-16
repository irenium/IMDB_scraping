# Scraping IMDb to investigate resource allocation in animated movies

The blog post for this project can be found here: https://irenium.github.io/imdb/

### Details:

   movie_scrapers.py is comprised of the following:  
     scrape_movie_lists: takes a wikipedia url as input (string), and returns a list of movie titles  
     get_imdb_links: takes a movie title (unicode) and release year (unicode) as input, and returns the IMDb url key
  
   Movie class: takes an IMDb url key as input, and scrapes data from IMDb  
     Movie has the following methods:  
     get_team_members: takes a teamname as input (string), and returns a list of names for people on that team  
     to_dict: takes no input, and returns a dictionary representation of all movie data  
    
### Example:
   url_key = get_imdb_links(u'Toy Story', u'1995')  -->  '/title/tt0114709/'  
   toystory = Movie(url_key)  
   toystory.rating = 8.3  
   toystory.release_year = 1995  
   toystory.num_ratings = 655,191  
   toystory.production_co = Pixar Animation Studios  
   toystory.budget = $30,000,000  
  
