import json
import os
import traceback
import geopandas as gpd
from typing import List, Optional

import ee
import numpy as np
from PIL import Image
from ee.batch import Export
from shapely.geometry import shape

from digitalarztools.io.file_io import FileIO
from digitalarztools.io.raster.rio_process import RioProcess
from digitalarztools.io.url_io import UrlIO
from digitalarztools.pipelines.gee.core.region import GEERegion
from tqdm import tqdm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from io import BytesIO


class GEEImage:
    image: ee.Image

    def __init__(self, img: ee.Image):
        self.image = img
        # self.bands = self.get_image_bands()
        self.bands = None

    @classmethod
    def get_image_by_tag(cls, tag: str) -> 'GEEImage':
        img = ee.Image(tag)
        return cls(img)

    def get_gee_image(self) -> ee.Image:
        return self.image

    def get_gee_id(self):
        return self.image.get('system:index').getInfo()

    def get_band(self, band_name, in_place=False) -> 'GEEImage':
        # nir = self.image.select('B5')
        if in_place:
            self.image = self.image.select(band_name)
        else:
            return GEEImage(self.image.select(band_name))

    def get_band_names(self):
        band_names = self.image.bandNames()
        # print('Band names:', band_names.getInfo())
        return band_names.getInfo()

    def get_min_max_scale(self, band_names: list = None) -> tuple:
        band_names = self.get_image_bands(self.image) if band_names is None else band_names
        min_scale, max_scale = -1, -1
        for band_name in band_names:
            scale = self.get_band_scale(band_name)[1]
            if min_scale == -1 or min_scale > scale:
                min_scale = scale
            if max_scale == -1 or max_scale < scale:
                max_scale = scale

        return min_scale, max_scale

    def get_band_scale(self, band_name: str):
        band_projection = self.image.select(band_name).projection()
        band_scale = band_projection.nominalScale()
        return (band_name, band_scale.getInfo())

    def get_band_projection(self, band_name: str):
        band_projection = self.image.select(band_name).projection()
        # band_scale = band_projection.nominalScale()
        # return (band_name, band_scale.getInfo())
        return band_projection.getInfo()

    def get_image_bands_info(self):
        # band_names = self.image.bandNames()
        # band_info = band_names.getInfo()
        band_info = self.get_image_bands(self.image)
        # print('Band names:', band_info)
        return band_info

    def get_image_metadata(self) -> dict:
        # print(self.image.getInfo())
        properties = self.image.propertyNames()
        print('Metadata properties:',
              properties.getInfo())  # ee.List of metadata properties
        return self.image.getInfo()

    def get_projection(self, is_info=True):
        # Get projection information from band 1.
        band_name = self.image.bandNames().getInfo()[0]
        # for b_name in band_names:
        #     b1_proj = self.image.select(b_name).projection()
        #     print('{} projection:'.format(b_name), b1_proj.getInfo())  # ee.Projection object

        projection = self.image.select(band_name).projection()
        return projection.getInfo() if is_info else projection

    def get_geo_transform(self, is_info=True):
        projection = self.get_projection(False)
        transform = projection.transform
        return transform.getInfo() if is_info else transform

    def get_crs(self, is_info=True):
        projection = self.get_projection(False)
        crs = projection.crs
        return crs.getInfo() if is_info else crs

    import ee

    def get_region(self):
        """Extracts the region of an ee.Image, raising an Exception if not set.

        Returns:
            The extracted ee.Geometry region.

        Raises:
            ValueError: If the image does not have a defined region.
        """
        # Get the geometry (region) of the image
        geometry = self.image.geometry()

        # Check if the geometry is empty
        if geometry is None:  # or geometry.type().getInfo() == 'GeometryCollection':
            raise Exception("Region is not set for this image")

        # If the image has a geometry then return it
        return geometry

    def get_datatype(self):
        band_name = self.get_band_names()
        # Fetch information about this band
        if len(band_name) == 0:
            band_info = self.image.select(band_name[0]).getInfo()
            return band_info['data_type']

    def get_scale(self, b_name=None):
        # Get scale (in meters) information from band 1.
        if b_name is None:
            band_names = self.image.bandNames().getInfo()
            res = {}
            for b_name in band_names:
                b1_scale = self.image.select(b_name).projection().nominalScale()
                # print('{} scale:'.format(b_name), b1_scale.getInfo())  # ee.Number
                res[b_name] = b1_scale.getInfo()
            return res
        else:
            b1_scale = self.image.select(b_name).projection().nominalScale()
            return b1_scale.getInfo()

    def get_cloude_cover(self):
        # Get a specific metadata property.
        cloudiness = self.image.get('CLOUD_COVER')
        print('CLOUD_COVER:', cloudiness.getInfo())  # ee.Number

    def get_pixel_value(self, lon, lat):
        p = ee.Geometry.Point([lon, lat], 'EPSG:4326')
        band_names = self.image.bandNames().getInfo()
        pixel_info = []
        for b_name in band_names:
            data = self.image.select(b_name).reduceRegion(ee.Reducer.first(), p, 10).get(b_name)
            info = {"band": b_name, "value": ee.Number(data)}
            pixel_info.append(info)

    def get_map_id_dict(self, vis_params):
        map_id_dict = self.image.getMapId(vis_params)
        # print(map_id_dict)
        # print(map_id_dict['tile_fetcher'].url_format)
        return map_id_dict

    def get_map_id(self, vis_params):
        map_id_dict = self.image.getMapId(vis_params)
        res = {
            'mapid': map_id_dict['mapid'],
            'token': map_id_dict['token'],
            'url_format': map_id_dict['tile_fetcher'].url_format,
            'image': map_id_dict['image'].getInfo()
        }
        return res

    def get_url_template(self, vis_params):
        map_id_dict = self.image.getMapId(vis_params)
        return map_id_dict['tile_fetcher'].url_format

    def get_download_url(self, img_name, aoi: ee.Geometry.Polygon, scale=None):
        if not self.bands:
            self.bands = self.get_image_bands(self.image)
        url = self.image.getDownloadURL({
            'image': self.image.serialize(),
            'region': aoi,
            'bands': self.bands,
            'name': img_name,
            'scale': scale,
            'format': 'GEO_TIFF'
        })
        # print(url)
        return url

    def download_bands(self, fp, region):
        meta_data = self.get_image_metadata()
        bands = meta_data['bands']
        # self.bands = self.get_image_bands()
        for index, band in enumerate(bands):
            id = band["id"]

    def download_image(self, file_path, img_region: GEERegion, scale=-1,
                       bit_depth=32, no_of_bands=None, delete_folder=True, within_aoi_only=True):
        if scale == -1:
            scale = self.get_scale()
            scale = min(scale.values())

        if no_of_bands is None:
            self.bands = self.get_image_bands(self.image)
            no_of_bands = len(self.bands)
        print("saving meta data...")
        meta_data = self.get_image_metadata()
        meta_data_fp = f"{file_path[:-4]}_meta_data.json"
        dirname = FileIO.mkdirs(meta_data_fp)
        with open(meta_data_fp, "w") as f:
            # Serialize the dictionary to a JSON string and write it to the file
            json.dump(meta_data, f)
        print("downloading images...")
        dir_name = os.path.dirname(file_path)
        img_name, img_ext = FileIO.get_file_name_ext(os.path.basename(file_path))
        download_dir_name = os.path.join(dir_name, img_name)
        dirname = FileIO.mkdirs(download_dir_name)

        required_tiles = []

        for region, index in img_region.get_tiles(no_of_bands, scale, bit_depth=bit_depth,
                                                  within_aoi_only=within_aoi_only):
            required_tiles.append((region, index))
            # print(region, index)
        # df = pd.DataFrame(required_tiles)
        # Create a tqdm progress bar for the loop
        progress_bar = tqdm(desc="Processing Tiles", unit="tile", total=len(required_tiles))
        for i, (region, index) in enumerate(required_tiles):
            temp_file_path = os.path.join(download_dir_name, f"r{index[0]}c{index[1]}.tif")
            if not os.path.exists(temp_file_path):
                aoi = region.get_aoi()
                url = self.get_download_url(img_name, aoi=aoi, scale=scale)

                res = UrlIO.download_url(url, temp_file_path)
            # Simulate some processing time
            # time.sleep(0.1)

            # Update the tqdm progress bar
            progress_bar.update(1)
        # Close the tqdm progress bar
        progress_bar.close()
        res = False
        try:
            raster = RioProcess.mosaic_images(download_dir_name)

            raster.save_to_file(file_path)
            if delete_folder:
                FileIO.delete_folder(download_dir_name)
            print('Image downloaded as ', file_path)

            res = True
        except:
            traceback.print_exc()
            res = False
        return res

    def to_geojson(self, scale=None, gee_region: GEERegion = None):
        if scale is None:
            scale = self.get_scale()
        region = gee_region.aoi if gee_region is not None else self.get_region()
        # Reduce the masked image to vectors (polygons).
        first_band_int = self.image.select(0).toInt()
        # Create a new image by combining the cast band with the rest of the image bands.
        image_int = first_band_int.addBands(
            self.image.select(ee.List.sequence(1, self.image.bandNames().size().subtract(1))))

        vector_polygons = image_int.reduceToVectors(
            geometryType='polygon',
            reducer=ee.Reducer.countEvery(),
            geometry=region,
            scale=scale,  # Adjust scale as needed.
            maxPixels=1e13
        )

        # Get the vector polygons as a GeoJSON dictionary.
        return vector_polygons.getInfo()

    def to_gdf(self, scale=None, gee_region: GEERegion = None):
        vector_polygons_geojson = self.to_geojson(scale, gee_region)
        # Create a list to hold the feature geometries and properties.
        features = []

        for feature in vector_polygons_geojson['features']:
            geom = shape(feature['geometry'])
            properties = feature['properties']
            features.append({'geometry': geom, **properties})

        # Create a GeoDataFrame from the features.
        gdf = gpd.GeoDataFrame(features)
        return gdf

    def to_numpy(self, aoi: ee.Geometry.Polygon = None, band_names: List[str] = [], is_r_c_b=True):
        """
        @param aoi:  ee.Geometry.Polygon
        @param band_names: list of band names
        @param is_r_c_b: row x col x band or band x row xcol
        @return:
        """
        image = self.image
        if aoi is None:
            aoi = self.get_region()
        if image.args:
            band_arrs = image.sampleRectangle(region=aoi)
            # Get band names
            if len(band_names) == 0:
                band_names = self.get_band_names()

            bands = []

            # Iterate over each band
            for i, name in enumerate(band_names):
                # name = band_names.get(i).getInfo()
                print('Band name: ', name)

                # Get the band data
                band_arr = band_arrs.get(name)
                np_arr = np.array(band_arr.getInfo())
                print("np_arr", np_arr.shape)

                # Expand the dimensions of the images so they can be concatenated into 3-D.
                np_arr_expanded = np.expand_dims(np_arr, 2)
                print("np_arr_expanded", np_arr_expanded.shape)

                # Append the expanded array to the list
                bands.append(np_arr_expanded)
            if is_r_c_b:
                # Concatenate all the bands along the third dimension
                np_image = np.concatenate(bands, axis=2)
            else:
                # Stack all the bands along the first dimension to get (bands, rows, cols)
                np_image = np.stack(bands, axis=0)
            if len(band_names) == 1:
                # Remove the singleton dimension to get (rows, cols)
                np_image = np.squeeze(np_image, axis=2)
            return np_image

    def export_output(self, name: str, bucket_name: str, region: ee.Geometry.Polygon, description: str = ''):
        # res = Export.image.toDrive(**{
        #     "image": self.output_image,
        #     "description": 'test',
        #     "folder": 'gee_python',
        #     "fileNamePrefix": name,
        #     "scale": 30,
        #     # "maxPixels": 1e13,
        #     "region": self.aoi.bounds().getInfo()['coordinates']
        # })
        # self.gee_image_2_numpy(self.output_image)
        res = Export.image.toCloudStorage(
            image=self.image,
            description=description,
            bucket=bucket_name,
            fileNamePrefix=name,
            scale=30,
            region=region
        )
        res.start()
        while res.status()['state'] not in ['FAILED', 'COMPLETED']:
            print(res.status())
        res_status = res.status()
        if res_status['state'] == 'FAILED':
            print("error:", res_status['error_message'])
        return res_status

    def get_histogram_data(self, band_name, aoi_sub: ee.Geometry.Polygon):
        data = self.image.select(band_name).reduceRegion(
            ee.Reducer.fixedHistogram(0, 0.5, 500), aoi_sub).get(band_name).getInfo()
        return data

    @staticmethod
    def get_histogram(img, region: GEERegion, scale: int, is_info_needed=True):
        histogram = img.reduceRegion(
            reducer=ee.Reducer.histogram(255),  # Adjust bin count as needed
            geometry=region,
            scale=scale,  # Adjust scale to match your imagery resolution
            bestEffort=True
        )
        values, frequencies = None, None
        if is_info_needed:
            histogram_info = histogram.getInfo()
            values = histogram_info['nd']['bucketMeans']
            frequencies = histogram_info['nd']['histogram']

        return histogram, values, frequencies

    def get_statistic(self, band_name, aoi_sub: ee.Geometry.Polygon):
        mean = self.image.select(band_name).reduceRegion(
            ee.Reducer.mean(), aoi_sub).get(band_name).getInfo()
        variance = self.image.select(band_name).reduceRegion(
            ee.Reducer.variance(), aoi_sub).get(band_name).getInfo()

        return mean, variance

    @staticmethod
    def generate_legend_as_bytes(label: str, palette: List[str], min_val: Optional[float] = None,
                                 max_val: Optional[float] = None) -> bytes:
        """
        Generate a color legend as bytes.
        """
        fig = Figure(figsize=(6, 1))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.5)

        # Ensure palette colors are in the correct format
        palette = ["#" + val if val[0] != "#" else val for val in palette]

        """
                Generate a color legend as bytes.
                """
        if min_val is not None and max_val is not None:
            # Create gradient color legend with Matplotlib
            fig = Figure(figsize=(6, 1))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            fig.subplots_adjust(bottom=0.5)

            # Ensure palette colors are in the correct format
            palette = ["#" + val if val[0] != "#" else val for val in palette]

            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", palette)
            norm = matplotlib.colors.Normalize(vmin=min_val, vmax=max_val)
            cbar = matplotlib.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')

            buf = BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
            buf.seek(0)  # Rewind the buffer to the beginning
        else:
            # Create solid color legend with PIL
            width, height = 600, 100  # Define the size of the image
            image = Image.new("RGB", (width, height), palette[0])

            buf = BytesIO()
            image.save(buf, format='PNG')
            buf.seek(0)  # Rewind the buffer to the beginning

        return buf

    @staticmethod
    def convert_timestamp_to_datetime(timestamp) -> str:
        max_date = ee.Date(timestamp)

        # Format the date as a string (server-side)
        formatted_date = max_date.format('YYYY-MM-dd')
        return formatted_date.getInfo()

    @staticmethod
    def get_image_date(img):
        """
        return system time stamp
        """
        return img.get('system:time_start')

    def get_band_count(self):
        band_names = self.image.bandNames()

        return band_names.size().getInfo()

    @staticmethod
    def get_image_bands(img):
        try:
            return img.bandNames().getInfo()
        except ee.EEException as e:
            print(f"An error occurred while getting band names: {e}")
            return []

    @classmethod
    def get_imgae_url(cls, img, vis_params):
        bands = cls.get_image_bands(img)
        if len(bands) > 0:
            url = img.getMapId(vis_params)
            return url['tile_fetcher'].url_format

    def convert_to_binary_image(self, value, is_gt=True):
        # Create a binary mask where values greater than 1 are set to 1
        img_mask = self.image.gt(value) if is_gt else self.image.lt(value)

        # Apply the mask to the image
        binary_img = self.image.updateMask(img_mask)

        # Convert the masked image to binary (0s and 1s)
        return binary_img.selfMask().unmask(0)
