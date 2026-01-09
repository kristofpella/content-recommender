from collections import defaultdict
import pandas as pd
import numpy as np
import joblib
from config.paths_config import *

def get_anime_frame(anime):
    df = pd.read_csv(ANIME_DF)

    if isinstance(anime, int):
        return df[df['anime_id'] == anime]
        
    if isinstance(anime, str):
        return df[df['eng_version'] == anime]





def get_synopsis(anime):
    df = pd.read_csv(SYNOPSIS_DF)

    if isinstance(anime, int):
        return df[df['MAL_ID'] == anime].synopsis.values[0]
    
    if isinstance(anime, str):
        return df[df['Name'] == anime].synopsis.values[0]







def find_similar_animes(name, n=10, return_dist=False, neg=False):
    df = pd.read_csv(ANIME_DF)
    anime_weights = joblib.load(ANIME_WEIGHTS_PATH)
    anime2anime_encoded = joblib.load(ANIME_TO_ANIME_ENCODED)
    anime2anime_decoded = joblib.load(ANIME_TO_ANIME_DECODED)

    # Get the anime_id for the given name
    index = get_anime_frame(name).anime_id.values[0]
    encoded_index = anime2anime_encoded.get(index)

    if encoded_index is None:
        raise ValueError(f"Encoded index not found for anime ID: {index}")

    weights = anime_weights

    # Compute the similarity distances
    dists = np.dot(weights, weights[encoded_index])  # Ensure weights[encoded_index] is a 1D array
    sorted_dists = np.argsort(dists)

    n = n + 1

    # Select closest or farthest based on 'neg' flag
    if neg:
        closest = sorted_dists[:n]
    else:
        closest = sorted_dists[-n:]

    # Return distances and closest indices if requested
    if return_dist:
        return dists, closest

    # Build the similarity array
    SimilarityArr = []
    for close in closest:
        decoded_id = anime2anime_decoded.get(close)
        
        # Skip if decoded_id is None
        if decoded_id is None:
            continue
       
        anime_frame = get_anime_frame(decoded_id)

        # Skip if anime_frame is empty
        if anime_frame.empty or len(anime_frame) == 0:
            continue

        anime_name = anime_frame.eng_version.values[0]
        genre = anime_frame.Genres.values[0]
        similarity = dists[close]

        SimilarityArr.append({
            "anime_id": decoded_id,
            "name": anime_name,
            "similarity": similarity,
            "genre": genre,
        })
       

    # Create a DataFrame with results and sort by similarity
    Frame = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
    return Frame[Frame.anime_id != index].drop(['anime_id'], axis=1)




def find_similar_users(item_input, n=10, return_dist=False, neg=False):
    user_weights = joblib.load(USER_WEIGHTS_PATH)
    user_to_user_encoded = joblib.load(USER_TO_USER_ENCODED)
    user_to_user_decoded = joblib.load(USER_TO_USER_DECODED)

    try:
        index = item_input
        encoded_index = user_to_user_encoded.get(index)

        weights = user_weights

        dists = np.dot(weights, weights[encoded_index])
        sorted_dists = np.argsort(dists)

        n = n + 1

        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:]

        if return_dist:
            return dists, closest

        SimilarityArr = []

        for close in closest:
            similarity = dists[close]

            if isinstance(item_input, int):
                decoded_id = user_to_user_decoded.get(close)
                SimilarityArr.append({
                    "similar_users": decoded_id,
                    "similarity": similarity,
                })

        similar_users = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
        similar_users = similar_users[similar_users["similar_users"] != item_input]

        return similar_users

    
    except Exception as e:
        print(f"Error finding similar users: {e}")
        return pd.DataFrame()




def get_favorite_genre(frame):
    frame.dropna(inplace=True)

    all_genres = defaultdict(int)

    genres_list = []

    for genres in frame['Genres']:
        if isinstance(genres, str):
            for genre in genres.split(','):
                genres_list.append(genre)
                all_genres[genre.strip()] += 1

    return genres_list



def get_user_preference(user_id, plot=False):
    rating_df = pd.read_csv(RATING_DF)
    df = pd.read_csv(ANIME_DF)

    animes_watched_by_user = rating_df[rating_df['user_id'] == user_id]

    user_rating_percentile = np.percentile(animes_watched_by_user['rating'], 75)

    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user['rating'] >= user_rating_percentile]

    top_animes_from_user = (
        animes_watched_by_user.sort_values(by='rating', ascending=False).anime_id.values
    )

    anime_df_rows = df[df['anime_id'].isin(top_animes_from_user)]
    anime_df_rows = anime_df_rows[['eng_version', 'Genres']]

    if plot:
        get_favorite_genre(anime_df_rows, plot=True)

    return anime_df_rows




def get_user_recommendation(similar_users, user_preferences, n=10):
    df = pd.read_csv(ANIME_DF)
    rating_df = pd.read_csv(RATING_DF)
    synopsis_df = pd.read_csv(SYNOPSIS_DF)

    recommended_animes = []
    anime_list = []

    for user_id in similar_users['similar_users'].values:
        pref_list = get_user_preference(int(user_id))
        
        pref_list = pref_list[~pref_list['eng_version'].isin(user_preferences['eng_version'])]

        if not pref_list.empty:
            anime_list.append(pref_list['eng_version'].values)


    if anime_list:
        anime_list = pd.DataFrame(anime_list)
        sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)

        for i, anime_name in enumerate(sorted_list.index):
            n_user_pref = sorted_list[sorted_list.index == anime_name].values[0]

            if isinstance(anime_name, str):
                frame = get_anime_frame(anime_name)

                anime_id = frame.anime_id.values[0]
                synopsis = get_synopsis(int(anime_id))
                genre = frame.Genres.values[0]

                recommended_animes.append({
                    'n': n_user_pref[0],
                    'anime_name': anime_name,
                    'Synopsis': synopsis,
                    'Genres': genre,
                })

    return pd.DataFrame(recommended_animes).head(n)
