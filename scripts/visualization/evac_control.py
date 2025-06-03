import pandas as pd
import geopandas as gpd
import osmnx as ox
import networkx as nx
import folium
from shapely.geometry import Point
import pyproj
from shapely.ops import transform
import functools
from folium.plugins import MarkerCluster
import matplotlib.colors as colors
import matplotlib.cm as cm

evac_df = pd.read_csv("evac_control.csv")

evac_gdf = gpd.GeoDataFrame(
    evac_df,
    geometry=gpd.points_from_xy(evac_df.longitude, evac_df.latitude),
    crs='EPSG:4326')

center_lat, center_lon = 35.6812, 139.7742

place_name = "Chūō, Tokyo, Japan"
G_drive = ox.graph_from_point((center_lat, center_lon), dist=3000, network_type='drive', simplify=True)
G_walk = ox.graph_from_point((center_lat, center_lon), dist=3000, network_type='walk', simplify=True)

orig_drive = ox.distance.nearest_nodes(G_drive, center_lon, center_lat)
orig_walk = ox.distance.nearest_nodes(G_walk, center_lon, center_lat)

evac_gdf['drive_node'] = evac_gdf.geometry.apply(lambda point: ox.distance.nearest_nodes(G_drive, point.x, point.y))
evac_gdf['walk_node'] = evac_gdf.geometry.apply(lambda point: ox.distance.nearest_nodes(G_walk, point.x, point.y))

def safe_shortest_path_length(g, source, target, weight):
    try:
        return nx.shortest_path_length(g, source, target, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return float('inf')

evac_gdf['drive_dist'] = evac_gdf['drive_node'].apply(lambda node: safe_shortest_path_length(G_drive, orig_drive, node, weight='length'))
evac_gdf['walk_dist'] = evac_gdf['walk_node'].apply(lambda node: safe_shortest_path_length(G_walk, orig_walk, node, weight='length'))

evac_gdf = evac_gdf[(evac_gdf['drive_dist'] != float('inf')) & (evac_gdf['walk_dist'] != float('inf'))]

m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles='cartodbpositron')

folium.Marker([center_lat, center_lon], popup='Center of Nihonbashi', icon=folium.Icon(color='blue')).add_to(m)

marker_cluster = MarkerCluster().add_to(m)

for _, row in evac_gdf.iterrows():
    folium.Marker(
        location=[row.latitude, row.longitude],
        popup=f"{row.Name}<br>Capacity: {row.Capacity}",
        icon=folium.Icon(color='gray', icon='info-sign')
    ).add_to(marker_cluster)
for _, row in evac_gdf.iterrows():
    fg = folium.FeatureGroup(name=row.Name, show=False)
    try:
        drive_route = nx.shortest_path(G_drive, orig_drive, row['drive_node'], weight='length')
        drive_coords = [(G_drive.nodes[n]['y'], G_drive.nodes[n]['x']) for n in drive_route]
        drive_length_m = nx.shortest_path_length(G_drive, orig_drive, row['drive_node'], weight='length')
        drive_length_km = drive_length_m / 100
        folium.PolyLine(drive_coords, color='red', weight=6, opacity=0.9,
                        tooltip=f"{row.Name} (Drive) - {drive_length_km:.2f} km").add_to(fg)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        print(f"No driving path for {row.Name}")

    try:
        walk_route = nx.shortest_path(G_walk, orig_walk, row['walk_node'], weight='length')
        walk_coords = [(G_walk.nodes[n]['y'], G_walk.nodes[n]['x']) for n in walk_route]
        walk_length_m = nx.shortest_path_length(G_walk, orig_walk, row['walk_node'], weight='length')
        walk_length_km = walk_length_m / 1000
        folium.PolyLine(walk_coords, color='blue', weight=6, opacity=0.9,
                        tooltip=f"{row.Name} (Walk) - {walk_length_km:.2f} km").add_to(fg)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        print(f"No walking path for {row.Name}")

    m.add_child(fg)

edge_centrality = nx.edge_betweenness_centrality(G_walk, k=1000, weight='length')
top_pct = 0.01
threshold = sorted(edge_centrality.values(), reverse=True)[int(len(edge_centrality)*top_pct)]
top_edges = [edge for edge, val in edge_centrality.items() if val >= threshold]

bottleneck_layer = folium.FeatureGroup(name="Potential Bottlenecks")
for u, v, k in top_edges:
    edge_data = G_walk[u][v][k]
    if 'geometry' in edge_data:
        points = [(pt[1], pt[0]) for pt in edge_data['geometry'].coords]
    else:
        points = [(G_walk.nodes[u]['y'], G_walk.nodes[u]['x']),
                  (G_walk.nodes[v]['y'], G_walk.nodes[v]['x'])]

    folium.PolyLine(
        locations=points,
        color='orange',
        weight=4,
        opacity=0.8,
        tooltip="High Traffic Likelihood"
    ).add_to(bottleneck_layer)
bottleneck_layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

evac_gdf['drive_km'] = (evac_gdf['drive_dist'] / 1000).round(2)
evac_gdf['walk_km'] = (evac_gdf['walk_dist'] / 1000).round(2)
distance_table = evac_gdf[['Name', 'drive_km', 'walk_km']]
distance_table.columns = ['Shelter Name', 'Driving Distance (km)', 'Walking Distance (km)']
print(distance_table.to_string(index=False))

m.save("evacuation_routes_full_map.html")