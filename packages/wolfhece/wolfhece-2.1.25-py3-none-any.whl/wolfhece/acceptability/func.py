import geopandas as gpd
import pandas as pd
import numpy as np
from osgeo import gdal, ogr, osr, gdalconst
import os
import glob
from pathlib import Path
import logging
from tqdm import tqdm

def get_data_type(fname:Path):

    fname = Path(fname)
    """ Get the data type of the input file from extension """
    if fname.name.endswith('.gpkg'):
        return 'GPKG'
    elif fname.name.endswith('.shp'):
        return 'ESRI Shapefile'
    elif fname.name.endswith('.gdb'):
        return 'OpenfileGDB'
    else:
        return None

def cleaning_directory(dir:Path):
    """ Cleaning the directory """

    logging.info("Cleaning the directory {}".format(dir))

    files_in_output = list(dir.iterdir())
    for item in files_in_output:
        if item.is_file():
            os.remove(item)

class Accept_Manager():
    """
    Structure to store the directories and names of the files.

    In the main directory, the following directories are mandatory/created:
        - INPUT : filled by the user - contains the input data
        - TEMP  : created by the script - contains the temporary data for the study area
        - OUTPUT: created by the script - contains the output data for each scenario of the study area

    The INPUT directory contains the following subdirectories:
        - DATABASE: contains the data for the **entire Walloon region**
            - Cadastre_Walloon.gpkg: the Cadastre Walloon file
            - GT_Resilence_dataRisques202010.gdb: the original gdb file from SPW - GT Resilience
            - PICC-vDIFF.gdb: the PICC Walloon file
            - CE_IGN_TOP10V: the IGN top10v shapefile
        - EPU_STATIONS_NEW:
            - AJOUT_PDET_EPU_DG03_STATIONS.shp: the EPU stations shapefile
        - STUDY_AREA: contains the study area shapefiles - one for each study area - e.g. Bassin_Vesdre.shp
        - CSVs: contains the CSV files
            - Intermediate.csv: contains the matrices data for the acceptability computation
            # - Ponderation.csv: contains the ponderation data for the acceptability computation
            - Vulnerability.csv: contains the mapping between layers and vulnerability levels - a code value is also provided
        - WATER_DEPTH: contains the water depth data for each scenario
            - Study_area1:
                - Scenario1
                - Scenario2
                -...
                - ScenarioN
            - Study_area2:
                - Scenario1
                - Scenario2
                -...
                - ScenarioN
            -...
            - Study_areaN:
                - Scenario1
                - Scenario2
                -...
                - ScenarioN

    The TEMP directory contains the following subdirectories:
        - DATABASES: contains the temporary data each study area
            - Study_area1:
                - database.gpkg: the clipped database
                - CaPa.gpkg: the clipped Cadastre Walloon file
                - PICC.gpkg: the clipped PICC Walloon file
                - database_final.gpkg: the final database
                - database_final_V.gpkg: the final database with vulnerability levels
                - CE_IGN_TOP10V.tiff: the IGN top10v raster file
                - Maske_River_extent.tiff: the river extent raster file from IGN
                - VULNERABILITY: the vulnerability data
                    - RASTERS:
                        - Code  : one file for each layer
                        - Vulne : one file for each layer
                    - Scenario1:

    """

    def __init__(self,
                 main_dir:str = 'Data',
                 Study_area:str = 'Bassin_Vesdre.shp',
                 scenario = None,
                 Original_gdb:str = 'GT_Resilence_dataRisques202010.gdb',
                 CaPa_Walloon:str = 'Cadastre_Walloon.gpkg',
                 PICC_Walloon:str = 'PICC_vDIFF.gdb',
                 CE_IGN_top10v:str = 'CE_IGN_TOP10V/CE_IGN_TOP10V.shp',
                                                         ) -> None:

        self.old_dir:Path    = Path(os.getcwd())

        self.main_dir:Path   = Path(main_dir)

        # If it is a string, concatenate it with the current directory
        if not self.main_dir.is_absolute():
            self.main_dir = Path(os.getcwd()) / self.main_dir

        self._study_area = Study_area
        if Study_area is not None:
            if not self._study_area.endswith('.shp'):
                self._study_area += '.shp'

        self._scenario = scenario
        self._original_gdb = Original_gdb
        self._capa_walloon = CaPa_Walloon
        self._picc_walloon = PICC_Walloon
        self._ce_ign_top10v = CE_IGN_top10v

        self.IN_DIR         = self.main_dir / "INPUT"
        self.IN_DATABASE    = self.IN_DIR / "DATABASE"
        self.IN_STUDY_AREA  = self.IN_DIR / "STUDY_AREA"
        self.IN_CSV         = self.IN_DIR / "CSVs"
        self.IN_WATER_DEPTH = self.IN_DIR / "WATER_DEPTH"

        self.ORIGINAL_GDB   = self.IN_DATABASE / self._original_gdb
        self.CAPA_WALLOON   = self.IN_DATABASE / self._capa_walloon
        self.PICC_WALLOON   = self.IN_DATABASE / self._picc_walloon
        self.CE_IGN_TOP10V  = self.IN_DATABASE / self._ce_ign_top10v

        self.VULNERABILITY_CSV = self.IN_CSV / "Vulnerability.csv"
        self.POINTS_CSV        = self.IN_CSV / "Intermediate.csv"
        # self.PONDERATION_CSV   = self.IN_CSV / "Ponderation.csv"

        self._CSVs = [self.VULNERABILITY_CSV, self.POINTS_CSV] #, self.PONDERATION_CSV]
        self._GPKGs= [self.CAPA_WALLOON, self.PICC_WALLOON]
        self._GDBs = [self.ORIGINAL_GDB]
        self._SHPs = [self.CE_IGN_TOP10V]
        self._ALLS = self._CSVs + self._GPKGs + self._GDBs + self._SHPs

        self.TMP_DIR            = self.main_dir / "TEMP"

        self.TMP_DATABASE       = self.TMP_DIR / "DATABASES"

        self.OUT_DIR        = self.main_dir / "OUTPUT"

        self.create_paths()
        self.create_paths_scenario()

    def create_paths(self):
        """ Create the paths for the directories and files """

        if self._study_area is not None:

            self.Study_area:Path = Path(self._study_area)

            self.TMP_STUDYAREA      = self.TMP_DATABASE / self.Study_area.stem
            self.TMP_VULN_DIR       = self.TMP_STUDYAREA / "VULNERABILITY"
            self.TMP_RASTERS        = self.TMP_VULN_DIR / "RASTERS"
            self.TMP_RASTERS_CODE   = self.TMP_RASTERS / "Code"
            self.TMP_RASTERS_VULNE  = self.TMP_RASTERS / "Vulne"

            self.OUT_STUDY_AREA = self.OUT_DIR / self.Study_area.stem

            self.SA          = self.IN_STUDY_AREA / self.Study_area
            self.SA_DATABASE = self.TMP_STUDYAREA / "database.gpkg"
            self.SA_CAPA     = self.TMP_STUDYAREA / "CaPa.gpkg"
            self.SA_PICC     = self.TMP_STUDYAREA / "PICC.gpkg"
            self.SA_FINAL    = self.TMP_STUDYAREA / "database_final.gpkg"
            self.SA_FINAL_V  = self.TMP_STUDYAREA / "database_final_V.gpkg"
            self.SA_MASKED_RIVER = self.TMP_STUDYAREA / "CE_IGN_TOP10V.tiff"

            self.SA_VULN    = self.TMP_VULN_DIR / "Vulnerability.tiff"
            self.SA_CODE    = self.TMP_VULN_DIR / "Vulnerability_Code.tiff"

        else:
            self.Study_area = None
            self._scenario = None

            self.TMP_STUDYAREA      = None
            self.TMP_VULN_DIR       = None
            self.TMP_RASTERS        = None
            self.TMP_RASTERS_CODE   = None
            self.TMP_RASTERS_VULNE  = None

            self.OUT_STUDY_AREA = None

            self.SA          = None
            self.SA_DATABASE = None
            self.SA_CAPA     = None
            self.SA_PICC     = None
            self.SA_FINAL    = None
            self.SA_FINAL_V  = None
            self.SA_MASKED_RIVER = None

            self.SA_VULN    = None
            self.SA_CODE    = None

        self.create_paths_scenario()

        self.check_inputs()
        self.check_temporary()
        self.check_outputs()

    def create_paths_scenario(self):

        if self._scenario is not None:

            self.scenario:str       = str(self._scenario)

            self.IN_SCEN_DIR        = self.IN_WATER_DEPTH / self.SA.stem / self.scenario
            self.IN_RM_BUILD_DIR    = self.IN_SCEN_DIR / "REMOVED_BUILDINGS"

            self.TMP_SCEN_DIR       = self.TMP_VULN_DIR / self.scenario
            self.TMP_RM_BUILD_DIR   = self.TMP_SCEN_DIR / "REMOVED_BUILDINGS"
            self.TMP_QFILES         = self.TMP_SCEN_DIR / "Q_FILES"

            self.TMP_VULN           = self.TMP_SCEN_DIR / "Vulnerability.tiff"
            self.TMP_CODE           = self.TMP_SCEN_DIR / "Vulnerability_Code.tiff"

            self.OUT_SCEN_DIR       = self.OUT_STUDY_AREA / self.scenario
            self.OUT_VULN           = self.OUT_SCEN_DIR / "Vulnerability.tiff"
            self.OUT_CODE           = self.OUT_SCEN_DIR / "Vulnerability_Code.tiff"
            self.OUT_MASKED_RIVER   = self.OUT_SCEN_DIR / "Masked_River_extent.tiff"
            self.OUT_ACCEPT         = self.OUT_SCEN_DIR / "Acceptability.tiff"
            self.OUT_ACCEPT_100M    = self.OUT_SCEN_DIR / "Acceptability_100m.tiff"

        else:
            self.scenario = None

            self.IN_SCEN_DIR       = None
            self.IN_RM_BUILD_DIR   = None

            self.TMP_SCEN_DIR      = None
            self.TMP_RM_BUILD_DIR  = None
            self.TMP_QFILES        = None

            self.TMP_VULN          = None
            self.TMP_CODE          = None

            self.OUT_SCEN_DIR      = None
            self.OUT_VULN          = None
            self.OUT_CODE          = None
            self.OUT_MASKED_RIVER  = None
            self.OUT_ACCEPT        = None
            self.OUT_ACCEPT_100M   = None

    @property
    def is_valid_inputs(self) -> bool:
        return self.check_inputs()

    @property
    def is_valid_study_area(self) -> bool:
        return self.SA.exists()

    @property
    def is_valid_vulnerability_csv(self) -> bool:
        return self.VULNERABILITY_CSV.exists()

    @property
    def is_valid_points_csv(self) -> bool:
        return self.POINTS_CSV.exists()

    @property
    def is_valid_ponderation_csv(self) -> bool:
        return self.PONDERATION_CSV.exists()

    def check_files(self) -> str:
        """ Check the files in the directories """

        files = ""
        for a in self._ALLS:
            if not a.exists():
                files += str(a) + "\n"

        return files

    def change_studyarea(self, Study_area:str = None) -> None:

        if Study_area is None:
            self._study_area = None
            self._scenario = None
        else:
            if Study_area in self.get_list_studyareas(with_suffix=True):
                self._study_area = Path(Study_area)
            else:
                logging.error("The study area does not exist in the study area directory")

        self.create_paths()

    def change_scenario(self, scenario:str) -> None:

        if scenario in self.get_list_scenarios():
            self._scenario = scenario
            self.create_paths_scenario()
            self.check_temporary()
            self.check_outputs()
        else:
            logging.error("The scenario does not exist in the water depth directory")

    def get_files_in_rm_buildings(self) -> list[Path]:
        return [Path(a) for a in glob.glob(str(self.IN_RM_BUILD_DIR / "*.shp"))]

    def get_files_in_rasters_vulne(self) -> list[Path]:
        return [Path(a) for a in glob.glob(str(self.TMP_RASTERS_VULNE / "*.tiff"))]

    def get_files_in_rasters_code(self) -> list[Path]:
        return [Path(a) for a in glob.glob(str(self.TMP_RASTERS_CODE / "*.tiff"))]

    def get_q_files(self) -> list[Path]:
        return [Path(a) for a in glob.glob(str(self.TMP_QFILES / "*.tif"))]

    def get_list_scenarios(self) -> list[str]:
        return [Path(a).stem for a in glob.glob(str(self.IN_WATER_DEPTH / self.SA.stem / "Scenario*"))]

    def get_list_studyareas(self, with_suffix:bool = False) -> list[str]:

        if with_suffix:
            return [Path(a).name for a in glob.glob(str(self.IN_STUDY_AREA / "*.shp"))]
        else:
            return [Path(a).stem for a in glob.glob(str(self.IN_STUDY_AREA / "*.shp"))]

    def get_sims_files_for_scenario(self) -> list[Path]:

        return [Path(a) for a in glob.glob(str(self.IN_SCEN_DIR / "*.tif"))]

    def get_sim_file_for_return_period(self, return_period:int) -> Path:

        sims = self.get_sims_files_for_scenario()

        if len(sims)==0:
            logging.error("No simulations found")
            return None

        if "_h.tif" in sims[0].name:
            for cursim in sims:
                if cursim.stem.find("_T{}_".format(return_period)) != -1:
                    return cursim
        else:
            for cursim in sims:
                if cursim.stem.find("T{}".format(return_period)) != -1:
                    return cursim

        return None

    def get_return_periods(self) -> list[int]:

        sims = self.get_sims_files_for_scenario()

        if len(sims)==0:
            logging.error("No simulations found")
            return None

        if "_h.tif" in sims[0].name:
            idx_T = [cursim.stem.find("_T") for cursim in sims]
            idx_h = [cursim.stem.find("_h.tif") for cursim in sims]
            sims = [int(cursim.stem[idx_T[i]+2:idx_h[i]-1]) for i, cursim in enumerate(sims)]
        else:
            idx_T = [cursim.stem.find("T") for cursim in sims]
            idx_h = [cursim.stem.find(".tif") for cursim in sims]
            sims = [int(cursim.stem[idx_T[i]+1:idx_h[i]]) for i, cursim in enumerate(sims)]

        return sorted(sims)

    def get_ponderations(self) -> pd.DataFrame:
        """ Get the ponderation data from available simulations """

        rt = self.get_return_periods()

        if len(rt)==0:
            logging.error("No simulations found")
            return None

        pond = []

        pond.append(1./float(rt[0]) + (1./float(rt[0]) - 1./float(rt[1]))/2.)
        for i in range(1, len(rt)-1):
            # pond.append((1./float(rt[i-1]) - 1./float(rt[i]))/2. + (1./float(rt[i]) - 1./float(rt[i+1]))/2.)
            pond.append((1./float(rt[i-1]) - 1./float(rt[i+1]))/2.)
        pond.append(1./float(rt[-1]) + (1./float(rt[-2]) - 1./float(rt[-1]))/2.)

        return pd.DataFrame(pond, columns=["Ponderation"], index=rt)

    def get_filepath_for_return_period(self, return_period:int) -> Path:

        return self.get_sim_file_for_return_period(return_period)

    def change_dir(self) -> None:
        os.chdir(self.main_dir)
        logging.info("Current directory: %s", os.getcwd())

    def restore_dir(self) -> None:
        os.chdir(self.old_dir)
        logging.info("Current directory: %s", os.getcwd())

    def check_inputs(self) -> bool:
        """
        Check if the input directories exist.

        Inputs can not be created automatically. The user must provide them.

        """

        err = False
        if not self.IN_DATABASE.exists():
            logging.error("INPUT : The database directory does not exist")
            err = True

        if not self.IN_STUDY_AREA.exists():
            logging.error("INPUT : The study area directory does not exist")
            err = True

        if not self.IN_CSV.exists():
            logging.error("INPUT : The CSV directory does not exist")
            err = True

        if not self.IN_WATER_DEPTH.exists():
            logging.error("INPUT : The water depth directory does not exist")
            err = True

        if self.Study_area is not None:
            if not self.SA.exists():
                logging.error("INPUT : The study area file does not exist")
                err = True

        if not self.ORIGINAL_GDB.exists():
            logging.error("INPUT : The original gdb file does not exist - Please pull it from the SPW-ARNE")
            err = True

        if not self.CAPA_WALLOON.exists():
            logging.error("INPUT : The Cadastre Walloon file does not exist - Please pull it from the SPW")
            err = True

        if not self.PICC_WALLOON.exists():
            logging.error("INPUT : The PICC Walloon file does not exist - Please pull it from the SPW website")
            err = True

        if not self.CE_IGN_TOP10V.exists():
            logging.error("INPUT : The CE IGN top10v file does not exist - Please pull it from the IGN")
            err = True

        if self.scenario is None:
            logging.warning("The scenario has not been defined")
        else:
            if not self.IN_SCEN_DIR.exists():
                logging.error("The scenario directory does not exist")
                err = True

        return not err

    def check_temporary(self) -> bool:
        """
        Check if the temporary directories exist.

        If not, create them.
        """

        self.TMP_DIR.mkdir(parents=True, exist_ok=True)
        self.TMP_DATABASE.mkdir(parents=True, exist_ok=True)

        if self.Study_area is not None:
            self.TMP_STUDYAREA.mkdir(parents=True, exist_ok=True)
            self.TMP_VULN_DIR.mkdir(parents=True, exist_ok=True)

        if self.scenario is not None:
            self.TMP_SCEN_DIR.mkdir(parents=True, exist_ok=True)
            self.TMP_RM_BUILD_DIR.mkdir(parents=True, exist_ok=True)
            self.TMP_QFILES.mkdir(parents=True, exist_ok=True)

        return True

    def check_outputs(self) -> bool:
        """
        Check if the output directories exist.

        If not, create them.
        """

        self.OUT_DIR.mkdir(parents=True, exist_ok=True)

        if self.Study_area is not None:
            self.OUT_STUDY_AREA.mkdir(parents=True, exist_ok=True)

        if self.scenario is not None:
            self.OUT_SCEN_DIR.mkdir(parents=True, exist_ok=True)

        return True

    def check_database_creation(self) -> bool:
        """
        Check if the database files have been created.
        """

        if not self.SA_DATABASE.exists():
            logging.error("The database file does not exist")
            return False

        if not self.SA_CAPA.exists():
            logging.error("The Cadastre Walloon file does not exist")
            return False

        if not self.SA_PICC.exists():
            logging.error("The PICC Walloon file does not exist")
            return False

        if not self.SA_FINAL.exists():
            logging.error("The final database file does not exist")
            return False

        if not self.SA_FINAL_V.exists():
            logging.error("The final database with vulnerability levels does not exist")
            return False

        return True

    def check_before_database_creation(self) -> bool:
        """ Check if the necessary files are present before the database creation"""

        if not self.is_valid_inputs:
            logging.error("Theere are missing input directories - Please check carefully the input directories and the logs")
            return False

        if not self.is_valid_study_area:
            logging.error("The study area file does not exist - Please create it")
            return False

        if not self.is_valid_vulnerability_csv:
            logging.error("The vulnerability CSV file does not exist - Please create it")
            return False

        return True

    def check_before_rasterize(self) -> bool:

        if not self.SA_FINAL_V.exists():
            logging.error("The final database with vulnerability levels does not exist")
            return False

        if not self.SA.exists():
            logging.error("The study area file does not exist")
            return False

        return True

    def check_before_vulnerability(self) -> bool:

        if not self.SA.exists():
            logging.error("The area of interest does not exist")
            return False

        if not self.IN_WATER_DEPTH.exists():
            logging.error("The water depth directory does not exist")
            return False

        if not self.IN_SCEN_DIR.exists():
            logging.error("The scenario directory does not exist in the water depth directory")
            return False

        if not self.SA_MASKED_RIVER.exists():
            logging.error("The IGN raster does not exist")
            return False

        return True

    def check_vuln_code_sa(self) -> bool:

        if not self.SA_VULN.exists():
            logging.error("The vulnerability raster file does not exist")
            return False

        if not self.SA_CODE.exists():
            logging.error("The vulnerability code raster file does not exist")
            return False

        return True

    def check_vuln_code_scenario(self) -> bool:

        if not self.TMP_VULN.exists():
            logging.error("The vulnerability raster file does not exist")
            return False

        if not self.TMP_CODE.exists():
            logging.error("The vulnerability code raster file does not exist")
            return False

        return True

