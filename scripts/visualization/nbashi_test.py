import osmnx as ox
import folium
import pandas as pd
from folium import CircleMarker, Tooltip

place_name = "Chūō, Tokyo, Japan"
boundary = ox.geocode_to_gdf(place_name)
polygon = boundary.loc[0, 'geometry']
nbashi_boundary = ox.geocode_to_gdf("Nihonbashi, Tokyo, Japan")

network_types = {"walk": "blue", "drive": "red", "bike": "green"}
tags = {'railway': True}
transit_routes = ox.features_from_polygon(polygon, tags)
transit_lines = transit_routes[transit_routes.geometry.type.isin(['LineString', 'MultiLineString'])]

G = ox.graph_from_polygon(polygon, network_type='all')
nodes, _ = ox.graph_to_gdfs(G)
center = nodes.geometry.union_all().centroid
center_latlon = center.y, center.x

m = folium.Map(location=center_latlon, zoom_start=15, tiles='cartodbpositron')
def style_transit(feature):
    return {
        'color': 'purple',
        'weight': 4,
        'opacity': 0.9}

def make_style_fn(color_value):
    return lambda _: {
        "color": color_value,
        "weight": 4}

for net_type, path_color in network_types.items():
    G = ox.graph_from_polygon(polygon, network_type=net_type)
    _, edges = ox.graph_to_gdfs(G)
    edges = edges[edges.geometry.notnull()]
    edges = edges[edges.geometry.is_valid]
    feature_group = folium.FeatureGroup(name=f"{net_type.title()} Network")
    geojson_layer = folium.GeoJson(
        data=edges.to_json(),
        name=f"{net_type.title()} Network",
        style_function=make_style_fn(path_color))
    geojson_layer.add_to(feature_group)
    feature_group.add_to(m)

evac_data = pd.read_csv("evac.csv")

evac_layer = folium.FeatureGroup(name="Evacuation Centers")
transit_layer = folium.FeatureGroup(name="Public Transit Lines")

for _, row in evac_data.iterrows():
    popup_content = f"""
    <b>{row['Name']}</b><br>
    Capacity: {row['Capacity']:,}"""
    CircleMarker(
        location=(row['latitude'], row['longitude']),
        radius=7,
        color='darkgreen',
        fill=True,
        fill_color='limegreen',
        fill_opacity=0.7,
        tooltip=Tooltip(row['Name']),
        popup=folium.Popup(popup_content, max_width=300)
    ).add_to(evac_layer)
evac_layer.add_to(m)

folium.GeoJson(
    data=nbashi_boundary.to_json(),
    name="Nihonbashi Boundary",
    style_function=lambda _: {
        "color": "black",
        "weight": 9,
        "fill": False}).add_to(m)
folium.GeoJson(
    data=transit_lines.to_json(),
    name="Transit Lines",
    style_function=style_transit
).add_to(transit_layer)
transit_layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

m.save("nbashi_test.html")