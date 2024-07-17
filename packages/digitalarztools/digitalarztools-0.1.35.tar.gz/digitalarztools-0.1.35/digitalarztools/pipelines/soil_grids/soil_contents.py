import os
import time
import traceback
import urllib
from io import BytesIO

import numpy as np
import rasterio
import requests
from digitalarztools.io.file_io import FileIO

from digitalarztools.io.raster.band_process import BandProcess
from digitalarztools.io.raster.rio_raster import RioRaster
from digitalarztools.utils.logger import da_logger
from digitalarztools.utils.waitbar_console import WaitBarConsole


class SoilContent:
    @classmethod
    def get_clay_content(cls, des_dir, lat_lim, lon_lim, level='sl1', wait_bar=1):
        """
        Downloads SoilGrids data from ftp://ftp.soilgrids.org/data/recent/

        this data includes a Digital Elevation Model (DEM)
        The spatial resolution is 90m (3s) or 450m (15s)

        The following keyword arguments are needed:
        des_dir -- path to store data
        lat_lim -- [ymin, ymax]
        lon_lim -- [xmin, xmax]
        level -- 'sl1' (Default)
                 'sl2'
                 'sl3'
                 'sl4'
                 'sl5'
                 'sl6'
                 'sl7'
        wait_bar -- '1' if you want a waitbar (Default = 1)
        """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Clay_Content')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'ClayContentMassFraction_%s_SoilGrids_percentage.tif' % level)

        if not os.path.exists(fp_end):

            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text('\nDownload Clay Content soil map of %s from SoilGrids.org' % level)

                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "CLAY", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nClay Content soil map of {level} from SoilGrids.org already exists in {fp_end}")

    @classmethod
    def get_silt_content(cls, des_dir, lat_lim, lon_lim, level='sl1', wait_bar=1):
        """
        Downloads SoilGrids data from ftp://ftp.soilgrids.org/data/recent/

        The following keyword arguments are needed:
        Dir -- 'C:/file/to/path/'
        lat_lim -- [ymin, ymax]
        lon_lim -- [xmin, xmax]
        level -- 'sl1' (Default)
                 'sl2'
                 'sl3'
                 'sl4'
                 'sl5'
                 'sl6'
                 'sl7'
        wait_bar -- '1' if you want a waitbar (Default = 1)
        """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Silt_Content')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'SiltContentMassFraction_%s_SoilGrids_percentage.tif' % level)

        if not os.path.exists(fp_end):

            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text(
                    '\nDownload Silt Content Mass Fraction soil map of %s from SoilGrids.org' % level)
                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "SILT", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nSilt Content Mass Fraction soil map of {level} from SoilGrids.org already exists in {fp_end}")

    @staticmethod
    def get_soil_data_level() -> dict:
        """
         https://www.isric.org/ soil grids data level in cm
        """
        dict_levels = dict()
        dict_levels["sl1"] = "0-5"
        dict_levels["sl2"] = "5-15"
        dict_levels["sl3"] = "15-30"
        dict_levels["sl4"] = "30-60"
        dict_levels["sl5"] = "60-100"
        dict_levels["sl6"] = "100-200"
        return dict_levels

    @classmethod
    def download_data(cls, output_folder, lat_lim, lon_lim, dataset, level, apply_conversion=True):
        """
        This function downloads SoilGrids data from SoilGrids.org in percentage
        Keyword arguments:
        output_folder -- directory of the result
        lat_lim -- [ymin, ymax] (values must be between -50 and 50)
        lon_lim -- [xmin, xmax] (values must be between -180 and 180)
        level -- "sl1" .... "sl7"
                dict_levels["sl1"] = "0-5_cm"
                dict_levels["sl2"] = "5-15_cm"
                dict_levels["sl3"] = "15-30_cm"
                dict_levels["sl4"] = "30-60_cm"
                dict_levels["sl5"] = "60-100_cm"
                dict_levels["sl6"] = "100-200_cm"
        dataset -- (in capital) clay, sand, silt, soc, sod, ph,  nitrogen, bulkdensity,\
        """

        dict_levels = cls.get_soil_data_level()

        FileIO.mkdirs(output_folder)

        # if "conversion" in locals():
        #     del "conversion"

        # Define parameter depedent variables
        if dataset == "BULKDENSITY":
            fp = os.path.join(output_folder,
                              f'BulkDensity_{dict_levels[level]}_SoilGrids_{"kg_m3" if apply_conversion else "cg_cm3"}.tif')
            parameter = "bdod"
            conversion = 10  # cg/cm3 to kg/m3
            level_str = dict_levels[level]
        if dataset == "NITROGEN":
            fp = os.path.join(output_folder,
                              f'Nitrogen_{dict_levels[level]}_SoilGrids_{"g_kg" if apply_conversion else "g_kg"}.tif')
            parameter = "nitrogen"
            level_str = dict_levels[level]
            conversion = 0.01  # cg/kg to g/kg
        if dataset == "SOC":
            fp = os.path.join(output_folder,
                              f'SoilOrganicCarbonContent_{dict_levels[level]}_SoilGrids_{"g_kg" if apply_conversion else "dg_kg"}.tif')
            parameter = "soc"
            level_str = dict_levels[level]
            conversion = 0.1  # dg/kg to g/kg
        if dataset == "SOD":
            fp = os.path.join(output_folder, f'SoilOrganicCarbonDensity_{dict_levels[level]}_SoilGrids_g_dm3.tif')
            parameter = "ocd"
            conversion = 1.0
            level_str = dict_levels[level]
        if dataset == "PH":
            fp = os.path.join(output_folder, f'SoilPH_{dict_levels[level]}_SoilGrids_pH10.tif')
            parameter = "phh2o"
            level_str = dict_levels[level]
            conversion = 1.0
        if dataset == "CLAY":
            fp = os.path.join(output_folder,
                              f'ClayContentMassFraction_{dict_levels[level]}_SoilGrids_{"percentage" if apply_conversion else "g_kg"}.tif')
            parameter = "clay"
            level_str = dict_levels[level]
            conversion = 0.1  # g/kg to percentage
        if dataset == "SAND":
            fp = os.path.join(output_folder,
                              f'SandContentMassFraction_{dict_levels[level]}_SoilGrids_{"percentage" if apply_conversion else "g_kg"}.tif')
            parameter = "sand"
            level_str = dict_levels[level]
            conversion = 0.1  # g/kg to percentage
        if dataset == "SILT":
            fp = os.path.join(output_folder,
                              f'SiltContentMassFraction_{dict_levels[level]}_SoilGrids_{"percentage" if apply_conversion else "g_kg"}.tif')
            parameter = "silt"
            level_str = dict_levels[level]
            conversion = 0.1  # g/kg to percentage

        if not os.path.exists(fp):
            dir = FileIO.mkdirs(fp)
            # Download, extract, and converts all the files to tiff files
            try:

                url = "https://maps.isric.org/mapserv?map=/map/%s.map&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=%s_%scm_mean&FORMAT=image/tiff&SUBSET=long(%f,%f)&SUBSET=lat(%f,%f)&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/4326&OUTPUTCRS=http://www.opengis.net/def/crs/EPSG/0/4326" % (
                    parameter, parameter, level_str, lon_lim[0], lon_lim[1], lat_lim[0], lat_lim[1])
                # url = "http://85.214.241.121:8080/geoserver/ows?service=WCS&version=2.0.1&request=GetCoverage&CoverageId=%s_M_%s250m&subset=Long(%f,%f)&subset=Lat(%f,%f)" %(dataset, level_name, lonlim[0], lonlim[1], latlim[0], latlim[1])
                # print(url)
                # urllib.request.urlretrieve(url, filename=name_end)
                # Make an HTTP request to the URL
                response = requests.get(url)

                if response.status_code == 200:
                    # Save the binary content to a file (e.g., "sand_image.tif")
                    with open(fp, "wb") as f:
                        f.write(response.content)

                    print("Image downloaded and saved successfully.")

                else:
                    print(f"Error: Unable to download the image. Status code: {response.status_code}")

                if "conversion" in locals():
                    print("Conversion is applied of %s" % conversion)
                    # dest = gdal.Open(nameEnd)
                    raster = RioRaster(fp)
                    # geo = dest.GetGeoTransform()
                    affine_transform = raster.get_geo_transform()
                    # proj = "WGS84"
                    proj = raster.get_crs()
                    # Array = dest.GetRasterBand(1).ReadAsArray()
                    data = raster.get_data_array(1)
                    # del raster
                    time.sleep(1)
                    data = np.float_(data) * conversion
                    nodata_value = 0

                    data = BandProcess.gap_filling(data, nodata_value)

                    # DC.Save_as_tiff(name_end, data, geo, proj)
                    RioRaster.write_to_file(fp, data, raster.get_crs(), raster.get_geo_transform(), nodata_value)

            except Exception as e:
                da_logger.error(traceback.print_stack())
                da_logger.error(str(e))

        return fp

    @classmethod
    def get_organic_carbon_content(cls, des_dir, lat_lim, lon_lim, level, wait_bar=1):
        """
            Downloads SoilGrids data from ftp://ftp.soilgrids.org/data/recent/

            The following keyword arguments are needed:
            des_dir -- destination directory
            lat_lim -- [ymin, ymax]
            lon_lim -- [xmin, xmax]
            level -- 'sl1' (Default)
                     'sl2'
                     'sl3'
                     'sl4'
                     'sl5'
                     'sl6'
                     'sl7'
            wait_bar -- '1' if you want a waitbar (Default = 1)
            """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Soil_Organic_Carbon_Content')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'SoilOrganicCarbonContent_%s_SoilGrids_g_kg.tif' % level)

        if not os.path.exists(fp_end):

            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text(
                    '\nDownload Soil Organic Carbon Content soil map of %s from SoilGrids.org' % level)
                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "SOC", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nSoil Organic Carbon Content soil map of {level} from SoilGrids.org already exists in {fp_end}")

    @classmethod
    def get_bulk_density(cls, des_dir, lat_lim, lon_lim, level, wait_bar=1):
        """
            Downloads data from SoilGrids (www.soilgrids.org)

            The following keyword arguments are needed:
            des_dir -- destination directory
            lat_lim -- [ymin, ymax]
            lon_lim -- [xmin, xmax]
            level -- 'sl1' (Default)
                     'sl2'
                     'sl3'
                     'sl4'
                     'sl5'
                     'sl6'
                     'sl7'
            wait_bar -- '1' if you want a waitbar (Default = 1)
            """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Bulk_Density')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'BulkDensity_%s_SoilGrids_kg-m-3.tif' % level)

        if not os.path.exists(fp_end):
            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text('\nDownload Bulk Density soil map of %s from SoilGrids.org' % level)
                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "BULKDENSITY", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nBulk Density soil map of {level} from SoilGrids.org already exists in {fp_end}")
