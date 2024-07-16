import ee

from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.region import GEERegion


class GEEWater:
    @staticmethod
    def surface_water_using_jrc( band="max_extent", region: GEERegion = None) ->GEEImage:
        """
        https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater
        recommended bands are max_extent for flood extent and
        occurrence to see how frequent water flow there
        bands are
        name        unit min max description
        occurrence	%	0	100
        The frequency with which water was present.

        change_abs	%	-100	100
        Absolute change in occurrence between two epochs: 1984-1999 vs 2000-2021.

        change_norm	%	-100	100
        Normalized change in occurrence. (epoch1-epoch2)/(epoch1+epoch2) * 100

        seasonality		0	12
        Number of months water is present.

        recurrence	%	0	100
        The frequency with which water returns from year to year.

        transition
        Categorical classification of change between first and last year.

        max_extent
        Binary image containing 1 anywhere water has ever been detected.
        @return:
        """
        dataset = ee.Image('JRC/GSW1_4/GlobalSurfaceWater')
        if region is not None:
            dataset.clip(region.aoi)
        selected_band = dataset.select(band)
        return GEEImage(selected_band)

    @classmethod
    def get_water_mask_jrc(cls,  region: GEERegion) -> GEEImage:
        """
        https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater
        recommended bands are max_extent for flood extent and
        occurrence to see how frequent water flow there
        bands are
        name        unit min max description
        occurrence	%	0	100
        The frequency with which water was present.

        change_abs	%	-100	100
        Absolute change in occurrence between two epochs: 1984-1999 vs 2000-2021.

        change_norm	%	-100	100
        Normalized change in occurrence. (epoch1-epoch2)/(epoch1+epoch2) * 100

        seasonality		0	12
        Number of months water is present.

        recurrence	%	0	100
        The frequency with which water returns from year to year.

        transition
        Categorical classification of change between first and last year.

        max_extent
        Binary image containing 1 anywhere water has ever been detected.
        @return:
        """
        selected_band = cls.surface_water_using_jrc("max_extent", region).image
        mask = selected_band.gt(0)
        masked_band = selected_band.updateMask(mask)
        return masked_band
