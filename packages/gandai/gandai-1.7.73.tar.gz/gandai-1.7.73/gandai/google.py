import googlemaps
import pandas as pd
from googleapiclient.discovery import build

import gandai as ts
from gandai import secrets

gmaps = googlemaps.Client(key=secrets.access_secret_version("GOOLE_MAPS_KEY"))


def search(q: str, count: int = 10) -> pd.DataFrame:
    if count > 100:
        print("max @ 100 for now")
        count = 100

    all_results = []
    for i in range(0, count, 10):
        service = build(
            "customsearch",
            "v1",
            developerKey=secrets.access_secret_version("GOOGLE_SEARCH_KEY"),
        )
        results = service.cse().list(q=q, cx="12cb7a511cc804eb0", start=i).execute()
        all_results.extend(results["items"])
    df = pd.DataFrame(all_results)[["title", "link", "snippet"]]
    return df


def get_google_places(q: str) -> pd.DataFrame:
    results = []
    resp = gmaps.places(
        query=q,
    )
    results.extend(resp["results"])
    results = pd.DataFrame(results)[
        ["name", "place_id", "rating", "user_ratings_total"]
    ]
    return results
