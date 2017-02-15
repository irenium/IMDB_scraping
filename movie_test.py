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
                         movie_scrapers.get_imdb_links(u'Toy Story', u'1995'))
        self.assertEqual('/title/tt0431769/', 
                         movie_scrapers.get_imdb_links(u'Fumoon', u'1980'))
        self.assertEqual(None,
                        movie_scrapers.get_imdb_links(u'15 Sonyeon Uju Pyoryugi', u'1980'))
        self.assertEqual('/title/tt0356577/', 
                         movie_scrapers.get_imdb_links(u'Elysium', u'2003'))


if __name__ == '__main__':
    unittest.main()