# Step 1, Clip GDB data

def gpd_clip(layer:str,
             file_path:str,
             Study_Area:str,
             geopackage:str):
    """
    Clip the input data based on the selected bassin and saves it in a separate database

    :param layer: the layer name in the GDB file
    :param file_path: the path to the GDB file
    :param Study_Area: the path to the study area shapefile
    :param geopackage: the path to the geopackage file
    """

    layer = str(layer)
    file_path = str(file_path)
    Study_Area = str(Study_Area)
    geopackage = str(geopackage)

    St_Area = gpd.read_file(Study_Area)

    logging.info(layer)

    # The data is clipped during the reading
    # **It is more efficient than reading the entire data and then clipping it**
    df:gpd.GeoDataFrame = gpd.read_file(file_path, layer=layer, mask=St_Area)

    # Force Lambert72 -> EPSG:31370
    df.to_crs("EPSG:31370", inplace=True)

    df.to_file(geopackage, layer=layer, mode='w')

    return "Saved the clipped " +str(layer)+ " to GPKG"

def data_modification(input_database:str,
                      layer:str,
                      output_database:str,
                      picc:gpd.GeoDataFrame,
                      capa:gpd.GeoDataFrame ):
    """
    Apply the data modifications as described in the LEMA report

    FIXME : Add more doc in this docstring

    :param input_database: the path to the input database
    :param layer: the layer name in the database
    :param output_database: the path to the output database
    :param picc: the PICC Walloon file -- Preloaded
    :param capa: the Cadastre Walloon file -- Preloaded
    """

    df1:gpd.GeoDataFrame
    df2:gpd.GeoDataFrame

    LAYERS_WALOUS = ["WALOUS_2018_LB72_112",
                     "WALOUS_2018_LB72_31",
                     "WALOUS_2018_LB72_32",
                     "WALOUS_2018_LB72_331",
                     "WALOUS_2018_LB72_332",
                     "WALOUS_2018_LB72_333",
                     "WALOUS_2018_LB72_34"]

    input_database = str(input_database)
    layer = str(layer)
    output_database = str(output_database)

    df:gpd.GeoDataFrame = gpd.read_file(input_database, layer = layer)
    x1,y1 = df.shape
    a = df.geom_type.unique()
    #print(layers[i])
    x,=a.shape
    if x1>0:
        if layer in LAYERS_WALOUS: #Walous layers changed to PICC buidings
                #print("walous")

                assert picc.crs == df.crs, "CRS of PICC and input data do not match"

                df1= gpd.sjoin(picc, df, how="inner", predicate="intersects" )
                cols=df.columns
                cols = np.append(cols, "GEOREF_ID")
                cols = np.append(cols, "NATUR_CODE")
                df1=df1[cols]
                df1.to_file(output_database,layer=layer)
        elif layer =="BDREF_DGO3_PASH__SCHEMA_STATIONS_EPU": #Change BDREF based on AJOUT_PDET sent by Perrine
                #print("yes")
                df1 = gpd.read_file(os.getcwd()+"//INPUT//EPU_STATIONS_NEW//AJOUT_PDET_EPU_DG03_STATIONS.shp")

                assert df1.crs == df.crs, "CRS of AJOUT_PDET and input data do not match"

                df2 = gpd.sjoin(picc, df1, how="inner", predicate="intersects" )
                df2.to_file(output_database, layer=layer)
        elif layer =="INFRASIG_SOINS_SANTE__ETAB_AINES":

                assert capa.crs == df.crs, "CRS of CaPa and input data do not match"

                df1= gpd.sjoin(capa, df, how="inner", predicate="intersects" )
                cols=df.columns
                #print(cols)
                cols = np.append(cols, "CaPaKey")
                #print(cols)
                df1=df1[cols]
                df2=gpd.sjoin(picc, df1, how="inner", predicate="intersects" )
                cols = np.append(cols, "GEOREF_ID")
                cols = np.append(cols, "NATUR_CODE")
                #df2=df2[cols]
                #print(df2.columns)
                df2.to_file(output_database, layer=layer)

        elif a[0,]=="Point" and layer!="BDREF_DGO3_PASH__SCHEMA_STATIONS_EPU" and layer!="INFRASIG_SOINS_SANTE__ETAB_AINES":

                assert capa.crs == df.crs, "CRS of CaPa and input data do not match"
                assert picc.crs == df.crs, "CRS of PICC and input data do not match"

                df1= gpd.sjoin(capa, df, how="inner", predicate="intersects" )
                cols=df.columns
                #print(cols)
                cols = np.append(cols, "CaPaKey")
                #print(cols)
                df1=df1[cols]
                df2=gpd.sjoin(picc, df1, how="inner", predicate="intersects" )
                cols = np.append(cols, "GEOREF_ID")
                cols = np.append(cols, "NATUR_CODE")
                df2=df2[cols]
                #print(df2.columns)
                df2.to_file(output_database, layer=layer)
                #print(layers[i])
        elif layer =="Hab_2018_CABU":
                df1=df[df["NbsHabTOT"]>0]
                #print(df1.shape)
                df1.to_file(output_database, layer=layer)
        elif layer =="INFRASIG_ROUTE_RES_ROUTIER_TE_AXES":
                df1=df.buffer(6, cap_style=2)
                df1.to_file(output_database, layer=layer)
        else:
                df.to_file(output_database, layer=layer)
    else:
        logging.info("skipped" + str(layer) + "due to no polygon in the study area")

