# src/data_acs.py

# load packages
from census import Census
import pandas as pd
import geopandas as gpd

# fips codes for pa and philadlephia county
PA_FIPS = "42"
PHILLY_FIPS = "101" 

# define function to pull median home value from acs5 year
# with geodata
def load_acs_philly(api_key: str, year: int = 2022):

    c = Census(api_key, year=year)

    # B25077_001E → Median Home Value
    acs_rows = c.acs5.state_county_tract(
        ["NAME", "B25077_001E"],
        PA_FIPS,
        PHILLY_FIPS,
        "*"
    )

    df = pd.DataFrame(acs_rows)
    df.rename(columns={"B25077_001E": "median_home_value"}, inplace=True)

    # Build GEOID for merges
    df["GEOID"] = df["state"] + df["county"] + df["tract"]

    return df

# defining function to load philadelphia tract shapes
# frome census website
def load_philly_tract_shapes(year: int = 2022):

    # TIGER tract shapefiles: tl_<year>_<STATE>_<county>_tract.zip
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{PA_FIPS}{PHILLY_FIPS}_tract.zip"

    gdf = gpd.read_file(url)

    # GEOID column already exists in TIGER data
    return gdf

# def function to merge acs data (home value) with census tract shapes
def load_philly_acs_geo(api_key: str, year: int = 2022):


    df_acs = load_acs_philly(api_key, year)
    gdf_shapes = load_philly_tract_shapes(year)

    gdf_merged = gdf_shapes.merge(df_acs[["GEOID", "median_home_value"]], on="GEOID")

    return gdf_merged
