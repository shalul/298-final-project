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

Note that only two of these are called explicitly, but those calls call the other files implicitly, so all files are needed
'''

#class to read in public school information
class PublicSchool:
    def __init__(self, shapefile_path):
        self.schools = gpd.read_file(shapefile_path) #read in gpd file
        self._standardize_crs() #standardize lat/long format, for compatibility with the census formatting

    def _standardize_crs(self):
        # Ensure CRS is in WGS84 (lat/lon)
        if self.schools.crs and not self.schools.crs.is_geographic:
            self.schools = self.schools.to_crs(epsg=4326)


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