def vector_to_raster(layer:str,
                     vector_input:Path,
                     extent:Path,
                     attribute:str,
                     pixel_size:float):
    """
    Convert a vector layer to a raster tiff file

    :param layer: the layer name in the GDB file
    :param vector_input: the path to the vector file
    :param extent: the path to the extent file
    :param attribute: the attribute to rasterize
    :param pixel_size: the pixel size of the raster

    """

    old_dir = os.getcwd()

    layer = str(layer)
    vector_input = Path(vector_input)
    extent = Path(extent)
    attribute = str(attribute)
    pixel_size = float(pixel_size)

    OUT_DIR = vector_input.parent / "VULNERABILITY/RASTERS" / attribute
    OUT_NAME =  layer + ".tiff"

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if (OUT_DIR/OUT_NAME).exists():
        os.remove(OUT_DIR/OUT_NAME)

    os.chdir(OUT_DIR)

    NoData_value = 0

    extent_ds:ogr.DataSource = ogr.Open(str(extent))
    extent_layer = extent_ds.GetLayer()

    x_min, x_max, y_min, y_max = extent_layer.GetExtent()

    x_min = float(int(x_min))
    x_max = float(np.ceil(x_max))
    y_min = float(int(y_min))
    y_max = float(np.ceil(y_max))

    # Open the data sources and read the extents
    source_ds:ogr.DataSource = ogr.Open(str(vector_input))
    source_layer = source_ds.GetLayer(layer)

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds:gdal.Driver = gdal.GetDriverByName('GTiff').Create(str(OUT_NAME),
                                                     x_res, y_res, 1,
                                                     gdal.GDT_Byte,
                                                     options=["COMPRESS=LZW"])

    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(31370)
    target_ds.SetProjection(srs.ExportToWkt())

    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)

    # Rasterize the areas
    gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE="+attribute, "ALL_TOUCHED=TRUE"])
    target_ds = None

    os.chdir(old_dir)

