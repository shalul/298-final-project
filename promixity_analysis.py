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

print("Initializing proximity analysis columns...")
queens_schools['nearest_route_id'] = None
queens_schools['nearest_route_distance'] = float('inf')  # Initialize with infinity
queens_schools['accessibility_category'] = None

print("Calculating nearest transit route for each school...")
for school_idx, school in queens_schools.iterrows():
    for route_idx, route in routes_df.iterrows():
        distance = haversine_distance(
            school['Latitude'], school['Longitude'],
            route['latitude'], route['longitude']
        )
        if distance < queens_schools.at[school_idx, 'nearest_route_distance']:
            # print(f"New nearest route found for school {school['Name']}: {route['route_id']} with distance {distance}")
            queens_schools.at[school_idx, 'nearest_route_distance'] = distance
            queens_schools.at[school_idx, 'nearest_route_id'] = route['route_id']

print("Categorizing accessibility levels...")
def get_accessibility_category(distance):
    if distance < 0.25:
        return "Very accessible"
    elif distance < 0.5:
        return "Accessible"
    elif distance < 1.0:
        return "Moderately accessible"
    else:
        return "Limited accessibility"

queens_schools['accessibility_category'] = queens_schools['nearest_route_distance'].apply(get_accessibility_category)

print("Generating summary statistics...")
accessibility_summary = queens_schools['accessibility_category'].value_counts(normalize=True) * 100
zip_summary = queens_schools.groupby('ZCTA5CE10')['nearest_route_distance'].agg(['mean', 'min', 'max', 'count'])

# Print results
print("\nSchools proximity analysis:")
print(f"Total Queens schools analyzed: {len(queens_schools)}")

print("\nAccessibility breakdown:")
print(accessibility_summary)

print("\nZip code summary:")
print(zip_summary)

print("\nIdentifying underserved schools...")
underserved_schools = queens_schools[queens_schools['accessibility_category'] == "Limited accessibility"]
print(f"Number of underserved schools: {len(underserved_schools)}")

if len(underserved_schools) > 0:
    print("Underserved schools:")
    print(underserved_schools[['Name', 'ZCTA5CE10', 'nearest_route_distance']])

# SAVE OUTPUTS
print("\nSaving results to CSV files...")

queens_schools.to_csv('queens_schools_accessibility.csv', index=False)
underserved_schools.to_csv('underserved_schools.csv', index=False)
accessibility_summary.to_csv('accessibility_summary.csv')
zip_summary.to_csv('zip_summary.csv')

print("Files saved successfully!")