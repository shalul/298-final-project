import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colors

# Load ZIP-level transit density data
density = pd.read_csv("heatmap/zip_avg_transit_density.csv")
density["ZCTA5CE10"] = density["ZCTA5CE10"].astype(float).astype(int).astype(str).str.zfill(5)

# Load ZIP-level income data
income = pd.read_csv("heatmap/zcta_income_mapping.csv")
income["ZCTA"] = income["ZCTA"].astype(str).str.zfill(5)
income = income.rename(columns={"ZCTA": "ZCTA5CE10"})
# Merge density and income on ZIP code
density = density.merge(income, on="ZCTA5CE10", how="left")
density["norm_income"] = (density["Median_Income"] - density["Median_Income"].min()) / (density["Median_Income"].max() - density["Median_Income"].min())
density["norm_density"] = (density["avg_transit_density"] - density["avg_transit_density"].min()) / (density["avg_transit_density"].max() - density["avg_transit_density"].min())
density["combined_score"] = (density["norm_income"] + density["norm_density"]) / 2

# Load NYC ZIP code boundaries
nyc_zips = gpd.read_file("nyc-zip-code-tabulation-areas-polygons.geojson")

# Rename column to match if needed
if "postalCode" in nyc_zips.columns:
    nyc_zips = nyc_zips.rename(columns={"postalCode": "ZCTA5CE10"})

# Convert ZIP code to string in GeoDataFrame
nyc_zips["ZCTA5CE10"] = nyc_zips["ZCTA5CE10"].astype(str)

# Filter for Queens ZIP codes
queens_zips = nyc_zips[nyc_zips["borough"] == "Queens"]

# Merge only the transit density values
map_data = queens_zips.merge(density, on="ZCTA5CE10", how="left")
map_data = map_data[map_data["combined_score"].notna()]

# Drop rows without a transit density score
#map_data = map_data[map_data["avg_transit_density"].notna()]

# Plot
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Create a colormap
cmap = cm.OrRd
norm = colors.Normalize(vmin=map_data["combined_score"].min(),
                        vmax=map_data["combined_score"].max())

# Plot map
map_data.plot(column="combined_score", cmap=cmap, linewidth=0.8,
              edgecolor="0.8", ax=ax, legend=False)

# Add a colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label("Normalized Income to Density Score")

# Title and cleanup
plt.title("Income to Transit Density Normalization by ZIP Code in Queens", fontsize=16)
plt.axis("off")
plt.show()

# income
map_data = map_data[map_data["Median_Income"].notna()]

# Drop rows without a transit density score
#map_data = map_data[map_data["avg_transit_density"].notna()]

# Plot
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Create a colormap
cmap = cm.OrRd
norm = colors.Normalize(vmin=map_data["Median_Income"].min(),
                        vmax=map_data["Median_Income"].max())

# Plot map
map_data.plot(column="Median_Income", cmap=cmap, linewidth=0.8,
              edgecolor="0.8", ax=ax, legend=False)

# Add a colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label("Median Income Score")

# Title and cleanup
plt.title("Median Income", fontsize=16)
plt.axis("off")
plt.show()

# transit
map_data = map_data[map_data["avg_transit_density"].notna()]

# Drop rows without a transit density score
#map_data = map_data[map_data["avg_transit_density"].notna()]

# Plot
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Create a colormap
cmap = cm.OrRd
norm = colors.Normalize(vmin=map_data["avg_transit_density"].min(),
                        vmax=map_data["avg_transit_density"].max())

# Plot map
map_data.plot(column="avg_transit_density", cmap=cmap, linewidth=0.8,
              edgecolor="0.8", ax=ax, legend=False)

# Add a colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label("avg_transit_density Score")

# Title and cleanup
plt.title("avg_transit_density", fontsize=16)
plt.axis("off")
plt.show()
