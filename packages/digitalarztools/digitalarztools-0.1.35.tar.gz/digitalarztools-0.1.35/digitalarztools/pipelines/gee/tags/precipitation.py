from datetime import datetime, date, timedelta
from typing import Union

import ee

from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion


class Precipitation:
    """
    Extrat data from different sources
    """

    @staticmethod
    def chirps_data_using_gee(region: GEERegion, start_date: Union[str, datetime],
                              end_date: Union[str, datetime], how='mean') -> GEEImage:
        """
        Extract CHIRPS data using following code
            https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
       `:param gdv: for define AOI
        :param start_date:
        :param end_date:
        :param how: choices are 'median', 'max', 'mean', 'first', 'cloud_cover', 'sum'
        :return:
        """

        # date_range = (start_date, end_date)
        date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        img_collection = GEEImageCollection(ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY"))
        img_collection.set_date_range(date_range)
        img_collection.set_region(region)

        # img_collection = GEEImageCollection(region, 'UCSB-CHG/CHIRPS/DAILY', date_range)
        img_collection.select_dataset('precipitation')
        return GEEImage(img_collection.get_image(how))

    @staticmethod
    def get_chirps_vis_parameters():
        # ['sky_blue', 'green', 'yellow', 'orange', 'red']
        return {'min': 10, 'max': 200, 'palette':
            ['87CEEB', '00ff00', 'ffff00', 'ffa500', 'ff0000']}

    @staticmethod
    def precipitation_with_et(i_date=None, f_date=None, no_of_days=10):
        """
        :param i_date: inital date (2023-01-01)
        :param f_date:  final date like 2023-12-07
        :return:
        """
        if f_date is None:
            f_date = datetime.date.today()
        if i_date is None:
            # first = today.replace(day=1)
            i_date = f_date - datetime.timedelta(days=no_of_days)
            date_range = (i_date.strftime("%Y-%m-%d"), f_date.strftime("%Y-%m-%d"))

        pr = GEEImageCollection.from_tags("UCSB-CHG/CHIRPS/DAILY", date_range)
        pr.select_bands(["precipitation"])

        pet = GEEImageCollection.from_tags("MODIS/006/MOD16A2", date_range)
        pet.select_bands(["PET", "ET_QC"])

        # local_pr = pr.get_image_info_within_poi(poi, scale)
        # pprint.pprint(local_pr[:5])

        pr_m = pr.sum_resampler(pr.img_collection, 1, "month", 1, "pr")

        # # Evaluate the result at the location of interest.
        # pprint.pprint(pr_m.getRegion(poi, scale).getInfo()[:5])

        """
        For evapotranspiration, we have to be careful with the unit. The dataset gives us an 8-day sum and a scale factor of 10 is applied. Then, to get a homogeneous unit, we need to rescale by dividing by 8 and 10: 1/(8*10) = 0.0125
        .
        """
        # Apply the resampling function to the PET dataset.
        pet_m = pet.sum_resampler(pet.img_collection.select(["PET"]), 1, "month", 0.0125, "pet")

        # # Evaluate the result at the location of interest.
        # pprint.pprint(pet_m.getRegion(poi, scale).getInfo()[:5])

        meteo = pr_m.combine(pet_m)
        return meteo

    @staticmethod
    def get_accumulated_precipitation(region: GEERegion, no_of_days:int=7, end_date=None, mask_threshold=-1):
        """
        @param region:
        @param end_date:
        @return:
        """
        date_range = GEEImageCollection.get_date_range(no_of_days * 5, end_date)
        # Load the CHIRPS daily precipitation dataset and filter by date and bounds.
        img_collection = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate(date_range[0], date_range[1]) \
            .filterBounds(region.bounds) \
            .sort('system:time_start', False) \
            .limit(no_of_days)

        # Calculate the 16-day total precipitation.
        chirps_total = img_collection.sum().rename('total_precipitation')

        # Create a mask for areas with precipitation greater than 10mm.
        mask = chirps_total.gt(mask_threshold) if mask_threshold != -1 else chirps_total

        # Update the precipitation image with the mask.
        masked_img = chirps_total.updateMask(mask)

        return masked_img

    @classmethod
    def get_accumulated_precipitation_url(cls, region: GEERegion, end_date=None, no_of_days=16):
        masked_img = cls.get_accumulated_precipitation(region, no_of_days=no_of_days, end_date=end_date,
                                                       mask_threshold=5)
        vis_params = cls.get_chirps_vis_parameters()
        # url = masked_img.getMapId(vis_params)
        # return url['tile_fetcher'].url_format
        return GEEImage.get_imgae_url(masked_img, vis_params)
