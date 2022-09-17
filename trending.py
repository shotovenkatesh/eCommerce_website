import requests

API_KEY = "9b103ab1054705e31dffe1fd97af9753"
GENRE = { 28: 'Action', 12: 'Adventure',  16: 'Animation',
          35: 'Comedy', 80: 'Crime',  99: 'Documentary',
          18: 'Drama', 10751: 'Family',  14: 'Fantasy',
          36: 'History', 27: 'Horror',  10402: 'Music',
          9648: 'Mystery', 10749: 'Romance',  878: 'Science Fiction',
          10770: 'TV Movie', 53: 'Thriller',  10752: 'War',
          37: 'Western'}



class Movies:

    def __init__(self):
        self.page = 1
        self.movie_data = {
            "title": [],
            "overview": [],
            "poster": [],
            "release_date": [],
            "ratings": [],
            "genre": [],
            "duration": []
        }

    def get_trending_movies(self):
        while self.page < 6:
            response = requests.get(
                f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}&page={self.page}")
            data = response.json()
            for result in data["results"]:
                self.movie_data["title"].append(result['title'])
                self.movie_data["overview"].append(result['overview'])
                self.movie_data["poster"].append(f"https://image.tmdb.org/t/p/original{result['poster_path']}")
                self.movie_data["release_date"].append(result['release_date'])
                self.movie_data["ratings"].append(result['vote_average'])
                g_list = [GENRE[g] for g in result['genre_ids']]
                self.movie_data["genre"].append(g_list)


                # for g in result['genre_ids']:
                #     self.movie_data["genre"].append(GENRE[g])
                # self.genre.append()

            self.page += 1

    def find_movie(self,movie_name):
        movie_request = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}")
        movie_data = movie_request.json()["results"][0]
        # print(movie_data)
        g_list = [GENRE[g] for g in movie_data['genre_ids']]
        movie_info = {
            "title" : movie_data["original_title"],
            "overview" : movie_data["overview"],
            "poster" : f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}",
            "release_date" : movie_data["release_date"],
            "genre" : g_list,
            "ratings" : movie_data["vote_average"]
        }
        # print(movie_info)
        return movie_info

    def get_genre(self):
        print(self.movie_data["genre"])

    # for key in self.movie_data:
    #     print(self.movie_data[key])

#
# t = Movies()
# t.find_movie("one piece red")
