from .Parallels import parallel_gpd_clip, parallel_v2r 
from .func import data_modification, Comp_Vulnerability, Comp_Vulnerability_Scen, match_vuln_modrec, VulMod, shp_to_raster, Accept_Manager, cleaning_directory

import pandas as pd
import os
from osgeo import gdal
import fiona
import glob
import numpy as np
import geopandas as gpd
from pathlib import Path
import logging
from tqdm import tqdm




class Vulnerability_csv():

    def __init__(self, file:Path) -> None:
        self.file = file
        self.data = pd.read_csv(file, sep=",", encoding='latin-1')

    def get_layers(self) -> list:
        return [a[1] for a in self.data["Path"].str.split('/')]
    
    def get_vulnerability_level(self, layer:str) -> str:
        idx = self.get_layers().index(layer)
        return self.data.iloc[idx]["Vulne"]
    
    def get_vulnerability_code(self, layer:str) -> str:
        idx = self.get_layers().index(layer)
        return self.data.iloc[idx]["Code"]

def Base_data_creation(main_dir:str = 'Data', 
                       Original_gdb:str = 'GT_Resilence_dataRisques202010.gdb', 
                       Study_area:str = 'Bassin_Vesdre.shp', 
                       CaPa_Walloon:str = 'Cadastre_Walloon.gpkg', 
                       PICC_Walloon:str = 'PICC_vDIFF.gdb', 
                       CE_IGN_top10v:str = 'CE_IGN_TOP10V/CE_IGN_TOP10V.shp',
                       resolution:float = 1.,
                       number_procs:int = 8):
    """
    Create the databse.

    In this step, the following operations are performed:
        - Clip the original gdb file to the study area
        - Clip the Cadastre Walloon file to the study area
        - Clip the PICC Walloon file to the study area
        - Clip and Rasterize the IGN top10v file
        - Create the study area database with the vulnerability levels


    :param main_dir: The main data directory
    :param Original_gdb: The original gdb file from SPW - GT Resilience
    :param Study_area: The study area shapefile -- Data will be clipped to this area
    :param CaPa_Walloon: The Cadastre Walloon file -- Shapfeile from SPW
    :param PICC_Walloon: The PICC Walloon file -- Shapefile from SPW
    :param CE_IGN_top10v: The CE "Cours d'eau" IGN top10v file -- Shapefile from IGN with river layer
    :param resolution: The output resolution of the raster files
    :param number_procs: The number of processors to use for parallel processing
    
    """
    NUMBER_PROCS = number_procs

    dirsnames = Accept_Manager(main_dir, 
                           Study_area,
                           Original_gdb=Original_gdb,
                           CaPa_Walloon=CaPa_Walloon,
                           PICC_Walloon=PICC_Walloon,
                           CE_IGN_top10v=CE_IGN_top10v)

    if not dirsnames.check_before_database_creation():
        logging.error("The necessary files are missing - Verify logs for more information")
        return
    
    dirsnames.change_dir()
    
    # Clean the directory to avoid any conflict
    # GPKG driver does not overwrite the existing file but adds new layers
    cleaning_directory(dirsnames.TMP_STUDYAREA)

    # ********************************************************************************************************************
    # Step 1, Clip Original GDB

    # Load the vulnerability CSV to get the layers
    vulnerability_csv = Vulnerability_csv(dirsnames.VULNERABILITY_CSV)
    # Clip the GDB file and store it in dirsnames.SA_DATABASE
    parallel_gpd_clip(vulnerability_csv.get_layers(), dirsnames.ORIGINAL_GDB, dirsnames.SA, dirsnames.SA_DATABASE, NUMBER_PROCS)
    
    # ********************************************************************************************************************
    # Step 2, Clip Cadaster data

    # Only 2 layers are present in the Cadastre Walloon file
    LAYER_CABU = "CaBu"
    LAYER_CAPA = "CaPa"
    # Clip the Cadastre Walloon file and store it in dirsnames.SA_CAPA
    parallel_gpd_clip([LAYER_CABU, LAYER_CAPA], dirsnames.CAPA_WALLOON, dirsnames.SA, dirsnames.SA_CAPA, min(2, NUMBER_PROCS))

    # ********************************************************************************************************************
    # Step 3, Clip PICC data

    # ONly 1 layer is needed from the PICC Walloon file
    LAYER_BATIEMPRISE = "CONSTR_BATIEMPRISE"
    # Clip the PICC Walloon file and store it in dirsnames.SA_PICC
    parallel_gpd_clip([LAYER_BATIEMPRISE], dirsnames.PICC_WALLOON, dirsnames.SA, dirsnames.SA_PICC, min(1, NUMBER_PROCS))
	
    # ********************************************************************************************************************
    # Step 4, create database based on changes in report

    layers = fiona.listlayers(dirsnames.SA_DATABASE)
    # PreLoad Picc and CaPa from clipped files
    Picc:gpd.GeoDataFrame = gpd.read_file(dirsnames.SA_PICC, layer = LAYER_BATIEMPRISE)
    CaPa:gpd.GeoDataFrame = gpd.read_file(dirsnames.SA_CAPA, layer = LAYER_CAPA)

    assert Picc.crs == CaPa.crs, "The crs of the two shapefiles are different"

    for curlayer in tqdm(layers, desc="Vulnerability : Processing layers"):
        data_modification(dirsnames.SA_DATABASE, curlayer, dirsnames.SA_FINAL, Picc, CaPa)

    # ********************************************************************************************************************
    # Step 5 : Rasaterize the IGN data "Course d'eau" to get the riverbed mask
    shp_to_raster(dirsnames.CE_IGN_TOP10V, dirsnames.SA_MASKED_RIVER, resolution)
    
    # ********************************************************************************************************************
    # Step 6 :  Pre-processing for Vulnerability
    #           Save the database with vulnerability levels and codes
    # This database will be rasterized in 'Database_to_raster'

    layers_sa = fiona.listlayers(dirsnames.SA_FINAL)
    layers_csv = vulnerability_csv.get_layers()
    
    # Search difference between the two lists of layers
    list_shp = list(set(layers_csv).difference(layers_sa))

    logging.info("Excluded layers due to no features in shapefiles:")
    logging.info(list_shp)

    logging.info("STEP1: Saving the database for Vulnerability with attributes Vulne and Code")
    
    for curlayer in layers_sa:
        logging.info(curlayer)

        shp:gpd.GeoDataFrame = gpd.read_file(dirsnames.SA_FINAL, layer=curlayer)
        
        x, y = shp.shape
        if x > 0:
            shp["Path"]  = curlayer
            shp["Vulne"] = vulnerability_csv.get_vulnerability_level(curlayer)
            shp["Code"]  = vulnerability_csv.get_vulnerability_code(curlayer)
            shp = shp[["geometry", "Path", "Vulne","Code"]]
            shp.to_file(dirsnames.SA_FINAL_V, layer=curlayer)
    
    # Rasterize the database
    Database_to_raster(main_dir, Study_area, resolution)

    dirsnames.restore_dir()

