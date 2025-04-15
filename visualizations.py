import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import folium
from folium.plugins import MarkerCluster

# Load the saved CSV files
queens_schools = pd.read_csv('queens_schools_accessibility.csv')
underserved_schools = pd.read_csv('underserved_schools.csv')
accessibility_summary = pd.read_csv('accessibility_summary.csv')
zip_summary = pd.read_csv('zip_summary.csv')
density_summary = pd.read_csv('density_summary.csv')
zip_density_summary = pd.read_csv('zip_density_summary.csv')
zip_avg_density = pd.read_csv('zip_avg_transit_density.csv')
transit_deserts = pd.read_csv('transit_deserts.csv')

# 1. Visualizing Accessibility Categories
plt.figure(figsize=(10, 6))
accessibility_data = accessibility_summary.set_index('accessibility_category')['proportion']
accessibility_data = accessibility_data * 1.0
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']  # Green, Blue, Orange, Red
ax = accessibility_data.plot(kind='bar', color=colors)
plt.title('School Transit Accessibility in Queens', fontsize=14)
plt.xlabel('Accessibility Category')
plt.ylabel('Percentage of Schools')
plt.xticks(rotation=45)
for i, v in enumerate(accessibility_data):
    ax.text(i, v + 1, f'{v:.1f}%', ha='center')
plt.tight_layout()
plt.savefig('accessibility_categories.png')

# 2. Transit Distance Heatmap by Zip Code
# First prepare the data
zip_transit_stats = pd.read_csv('zip_summary.csv')
print(zip_transit_stats.columns)
print(zip_transit_stats.shape)
# Rename the remaining columns
zip_transit_stats.columns = ['zip_code', 'mean_distance', 'min_distance', 'max_distance', 'school_count']
zip_transit_stats = zip_transit_stats.sort_values('mean_distance')

plt.figure(figsize=(14, 8))
sns.barplot(x='zip_code', y='mean_distance', data=zip_transit_stats, 
            palette='viridis_r')  # Reversed so lower distances (better) are green
plt.title('Average Distance to Transit by Queens Zip Code', fontsize=14)
plt.xlabel('Zip Code')
plt.ylabel('Average Distance to Transit (miles)')
plt.xticks(rotation=90)
plt.axhline(y=0.5, color='red', linestyle='--', label='Accessible Threshold (0.5 miles)')
plt.legend()
plt.tight_layout()
plt.savefig('zip_transit_distance.png')


# 3. Transit Density Map
zip_density = zip_density_summary
zip_density.columns = ['zip_code', 'mean_routes', 'min_routes', 'max_routes', 'school_count']
zip_density = zip_density.sort_values('mean_routes', ascending=False)

plt.figure(figsize=(14, 8))
ax = sns.barplot(x='zip_code', y='mean_routes', data=zip_density, palette='viridis')
plt.title('Average Transit Density by Queens Zip Code', fontsize=14)
plt.xlabel('Zip Code')
plt.ylabel('Average Number of Transit Routes within 0.5 Miles')
plt.xticks(rotation=90)
for i, v in enumerate(zip_density['mean_routes']):
    ax.text(i, v + 0.1, f'{v:.1f}', ha='center')
plt.tight_layout()
plt.savefig('zip_transit_density.png')

# 4. Combine Proximity and Density for Overall Access
# Create a combined dataset
zip_combined = pd.merge(
    zip_transit_stats[['zip_code', 'mean_distance', 'school_count']],
    zip_density[['zip_code', 'mean_routes']],
    on='zip_code'
)

# Calculate a composite score (lower distance + higher route count = better)
# Normalize both metrics to 0-1 scale first
zip_combined['norm_distance'] = 1 - (zip_combined['mean_distance'] - zip_combined['mean_distance'].min()) / (zip_combined['mean_distance'].max() - zip_combined['mean_distance'].min())
zip_combined['norm_routes'] = (zip_combined['mean_routes'] - zip_combined['mean_routes'].min()) / (zip_combined['mean_routes'].max() - zip_combined['mean_routes'].min())
zip_combined['transit_access_score'] = (zip_combined['norm_distance'] + zip_combined['norm_routes']) / 2
zip_combined = zip_combined.sort_values('transit_access_score', ascending=False)

