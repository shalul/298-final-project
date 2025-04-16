import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
import folium


# Specify the path to your .tsv file
file_path = 'data.tsv'

# Read the TSV file using pandas
try:
    tsv_df = pd.read_csv(file_path, sep='\t')
    
    # Check if provided headers match expectations
    expected_headers = [
        "ZCTA20", "ZCTA_AREA20", "TOT_POP_2020", 
        "COUNT_NTM_STOPS", "STOPS_PER_CAPITA", "STOPS_PER_SQMILE"
    ]
    

except Exception as e:
    print(f"An error occurred while reading the file: {e}")

# Call the function
#read_tsv(file_path)

#------
# Load the CSV file into a DataFrame
csv_df = pd.read_csv('2024_household_data.csv')

# Check if the DataFrame has at least 25 columns
if len(csv_df.columns) >= 24:
   
    column_24 = csv_df.iloc[:, 24]  # Columns are zero-based
    column_1 = csv_df.iloc[:, 1]  # Columns are zero-based


if tsv_df is not None and csv_df is not None:
    # Assuming zip_code_column_csv is the column with the "ZCTA5" style entries
    if 'NAME' in csv_df.columns:
        # Extract and assign the formatted ZIP codes to a new column in csv_df
        zip_code_formatted = (
            csv_df['NAME'].str.extract(r'ZCTA5 (\d{5})')[0]
        )
        
        # Fill any NaN values as appropriate, e.g., use '00000' or another placeholder
        zip_code_formatted = zip_code_formatted.fillna('-1')
        #csv_df['NAME'] = zip_code_formatted.astype('int64')

    tsv_df['ZCTA20'] = tsv_df['ZCTA20'].astype(str)
    csv_df['NAME'] = csv_df['NAME'].astype(str)
    # Perform an inner join on the ZIP code
    merged_df = pd.merge(tsv_df, csv_df, left_on='ZCTA20', right_on=zip_code_formatted, how='inner')

    
    #for c in merged_df.columns:
    #    print(c)
    # Specify the necessary columns to print
    columns_to_print = ['NAME', 'S1901_C01_012E', 'STOPS_PER_CAPITA']


    #filtered_df = merged_df[merged_df['S1901_C01_012E'] != 0]
    sorted_df = merged_df.sort_values(by='S1901_C01_012E', ascending=False)
   
   # First, convert income and stops per capita to numeric values
    merged_df['S1901_C01_012E'] = pd.to_numeric(merged_df['S1901_C01_012E'], errors='coerce')
    merged_df['STOPS_PER_CAPITA'] = pd.to_numeric(merged_df['STOPS_PER_CAPITA'], errors='coerce')

    # Convert ZCTA20 to numeric (assuming this is your ZIP code column)
    merged_df['ZCTA20'] = pd.to_numeric(merged_df['ZCTA20'], errors='coerce')

    # Filter for ZIP codes within the NYC range (10001 to 11210)
    nyc_df = merged_df[
        (merged_df['ZCTA20'] >= 10001) & 
        (merged_df['ZCTA20'] <= 11210)
    ]

    # Now filter out any NaN or zero values
    filtered_df = nyc_df.dropna(subset=['S1901_C01_012E', 'STOPS_PER_CAPITA'])
    filtered_df = filtered_df[
        (filtered_df['S1901_C01_012E'] > 0) & 
        (filtered_df['STOPS_PER_CAPITA'] > 0)
    ]

    # Extract node labels and stops per capita
    tracts = filtered_df['ZCTA20'].astype(int).tolist()
    stops_per_capita = filtered_df['STOPS_PER_CAPITA'].tolist()

    # Map from ZIP to stops per capita
    stops = dict(zip(tracts, stops_per_capita))

    # Initialize variables
    nodes = tracts
    key = {node: float('inf') for node in nodes}
    parent = {node: None for node in nodes}
    mst_set = {node: False for node in nodes}

    # Start from the first ZIP code
    key[nodes[0]] = 0

    for _ in range(len(nodes)):
        # Pick the node with the smallest key not yet in MST
        u = min((node for node in nodes if not mst_set[node]), key=lambda node: key[node])
        mst_set[u] = True

        for v in nodes:
            if not mst_set[v] and u != v:
                weight_uv = stops[u] + stops[v]
                if weight_uv < key[v]:
                    key[v] = weight_uv
                    parent[v] = u

    # Print the MST
    print("Minimum Spanning Tree (ZIP Code Graph):")
    total_weight = 0
    for node in nodes:
        if parent[node] is not None:
            edge_weight = stops[node] + stops[parent[node]]
            total_weight += edge_weight
            print(f"{parent[node]} -- {node}  [weight: {edge_weight:.4f}]")
    print(f"Total weight of MST: {total_weight:.4f}")


    # Load ZCTA shapefile (or GeoJSON)
    zcta_gdf = gpd.read_file("tl_2020_us_zcta510.shp")  # <-- path to shapefile

    print(zcta_gdf.columns.tolist())

    # Make sure ZCTA5CE10 column is treated as string
    zcta_gdf['ZCTA5CE10'] = zcta_gdf['ZCTA5CE10'].astype(str)

    # Convert your ZIP column to string for merging
    filtered_df['ZCTA20'] = filtered_df['ZCTA20'].astype(int).astype(str)

    # Merge geometry with your data
    geo_merged = pd.merge(filtered_df, zcta_gdf, left_on='ZCTA20', right_on='ZCTA5CE10')
    geo_gdf = gpd.GeoDataFrame(geo_merged, geometry='geometry')




def plot_mst_on_map(geo_gdf):
    # Build the MST structure
    zips = geo_gdf['ZCTA20'].astype(int).tolist()
    stops = geo_gdf['STOPS_PER_CAPITA'].tolist()
    stops_map = dict(zip(zips, stops))

    # Get centroids of ZIP polygons
    centroids = geo_gdf.set_index('ZCTA20').centroid
    coords = {int(zip_code): (pt.y, pt.x) for zip_code, pt in centroids.items()}

    # Prim's MST
    key = {z: float('inf') for z in zips}
    parent = {z: None for z in zips}
    mst_set = {z: False for z in zips}
    key[zips[0]] = 0

    for _ in range(len(zips)):
        u = min((z for z in zips if not mst_set[z]), key=lambda z: key[z])
        mst_set[u] = True

        for v in zips:
            if not mst_set[v] and u != v:
                weight_uv = stops_map[u] + stops_map[v]
                if weight_uv < key[v]:
                    key[v] = weight_uv
                    parent[v] = u

    # Create Folium Map centered on NYC
    nyc_coords = [40.7128, -74.0060]
    fmap = folium.Map(location=nyc_coords, zoom_start=10)

    # Plot MST edges
    for v in zips:
        u = parent[v]
        if u is not None and u in coords and v in coords:
            line = [coords[u], coords[v]]
            folium.PolyLine(
                line,
                color='blue',
                weight=3,
                opacity=0.6,
                tooltip=f"{u} ⇄ {v} | weight: {stops_map[u] + stops_map[v]:.2f}"
            ).add_to(fmap)

    # Plot ZIP nodes
    for z in zips:
        lat, lon = coords[z]
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup=f"ZIP: {z}\nStops/capita: {stops_map[z]:.2f}"
        ).add_to(fmap)

    return fmap


fmap = plot_mst_on_map(geo_gdf)
fmap.save("/mnt/c/Users/margw/Downloads/nyc_mst_map.html")