def Database_to_raster(main_dir:str = 'Data',
                       Study_area:str = 'Bassin_Vesdre.shp',
                       resolution:float = 1.,
                       number_procs:int = 16):
    """ 
    Convert the vector database to raster database based on their vulnerability values 
    
    Ecah leyer is converted to a raster file with the vulnerability values
    and the code values.

    They are stored in the TEMP/DATABASES/*StudyArea*/VULNERABILITY/RASTERS in:
        - Code
        - Vulne

    :param main_dir: The main data directory
    :param Study_area: The study area shapefile
    :param resolution: The resolution of the output raster files - default is 1 meter
    :param number_procs: The number of processors to use for parallel processing

    The parellel processing is safe as each layer is processed independently.
    """

    dirsnames = Accept_Manager(main_dir, Study_area)

    resolution = float(resolution)

    if not dirsnames.check_before_rasterize():
        logging.error("The necessary files are missing - Verify logs for more information")
        return

    dirsnames.change_dir()

    logging.info("Convert vectors to raster based on their vulnerability values")
    layers = fiona.listlayers(dirsnames.SA_FINAL_V)
    
    attributes = ["Vulne", "Code"]
    for cur_attrib in attributes:
        parallel_v2r(layers, dirsnames.SA_FINAL_V, dirsnames.SA, cur_attrib, resolution, number_procs)

    dirsnames.restore_dir()

