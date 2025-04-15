import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

# Function to calculate the Haversine distance (distance between points on a sphere)
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in miles
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of earth in miles
    return c * r

# Function to check if a zip code is in Queens
def is_queens_zip(zip_code):
    """Check if a zip code is in the Queens range"""
    if pd.isna(zip_code):
        return False
    zip_num = int(zip_code)
    return (11004 <= zip_num <= 11109) or (11351 <= zip_num <= 11697)

print("Loading data...")
schools_df = pd.read_csv('new_york_schools.csv')
routes_df = pd.read_csv('routes_with_zcta.csv')

print("Filtering for Queens schools...")
queens_schools = schools_df[schools_df['ZCTA5CE10'].apply(is_queens_zip)].copy()
print(f"Number of schools in Queens: {len(queens_schools)}")

# Define the radius for density analysis (in miles)
radius = 0.5  # half-mile radius

# Initialize columns for density analysis
queens_schools['routes_within_radius'] = 0
queens_schools['unique_routes'] = None
queens_schools['transit_density_score'] = 0

# For each school, count the number of routes within the specified radius
for school_idx, school in queens_schools.iterrows():
    routes_within_radius = []
    
    for _, route in routes_df.iterrows():
        distance = haversine_distance(
            school['Latitude'], school['Longitude'],
            route['latitude'], route['longitude']
        )
        
        if distance <= radius:
            routes_within_radius.append(route['route_id'])
    
    # Store the count and list of unique routes
    unique_routes = list(set(routes_within_radius))
    queens_schools.at[school_idx, 'routes_within_radius'] = len(unique_routes)
    queens_schools.at[school_idx, 'unique_routes'] = ','.join(unique_routes) if unique_routes else ''

# Calculate a simple transit density score
# For a more sophisticated score, you might want to weight by route frequency or type
queens_schools['transit_density_score'] = queens_schools['routes_within_radius']

# Define density categories
def get_density_category(num_routes):
    if num_routes == 0:
        return "No transit options"
    elif num_routes <= 1:
        return "Low transit density"
    elif num_routes <= 3:
        return "Medium transit density"
    else:
        return "High transit density"

# Apply the categorization
queens_schools['density_category'] = queens_schools['routes_within_radius'].apply(get_density_category)

# Summary statistics
density_summary = queens_schools['density_category'].value_counts(normalize=True) * 100

# Group by zip code to see density patterns
zip_density_summary = queens_schools.groupby('ZCTA5CE10')['routes_within_radius'].agg(['mean', 'min', 'max', 'count'])

# Print results
print("Schools transit density analysis:")
print(f"Total Queens schools analyzed: {len(queens_schools)}")
print(f"Analysis radius: {radius} miles")
print("\nDensity category breakdown:")
print(density_summary)
print("\nZip code density summary:")
print(zip_density_summary)

# Identify transit deserts (areas with no or low transit density)
transit_deserts = queens_schools[queens_schools['density_category'].isin(["No transit options", "Low transit density"])]
print(f"\nNumber of schools in transit deserts: {len(transit_deserts)}")
if len(transit_deserts) > 0:
    print("Schools in transit deserts:")
    print(transit_deserts[['Name', 'ZCTA5CE10', 'routes_within_radius']])

# Get average density score by zip code for later correlation with income data
zip_avg_density = queens_schools.groupby('ZCTA5CE10')['transit_density_score'].mean().reset_index()
zip_avg_density.columns = ['ZCTA5CE10', 'avg_transit_density']
print("\nAverage transit density by zip code:")
print(zip_avg_density.sort_values('avg_transit_density'))

density_summary.to_csv('density_summary.csv')
zip_density_summary.to_csv('zip_density_summary.csv')
zip_avg_density.to_csv('zip_avg_transit_density.csv', index=False)
transit_deserts.to_csv('transit_deserts.csv', index=False)