def Comp_Vulnerability(dirsnames:Accept_Manager):
    """
    Compute the vulnerability for the Study Area

    This function **will not modify** the data by the removed buildings/scenarios.

    :param dirsnames: the Dirs_Names object from the calling function
    """

    rasters_vuln = dirsnames.get_files_in_rasters_vulne()
    rasters_code = dirsnames.get_files_in_rasters_code()

    logging.info("Number of files",len(rasters_vuln))

    ds:gdal.Dataset = gdal.Open(str(rasters_vuln[0]))
    ds1:gdal.Dataset = gdal.Open(str(rasters_code[0]))

    tmp_vuln = np.array(ds.GetRasterBand(1).ReadAsArray())
    tmp_code = np.array(ds1.GetRasterBand(1).ReadAsArray())

    x, y = tmp_vuln.shape

    logging.info("Computing Vulnerability")

    array_vuln = np.zeros((x, y), dtype=np.int8)
    array_code = np.zeros((x, y), dtype=np.int8)

    for i in tqdm(range(len(rasters_vuln))):
        logging.info("Computing layer {} / {}".format(i, len(rasters_vuln)))
        ds  = gdal.Open(str(rasters_vuln[i]))
        ds1 = gdal.Open(str(rasters_code[i]))

        tmp_vuln = ds.GetRasterBand(1).ReadAsArray()
        tmp_code = ds1.GetRasterBand(1).ReadAsArray()

        ij = np.where(tmp_vuln >= array_vuln)
        array_vuln[ij] = tmp_vuln.max()
        array_code[ij] = tmp_code.max()

    ij = np.where(array_vuln == 0)
    array_vuln[ij] = 1
    array_code[ij] = 1

    dst_filename= str(dirsnames.SA_VULN)
    y_pixels, x_pixels = array_vuln.shape  # number of pixels in x

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename, x_pixels, y_pixels, gdal.GDT_Byte, 1, options=["COMPRESS=LZW"])
    dataset.GetRasterBand(1).WriteArray(array_vuln.astype(np.int8))
    # follow code is adding GeoTranform and Projection
    geotrans = ds.GetGeoTransform()  # get GeoTranform from existed 'data0'
    proj = ds.GetProjection()  # you can get from a exsited tif or import
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None


    dst_filename= str(dirsnames.SA_CODE)
    y_pixels, x_pixels = array_code.shape  # number of pixels in x
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename, x_pixels, y_pixels, gdal.GDT_Byte, 1, options=["COMPRESS=LZW"])
    dataset.GetRasterBand(1).WriteArray(array_code.astype(np.int8))
    # follow code is adding GeoTranform and Projection
    geotrans = ds.GetGeoTransform()  # get GeoTranform from existed 'data0'
    proj = ds.GetProjection()  # you can get from a exsited tif or import
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None

    logging.info("Computed Vulnerability for the Study Area - Done")

