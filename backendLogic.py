# backendLogic.py

import os
import gdown
import pandas as pd
import joblib
from geopy.distance import geodesic
from sklearn.metrics.pairwise import cosine_similarity
from datetime import timedelta, datetime

# --------- Model Downloader ---------
def download_models():
    model_folder = "models"
    os.makedirs(model_folder, exist_ok=True)

    files = {
        "budget_predictor.pkl": "1uO-Xyn8oXd_ThfuxMpjQCkNdpItia6yl",      # Replace with real ID
        "collab_knn_model.pkl": "1B8feCqUNYDCJ5USNDwgVLR9QTGf-Maf0"     # Replace with real ID
    }

    for fname, fid in files.items():
        path = os.path.join(model_folder, fname)
        if not os.path.exists(path):
            print(f"Downloading {fname}...")
            gdown.download(f"https://drive.google.com/uc?id={fid}", path, quiet=False)

download_models()

# --------- Load Data and Models ---------
DATA_PATH = "cleaned_tourism_dataset.csv"
df = pd.read_csv(DATA_PATH)
df.fillna("", inplace=True)
df.columns = df.columns.str.strip()

vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
mood_model = joblib.load("models/mood_classifier.pkl")
budget_model = joblib.load("models/budget_predictor.pkl")

df["combined"] = df["description"]
tfidf_matrix = vectorizer.transform(df["combined"])

# --------- Helper Functions ---------
def predict_mood(text):
    return mood_model.predict([text])[0]

def predict_budget(text):
    return budget_model.predict(vectorizer.transform([text]))[0]

# --------- Recommender Logic ---------
def recommend_places(user_text, location_coords=None, moods=None, budget=None, time_hr=4):
    from geopy.geocoders import Nominatim

    if location_coords is None:
        geolocator = Nominatim(user_agent="smart_tourism_app", timeout=10)
        loc = geolocator.geocode(user_text)
        if loc is None:
            return pd.DataFrame(), pd.DataFrame()
        location_coords = (loc.latitude, loc.longitude)

    if not moods:
        moods = [predict_mood(user_text)]
    if not budget:
        budget = predict_budget(user_text)

    df_loc = df.copy()
    df_loc = df_loc[(df_loc["lat"] != 0) & (df_loc["lng"] != 0)]

    coords = df_loc[["lat", "lng"]].values
    distances = [geodesic(location_coords, (lat, lng)).km for lat, lng in coords]
    travel_times = [d / 30 for d in distances]
    total_times = [t + 1 for t in travel_times]

    df_loc["distance_km"] = distances
    df_loc["travel_time_hr"] = travel_times
    df_loc["total_time_hr"] = total_times

    df_loc = df_loc[df_loc["total_time_hr"] <= time_hr]
    if df_loc.empty:
        return pd.DataFrame(), pd.DataFrame()

    user_vector = vectorizer.transform([" ".join(moods)])
    place_vectors = vectorizer.transform(df_loc["combined"])
    sim_scores = cosine_similarity(user_vector, place_vectors).flatten()

    df_loc["similarity_score"] = sim_scores
    df_loc["final_score"] = df_loc["similarity_score"] / (1 + df_loc["total_time_hr"] + df_loc["distance_km"])
    df_loc = df_loc[df_loc['rating'] * 100 <= budget + 200]

    tourist_df = df_loc.iloc[:523].sort_values("final_score", ascending=False).head(20)
    food_df = df_loc.iloc[523:].sort_values("final_score", ascending=False).head(10)

    return tourist_df, food_df

# --------- Itinerary Generator ---------
def create_itinerary(user_location, tourist_df, food_df, total_time_hr=4, start_time="10:00"):
    itinerary = []
    current_location = user_location
    current_time = datetime.strptime(start_time, "%H:%M")
    end_time = current_time + timedelta(hours=total_time_hr)

    remaining = tourist_df.copy()
    remaining["distance"] = remaining.apply(
        lambda row: geodesic(current_location, (row["lat"], row["lng"])).km, axis=1
    )
    remaining.sort_values("distance", inplace=True)

    food_added = 0
    food_inserted = False

    while not remaining.empty:
        next_place = remaining.iloc[0]
        travel_time = geodesic(current_location, (next_place["lat"], next_place["lng"])).km / 30
        arrival = current_time + timedelta(hours=travel_time)
        stay = 1

        if arrival + timedelta(hours=stay) > end_time:
            break

        itinerary.append({
            "type": "place",
            "name": next_place["name"],
            "desc": next_place["description"],
            "address": next_place["address"],
            "arrival": arrival,
            "stay_duration_hr": stay,
            "lat": next_place["lat"],
            "lng": next_place["lng"],
            "rating": next_place["rating"],
            "reviews": next_place["reviews"]
        })

        current_time = arrival + timedelta(hours=stay)
        current_location = (next_place["lat"], next_place["lng"])
        remaining.drop(index=next_place.name, inplace=True)

        if total_time_hr > 4 and not food_inserted and 12 <= current_time.hour <= 14 and not food_df.empty:
            top_food = food_df.sort_values("final_score", ascending=False).head(2 - food_added)
            for _, food_place in top_food.iterrows():
                travel = geodesic(current_location, (food_place["lat"], food_place["lng"])).km / 30
                arrival_food = current_time + timedelta(hours=travel)

                if arrival_food + timedelta(hours=1) > end_time:
                    continue

                itinerary.append({
                    "type": "food",
                    "name": food_place["name"],
                    "desc": food_place["description"],
                    "address": food_place["address"],
                    "arrival": arrival_food,
                    "stay_duration_hr": 1,
                    "lat": food_place["lat"],
                    "lng": food_place["lng"],
                    "rating": food_place["rating"],
                    "reviews": food_place["reviews"]
                })

                current_time = arrival_food + timedelta(hours=1)
                current_location = (food_place["lat"], food_place["lng"])
                food_df.drop(index=food_place.name, inplace=True)
                food_added += 1

                if food_added >= 2:
                    break
            food_inserted = True

    return itinerary
