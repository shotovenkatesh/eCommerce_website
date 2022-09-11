import requests

API_KEY = "9b103ab1054705e31dffe1fd97af9753"


class Movies:

    def __init__(self):
        self.page = 1
        self.movie_data = {
            "title": [],
            "overview": [],
            "poster": [],
            "release_date": [],
            "ratings": []
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
            self.page += 1

#         for key in self.movie_data:
#             print(self.movie_data[key][1])
#
#
# t = Movies()
# t.get_trending_movies()