def Vulnerability(main_dir:str = 'Data',
                  scenario:str = 'Scenario1',
                  Study_area:str = 'Bassin_Vesdre.shp',
                  resolution:float = 1.,
                  steps:list[int] = [1,2,3]):
    """
    Compute the vulnerability for the study area and the scenario, if needed.

    The vulnerability is computed in 3 steps:
        1.  Compute the vulnerability for the study area
        2.  Compute the vulnerability for the scenario
        3.  Clip the vulnerability rasters to the simulation area

    During step 3, three matrices are computed and clipped to the simulation area:
        - Vulnerability
        - Code
        - Masked River
    
    :param main_dir: The main data directory    
    :param scenario: The scenario name
    :param Study_area: The study area shapefile
    :param resolution: The resolution of the output raster files - default is 1 meter
    :param steps: The steps to compute the vulnerability - default is [1,2,3]

    To be more rapid, the steps can be computed separately.
        - [1,2,3] : All steps are computed - Necessary for the first time
        - [2,3]   : Only the scenario and clipping steps are computed -- Useful for scenario changes
        - [3]     : Only the clipping step is computed -- Useful if simulation area changes but scenario is the same

    """

    dirsnames = Accept_Manager(main_dir, Study_area, scenario=scenario)

    if not dirsnames.check_before_vulnerability():
        logging.error("The necessary files are missing - Verify logs for more information")
        return

    logging.info("Starting VULNERABILITY computations at {} m resolution".format(resolution))
    
    dirsnames.change_dir()
    
    if 1 in steps:
        # Step 1 :  Compute the vulnerability rasters for the study area
        #           The data **will not** be impacted by the scenario modifications
    
        logging.info("Generate Vulnerability rasters {}m".format(resolution))

        cleaning_directory(dirsnames.TMP_SCEN_DIR)

        Comp_Vulnerability(dirsnames)

    if 2 in steps:
        # Step 2 :  Compute the vulnerability rasters for the scenario
        #           The data **will be** impacted by the scenario modifications  

        if not dirsnames.check_vuln_code_sa():
            logging.error("The vulnerability and code files for the study area are missing")
            logging.warning("Force the computation even if not prescribed in the steps")

            Vulnerability(main_dir, scenario, Study_area, resolution, [1])

        bu:list[Path] = dirsnames.get_files_in_rm_buildings()

        if len(bu)>0:
            for curfile in bu:
                tiff_file = dirsnames.TMP_RM_BUILD_DIR / (curfile.stem + ".tiff")
                shp_to_raster(curfile, tiff_file)

            Comp_Vulnerability_Scen(dirsnames)
        else:
            logging.warning(f"No buildings were removed in water depth analysis OR No shapefiles in {dirsnames.IN_RM_BUILD_DIR}")

    if 3 in steps:
        # Step 3 :  Clip the vulnerability/code rasters to the **simulation area**

        logging.info("Save Vulnerability files for the area of interest")
        
        return_periods = dirsnames.get_return_periods()
        TMAX = dirsnames.get_filepath_for_return_period(return_periods[-1])

        if TMAX is None:
            logging.error("The file for the maximum return period is missing")
            return

        match_vuln_modrec(dirsnames.SA_MASKED_RIVER,dirsnames.OUT_MASKED_RIVER, TMAX)
        match_vuln_modrec(dirsnames.SA_VULN,        dirsnames.OUT_VULN,         TMAX)
        match_vuln_modrec(dirsnames.SA_CODE,        dirsnames.OUT_CODE,         TMAX)

    dirsnames.restore_dir()

