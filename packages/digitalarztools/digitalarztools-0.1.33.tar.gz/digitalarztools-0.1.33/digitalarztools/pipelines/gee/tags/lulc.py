from digitalarztools.pipelines.gee.core.auth import GEEAuth
from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.utils.logger import da_logger


class LandUseLandCover:
    def __init__(self):
        pass

    @staticmethod
    def esa_world_cover_using_gee(gee_auth: GEEAuth, region: GEERegion) -> GEEImage:
        """
        Extreact latest ESA world cover data (10m) from GEE. The details can be seen at
        https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200#description
            10	006400	Tree cover
            20	ffbb22	Shrubland
            30	ffff4c	Grassland
            40	f096ff	Cropland
            50	fa0000	Built-up
            60	b4b4b4	Bare / sparse vegetation
            70	f0f0f0	Snow and ice
            80	0064c8	Permanent water bodies
            90	0096a0	Herbaceous wetland
            95	00cf75	Mangroves
            100	fae6a0	Moss and lichen

        :param gee_auth:
        :param region:
        :return:
        """
        if gee_auth.is_initialized:
            # date_range = (start_date, end_date)
            img_collection = GEEImageCollection(region, 'ESA/WorldCover/v200')
            return GEEImage(img_collection.get_image('first'))
        else:
            da_logger.error("Please initialized GEE before further processing")