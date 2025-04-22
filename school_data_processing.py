import geopandas as gpd

'''
FILES NEEDED TO RUN THIS CODE:
School files:
SchoolPoints_APS_2024_08_28.cpg
SchoolPoints_APS_2024_08_28.dbf
SchoolPoints_APS_2024_08_28.prj
SchoolPoints_APS_2024_08_28.sbn
SchoolPoints_APS_2024_08_28.sbx
SchoolPoints_APS_2024_08_28.shp
SchoolPoints_APS_2024_08_28.shx

Census files:
tl_2020_us_zcta510.cpg
tl_2020_us_zcta510.dbf
tl_2020_us_zcta510.prj
tl_2020_us_zcta510.shp
tl_2020_us_zcta510.shx

Dataset links:
https://data.cityofnewyork.us/Education/School-Point-Locations/jfju-ynrr/about_data
https://catalog.data.gov/dataset/tiger-line-shapefile-2020-nation-u-s-2010-5-digit-zip-code-tabulation-areas-zcta5 

Note that only two of these are called explicitly, but those calls call the other files implicitly, so all files are needed
'''

shapefile_path = "SchoolPoints_APS_2024_08_28.shp" #might need to be changed depending on local path

zcta = gpd.read_file("tl_2020_us_zcta510.shp") #load census data as geographic data

schools = gpd.read_file(shapefile_path) #load school data as geographic data

zcta = zcta.to_crs(epsg=4326) #set CRS format
schools = schools.to_crs(epsg=4326) #set CRS format

schools_with_zcta = gpd.sjoin(schools, zcta, how="left", predicate="within") #spatial join by zip code

# drop all columns minus school name, lat, long, and zcta
columns_to_drop=["ATS","Building_C","Location_C","Geographic","index_right","GEOID10","CLASSFP10","MTFCC10","FUNCSTAT10","ALAND10","AWATER10","INTPTLAT10","INTPTLON10", 'geometry']
schools_with_zcta_csv = schools_with_zcta.drop(columns=columns_to_drop) #drop the columns from the dataset


schools_with_zcta_csv.to_csv("new_york_schools.csv", index=False) #save to a csv

