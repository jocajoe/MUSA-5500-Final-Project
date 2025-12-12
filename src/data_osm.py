# src/data_osm.py

# load packages
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point

# def function to dowload walkable street network philly
def load_walk_network(place="Philadelphia, Pennsylvania"):

    G = ox.graph_from_place(place, network_type="walk")
    return G

# def function to compute walking distance from tract centroid
# to nearest brewery using street network
def nearest_brewery_distance(G, tract_gdf, brewery_gdf):

    brewery_nodes = [
        ox.nearest_nodes(G, geom.x, geom.y)
        for geom in brewery_gdf.geometry
    ]

    distances = []

    for geom in tract_gdf.centroid:
        try:
            source = ox.nearest_nodes(G, geom.x, geom.y)
        except:
            distances.append(None)
            continue

        # shortest path to brewery node
        dists = []
        for bnode in brewery_nodes:
            try:
                length = ox.shortest_path_length(G, source, bnode, weight="length")
                dists.append(length)
            except:
                continue

        distances.append(min(dists) if len(dists) > 0 else None)

    tract_gdf["nearest_brewery_walk_meters"] = distances
    return tract_gdf

# def function to count breweries within walking distanct
# of tract centroid
def breweries_within_radius(G, tract_gdf, brewery_gdf, radius=800):

    counts = []

    for geom in tract_gdf.centroid:
        try:
            source = ox.nearest_nodes(G, geom.x, geom.y)
        except:
            counts.append(0)
            continue

        subgraph = ox.truncate.truncate_graph_dist(G, source, radius)
        reachable_nodes = set(subgraph.nodes)

        # reachable nodes
        bcount = 0
        for geom2 in brewery_gdf.geometry:
            bnode = ox.nearest_nodes(G, geom2.x, geom2.y)
            if bnode in reachable_nodes:
                bcount += 1

        counts.append(bcount)

    tract_gdf[f"breweries_within_{radius}m"] = counts
    return tract_gdf
