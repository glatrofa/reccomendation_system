import pandas as pd

MOVIES_PATH = '../movie_recommendation/data/output/movies.csv' # path to movies information
MOVIES_SIM_PATH = '../movie_recommendation/data/output/movies_similarity.csv' # path to movies similarities couples
DATA_PATH = 'data/data_recorded.csv' # path for storing user data

mov_df = ''
mov_sim_df = ''

def load_data():
    global mov_df, mov_sim_df,
    mov_sim_df = pd.read_csv(MOVIES_SIM_PATH)
    # mov_sim_df = mov_sim_df.set_index('movieId')
    mov_df = pd.read_csv(MOVIES_PATH)
    # mov_df = mov_df.set_index('movieId')

def get_movie_from_name(movie_name: str):
    """Query offline db for movie information by movie name."""
    global mov_df
    movie = mov_df[mov_df['title'].str.contains(movie_name, case=False)].iloc[0, :]
    result = mov_df[mov_df['movieId'] == movie['movieId']]
    # result.index.name = None
    # print((result['title']).to_string(index=False))
    return result.head(1)

def get_movie_from_id(movie_id: int):
    """Query offline db for movie information by movie id."""
    global mov_df
    result = mov_df[mov_df['movieId'] == movie_id]

    return result.values.tolist()

def get_reccomended_movies(movie_id):
    # movie_id = int(movie_id)
    global mov_sim_df
    recommendations_df = mov_sim_df[mov_sim_df['movieId'] == int(movie_id)]
    reccomendations_list = recommendations_df['sim_movieId'].values.tolist()
    del recommendations_df
    
    return reccomendations_list
