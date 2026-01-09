from utils.helpers import find_similar_animes, find_similar_users, get_user_preference, get_user_recommendation


def hybrid_recommendation(user_id, collaborative_weight = 0.5, content_weight = 0.5):
    # Use global user_weights (embedding weights) for find_similar_users
    similar_users = find_similar_users(user_id)
    
    # Check if similar_users is empty
    if similar_users.empty or 'similar_users' not in similar_users.columns:
        print(f"Warning: No similar users found for user_id {user_id}")
        return []
    
    user_preferences = get_user_preference(user_id, plot=False)
    user_recommended_animes = get_user_recommendation(similar_users, user_preferences)
    
    # Check if user_recommended_animes is empty
    if user_recommended_animes.empty or 'anime_name' not in user_recommended_animes.columns:
        print(f"Warning: No recommendations found for user_id {user_id}")
        return []
    
    user_recommended_anime_list = user_recommended_animes['anime_name'].tolist()

    content_recommended_animes = []

    for anime in user_recommended_anime_list:
        similar_animes = find_similar_animes(anime)

        if similar_animes is not None and not similar_animes.empty:
            content_recommended_animes.extend(similar_animes['name'].tolist())
        
        else:
            print(f'No similar animes found for {anime}')

    combined_scores = {}

    for anime in user_recommended_anime_list:
        combined_scores[anime] = combined_scores.get(anime, 0) + collaborative_weight

    for anime in content_recommended_animes:
        combined_scores[anime] = combined_scores.get(anime, 0) + content_weight

    sorted_animes = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    return [anime for anime, score in sorted_animes[:10]]