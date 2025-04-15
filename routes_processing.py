import geopandas as gpd
import pandas as pd

def extract_route_data_and_overlay_with_census(geojson_path, census_shp_path, output_csv):

    routes = gpd.read_file(geojson_path)

    zcta = gpd.read_file(census_shp_path)
    zcta = zcta.to_crs(epsg=4326)  
    routes = routes.to_crs(epsg=4326)

    routes['latitude'] = routes.geometry.y
    routes['longitude'] = routes.geometry.x

    routes_with_zcta = gpd.sjoin(routes, zcta, how="left", predicate="within")

    columns_to_drop = ["timepoint_stop_name","cbd","timepoint_stop_id","geometry","index_right","GEOID10","CLASSFP10","MTFCC10","FUNCSTAT10","ALAND10","AWATER10","INTPTLAT10","INTPTLON10"]
    routes_with_zcta_csv = routes_with_zcta.drop(columns=columns_to_drop)


    routes_with_zcta_csv.to_csv(output_csv, index=False)


geojson_path = "MTA Bus Timepoints_20250414.geojson"
census_shp_path = "tl_2020_us_zcta510.shp"  # Census ZCTA shapefile

output_csv = "routes_with_zcta.csv"




extract_route_data_and_overlay_with_census(geojson_path,census_shp_path, output_csv)
