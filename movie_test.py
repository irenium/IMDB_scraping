import movie_scrapers
import unittest


class TestMovieScrapers(unittest.TestCase):
    """
    Check whether the function get_imdb_link fetches the correct url.
    Test cases should include movies with missing data, movies not
    listed on IMDb, and movies w/matching titles to non-animated films.
    """ 

    def test_url_key(self):

        self.assertEqual('/title/tt0114709/', 
                         movie_scrapers.get_imdb_links('Toy Story'))
        self.assertEqual('/title/tt0431769/', 
                         movie_scrapers.get_imdb_links('Fumoon'))
        self.assertEqual(None,
                        movie_scrapers.get_imdb_links('15 Sonyeon Uju Pyoryugi'))
        self.assertEqual('/title/tt0356577/', 
                         movie_scrapers.get_imdb_links('Elysium'))


if __name__ == '__main__':
    unittest.main()