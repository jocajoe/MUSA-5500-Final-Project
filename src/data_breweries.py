# src/data_breweries.py

# load packages
import requests
import pandas as pd
import geopandas as gpd

# define base url for openbrewerydb api
BASE_URL = "https://api.openbrewerydb.org/v1/breweries"

# define function to fetch breweries for specified city
def fetch_breweries_by_city(city: str, per_page: int = 200):

    params = {"by_city": city.lower(), "per_page": per_page}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()
    return pd.DataFrame(data)


# convert to geodataframe. drop invalid lat and long

def breweries_to_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:

    df = df.dropna(subset=["latitude", "longitude"])

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    return gdf
