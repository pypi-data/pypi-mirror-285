import json
import math
import os.path
import traceback
from typing import List, Dict

import fiona
import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import shapely
from geojson.geometry import Geometry
from pyproj import CRS
from rasterio.features import rasterize
from scipy.spatial import cKDTree
from shapely import wkt, LineString, Polygon
from shapely.geometry import GeometryCollection, box
from shapely.ops import split
from sqlalchemy import Engine, create_engine, text

from digitalarztools.adapters.manager import DBString, DBManager, GeoDBManager
from digitalarztools.io.file_io import FileIO
from digitalarztools.proccessing.operations.geodesy import GeodesyOps
from digitalarztools.proccessing.operations.transformation import TransformationOperations
from digitalarztools.utils.logger import da_logger


class GPDVector(gpd.GeoDataFrame):
    # gdf: gpd.GeoDataFrame
    orig_crs: CRS

    def __init__(self, gdf: gpd.GeoDataFrame = None):
        if gdf is None:
            gdf = gpd.GeoDataFrame()
        elif not hasattr(gdf, 'geometry'):
            g_cols = self.get_geometry_columns(gdf)
            if len(g_cols) > 0:
                gdf.set_geometry(g_cols[0])

        super().__init__(gdf)
        self.orig_crs = self.crs if hasattr(self, 'crs') else None

    @staticmethod
    def get_geometry_columns(gdf: gpd.GeoDataFrame):
        geometry_columns = [col for col in gdf.columns if gdf[col].apply(lambda x: isinstance(x, Geometry)).all()]

    @classmethod
    def from_extent(cls, extent, srid):
        polygon = Polygon([(extent[0], extent[1]),
                           (extent[2], extent[1]),
                           (extent[2], extent[3]),
                           (extent[0], extent[3])])
        crs = CRS.from_epsg(srid)
        gdf = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs=crs)

        return cls(gdf)

    @classmethod
    def from_kml(cls, fp):
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
        gdf = gpd.read_file(fp, driver='KML')
        return cls(gdf)

    @property
    def extent(self):
        return self.total_bounds

    @classmethod
    def from_xy(cls, data: List[Dict], x_col='X', y_col='Y', crs='epsg:4326') -> 'GPDVector':
        """
        create GeoDataFrame from xy value in the data
        :param data: array of dict
        :param x_col:
        :param y_col:
        :param crs:
        :return: GPDVector
        """
        df = pd.DataFrame(data)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['centerLon'], df['centerLat']), crs='EPSG:4326')
        return cls(gdf)

    @classmethod
    def from_excel_xy(cls, src, sheet_name='Sheet1', x_col='X', y_col='Y', crs='epsg:4326') -> 'GPDVector':
        """
        Create GeoDataFrame from xy value in an excel file
        :param src:
        :param sheet_name:
        :param x_col:
        :param y_col:
        :param crs:
        :return:
        """
        if os.path.exists(src):
            df = pd.read_excel(src, sheet_name=sheet_name)
            geom = gpd.points_from_xy(df[x_col], df[y_col])
            gdf = gpd.GeoDataFrame(df, geometry=geom, crs=crs)
            return cls(gdf)
        else:
            raise Exception(f"Excel file doesn't exist at {src}")

    @classmethod
    def from_excel(cls, src, sheet_name='Sheet1', crs='epsg:4326', geom_col='geometry') -> 'GPDVector':
        if os.path.exists(src):
            df = pd.read_excel(src, sheet_name=sheet_name)
            gdf = gpd.GeoDataFrame(df)

            def load_wkt(x):
                try:
                    if pd.notnull(x):
                        return shapely.wkt.loads(x)
                    else:
                        return GeometryCollection()
                except:
                    return GeometryCollection()

            # gdf[geom_col] = gdf[geom_col].apply(wkt.loads)
            gdf["geometry"] = gdf[geom_col].apply(load_wkt)
            gdf.drop([geom_col], axis=1)
            gdf.geometry = gdf["geometry"]
            gdf.crs = crs
            # for index, row in df.iterrows():
            #     value = row[geom_col]
            #     try:
            #         if pd.notnull(value):
            #             # df[index][geom_col] = wkt.loads(value)
            #             df.xs(geom_col)[index] = wkt.loads(value)
            #     except Exception as e:
            #         traceback.print_exc()
            #         print(f'{index} [{len(value)}] {value!r}')
            # gdf = gpd.GeoDataFrame(df, geometry=df[geom_col], crs=crs)
            return cls(gdf)
        else:
            raise Exception(f"Excel file doesn't exist at {src}")

    @classmethod
    def from_shp(cls, src, srid: int = None) -> 'GPDVector':
        gdf = gpd.read_file(src)
        if srid is not None:
            gdf.crs = srid
        return cls(gdf)

    @classmethod
    def from_df(cls, df, geom_col='geometry', crs="EPSG:4326") -> 'GPDVector':
        gdf = gpd.GeoDataFrame(df, geometry=df[geom_col], crs=crs)
        return cls(gdf)

    @classmethod
    def from_df_xy(cls, df, x_col, y_col, crs='epsg:4326') -> 'GPDVector':
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_col], df[y_col]))
        gdf.crs = crs
        return cls(gdf)

    @classmethod
    def from_geojson(cls, geojson: dict, crs='epsg:4326'):
        gdf = gpd.GeoDataFrame.from_features(geojson, crs)
        return cls(gdf)

    @classmethod
    def from_gpkg(cls, src, layer=None) -> 'GPDVector':
        gdf = gpd.read_file(src, layer=layer)
        return cls(gdf)

    @classmethod
    def from_postgis(cls, query: str, db_str: DBString, srid, geom_col='geom') -> 'GPDVector':
        engine = DBManager.create_postgres_engine(db_str)
        manager = GeoDBManager(engine)
        gdf = manager.execute_query_as_gdf(query, srid, geom_col)
        return cls(gdf)

    def to_gdf(self, inplace=True) -> gpd.GeoDataFrame:
        if not inplace:
            return gpd.GeoDataFrame(self.copy())
        return gpd.GeoDataFrame(self)

    def to_gpkg(self, des, layer):
        self.to_file(des, layer=layer, driver="GPKG")

    def to_excel(self, des, sheet_name="Sheet1", mode='a'):
        """
        :param des: destination file
        :param sheet_name:
        :param mode: either w (write) or a (append) default w
        :return:
        """
        cols = self.to_gdf().select_dtypes(include=['datetime64[ns, UTC]']).columns
        for col in cols:
            self[col] = self[col].dt.tz_localize(None)

        mode = mode if os.path.exists(des) else 'w'
        sheet_exists = 'replace' if os.path.exists(des) else None
        with pd.ExcelWriter(des, engine="openpyxl", mode=mode, if_sheet_exists=sheet_exists) as writer:
            self.to_gdf().to_excel(writer, sheet_name=sheet_name, index_label="id")
            da_logger.info(f"Excel file successfully created at {des}")

    # def to_file(self, des, driver=):
    #     self.to_gdf().to_file(des)

    def to_4326(self) -> 'GPDVector':
        if str(self.crs) != "EPSG:4326":
            aoi = GPDVector(self.get_gdf().to_crs(epsg=4326))
            return GPDVector(aoi)
        return self

    def get_srs(self) -> str:
        return self.crs.srs

    def get_crs(self):
        return self.crs

    def to_crs(self, crs=None, epsg=None) -> 'GPDVector':
        """
        :param crs:
        :param epsg:
        :return:
        """
        return GPDVector(self.get_gdf().to_crs(crs=crs, epsg=epsg))

    def to_raster(self, res: float = None, value_col: str = None, refRaster=None) -> 'RioRaster':
        """
            res: resolution of output raster file
            extent: extent of output raster
            size: size of output raster
            value_col: name of col with value to use for raster like 'id'
        """
        # out_arr = np.zeros((rows,cols))
        # shapes = ((geom, value) for geom, value in zip(self.geometry, self[value_col]))
        # rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
        if refRaster is None:
            extent = tuple(self.get_extent())
            out_shape = (math.ceil((extent[2] - extent[0]) / res), math.ceil((extent[3] - extent[1]) / res))
            transform = TransformationOperations.get_affine_matrix(extent, out_shape)
        else:
            # extent = refRaster.get_raster_extent()
            out_shape = refRaster.get_img_resolution()
            transform = refRaster.get_geo_transform()
        shapes = self.get_geometry_list(value_col)
        if value_col is None:
            shapes = list(zip(shapes, [1] * len(shapes)))
        data = rasterize(shapes, out_shape=out_shape, transform=transform)
        from digitalarztools.io.raster.rio_raster import RioRaster
        raster = RioRaster.raster_from_array(data, crs=self.crs, g_transform=transform,
                                             nodata_value=0)

        return raster

    def to_crs_original(self):
        if str(self.crs) != str(self.orig_crs):
            self = self.to_crs(crs=self.orig_crs)

    def get_extent(self):
        return tuple(self.geometry.total_bounds)

    def inplace_result(self, gdf, inplace) -> 'GPDVector':
        if inplace:
            # self = GPDVector(gdf)
            self.__init__(gdf)
            return self
        else:
            return GPDVector(gdf)

    def extract_sub_data(self, col_name: str, col_vals: list, inplace=False) -> 'GPDVector':
        """
        :param col_name: column name
        :param col_vals: column value as a list
        :param inplace:
        :return:
        """
        if isinstance(col_vals, list):
            res = []
            for v in col_vals:
                res.append(self[self[col_name] == v])

            gdf = gpd.GeoDataFrame(pd.concat(res, ignore_index=True), crs=self.get_crs())
        else:
            gdf = self[self[col_name] == col_vals]
        return self.inplace_result(gdf, inplace)

    def select_columns(self, cols, inplace=True):
        gdf = self[cols]
        return self.inplace_result(gdf, inplace)

    def select_by_index(self, selected_indices: list, inplace=True):
        gdf = self.iloc[selected_indices]
        return self.inplace_result(gdf, inplace)

    def add_id_col(self):
        """
        add id column in the dataframe
        """
        self["id"] = self.index + 1

    def add_class_id(self, class_id, value=None):
        # if value is not none:
        #     self.g
        self['cls_id'] = class_id

    def add_area_col(self, unit='sq.km'):
        """
        :param unit: values sq.km, sq.m
        :return:
        """
        gdf = self.to_crs(epsg='3857') if self.crs.is_geographic else self
        if unit == "sq.km":
            self['area'] = round(gdf.geometry.area / (1000 * 1000), 4)
        else:
            self['area'] = round(gdf.geometry.area, 4)

    def get_geometry(self, col_name, col_val):
        res = self[self[col_name] == col_val]['geometry']
        if not res.empty:
            return res.values[0]

    def get_gdf(self):
        return gpd.GeoDataFrame(self, crs=self.crs, geometry=self.geometry)

    def get_geometry_list(self, attr_name=None) -> list:
        if attr_name:
            # return [(row['geometry'], row[attr_name]) for index, row in self.iterrows()]
            return list(zip(self['geometry'], self[attr_name]))
        else:
            return self.geometry.tolist()

    def spatial_operation(self, gdf: gpd.GeoDataFrame):
        intersects_result = self.is_intersects(gdf)
        self.__init__(self[intersects_result])

    def is_intersects(self, gdf: gpd.GeoDataFrame):
        if str(self.crs) != str(gdf.crs):
            gdf.to_crs(self.crs)
        return self.intersects(gdf)

    def spatial_join(self, input_gdf: gpd.GeoDataFrame, predicate='intersects', how="inner", remove_input_columns=True,
                     in_place=True, geom_col='geometry') -> 'GPDVector':
        if str(input_gdf.crs) != str(self.get_crs()):
            input_gdf = input_gdf.to_crs(self.get_crs())
        if remove_input_columns:
            input_gdf = input_gdf[[geom_col]]
        join_result = gpd.sjoin(self.get_gdf(), input_gdf, how=how, predicate=predicate)
        join_result = join_result.drop(('index_right'), axis=1)
        if in_place:
            self.__init__(join_result)
        return GPDVector(join_result)

    def to_geojson(self, fp: str = None):
        # gdf = self.dropna()
        gdf_json = self.to_gdf(inplace=False)
        if '4326' not in str(self.crs):
            gdf_json.to_crs(epsg=4326, inplace=True)

        # convert date column to string column
        for col in gdf_json.columns:
            if pd.api.types.is_datetime64_any_dtype(gdf_json[col]):
                gdf_json[col] = gdf_json[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        # geojson = gdf_json.to_json()
        geojson = gdf_json.__geo_interface__
        if fp is not None:
            with open(fp, 'w') as file:
                file.write(geojson)
        # return json.loads(geojson)
        return geojson

    def apply_buffer(self, distance_in_meter: int) -> 'GPDVector':
        """
        :param distance_in_meter: buffer distance in radiuse
        :param inplace:
        :return: GPDVector
        """
        old_crs = self.crs
        if self.crs.is_geographic:
            gdv = self.to_crs(epsg=3857)
        else:
            gdv = self
        gdv.geometry = gdv.buffer(distance_in_meter)

        gdv = gdv.to_crs(crs=old_crs)
        return gdv

    # def get_unary_union(self):
    #     """
    #     combine all geometry as a single geometry
    #     :return: shapely geometry
    #     """
    #     if self.get_rows_count() > 1:
    #         return self.geometry.unary_union
    #     else:
    #         return self.geometry.values[0]

    @staticmethod
    def get_rows_count(gdf) -> int:
        """
        :return: rows count
        """
        return gdf.shape[0]

    @staticmethod
    def get_cols_count(gdf) -> int:
        """
        :return: no of columns
        """
        return gdf.shape[1]

    def get_cols_list(self) -> list:
        """
        :return: column name list
        """
        return self.columns.tolist()

    def get_col_values(self, col_name) -> list:
        return self[col_name].values.tolist()

    def calculate_total_area(self):
        gdf = self.to_crs(epsg=3857)
        return gdf.area.sum()

    def remove_duplicates(self, col_name=None):
        if col_name is None:
            gdf = self.drop_duplicates(keep='first')
        else:
            gdf = self[~self.set_index(col_name).index.duplicated()]
        self.inplace_result(gdf, inplace=True)

    def remove_duplicate_geometry(self, sort_by=[], ascending=[]):
        """
        :return:
        """
        if len(sort_by) > 0:
            self.sort_values(sort_by, ascending=ascending, inplace=True)
        unique_geometries = []
        unique_index = []
        # Iterate through the GeoDataFrame and check for spatial equality
        for idx, row in self.iterrows():
            geometry = row['geometry']
            # if not any(geometry.contains(existing_geom.centroid) for existing_geom in unique_geometries):
            if not any(geometry.equals(existing_geom) for existing_geom in unique_geometries):
                unique_geometries.append(geometry)
                unique_index.append(idx)

        self.select_by_index(unique_index)
        # Create a new GeoDataFrame with unique geometries
        # unique_data = {'geometry': unique_geometries}
        # selected_rows = self.iloc[unique_index]
        # unique_gdf = gpd.GeoDataFrame(unique_data, crs='EPSG:4326')

        # return GPDVector(selected_rows)

    def is_empty(self):
        return self.empty

    def check_dates_available(self, col_name, start_date, end_date):
        res = self[self[col_name].between(start_date, end_date)]
        return res

    @classmethod
    def extent_2_envelop(cls, min_x, min_y, max_x, max_y, crs) -> 'GPDVector':
        wkt = f"Polygon(({min_x} {max_y}, {max_x} {max_y}, {max_x} {min_y}, {min_x} {min_y}, {min_x} {max_y} ))"
        env = shapely.wkt.loads(wkt)

        return cls(gpd.GeoDataFrame({'geometry': env}, index=[0], crs=crs))

    def to_datetime(self, col_name, format):
        self[col_name] = pd.to_datetime(self[col_name], format=format)

    def clip_data(self, gdf: gpd.GeoDataFrame) -> 'GPDVector':
        if str(gdf.crs) != str(self.crs):
            gdf.to_crs(self.crs, inplace=True)
        new_gdf = self.clip(gdf, False)
        # new_gdf.set_geometry(gdf.geometry)
        # new_gdf.crs = gdf.crs
        return GPDVector(new_gdf)

    """"
        Spatial operation
    """

    def within_aoi(self, aoi: 'GPDVector') -> 'GPDVector':
        if str(self.crs).lower() != str(aoi.crs).lower():
            aoi = aoi.get_gdf().to_crs(self.crs)
        else:
            aoi = aoi.get_gdf()
        aoi_polygon = aoi.unary_union

        gdf_within_aoi = self[self.geometry.within(aoi_polygon)]
        return GPDVector(gdf_within_aoi)

    @staticmethod
    def combine_files(dir_path, output_fp, driver='GPKG'):
        if driver == 'GPKG':
            ext = 'gpkg'
        else:
            ext = 'shp'
        files = FileIO.list_files_in_folder(dir_path, ext)
        combined_gdf = gpd.GeoDataFrame()
        for fp in files:
            gdf = gpd.read_file(fp, driver=driver)
            gdf.columns = [col.lower() for col in gdf.columns]

            # final_gdf = gpd.GeoDataFrame(pd.concat([final_gdf, gdf]), geometry="geometry")
            combined_gdf = pd.concat([combined_gdf, gdf], ignore_index=True, sort=False)
            # print(combined_gdf.shape)
        combined_gdf.to_file(output_fp, driver=driver)

    @staticmethod
    def calculate_distance(lon1, lat1, lon2, lat2):
        wgs84 = pyproj.Geod(ellps='WGS84')
        _, _, distance = wgs84.inv(lon1, lat1, lon2, lat2)
        return distance

    def create_index_map(self, cell_size_meters: float) -> gpd.GeoDataFrame:
        target_geometry = self.unary_union
        minx, miny, maxx, maxy = target_geometry.bounds
        if self.crs.is_geographic:
            # Calculate the width and height of each grid cell in degrees
            cell_width = cell_size_meters / self.calculate_distance(minx, miny, maxx, miny)
            cell_height = cell_size_meters / self.calculate_distance(minx, miny, minx, maxy)
        else:
            cell_width = cell_size_meters / (maxx - minx)
            cell_height = cell_size_meters / (maxy - miny)
        print(cell_width, cell_height)
        # Create the index map GeoDataFrame
        # index_map = gpd.GeoDataFrame(geometry=[])
        index_map = []
        # Populate the index map with grid cells
        for row in range(int((maxy - miny) / cell_height)):
            for col in range(int((maxx - minx) / cell_width)):
                cell_minx = minx + col * cell_width
                cell_miny = miny + row * cell_height
                cell_maxx = cell_minx + cell_width
                cell_maxy = cell_miny + cell_height
                cell_geometry = box(cell_minx, cell_miny, cell_maxx, cell_maxy)
                if cell_geometry.intersects(target_geometry):
                    index_map.append({"geom": cell_geometry, "row": row, "col": col})

        return gpd.GeoDataFrame(index_map, geometry="geom", crs=self.crs)

    def remove_duplicate_point_nearby(self, distance_threshold_in_meter):

        distance_threshold = distance_threshold_in_meter if not self.crs.is_geographic else GeodesyOps.meters_to_dd_wgs_84(
            self.centroid, distance_threshold_in_meter)

        coords = np.array(list(self.geometry.apply(lambda geom: (geom.x, geom.y))))
        tree = cKDTree(coords)
        clusters = tree.query_ball_tree(tree, r=distance_threshold)

        # Create a set to keep track of points to retain
        retain_indices = set()
        for cluster in clusters:
            if cluster:
                retain_indices.add(cluster[0])  # Keep the first point in each cluster

        # Filter GeoDataFrame to retain only selected points
        self.__init__(self.iloc[list(retain_indices)])

    @staticmethod
    def get_geometry_column_name(gdf: gpd.GeoDataFrame):
        return gdf.geometry.name

    @staticmethod
    def split_geometry_half(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        # Combine all geometries into a single unified geometry
        polygon = gdf.unary_union

        # Compute the centroid of the unified geometry
        centroid = polygon.centroid

        # Determine the extension length for the transverse line based on the CRS
        ext = 1 if gdf.crs.is_geographic else 100000

        # Create a transverse line passing through the centroid
        transverse_line = LineString([(centroid.x, centroid.y - ext), (centroid.x, centroid.y + ext)])

        # Split the polygon using the transverse line
        cut_geometries = split(polygon, transverse_line)

        # Ensure the result is iterable
        if isinstance(cut_geometries, GeometryCollection):
            # Extract individual geometries from the collection
            geometries = [geom for geom in cut_geometries.geoms]
        else:
            # If not a collection, ensure it is a list
            geometries = [cut_geometries]

            # Handle cases where more than two geometries are produced
            if len(geometries) > 2:
                # Sort geometries by their area in descending order
                geometries = sorted(geometries, key=lambda geom: geom.area, reverse=True)
                # Take only the two largest geometries
                geometries = geometries[:2]

        # Create a GeoDataFrame from the resulting geometries
        res = gpd.GeoDataFrame(geometry=geometries, crs=gdf.crs)
        return res

    @staticmethod
    def standardize_geometry_column(gdf: gpd.GeoDataFrame, geom_col_name: str = 'geometry') -> gpd.GeoDataFrame:
        # Check if the expected geometry column name is in the columns
        if geom_col_name not in gdf.columns:
            # Find the actual geometry column
            actual_geom_col = gdf.geometry.name
            # Rename the geometry column to the standard name
            gdf = gdf.rename(columns={actual_geom_col: geom_col_name})
        # Ensure the geometry column is set as the active geometry
        gdf.set_geometry(geom_col_name, inplace=True)
        return gdf

    @classmethod
    def combine_geo_dataframe(cls, geo_dataframes: list) -> gpd.GeoDataFrame:
        standardized_gdfs = []
        for gdf in geo_dataframes:
            standardized_gdf = cls.standardize_geometry_column(gdf, 'geometry')
            standardized_gdf.set_geometry('geometry', inplace=True)
            standardized_gdfs.append(standardized_gdf)

        # Concatenating the standardized GeoDataFrames
        combined_gdf = gpd.GeoDataFrame(pd.concat(standardized_gdfs, ignore_index=True))

        # print(combined_gdf)
        return combined_gdf

    @classmethod
    def get_unary_union_gdf(cls, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        # Perform unary union of all geometries
        # unioned_geom = unary_union(gdf.geometry)
        if cls.get_rows_count(gdf) > 1:
            unioned_geom = gdf.geometry.unary_union
        else:
            unioned_geom = gdf.geometry.values[0]
        # Create a new GeoDataFrame with the unioned geometry
        return gpd.GeoDataFrame(geometry=[unioned_geom], crs=gdf.crs)

    @staticmethod
    def row_geometry_to_gdf(row_geom, crs) -> gpd.GeoDataFrame:
        new_gdf = gpd.GeoDataFrame(index=[1], crs=crs, geometry=[row_geom])
        return new_gdf
