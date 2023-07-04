from tmdbv3api import TMDb, Movie
import time


d = time.time()
tmdb = TMDb()
tmdb.api_key = 'a5beed50b62bc4886b8da6bb2b823fa3'
tmdb.language = 'fr'
tmdb.debug = True

movie = Movie()
id = movie.search("")[0].id
print(movie.similar(id)[0].title)