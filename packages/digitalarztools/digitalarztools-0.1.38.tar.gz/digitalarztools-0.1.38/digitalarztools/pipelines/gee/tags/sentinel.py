import enum
from datetime import datetime

import ee

from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.pipelines.gee.tags.water import GEEWater
from digitalarztools.proccessing.operations.thresholds import calculate_otsu_threshold

class SentinelTag(enum.Enum):
    SENTINEL1 = 'COPERNICUS/S1_GRD'
    SENTINEL2_SURFACE_REFLECTANCE = "COPERNICUS/S2_SR_HARMONIZED"
    SENTINEL2_TOA = 'COPERNICUS/S2_HARMONIZED'
    SENTINEL3 = "COPERNICUS/S3/OLCI"
    SENTINEL5_CH4 = "COPERNICUS/S5P/OFFL/L3_CH4"

class GEESentinelData:

    @staticmethod
    def sentinel1_water_mask(region: GEERegion, date_range: tuple, water_masked_s2=None):
        """
        @param region:
        @param date_range: range of date with start and end value like ('2021-01-01', '2021-12-31')
        @param s1_water_threshold: should be less than -15
        @return:
        """
        # Load Sentinel-1 SAR data
        polarization = 'VV'
        sentinel1_coll = ee.ImageCollection('COPERNICUS/S1_GRD') \
            .filterBounds(region.bounds) \
            .filterDate(date_range[0], date_range[1]) \
            .filter(ee.Filter.eq('instrumentMode', 'IW')) \
            .filter(ee.Filter.eq('resolution_meters', 10)) \
            .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING')) \
            .select(polarization)
        # Compute the median of the image collection
        median = sentinel1_coll.median()

        # setting threshold value
        # if water_masked_s2 is not None:
        #     masked_s1 = median.updateMask(water_masked_s2)
        #     stats = masked_s1.reduceRegion(
        #         # reducer=ee.Reducer.mean(),  # Use mean reducer to get the average value
        #         reducer=ee.Reducer.percentile([15]),
        #         geometry=region.bounds,
        #         scale=100,
        #         maxPixels=1e13,
        #         # bestEffort=True
        #     )
        #
        #     # Calculate the threshold as the average value
        #     s1_water_threshold = stats.get(polarization).getInfo()
        #     # s1_water_threshold = quantilies
        # else:
        s1_water_threshold = -18  # Adjust threshold for Pakistan conditions
        print("threshold", s1_water_threshold)
        # Apply a threshold to identify water bodiesk
        water = median.lt(s1_water_threshold)
        # Mask the water layer to only include the AOI
        water_masked = water.updateMask(water).clip(region.aoi)

        return water_masked

    @staticmethod
    def sentinel2_water_mask(region: GEERegion, date_range: tuple, water_threshold=0.3):
        """
           @param region:
           @param date_range: range of date with start and end value like ('2021-01-01', '2021-12-31')
           @param water_threshold: should be less than 0.5 as indices is between 0 - 1
           @return:
         """
        # Load and process Sentinel-2 optical data
        sentinel2 = ee.ImageCollection('COPERNICUS/S2') \
            .filterBounds(region.bounds) \
            .filterDate(date_range[0], date_range[1]) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
            .select(['B3', 'B11'])  # Green and SWIR bands for MNDWI
        # .select(['B3', 'B8'])  # Green and NIR bands for NDWI

        # Compute the median of the Sentinel-2 image collection
        median_s2 = sentinel2.median()

        # Calculate NDWI (Normalized Difference Water Index)
        # ndwi = median_s2.normalizedDifference(['B3', 'B8'])
        # Calculate MNDWI (Modified Normalized Difference Water Index)
        mndwi = median_s2.normalizedDifference(['B3', 'B11'])

        # histogram, values, frequencies = GEEImage.get_histogram(mndwi, region.bounds, 10)

        # Calculate Otsu threshold
        # water_threshold_s2 = calculate_otsu_threshold(values, frequencies)
        # print("otsu threshold", otsu_threshold)

        # Apply a threshold to identify water bodies in Sentinel-2
        water_threshold_s2 = 0.01  # Adjust threshold for local conditions
        # water_s2 = ndwi.gt(water_threshold_s2)
        water_mask = mndwi.gt(water_threshold_s2)

        # Mask the water layer to only include the AOI
        water_masked_s2 = mndwi.updateMask(water_mask).clip(region.aoi)

        return water_masked_s2

    @staticmethod
    def get_water_mask_vis_params():
        return {'palette': ['#0000cc']}

    @staticmethod
    def get_water_level_vis_params():
        # ['sky blue', 'dark blue', 'mahroon']
        return {'min': -1, 'max': 1, 'palette': ['#87CEEB', '#0000cc', '#800000']}

    @classmethod
    def combined_water_mask(cls, region: GEERegion, date_range: tuple = None):
        """
        @param region:
        @param date_range: range of date with start and end value like ('2021-01-01', '2021-12-31')
        @return:
        """
        water_masked_s2 = cls.sentinel2_water_mask(region, date_range)
        water_masked_s1 = cls.sentinel1_water_mask(region, date_range, water_masked_s2)

        # Combine water masks from Sentinel-1 and Sentinel-2
        combined_water = water_masked_s1.unmask(0).Or(water_masked_s2.unmask(0))
        return combined_water.updateMask(combined_water)

    @classmethod
    def get_water_mask_url(cls, region: GEERegion, date_range: tuple = None):
        """
        @param region:
        @param date_range: range of date with start and end value like ('2021-01-01', '2021-12-31')
        @return:
        """
        if date_range is None:
            date_range = GEEImageCollection.get_date_range(20)

        # water_masked = cls.sentinel2_water_mask(region, date_range)
        water_masked = cls.combined_water_mask(region, date_range)
        vis_params = cls.get_water_mask_vis_params()
        url = water_masked.getMapId(vis_params)
        return url['tile_fetcher'].url_format

    @staticmethod
    def get_water_level_using_change_detection_sentinel_1(region: GEERegion, water_mask: ee.Image,
                                                          before_date_range: tuple,
                                                          after_date_range: tuple) -> ee.Image:
        """"
        @param region:
        @param water_mask: ee.Image
        @param before_date_range: range of date with start and end
        @param after_date_range: range of date with start and end
             (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        """
        # if date_range is None:
        #     date_range = GEEImageCollection.get_date_range(no_of_days=90)
        # Load Sentinel-1 SAR data
        polarization = 'VV'
        sentinel1_collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
                                .filterBounds(region.bounds)
                                # .filterDate(date_range[0], date_range[1])
                                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', polarization))
                                .filter(ee.Filter.eq('instrumentMode', 'IW'))
                                # .sort('system:time_start', False)  # Sort descending to get latest first
                                .select(polarization))
        after_collection = sentinel1_collection.filterDate(after_date_range[0], after_date_range[1])
        before_collection = sentinel1_collection.filterDate(before_date_range[0], before_date_range[1])

        # Calculate the median image for each time period
        before_img = before_collection.sum()
        after_img = after_collection.sum()

        # Calibration Factor (needs to be determined through empirical analysis)
        # multiply this factor will convert db of back scattering into meter
        # For indus basin  save assumption is
        # 0.03 to -0.10 meters per dB: This range suggests that for every 1 dB increase in backscatter,
        # you might expect a decrease in water level between 3 and 10 centimeters.
        calibration_factor = 0.03  # replace with your calibrated value)

        # Load a DEM (replace with your DEM source)
        dem = ee.Image('USGS/SRTMGL1_003');

        # Calculate the difference in backscatter, adding a small constant (e.g., 0.01)
        epsilon = 0.01
        difference_image = after_img.subtract(before_img).add(epsilon)

        # Calibration and Conversion Function
        def db_to_meters(img, calibration_factor, dem):
            """Converts backscatter difference (dB) to estimated water level (m)."""
            linear_power_ratio = ee.Image(10).pow(img.divide(10))  # dB to linear power
            water_level_change = linear_power_ratio.subtract(1).multiply(calibration_factor)
            return water_level_change  # .add(dem)  # Add DEM to get absolute water level

        # Calculate the difference and apply the calibration function
        masked_difference = difference_image.updateMask(water_mask)
        estimated_water_level_change = db_to_meters(masked_difference, calibration_factor, dem)

        return estimated_water_level_change

    @classmethod
    def get_water_level_image(cls, region: GEERegion, end_date: datetime = None) -> ee.Image:
        """
        @param region:
        @param end_date:
        @return: ee.Image
        """
        if end_date is None:
            end_date = datetime.today()
        after_date_range = GEEImageCollection.get_date_range(20, end_date=end_date)
        before_end_date = datetime.strptime(after_date_range[0], '%Y-%m-%d')
        before_date_range = GEEImageCollection.get_date_range(20, end_date=before_end_date)
        date_range = (before_date_range[0], after_date_range[1])

        # water_masked = cls.sentinel2_water_mask(region, date_range)
        # water_masked = cls.combined_water_mask(region, date_range)
        water_masked = GEEWater.get_water_mask_jrc(region)
        water_level_change_image = cls.get_water_level_using_change_detection_sentinel_1(region, water_masked,
                                                                                         before_date_range,
                                                                                         after_date_range)
        return water_level_change_image

    @classmethod
    def get_water_level_url(cls, region: GEERegion, end_date: datetime = None):
        """
        @param region:
        @param end_date:
        @return:
        """
        water_level_change_image = cls.get_water_level_image(region)
        vis_params = cls.get_water_level_vis_params()
        url = water_level_change_image.getMapId(vis_params)
        return url['tile_fetcher'].url_format

    @classmethod
    def get_latest_date(cls, region: GEERegion, sen_tag: SentinelTag = SentinelTag.SENTINEL1 ):
        img_collection = GEEImageCollection(ee.ImageCollection(sen_tag.value)
                                            .filterBounds(region.bounds))
        return img_collection.get_latest_image_date()
