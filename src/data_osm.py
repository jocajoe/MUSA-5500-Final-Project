# src/data_osm.py

# load packages
import numpy as np
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point

# def function to dowload walkable street network philly
def load_walk_network(place="Philadelphia, Pennsylvania"):

    G = ox.graph_from_place(place, network_type="walk")
    return G

# def function to compute walking distance from tract centroid
# to nearest brewery using street network
def nearest_brewery_walk_distance(G, tract_gdf, brewery_gdf):

    tract_gdf = tract_gdf.copy()
    brewery_gdf = brewery_gdf.copy()

    # Ensure CRS for network matching
    tract_gdf = tract_gdf.to_crs(epsg=4326)
    brewery_gdf = brewery_gdf.to_crs(epsg=4326)

    # ---- SAFE centroid calculation ----
    tracts_proj = tract_gdf.to_crs(epsg=3857)
    centroids_proj = tracts_proj.centroid
    centroids = gpd.GeoSeries(centroids_proj, crs=3857).to_crs(epsg=4326)

    # Precompute brewery nodes
    brewery_nodes = [
        ox.nearest_nodes(G, geom.x, geom.y)
        for geom in brewery_gdf.geometry
    ]

    distances = []

    for geom in centroids:
        try:
            source = ox.nearest_nodes(G, geom.x, geom.y)
        except Exception:
            distances.append(np.nan)
            continue

        dists = []
        for bnode in brewery_nodes:
            try:
                dists.append(
                    ox.shortest_path_length(G, source, bnode, weight="length")
                )
            except Exception:
                continue

        distances.append(min(dists) if dists else np.nan)

    tract_gdf["walk_dist_to_brewery_m"] = distances
    return tract_gdf



# def function to count breweries within walking distanct
# of tract centroid
def breweries_within_radius(G, tract_gdf, brewery_gdf, radius=800):

    tract_gdf = tract_gdf.copy()
    brewery_gdf = brewery_gdf.copy()

    # Ensure CRS for OSMnx node snapping (lat/lon)
    tract_gdf = tract_gdf.to_crs(epsg=4326)
    brewery_gdf = brewery_gdf.to_crs(epsg=4326)

    # ---- SAFE centroid calculation ----
    tracts_proj = tract_gdf.to_crs(epsg=3857)
    centroids_proj = tracts_proj.centroid
    centroids = gpd.GeoSeries(centroids_proj, crs=3857).to_crs(epsg=4326)

    # Precompute brewery nodes once (faster)
    brewery_nodes = [
        ox.nearest_nodes(G, geom.x, geom.y)
        for geom in brewery_gdf.geometry
    ]

    counts = []

    for geom in centroids:
        try:
            source = ox.nearest_nodes(G, geom.x, geom.y)
        except Exception:
            counts.append(0)
            continue

        subgraph = ox.truncate.truncate_graph_dist(G, source, radius)
        reachable_nodes = set(subgraph.nodes)

        # Count reachable breweries
        bcount = sum(1 for bnode in brewery_nodes if bnode in reachable_nodes)
        counts.append(bcount)

    tract_gdf[f"breweries_within_{radius}m"] = counts
    return tract_gdf