def Acceptability(main_dir:str = 'Vesdre',
                  scenario:str = 'Scenario1',
                  Study_area:str = 'Bassin_Vesdre.shp'):
    """ Compute acceptability for the scenario """
    
    dirsnames = Accept_Manager(main_dir, Study_area, scenario=scenario)

    dirsnames.change_dir()

    # Load the vulnerability raster **for the scenario**
    vulne = gdal.Open(str(dirsnames.OUT_VULN))
    # Convert to numpy array
    vulne = vulne.GetRasterBand(1).ReadAsArray() 

    # Load the river mask
    riv = gdal.Open(str(dirsnames.OUT_MASKED_RIVER))

    # Get the geotransform and projection for the output tiff
    geotrans = riv.GetGeoTransform()  
    proj = riv.GetProjection()  

    # Convert to numpy array
    riv = riv.GetRasterBand(1).ReadAsArray()    

    # Get the return periods available
    return_periods = dirsnames.get_return_periods()

    # Prepare the river bed filter
    # Useful as we iterate over the return periods
    # and the river bed is the same for all return periods
    ij_riv = np.where(riv == 1)
    
    # Compute acceptability for each return period
    for curT in tqdm(return_periods):

        # Load the **FILLED** modelled water depth for the return period
        model_h = gdal.Open(str(dirsnames.get_sim_file_for_return_period(curT)))
        # Convert to numpy array
        model_h = model_h.GetRasterBand(1).ReadAsArray()

        # Set nan if the water depth is 0
        model_h[model_h == 0] = np.nan
        # Set nan in the river bed
        model_h[ij_riv] = np.nan

        logging.info("Return period {}".format(curT))
        # Compute the local acceptability for the return period
        VulMod(dirsnames, model_h, vulne, curT, (geotrans, proj))

    # At this point, the local acceptability for each return period is computed
    # and stored in tiff files in the TEMP/SutyArea/scenario/Q_FILES directory
    
    # Get the list of Q files
    qs = dirsnames.get_q_files()
    # Initialize the dictionary to store the acceptability values
    q_dict = {}

    # Iterate over the return periods
    for curT in return_periods:
        logging.info("vm"+str(curT))

        # We set the filename from the return period, not the "qs" list
        q_filename = dirsnames.TMP_QFILES / "Q{}.tif".format(curT)
        
        # Check if the file exists
        assert q_filename.exists(), "The file {} does not exist".format(q_filename)
        # Check if the file is in the "qs" list
        assert q_filename in qs, "The file {} is not in the list of Q files".format(q_filename)

        # Load the Q file for the return period
        tmp_data = gdal.Open(str(q_filename))
        # Convert to numpy array
        q_dict["vm"+str(curT)] = tmp_data.GetRasterBand(1).ReadAsArray()

        # Force the deletion of the variable, rather than waiting for the garbage collector
        # May be useful if the files are large
        del tmp_data

    # Pointing the last return period, maybe 1000 but not always
    array_t1000 = q_dict["vm{}".format(return_periods[-1])]
    # Get the indices where the value is -99999
    # We will force the same mask for all lower return periods
    ij_t1000 = np.where(array_t1000 == -99999)

    # Iterate over the return periods
    for curT in return_periods:
      
      if curT != return_periods[-1]:
        logging.info(curT)
        
        # Alias
        tmp_array = q_dict["vm{}".format(curT)]
        
        # Set the -99999 values to 0
        tmp_array[tmp_array == -99999] = 0.
        # Set the masked values, for the last return period, to nan
        tmp_array[ij_t1000] = np.nan

    # # Load the ponderation file
    # pond = pd.read_csv(dirsnames.PONDERATION_CSV)
    # # Set the index to the interval, so we can use the interval as a key
    # pond.set_index("Interval", inplace=True)

    # Get ponderations for the return periods
    pond = dirsnames.get_ponderations()

    assert len(pond) == len(return_periods), "The number of ponderations is not equal to the number of return periods"
    assert pond["Ponderation"].sum() > 0.999999 and pond["Ponderation"].sum()<1.0000001, "The sum of the ponderations is not equal to 1"

    # Initialize the combined acceptability matrix -- Ponderate mean of the local acceptability
    comb = np.zeros(q_dict["vm{}".format(return_periods[-1])].shape)
    
    for curT in return_periods:
         comb += q_dict["vm{}".format(curT)] * pond["Ponderation"][curT]

    y_pixels, x_pixels = comb.shape  # number of pixels in x

    # Set up output GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(str(dirsnames.OUT_ACCEPT), x_pixels, y_pixels, 1, gdal.GDT_Float32, options=["COMPRESS=LZW"])
    dataset.GetRasterBand(1).WriteArray(comb.astype(np.float32))   
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    del(dataset)

    # Resample to 100m
    Agg = gdal.Warp(str(dirsnames.OUT_ACCEPT_100M), str(dirsnames.OUT_ACCEPT), xRes=100, yRes=100, resampleAlg='Average')
    del(Agg)

    dirsnames.restore_dir()