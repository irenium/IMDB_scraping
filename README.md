# Scraping IMDb to investigate resource allocation in animated movies

Animated movies often have impressive stories with witty dialogue. In fact, I would guess that production companies invest more in having a quality writing team for an animated movie versus a non-animated movie, where a great cast can steal the show and make up for a dumb story. But not all animated movies are created equal. Some animated movies have dialogue that falls flat, but make up for it with impressive animation. To investigate the impact of crew size (including writing team, animation team, visual effects team, etc) on movie success, I scraped data for ~2000 animated movies from IMDb.

### Details:

   movie_scrapers.py is comprised of the following:  
     scrape_movie_lists: takes a wikipedia url as input (string), and returns a list of movie titles  
     get_imdb_links: takes a movie title as input (string), and returns the IMDb url key  
  
   Movie class: takes an IMDb url key as input (string), and scrapes data from IMDb  
     Movie has the following methods:  
     get_team_members: takes a teamname as input (string), and returns a list of names for people on that team  
     to_dict: takes no input, and returns a dictionary representation of all movie data  
    
### Example:
   url_key = get_imdb_links('Toy Story')  -->  '/title/tt0114709/'  
   toystory = Movie(url_key)  
   toystory.rating = 8.3  
   toystory.release_year = 1995  
   toystory.num_ratings = 655,191  
   toystory.production_co = Pixar Animation Studios  
   toystory.budget = $30,000,000  
  