def Comp_Vulnerability_Scen(dirsnames:Accept_Manager):
    """ Compute the vulnerability for the scenario

    This function **will modify** the data by the removed buildings/scenarios.

    FIXME: It could be interseting to permit the user to provide tiff files for the removed buildings and other scenarios.

    :param dirsnames: the Dirs_Names object from the calling function
    """

    array_vuln = gdal.Open(str(dirsnames.SA_VULN))
    geotrans = array_vuln.GetGeoTransform()  # get GeoTranform from existed 'data0'
    proj = array_vuln.GetProjection()  # you can get from a exsited tif or import

    array_vuln = np.array(array_vuln.GetRasterBand(1).ReadAsArray())

    array_code = gdal.Open(str(dirsnames.SA_CODE))
    array_code = np.array(array_code.GetRasterBand(1).ReadAsArray())

    Rbu = dirsnames.get_files_in_rm_buildings()

    if len(Rbu)>0:
        for curfile in Rbu:
            array_mod = gdal.Open(str(curfile))
            array_mod = np.array(array_mod.GetRasterBand(1).ReadAsArray())

            ij = np.where(array_mod == 1)
            array_vuln[ij] = 1
            array_code[ij] = 1

    dst_filename= str(dirsnames.TMP_VULN)
    y_pixels, x_pixels = array_vuln.shape  # number of pixels in x

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename, x_pixels, y_pixels, gdal.GDT_Byte, 1, options=["COMPRESS=LZW"])
    dataset.GetRasterBand(1).WriteArray(array_vuln.astype(np.int8))
    # follow code is adding GeoTranform and Projection
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None


    dst_filename= str(dirsnames.TMP_CODE)
    y_pixels, x_pixels = array_code.shape  # number of pixels in x
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename, x_pixels, y_pixels, gdal.GDT_Byte, 1, options=["COMPRESS=LZW"])
    dataset.GetRasterBand(1).WriteArray(array_code.astype(np.int8))
    # follow code is adding GeoTranform and Projection
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None

    logging.info("Computed Vulnerability for the scenario")

