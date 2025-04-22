import geopandas as gpd
import pandas as pd

'''
FILES NEEDED TO RUN THIS CODE:
Route files:
MTA Bus Timepoints_20250414.geojson

Census files:
tl_2020_us_zcta510.cpg
tl_2020_us_zcta510.dbf
tl_2020_us_zcta510.prj
tl_2020_us_zcta510.shp
tl_2020_us_zcta510.shx

Dataset links:
https://catalog.data.gov/dataset/tiger-line-shapefile-2020-nation-u-s-2010-5-digit-zip-code-tabulation-areas-zcta5 
https://www.mta.info/open-data 

Note that only two of these are called explicitly, but those calls call the other files implicitly, so all files are needed
'''

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
