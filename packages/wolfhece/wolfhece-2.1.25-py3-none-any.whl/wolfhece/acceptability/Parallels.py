from .func import gpd_clip, data_modification, vector_to_raster, Comp_Vulnerability, match_vuln_modrec, VulMod, shp_to_raster
import multiprocessing
from functools import partial
import os
from pathlib import Path

def parallel_gpd_clip(layer:list[str], 
                      file_path:str, 
                      Study_Area:str, 
                      output_gpkg:str, 
                      number_procs:int = 1):
    """ 
    Clip the layers to the study area.
    
    Process the layers in parallel.

    FIXME: The GPKG driver is it totally parallel compliant?

    :param layer: List of layers to clip
    :param file_path: The path to the file
    :param Study_Area: The study area
    :param output_gpkg: The output geopackage
    :param number_procs: The number of processors to use

    """
    file_path = str(file_path)
    Study_Area = str(Study_Area)
    output_gpkg = str(output_gpkg)

    if number_procs == 1:

        for curlayer in layer:
            gpd_clip(curlayer, file_path, Study_Area, output_gpkg)

    else:
        pool = multiprocessing.Pool(processes=number_procs)
        prod_x=partial(gpd_clip,
                    file_path=file_path,
                    Study_Area=Study_Area,
                    geopackage=output_gpkg)
        result_list = pool.map(prod_x, layer)
        print(result_list)

def parallel_v2r(layers:list[str], 
                 study_area_database:Path, 
                 extent:Path, 
                 attribute:str, 
                 pixel:float,
                 number_procs:int = 1):
    """ 
    Convert the vector layers to raster.

    Process the layers in parallel.

    :remark: It is permitted to execute this function in multiprocessing because we write separate files.

    :param layers: List of layers to convert to raster.
    :param study_area_database: The Path to the study area
    :param extent: The extent of the study area
    :param attribute: The attribute to convert to raster
    :param pixel: The pixel size of the raster
    :param number_procs: The number of processors to use

    """
    
    attribute = str(attribute)

    if number_procs == 1:
        for curlayer in layers:
            vector_to_raster(curlayer, study_area_database, extent, attribute, pixel)
    else:
        pool = multiprocessing.Pool(processes=number_procs)
        prod_x=partial(vector_to_raster,
                       vector_input=study_area_database,
                       extent=extent, 
                       attribute=attribute, 
                       pixel_size=pixel) # prod_x has only one argument x (y is fixed to 10)
        
        result_list = pool.map(prod_x, layers)
        print(result_list)