def match_vuln_modrec(inRas:Path, outRas:Path, MODREC:Path):
    """
    Clip the raster to the MODREC/simulation extent

    :param inRas: the input raster file
    :param outRas: the output raster file
    :param MODREC: the MODREC/simulation extent file

    """

    inRas  = str(inRas)
    outRas = str(outRas)
    MODREC = str(MODREC)

    data = gdal.Open(MODREC, gdalconst.GA_ReadOnly)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    ds = gdal.Open(inRas)
    ds = gdal.Translate(outRas, ds, projWin = [minx, maxy, maxx, miny])
    ds = None

def VulMod(dirsnames:Accept_Manager,
           model_h:np.ndarray,
           vulnerability:np.ndarray,
           interval:int,
           geo_projection):

    """
    Compute the local acceptability based on :
        - the vulnerability
        - the water depth
        - the matrices

    :param dirsnames: the Dirs_Names object from the calling function
    :param model_h: the water depth matrix
    :param vulnerability: the vulnerability matrix
    :param interval: the return period
    :param geo_projection: the geotransform and the projection - tuple extracted from another raster file

    """

    logging.info(interval)

    Qfile = pd.read_csv(dirsnames.POINTS_CSV)

    Qfile = Qfile[Qfile["Interval"]==interval]
    Qfile = Qfile.reset_index()

    x,y = vulnerability.shape
    accept = np.zeros((x,y))

    ij_1 = np.where(vulnerability == 1)
    ij_2 = np.where(vulnerability == 2)
    ij_3 = np.where(vulnerability == 3)
    ij_4 = np.where(vulnerability == 4)
    ij_5 = np.where(vulnerability == 5)

    bounds = [(0., 0.02), (0.02, 0.3), (0.3, 1), (1, 2.5), (2.5, 1000)]

    accept_1 = [Qfile["h-0"][4], Qfile["h-0.02"][4], Qfile["h-0.3"][4], Qfile["h-1"][4], Qfile["h-2.5"][4]]
    accept_2 = [Qfile["h-0"][3], Qfile["h-0.02"][3], Qfile["h-0.3"][3], Qfile["h-1"][3], Qfile["h-2.5"][3]]
    accept_3 = [Qfile["h-0"][2], Qfile["h-0.02"][2], Qfile["h-0.3"][2], Qfile["h-1"][2], Qfile["h-2.5"][2]]
    accept_4 = [Qfile["h-0"][1], Qfile["h-0.02"][1], Qfile["h-0.3"][1], Qfile["h-1"][1], Qfile["h-2.5"][1]]
    accept_5 = [Qfile["h-0"][0], Qfile["h-0.02"][0], Qfile["h-0.3"][0], Qfile["h-1"][0], Qfile["h-2.5"][0]]

    accept[:,:] = -99999
    for ij, loc_accept in zip([ij_1, ij_2, ij_3, ij_4, ij_5], [accept_1, accept_2, accept_3, accept_4, accept_5]):
        if len(ij[0]) > 0:
            for idx, (min_bound, max_bound) in enumerate(bounds):
                loc_ij = np.where((model_h[ij] > min_bound) & (model_h[ij] <= max_bound))
                accept[ij[0][loc_ij], ij[1][loc_ij]] = loc_accept[idx]

    #save raster
    dst_filename = str(dirsnames.TMP_QFILES / "Q{}.tif".format(interval))

    y_pixels, x_pixels = accept.shape  # number of pixels in x
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename, x_pixels, y_pixels, 1, gdal.GDT_Float32,  options=["COMPRESS=LZW"])
    dataset.GetRasterBand(1).WriteArray(accept.astype(np.float32))

    geotrans, proj = geo_projection
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None

def shp_to_raster(vector_fn:str, raster_fn:str, pixel_size:float = 1.):
    """
    Convert a vector layer to a raster tiff file

    :param vector_fn: the path to the vector file
    :param raster_fn: the path to the raster file
    :param pixel_size: the pixel size of the raster
    """

    # Force the input to be a string
    vector_fn = str(vector_fn)
    raster_fn = str(raster_fn)

    NoData_value = np.nan
    # Open the data sources and read the extents
    source_ds = ogr.Open(vector_fn)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()

    x_min = float(int(x_min))
    x_max = float(np.ceil(x_max))
    y_min = float(int(y_min))
    y_max = float(np.ceil(y_max))

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float64,
                                                     options=["COMPRESS=LZW"])

    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(31370)
    target_ds.SetProjection(srs.ExportToWkt())
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)
    # Rasterize the areas
    gdal.RasterizeLayer(target_ds, [1], source_layer,None, None, [1], options=["ALL_TOUCHED=TRUE"])
    target_ds = None
    vector_fn = raster_fn = None
