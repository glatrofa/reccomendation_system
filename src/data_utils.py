import pandas as pd

MOVIES_PATH = '../movie_recommendation/data/output/movies.csv' # path to movies information
MOVIES_SIM_PATH = '../movie_recommendation/data/output/movies_similarity.csv' # path to movies similarities couples
DATA_PATH = 'data/data_recorded.csv' # path for storing user data

movies_data = ''
movies_sim_data = ''
movies_data_lower = ''

def load_data():
    global movies_data, movies_sim_data, movies_data_lower
    movies_sim_data = pd.read_csv(MOVIES_SIM_PATH)
    movies_data_lower = pd.read_csv(MOVIES_PATH)
    movies_data_lower['title'] = movies_data_lower['title'].str.lower()

def get_movie_from_name(movie_name: str):
    """Query offline db for movie information by movie name."""
    movie_name = movie_name.lower()
    global movies_data_lower
    result = movies_data_lower[movies_data_lower['title'].str.contains(movie_name)]
    # result.index.name = None
    # print((result['title']).to_string(index=False))
    return result.head(1)

def get_movie_from_id(movie_id: int):
    """Query offline db for movie information by movie id."""
    global movies_data_lower
    result = movies_data_lower[movies_data_lower['movieId'] == movie_id]

    return result.values.tolist()

def get_reccomended_movies(movie_id):
    # movie_id = int(movie_id)
    global movies_sim_data
    recommendations_df = movies_sim_data[movies_sim_data['movieId'] == int(movie_id)]
    reccomendations_list = recommendations_df['sim_movieId'].values.tolist()
    del recommendations_df
    
    return reccomendations_list
