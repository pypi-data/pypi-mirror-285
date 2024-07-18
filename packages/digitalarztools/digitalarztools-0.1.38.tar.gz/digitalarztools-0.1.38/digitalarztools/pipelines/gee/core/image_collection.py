from datetime import datetime, date, timedelta
from typing import Union, List

import ee
import pandas as pd

from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.region import GEERegion


class GEEImageCollection:
    # image_type: str = None
    img_collection: ee.ImageCollection = None

    # region: GEERegion = None
    # date_rage: tuple = None

    def __init__(self, img_col: ee.ImageCollection):
        self.img_collection = img_col

    @staticmethod
    def get_image_count(img_col) -> int:
        return img_col.size().getInfo()

    @staticmethod
    def get_latest_image_in_collection(image_collection: ee.ImageCollection) -> ee.Image:
        return image_collection.sort('system:time_start', False).first()

    @staticmethod
    def get_oldest_image_in_collection(image_collection: ee.ImageCollection) -> ee.Image:
        return image_collection.sort('system:time_start').first()

    @staticmethod
    def get_image_at_index(img_col: ee.ImageCollection, index: int) -> ee.Image:
        """
            img_col.get(0) returns the first image.
            img_col.get(1) returns the second image.
            img_col.get(4) returns the fifth image.
        @param img_col:
        @param index:
        @return:
        """
        # Sort the collection in descending order
        sorted_img_col = img_col.sort('system:time_start', False)

        # Get the image at the specified index directly from a list
        img = ee.Image(sorted_img_col.toList(index + 1).get(index))  # Get list up to index+1 and then image at index

        return img

    @staticmethod
    def convert_timestamp_to_datetime(timestamp) -> str:
        return GEEImage.convert_timestamp_to_datetime(timestamp)

    @staticmethod
    def get_collection_max_date(img_col: ee.ImageCollection):
        max_timestamp = img_col.aggregate_max('system:time_start')
        # max_timestamp = img_col.first().get('system:time_start')
        # Convert the timestamp to an ee.Date object (server-side)
        max_date = ee.Date(max_timestamp)

        # Format the date as a string (server-side)
        formatted_date = max_date.format('YYYY-MM-dd')
        return formatted_date.getInfo()

    @staticmethod
    def get_collection_min_date(img_col: ee.ImageCollection):
        min_timestamp = img_col.aggregate_min('system:time_start').getInfo()
        # Convert the timestamp to an ee.Date object (server-side)
        min_date = ee.Date(min_timestamp)

        # Format the date as a string (server-side)
        formatted_date = min_date.format('YYYY-MM-dd')
        return formatted_date.getInfo()

    @staticmethod
    def get_date_range(no_of_days=10, end_date=None):
        if end_date is None:
            end_date = date.today()
        # first = today.replace(day=1)
        start_date = end_date - timedelta(days=no_of_days)
        date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        return date_range

    @staticmethod
    def get_uniques_dates_in_collection(img_col: ee.ImageCollection):
        # Map over the collection to extract the date of each image
        dates = img_col.map(lambda image: ee.Image(image).set('date', image.date().format('YYYY-MM-dd')))
        # Select only the date property and reduce to unique dates
        unique_dates = dates.distinct('date').aggregate_array('date');
        return unique_dates

    @staticmethod
    def get_latest_image_collection(img_collection: ee.ImageCollection, limit: int = -1):
        img_collection = img_collection.sort('system:time_start', False)
        if limit > 0:
            img_collection = img_collection.limit(limit)
        return img_collection

    @classmethod
    def from_tags(cls, image_type: str, date_range: tuple = None, region: Union[GEERegion, dict] = None):
        """
        Parameters
        ----------
        :param image_type:  dataset name or type like 'COPERNICUS/S2_SR' for other check gee documentation
        :param date_range: tuple
            range of date with start and end value like
            ('2021-01-01', '2021-12-31')
            or can be calculated through  time delta
            today = datetime.date.today()
             start_date = today - datetime.timedelta(days=365)
            self.date_range = (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        example:
              s2_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
             .filterDate(start_date, end_date) \
             .filterBounds(fc) \
             .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)
        """

        # self.image_type = image_type
        img_collection = ee.ImageCollection(image_type)
        if region is not None:
            region = GEERegion.from_geojson(region) if isinstance(region, dict) else region
            img_collection = img_collection.filterBounds(region.bounds)

        if date_range is not None:
            img_collection = img_collection.filterDate(date_range[0], date_range[1])
        return cls(img_collection)

    def set_region(self, region: Union[GEERegion, dict]):
        region = GEERegion.from_geojson(region) if isinstance(region, dict) else region
        self.img_collection = self.img_collection.filterBounds(region.bounds)

    def set_region_from_poi(self, poi: ee.Geometry.Point, buffer: float):
        self.img_collection = self.img_collection.getRegion(poi, buffer)
        # self.region = GEERegion(region)

    def get_dates(self):
        dates = self.img_collection.aggregate_array('system:time_start')
        dates_milliseconds = dates.getInfo()
        dates = [datetime.utcfromtimestamp(date / 1000) for date in dates_milliseconds]
        return dates

    def set_date_range(self, date_range=None, no_of_days=10):
        """
        :param date_range: range of date with start and end value like ('2021-01-01', '2021-12-31')
        :param no_of_days: or no_of_days starting from today
        :return:
        """
        if date_range is None:
            date_range = self.get_date_range(no_of_days)
        # self.date_range = date_range
        self.img_collection = self.img_collection.filterDate(date_range[0], date_range[1])

    def select_dataset(self, ds_name: str):
        """
        :param ds_name: dataset name like 'precipitation' in  'UCSB-CHG/CHIRPS/DAILY'
        :return:
        """
        self.img_collection = self.img_collection.select(ds_name)

    def select_bands(self, bands: Union[List, str]) -> 'GEEImageCollection':
        """
        example
            bands = ['B2', 'B3', 'B4', 'B7', 'B8', 'B8A', 'B11', 'B12']
            indices = ['NDVI', 'NDWI', 'NDBI', 'EVI']  additional bands added
            features = ee.List(bands + indices)
        :param bands:
        :return:
        """
        if isinstance(bands,List):
            features = ee.List(bands)
        else:
            features = bands
        new_img_collection = self.img_collection.select(features)
        return GEEImageCollection(new_img_collection)

    def add_bands(self, types: list):
        """
        use to add bands in the image collection
        :param types: list having value "mask_cloud", "NDVI", "NDWI", "NBI", "EVI"
        :return:
        """
        from digitalarztools.pipelines.gee.analysis.indices import GEEIndices
        for t in types:
            t = t.lower()
            if t == "mask_cloud":
                self.img_collection = self.img_collection.map(self.mask_s2_clouds)
            elif t == "ndvi":
                self.img_collection = self.img_collection.map(GEEIndices.add_ndvi)
            elif t == "ndwi":
                self.img_collection = self.img_collection.map(GEEIndices.add_ndwi)
            elif t == "ndbi":
                self.img_collection = self.img_collection.map(GEEIndices.add_ndbi)
            elif t == "evi":
                self.img_collection = self.img_collection.map(GEEIndices.add_evi)

    @staticmethod
    def mask_s2_clouds(image):
        qa = image.select('QA60')
        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloud_bit_mask = int(2 ** 10)
        cirrus_bit_mask = int(2 ** 11)
        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloud_bit_mask).eq(0). \
            And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))

        return image.updateMask(mask).divide(10000) \
            .select("B.*") \
            .copyProperties(image, ["system:time_start"])

    def get_collection_size(self):
        size = self.img_collection.size().getInfo()
        return size

    def get_collection_list(self):
        return self.img_collection.toList(self.img_collection.size()).getInfo()

    def get_ymd_list(self):
        def iter_func(image, newList):
            date = ee.String(image.date().format("YYYY-MM-dd"))
            newlist = ee.List(newList)
            return ee.List(newlist.add(date).sort())

        return self.get_image_collection().iterate(iter_func, ee.List([])).getInfo()

    def get_image_collection(self):
        return self.img_collection

    def enumerate_collection(self) -> (int, GEEImage):
        size = self.img_collection.size().getInfo()
        img_list = ee.List(self.img_collection.toList(self.img_collection.size()))
        for i in range(size):
            yield i, GEEImage(ee.Image(img_list.get(i)))

    def get_image(self, how=None, name='') -> ee.Image:
        """
        :param how: choices are 'median', 'max', 'mean', 'first', 'cloud_cover', 'sum' ,'latest'
        :return:
        """
        # if collection.size().getInfo() > 0:
        # image: ee.Image = None
        if how == 'median':
            image = self.img_collection.median().rename(f'median_{name}')
        elif how == "min":
            image = self.img_collection.min()#.rename(f'min_{name}')
        elif how == "std":
            image = self.img_collection.reduce(ee.Reducer.stdDev())#.rename(f'std_{name}')
        elif how == 'max':
            image = self.img_collection.max()#.rename(f'max_{name}')
        elif how == 'mean':
            image = self.img_collection.mean()#.rename(f'mean_{name}')
        elif how == 'sum':
            image = self.img_collection.sum()#.rename(f'total_{name}')
        elif how == 'cloud_cover':
            image = self.img_collection.sort('CLOUD_COVER').first()#.rename(f'least_cloud_{name}')
        elif how == "oldest":
            image = self.img_collection.sort('DATE_ADDED', True).first()#.rename(f'oldest_{name}')
        else:
            # self.img_collection.sort()
            image = self.img_collection.sort('DATE_ADDED', False).first()#.rename(f'latest_{name}')
        # ee.Date(image.get('system:time_start')).format('YYYY-MM-dd HH:mm:ss').getInfo()
        # ee.Date(image.get('system:time_end')).format('YYYY-MM-dd HH:mm:ss').getInfo()
        return image

    # def temporal_collection(self, temporal1: int, temporal2: int, temporal_type: str = 'day'):
    #     """
    #     Sentinel 2 Refined Image List (after 14-15 days)
    #     :param temporal1: no of days like 14
    #     :param temporal2: no of days like 15 (more than previous one
    #     :param temporal_type: default is day (check gee documentation for other type)
    #     """
    #     self.img_collection = GEEImageCollection.temporal_collection(self.img_collection, self.date_range[0], temporal1,
    #                                                                  temporal2, temporal_type)

    @staticmethod
    def temporal_collection(collection, start, count, interval, units):
        sequence = ee.List.sequence(0, ee.Number(count).subtract(1))
        originalStartDate = ee.Date(start)

        def filter_by_date(i):
            startDate = originalStartDate.advance(ee.Number(interval).multiply(i), units)
            endDate = originalStartDate.advance(ee.Number(interval).multiply(ee.Number(i).add(1)), units)
            resultImage = collection.filterDate(startDate, endDate).median() \
                .set('system:time_start', startDate.millis()) \
                .set('system:time_end', endDate.millis())

            return resultImage

        return ee.ImageCollection(sequence.map(filter_by_date))

    def get_image_info_within_poi(self, poi: ee.Geometry.Point, buffer):
        info = self.img_collection.getRegion(poi, buffer).getInfo()
        # pprint.pprint(local_pr[:5])
        return info

    def get_image_info_within_region(self, region: GEERegion):
        info = self.img_collection.getRegion(region.get_aoi()).getInfo()
        return info

    # def get_bands_name(self):
    #     # Select the first image from the collection
    #     first_image = self.img_collection.first()
    #
    #     # Get the list of band names from the first image
    #     band_names = first_image.bandNames()
    #
    #     # Use getInfo() to retrieve the band names as a Python list
    #     return band_names.getInfo()

    def info_ee_array_to_df(self, region: GEERegion, list_of_bands: list = None) -> pd.DataFrame:
        """
        Transforms client-side ee.Image.getRegion array to pandas.DataFrame.
        :param arr:
        :param list_of_bands:
        :return:
        """
        # img = self.get_image(how='median')
        # gee_image = GEEImage(img)
        try:
            gee_image = GEEImage(self.img_collection.first())

            list_of_bands = gee_image.get_band_names() if list_of_bands is None else list_of_bands
            if len(list_of_bands) != 0:
                min_scale, max_scale = gee_image.get_min_max_scale(list_of_bands)
                # print(min_scale, max_scale)

                arr = self.img_collection.getRegion(geometry=region.aoi, scale=min_scale).getInfo()

                df = pd.DataFrame(arr)

                # Rearrange the header.
                headers = df.iloc[0]
                df = pd.DataFrame(df.values[1:], columns=headers)

                # Convert the data to numeric values.
                for band in list_of_bands:
                    df[band] = pd.to_numeric(df[band], errors="coerce")

                # Convert the time field into a datetime.
                df["datetime"] = pd.to_datetime(df["time"], unit="ms")

                # Keep the columns of interest.
                # df = df[["time", "datetime", *list_of_bands]]

                # The datetime column is defined as index.
                # df = df.set_index("datetime")

                return df
            else:
                return pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    def sum_resampler(coll: ee.ImageCollection, freq, unit, scale_factor, band_name):
        """
        This function aims to resample the time scale of an ee.ImageCollection.
        The function returns an ee.ImageCollection with the averaged sum of the
        band on the selected frequency.

        coll: (ee.ImageCollection) only one band can be handled
        freq: (int) corresponds to the resampling frequence
        unit: (str) corresponds to the resampling time unit.
                    must be 'day', 'month' or 'year'
        scale_factor (float): scaling factor used to get our value in the good unit
        band_name (str) name of the output band
        example:
        # Apply the resampling function to the precipitation dataset.
            pr_m = sum_resampler(pr, 1, "month", 1, "pr")
        # Apply the resampling function to the PET dataset.
            pet_m = sum_resampler(pet.select("PET"), 1, "month", 0.0125, "pet")
        # Combine precipitation and evapotranspiration.
            meteo = pr_m.combine(pet_m)

        """
        # Define initial and final dates of the collection.
        firstdate = ee.Date(
            coll.sort("system:time_start", True).first().get("system:time_start")
        )

        lastdate = ee.Date(
            coll.sort("system:time_start", False).first().get("system:time_start")
        )

        # Calculate the time difference between both dates.
        # https://developers.google.com/earth-engine/apidocs/ee-date-difference
        diff_dates = lastdate.difference(firstdate, unit)

        # Define a new time index (for output).
        new_index = ee.List.sequence(0, ee.Number(diff_dates), freq)

        # Define the function that will be applied to our new time index.
        def apply_resampling(date_index):
            # Define the starting date to take into account.
            startdate = firstdate.advance(ee.Number(date_index), unit)

            # Define the ending date to take into account according
            # to the desired frequency.
            enddate = firstdate.advance(ee.Number(date_index).add(freq), unit)

            # Calculate the number of days between starting and ending days.
            diff_days = enddate.difference(startdate, "day")

            # Calculate the composite image.
            image = (
                coll.filterDate(startdate, enddate)
                .mean()
                .multiply(diff_days)
                .multiply(scale_factor)
                .rename(band_name)
            )

            # Return the final image with the appropriate time index.
            return image.set("system:time_start", startdate.millis())

        # Map the function to the new time index.
        res = new_index.map(apply_resampling)

        # Transform the result into an ee.ImageCollection.
        res = ee.ImageCollection(res)

        return res

    def get_latest_image_date(self):
        # Sort the collection by the acquisition date in descending order
        sorted_collection = self.img_collection.sort('system:time_start', False)

        # Get the latest image
        latest_image = sorted_collection.first()
        # Get the acquisition date of the latest image
        latest_date = ee.Date(latest_image.get('system:time_start')).getInfo()
        formatted_date = datetime.utcfromtimestamp(latest_date['value'] / 1000)

        print('Latest acquisition date:', formatted_date.strftime('%Y-%m-%d'))
        return formatted_date

