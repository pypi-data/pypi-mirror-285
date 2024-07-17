from io import BytesIO
from typing import Dict, Union

import mercantile
import numpy as np
import pyproj
import rasterio
import shapely
from PIL import Image
from rasterio.transform import from_origin

from digitalarztools.io.raster.rio_process import RioProcess
from digitalarztools.proccessing.operations.transformation import TransformationOperations
from geopandas import GeoDataFrame
from rasterio import MemoryFile
from rasterio.enums import Resampling
from rasterio.session import AWSSession

from rio_tiler.io import COGReader
from rio_tiler.colormap import cmap
from rio_tiler.models import ImageData

from digitalarztools.io.file_io import FileIO
from digitalarztools.io.raster.rio_raster import RioRaster

from digitalarztools.utils.logger import da_logger


class COGRaster(COGReader):
    # cog: COGReader
    file_path: str

    # def __init__(self, uuid: str, is_s3: bool = True):
    #     pass

    @staticmethod
    def open_cog(fp, s3_session=None):
        """

        :param fp:
        :param s3_session: required when for s3
        :return:
        example of local file
        cog_fp = os.path.join(media_dir, '**********.tif')
        COGRaster.open_cog(cog_fp)

        example of s3 data
        s3_utils = S3Utils(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,AWS_S3_REGION_NAME)
        cog_uri = s3_utils.get_s3_uri("****", "*******.tif")

        return COGRaster.open_cog(cog_uri, s3_utils.get_session())
        """
        if "s3://" in fp:
            return COGRaster.open_from_s3(fp, s3_session)
        else:
            return COGRaster.open_from_local(fp)

    @classmethod
    def open_from_url(cls, url):
        cog_raster = cls(url)
        cog_raster.file_path = url
        return cog_raster

    @classmethod
    def open_from_local(cls, file_path: str) -> 'COGRaster':
        cog_raster = cls(file_path)
        # cog_raster = COGReader(file_path)
        cog_raster.file_path = file_path
        return cog_raster

    @classmethod
    def open_from_s3(cls, s3_uri: str, session) -> 'COGRaster':
        # cog_raster = cls()
        # s3_uri = S3Utils.get_cog_uri(f"{file_name}.tif")
        # cog_raster.cog = S3Utils().get_cog_rio_dataset(s3_uri)
        session = rasterio.Env(AWSSession(session))
        with session:
            # cog_raster.cog = COGReader(s3_uri)
            cog_raster = cls(s3_uri)
            cog_raster.file_path = s3_uri
            return cog_raster

    # @staticmethod
    # def upload_to_s3(src_path_name, des_path_uri, session: Session):
    #     try:
    #         # file_path, object_name = CommonUtils.separate_file_path_name(des_path_name)
    #         bucket_name, object_path = S3Utils.get_bucket_name_and_path(des_path_uri)
    #         response = session.client("s3").upload_file(src_path_name, bucket_name, object_path)
    #     except ClientError as e:
    #         da_logger.error(e)
    #         da_logger.error(traceback.print_exc())
    #         return False
    #     return True

    def get_file_path(self):
        return self.file_path

    def get_rio_raster(self, mask_area: Union[GeoDataFrame, shapely.geometry.Polygon, shapely.geometry.MultiPolygon] = None, crs=0) -> RioRaster:
        raster = RioRaster(self.dataset)
        if mask_area is not None:
            raster.clip_raster(mask_area, crs=crs)
        return raster

    @classmethod
    def create_cog_using_rio(cls, src_fp: str, des_fp: str):
        with rasterio.open(src_fp) as src:
            # Read the metadata from the original dataset
            # data = src.read(1)

            meta = src.meta.copy()

            # Create an in-memory buffer to hold the COG data
            with MemoryFile() as memfile:
                # Update the metadata to make the file Cloud Optimized
                meta.update(
                    driver='COG',
                    # tiled=True,
                    # compressed=False,
                    # blockxsize=512,
                    # blockysize=512,
                    compress='deflate',  # You can use other compression options
                    predictor=2  # This predictor improves compression for floating-point data
                )

                # Create a new COG dataset in the in-memory buffer
                with memfile.open(**meta) as dst:
                    # Copy the original data to the COG dataset
                    for i in range(1, src.count + 1):
                        dst.write(src.read(i), i)

                # Write the COG data to a new file
                with open(des_fp, 'wb') as output_file:
                    output_file.write(memfile.read())

    @classmethod
    def create_cog(cls, src_path: str, des_path: str,
                   profile: str = "deflate",
                   profile_options: dict = {},
                   **options):
        """
        :param src_rio_raster:
        :param des_path:
        :param profile:  jpeg, webp, zstd, lzw, deflate, packbits, lzma, lerc, lerc_deflate, lerc_zstd, raw
        :param profile_options: read options from https://gdal.org/drivers/raster/cog.html
        :param options:
        :return:
        """
        FileIO.mkdirs(des_path)
        # with src_rio_raster.get_dataset() as src:
        #     """Convert image to COG."""
        #     output_profile = cog_profiles.get(profile)
        #     output_profile.update(dict(BIGTIFF="IF_SAFER"))
        #     output_profile.update(profile_options)
        #
        #     # Dataset Open option (see gdalwarp `-oo` option)
        #     config = dict(
        #         GDAL_NUM_THREADS="ALL_CPUS",
        #         GDAL_TIFF_INTERNAL_MASK=True,
        #         GDAL_TIFF_OVR_BLOCKSIZE="128",
        #     )
        #
        #     cog_translate(
        #         src,
        #         des_path,
        #         output_profile,
        #         overview_level=4,
        #         config=config,
        #         in_memory=False,
        #         quiet=True,
        #         **options,
        #     )
        #     print("cog created")
        #     return cls.open_from_local(des_path)
        with rasterio.open(src_path) as src:
            profile = src.profile

            # Copy the dataset and write as a COG
            profile['driver'] = 'COG'

            # Copy the dataset and write as a COG
            with rasterio.open(des_path, 'w', **profile) as dst:
                for i in range(1, src.count + 1):
                    resampled_data = src.read(i, out_shape=(src.height, src.width), resampling=Resampling.nearest)
                    dst.write(resampled_data, i)

    @staticmethod
    def create_color_map(style):
        """
         style = {'labels': ['sandy loam', 'loam', 'clay loam', 'clay loam'],
             'values': ['30', '40', '50', '60'], 'max_val': 59.79513168334961,
             'min_val': 30.0, 'palette': ['#1a9641', '#c4e687', '#fec981', '#d7191c']}

        style = {"labels": ["<= 18.0109", "18.0109 - 32.0722", "32.0722 - 46.1335", "46.1335 - 60.1948", "> 60.1948"],
             "values": [18.01091274, 32.07221998, 46.13352722, 60.194834459999996, 67.29322814941406], "max_val": 67.29322814941406, "min_val": 2.9422078132629395,
             "palette": ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]}


        style = {"labels": ["", "Wheat", "Potato and Maize", "Potato", "Spring Maize", "Double Maize", "Fodder", "Orchards", "Sugarcane", "Others", "Trees and Plantation", "Builtup Area", "Fallow Land", "Water Bodies"],
             "palette": {"0": "#00000000", "1": "#92ff57", "2": "#a020f0", "3": "#ffffe0", "4": "#00c0ff", "5": "#7fff00", "6": "#ffff00", "7": "#008000", "8": "#ff8000", "9": "#9200ff", "10": "#7fffd4", "11": "#ff0000", "12": "#a0522d", "13": "#0000ff"}}
        :param style:
        :return:
        """
        palette = style['palette']
        custom_color = {}
        j = 0
        for p in palette:
            h = f"{palette[p] if isinstance(palette, dict) else p}FF".lstrip('#')
            custom_color[j] = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
            j = j + 1
        if "values" in style:
            values = style["values"]
            values = sorted(values, key=float)
            values[0] = style['min_val'] if values[0] > style['min_val'] else values[0]
            values.append(style['max_val'] if values[-1] < style['max_val'] else values[-1] + 1)
            color_map = []
            for i in range(len(custom_color)):
                color_map.append(((values[i], values[i + 1]), custom_color[i]))
            return color_map
        else:
            # print("custom color", custom_color)
            cp = cmap.register({"cc": custom_color})
            return cp.get("cc")

    def read_tile_as_png(self, x: int, y: int, z: int, color_map: dict, tile_size=256):
        try:
            tile: ImageData = self.tile(x, y, z, tilesize=tile_size)
            # tile.rescale(
            #     in_range=((0, 25),),
            #     out_range=((0, 255),)
            # )
            # if not color_map:
            #     return BytesIO(tile.render(False, img_format="GTIFF"))
            # else:
            return BytesIO(tile.render(True, colormap=color_map, img_format='PNG'))
        except Exception as e:
            # da_logger.error(traceback.print_exc())
            return self.create_empty_image(tile_size, tile_size)
            # pass

    @staticmethod
    def create_alpha_band(size_x, size_y):
        return np.zeros([size_x, size_y], dtype=np.uint8)

    def create_empty_image(self, size_x, size_y):
        blank_image = np.zeros([size_x, size_y, 4], dtype=np.uint8)
        # np_array.fill(255)  # or img[:] = 255
        # blank_image[:, :, 3] = 0
        return self.create_image(blank_image)

    @staticmethod
    def create_image(np_array, format="PNG", f_name=None, is_data_file=False):
        img = Image.fromarray(np_array)
        # if f_name and is_data_file:
        #     fp = os.path.join('media/temp', f_name)
        #     FileIO.mkdirs(fp)
        #     img.save(fp, format)

        buffer = BytesIO()
        img.save(buffer, format=format)  # Enregistre l'image dans le buffer
        # return "data:image/PNG;base64," + base64.b64encode(buffer.getvalue()).decode()
        return buffer  # .getvalue()

    def get_pixel_value_at_long_lat(self, long: float, lat: float):
        try:
            pixel_val = self.point(long, lat)
            return pixel_val
        except Exception as e:
            # DataLogger.log_error_message(e)
            pass

    def read_tile(self, tile_x: int, tile_y: int, tile_z: int, tile_size: int = 256):
        # Read the tile data
        if self.tile_exists(tile_x, tile_y, tile_z):
            tile_data, tile_mask = self.tile(tile_x, tile_y, tile_z, tilesize=tile_size)
        else:
            tile_data = self.create_empty_image(tile_size, tile_size)
            tile_mask = None

        return tile_data, tile_mask

    def read_data_under_aoi(self, gdf:GeoDataFrame) -> RioRaster:
        """
        geojson in wgs84
        """
        tiles = mercantile.tiles(*gdf.to_crs(epsg=4326, inplace=False).total_bounds.tolist(),
                                 zooms=self.maxzoom - 1)

        ds_files = []
        for tile in tiles:
            data, mask = self.read_tile(tile.x, tile.y, tile.z)
            # extent = MVTUtils.xyz_to_extent_4326(tile.x, tile.y, tile.z)
            if isinstance(data,BytesIO):
                data = np.zeros((1, 256, 256))
            # if isinstance(data, np.ndarray):
            extent = mercantile.bounds(*tile)
            raster = self.rater_from_array(data, mask, list(extent))
            # raster.save_to_file(os.path.join(MEDIA_DIR, 'pak/temp', f'{tile.x}_{tile.y}_{tile.z}.tif'))
            ds_files.append(raster.get_dataset())
        final_raster = RioProcess.mosaic_images(ds_files=ds_files)
        return final_raster

    def rater_from_array(self, data, mask, extent: list,tile_size=256) -> RioRaster:
        # Create a masked array from the data using the mask
        # masked_data = np.ma.masked_array(data, ~mask)

        # Get metadata from the original COGReader
        meta = self.dataset.meta

        # Calculate the transform for the subset
        # g_transform = from_origin(extent[0], extent[3], meta["transform"][0], meta["transform"][4])
        g_transform = TransformationOperations.get_affine_matrix(extent, (tile_size,tile_size))
        raster = RioRaster.raster_from_array(data,crs=meta['crs'], g_transform=g_transform,nodata_value=meta['nodata'])
        return raster

    def save_tile_as_geotiff(self, tile_x, tile_y, tile_z, output_filename):
        if self.tile_exists(tile_x, tile_y, tile_z):
            metadata = self.info()
            # tile_bounds = list(mercantile.bounds(tile_x, tile_y, tile_z))
            tile_bounds = list(mercantile.xy_bounds(mercantile.Tile(tile_x, tile_y, tile_z)))
            tile_data, tile_mask = self.tile(tile_x, tile_y, tile_z)
            tile_data = np.squeeze(tile_data)
            # TransformationOperations.get_affine_matrix(tile_bounds,tile_data.shape)
            with rasterio.open(
                    output_filename,
                    'w',
                    driver='GTiff',
                    height=tile_data.shape[0],
                    width=tile_data.shape[1],
                    count=1,  # Adjust if you have multiple bands
                    dtype=str(tile_data.dtype),
                    crs=pyproj.CRS.from_string("EPSG:3857"),
                    transform=rasterio.transform.from_bounds(*tile_bounds, tile_data.shape[1], tile_data.shape[0]),
            ) as dst:

                dst.write(tile_data, 1)  # Assuming single-band data