plt.figure(figsize=(14, 8))
ax = sns.barplot(x='zip_code', y='transit_access_score', data=zip_combined, palette='viridis')
plt.title('Overall Transit Access Score by Queens Zip Code', fontsize=14)
plt.xlabel('Zip Code')
plt.ylabel('Transit Access Score (higher is better)')
plt.xticks(rotation=90)
for i, v in enumerate(zip_combined['transit_access_score']):
    ax.text(i, v + 0.02, f'{v:.2f}', ha='center')
plt.tight_layout()
plt.savefig('zip_overall_access.png')

# 5. Scatter plot of proximity vs density
plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    queens_schools['nearest_route_distance'], 
    queens_schools['routes_within_radius'],
    c=queens_schools['transit_density_score'],
    cmap='viridis',
    alpha=0.7,
    s=80
)
plt.colorbar(scatter, label='Transit Density Score')
plt.axvline(x=0.25, color='green', linestyle='--', label='Very Accessible (0.25 mi)')
plt.axvline(x=0.5, color='blue', linestyle='--', label='Accessible (0.5 mi)')
plt.axvline(x=1.0, color='orange', linestyle='--', label='Moderately Accessible (1.0 mi)')
plt.axhline(y=2, color='red', linestyle='-.', label='Multiple Transit Options')
plt.title('Transit Proximity vs Density for Queens Schools', fontsize=14)
plt.xlabel('Distance to Nearest Transit Route (miles)')
plt.ylabel('Number of Transit Routes within 0.5 Miles')
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('proximity_vs_density.png')

# 6. Interactive Map (if using in a notebook or saving as HTML)
m = folium.Map(location=[40.7282, -73.7949], zoom_start=11)  # Center of Queens

# Create a marker cluster group
marker_cluster = MarkerCluster().add_to(m)

# Color mapping for accessibility categories
color_map = {
    'Very accessible': 'green',
    'Accessible': 'blue',
    'Moderately accessible': 'orange',
    'Limited accessibility': 'red'
}

# Only add this if accessibility_category column exists
if 'accessibility_category' in queens_schools.columns:
    # Add each school as a marker
    for idx, row in queens_schools.iterrows():
        # Create popup text
        popup_text = f"""
        <b>{row['Name']}</b><br>
        Zip Code: {row['ZCTA5CE10']}<br>
        Distance to Transit: {row['nearest_route_distance']:.2f} miles<br>
        Routes within 0.5 mi: {row['routes_within_radius']}<br>
        Accessibility: {row['accessibility_category']}<br>
        """
        
        # Create marker
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color=color_map.get(row['accessibility_category'], 'gray'),
            fill=True,
            fill_color=color_map.get(row['accessibility_category'], 'gray'),
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(marker_cluster)

# Add a legend
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; padding: 10px; background-color: white; border: 2px solid grey; border-radius: 5px">
<h4>Transit Accessibility</h4>
<div><i style="background: green; width: 15px; height: 15px; display: inline-block"></i> Very accessible (<0.25 mi)</div>
<div><i style="background: blue; width: 15px; height: 15px; display: inline-block"></i> Accessible (0.25-0.5 mi)</div>
<div><i style="background: orange; width: 15px; height: 15px; display: inline-block"></i> Moderately accessible (0.5-1 mi)</div>
<div><i style="background: red; width: 15px; height: 15px; display: inline-block"></i> Limited accessibility (>1 mi)</div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
m.save('queens_schools_transit_map.html')

# 7. Underserved Schools Analysis
if len(underserved_schools) > 0:
    plt.figure(figsize=(12, len(underserved_schools) * 0.4 + 2))
    sns.barplot(
        x='nearest_route_distance', 
        y='Name', 
        data=underserved_schools.sort_values('nearest_route_distance', ascending=False),
        palette='Reds_r'
    )
    plt.title('Schools with Limited Transit Accessibility', fontsize=14)
    plt.xlabel('Distance to Nearest Transit (miles)')
    plt.ylabel('School Name')
    plt.tight_layout()
    plt.savefig('underserved_schools.png')

# 8. Transit Deserts Analysis 
if len(transit_deserts) > 0:
    plt.figure(figsize=(12, len(transit_deserts) * 0.4 + 2))
    sns.barplot(
        x='routes_within_radius', 
        y='Name', 
        data=transit_deserts.sort_values('routes_within_radius'),
        palette='Greens'
    )
    plt.title('Schools in Transit Deserts', fontsize=14)
    plt.xlabel('Number of Transit Routes within 0.5 Miles')
    plt.ylabel('School Name')
    plt.tight_layout()
    plt.savefig('transit_desert_schools.png')