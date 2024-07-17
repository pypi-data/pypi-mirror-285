import json
import os.path

import ee
import geopandas as gpd
from shapely.geometry import shape
from tqdm import tqdm

from digitalarztools.io.file_io import FileIO
from digitalarztools.io.vector.gpd_vector import GPDVector
from digitalarztools.pipelines.gee.core.region import GEERegion


class GEEFeatureCollection():
    fc: ee.FeatureCollection = None
    region: GEERegion = None

    def __init__(self, fc: ee.FeatureCollection, region: GEERegion = None):
        self.fc = fc
        if region is not None:
            self.region = region
            self.fc.filterBounds(region.get_aoi())

    def filter_bounds(self, region: GEERegion):
        self.region = region
        self.fc.filterBounds(region.get_aoi())

    def download_feature_collection(self, fp: str):
        if self.region is not None:
            region_gdv = self.region.aoi_gdv

            dir_name = FileIO.mkdirs(fp)
            # print(index_map.head())
            # for index, geometry in enumerate(index_map.geometry):
            temp_dir = os.path.join(dir_name, "temp")
            temp_dir = FileIO.mkdirs(temp_dir)
            index_map_fp = os.path.join(dir_name, "index_map.gpkg")
            if os.path.exists(index_map_fp):
                index_map = GPDVector.from_gpkg(index_map_fp)
            else:
                index_map = GPDVector(region_gdv.create_index_map(1000))
                index_map.to_file(index_map_fp, driver='GPKG')
            for index, row in tqdm(index_map.iterrows(),
                                   total=index_map.shape[0],
                                   desc='Downloading features'):
                fp = os.path.join(temp_dir, f"r{row.row}_c{row.col}.gpkg")
                if not os.path.exists(fp):
                    # print(index)
                    roi = ee.Geometry.Rectangle(row.geometry.bounds)  # Replace with actual coordinates

                    fc = self.fc.filterBounds(roi)
                    # Get the feature collection as a list of dictionaries
                    features_list = fc.getInfo()['features']

                    # Extract geometries from the features
                    # geometries = [shape(feature['geometry']) for feature in features_list]

                    # Create a GeoDataFrame
                    # gdf = gpd.GeoDataFrame(features_list)
                    # gdf['geometry'] = gdf.geometry.apply(lambda g: shape(g))
                    # gdf.geometry = gdf['geometry']
                    # gdf.crs = 'EPSG:4326'

                    gdf = GPDVector.from_geojson(features_list)
                    # print(gdv.head())

                    gdf.to_file(fp, driver='GPKG')
            # # gdv.to_file()
            GPDVector.combine_files(temp_dir, output_fp=fp)
        else:
            print("please specify region....")

    def get_fc(self):
        return self.fc

    @classmethod
    def from_shapefile(cls, shp_path):
        gdf = gpd.read_file(shp_path)
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        geojson = json.loads(gdf.to_json())
        return cls.from_geojson(geojson)

    @classmethod
    def from_gee_tag(cls, tags):
        return ee.FeatureCollection(tags)

    @classmethod
    def from_geojson(cls, geojson: dict, proj='EPSG:4326'):
        ee_features = []
        for feature in geojson['features']:
            geom = ee.Geometry(feature["geometry"], opt_proj=proj)
            ee_features.append(ee.Feature(geom, feature['properties']))
        obj = cls()
        obj.fc = ee.FeatureCollection(ee_features)
        return obj

    def getInfo(self):
        return self.fc.getInfo()

    def getMapId(self):
        return self.fc.getMapId()

    @staticmethod
    def get_max_value(feature_collection, property_name):
        features = feature_collection['features']
        max_temp = max(feature['properties'][f'{property_name}_max'] for feature in features)
        return max_temp


