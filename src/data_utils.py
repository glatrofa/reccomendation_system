import pandas as pd

MOV_PATH = '../movie_recommendation/data/output/movies.csv' # path to movies information
MOV_SIM_PATH = '../movie_recommendation/data/output/movies_similarity.csv' # path to movies similarities couples
DATA_PATH = 'data/data_recorded.csv' # path for storing user data
SG_COS_SIM = '../counterfactual-explanation/data/genres_cosine_similarity.csv'
ST_COS_SIM = '../counterfactual-explanation/data/tags_cosine_similarity.csv'

mov_df = ''
mov_sim_df = ''
sg_cos_sim_df = ''
st_cos_sim_df = ''


def load_data():
    global mov_df, mov_sim_df, sg_cos_sim_df, st_cos_sim_df
    mov_sim_df = pd.read_csv(MOV_SIM_PATH)
    # mov_sim_df = mov_sim_df.set_index('movieId')
    mov_df = pd.read_csv(MOV_PATH)
    # mov_df = mov_df.set_index('movieId')
    sg_cos_sim_df = pd.read_csv(SG_COS_SIM)
    st_cos_sim_df = pd.read_csv(ST_COS_SIM)
    # sg_cos_sim_df = sg_cos_sim_df.set_index('movieId')


def get_movie_from_name(movie_name: str):
    """Query offline db for movie information by movie name."""
    global mov_df
    movie = mov_df[mov_df['title'].str.contains(movie_name, case=False)].iloc[0, :]
    result = mov_df[mov_df['movieId'] == movie['movieId']]
    # result.index.name = None
    # print((result['title']).to_string(index=False))
    return result.head(1)


def get_movie_from_id(movie_id):
    """Query offline db for movie information by movie id."""
    global mov_df
    result = mov_df[mov_df['movieId'] == int(movie_id)]

    return result.values.tolist()


def get_reccomended_movies(movie_id):
    # movie_id = int(movie_id)
    global mov_sim_df
    recommendations_df = mov_sim_df[mov_sim_df['movieId'] == int(movie_id)]
    reccomendations_list = recommendations_df['sim_movieId'].values.tolist()
    del recommendations_df
    
    return reccomendations_list


def cf_genres_get_similar(movie_id):
    global sg_cos_sim_df
    # df = sg_cos_sim_df.loc[sg_cos_sim_df.index == int(movie_id)].reset_index(). \
    #         melt(id_vars='movieId', var_name='sim_movieId', value_name='relevance'). \
    #         sort_values('relevance', axis=0, ascending=False)
    recommendations_df = sg_cos_sim_df[sg_cos_sim_df['movieId'] == int(movie_id)]
    reccomendations_list = recommendations_df['sim_movieId'].values.tolist()
    del recommendations_df
    # print(df.head())
    # print("ciao")
    # print(df.tolist())
    # print("ciao")
    # df = df.iloc[0, :]
    # print("ciao")
    # print(df)
    return reccomendations_list[0]


def cf_tags_get_similar(movie_id):
    global st_cos_sim_df
    # df = sg_cos_sim_df.loc[sg_cos_sim_df.index == int(movie_id)].reset_index(). \
    #         melt(id_vars='movieId', var_name='sim_movieId', value_name='relevance'). \
    #         sort_values('relevance', axis=0, ascending=False)
    recommendations_df = st_cos_sim_df[st_cos_sim_df['movieId'] == int(movie_id)]
    reccomendations_list = recommendations_df['sim_movieId'].values.tolist()
    print(recommendations_df)
    # print(recommendations_list)
    del recommendations_df
    # print(df.head())
    # print("ciao")
    # print(df.tolist())
    # print("ciao")
    # df = df.iloc[0, :]
    # print("ciao")
    # print(df)
    return reccomendations_list[0]
