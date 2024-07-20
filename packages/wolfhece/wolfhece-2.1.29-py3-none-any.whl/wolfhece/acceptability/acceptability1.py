# import pandas as pd
# import Parallels
# import os
# import func
# from osgeo import gdal
# import fiona
# import glob
# import numpy as np
# import geopandas as gpd

# def Vulnerability2(main_dir, resolution):
#     os.chdir(main_dir)
#     print("STEP2: convert vectors to raster based on their vulnerability values")
#     layer = fiona.listlayers(os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg")
#     database = os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg"
#     extent = os.getcwd()+"//INPUT//STUDY_AREA//Bassin_SA.shp"
#     pixel=resolution
#     attribute = "Vulne"
#     parallel_v2r(layer, database, extent, attribute, pixel)
#     attribute = "Code"
#     parallel_v2r(layer, database, extent, attribute, pixel) 

# def base_data_creation(main_dir, Original_gdb, Study_Area, CaPa_Walloon, PICC_Walloon):
#     #Change the directory
#     os.chdir(main_dir)
#     # Step 1, Clip GDB data
#     file_path=os.getcwd()+"//INPUT//DATABASE//"+str(Original_gdb)
#     Study_Area=os.getcwd()+"//INPUT//STUDY_AREA//"+str(Study_Area)
#     data_type="OpenfileGDB"
#     number_procs = 8
#     output_gpkg = os.getcwd()+"//TEMP//DATABASES//SA_database.gpkg"
#     paths = pd.read_csv(os.getcwd()+"//INPUT//CSVs//Vulnerability_matrix_new1.csv", sep=",", encoding='latin-1')
#     paths["subfolder"]=None
#     x, y = paths.shape
#     for i in range(x):
#        a=paths["Path"][i].split('/')
#        paths["subfolder"][i]=a[1]
#     layers = paths["subfolder"].to_list()
#     Parallels.parallel_gpd_clip(layers, file_path, Study_Area, output_gpkg, data_type, number_procs)
#     # Step 2, Clip Cadaster data
#     file_path=os.getcwd()+"//INPUT//DATABASE//"+str(CaPa_Walloon)
#     data_type='GPKG'
#     number_procs = 8
#     output_gpkg = os.getcwd()+"//TEMP//DATABASES//SA_CaPa.gpkg"
#     layers = ["CaBu", "CaPa"]
#     Parallels.parallel_gpd_clip(layers, file_path, Study_Area, output_gpkg, data_type, number_procs)
#     # Step 3, Clip PICC data
#     file_path=os.getcwd()+"//INPUT//DATABASE//"+str(PICC_Walloon)
#     data_type='OpenfileGDB'
#     number_procs = 8
#     output_gpkg = os.getcwd()+"//TEMP//DATABASES//SA_PICC.gpkg"
#     layers=['CONSTR_BATIEMPRISE']
#     Parallels.parallel_gpd_clip(layers, file_path, Study_Area, output_gpkg, data_type, number_procs)
# 	#Step 4, create database based on changes in report
#     input_database=os.getcwd()+"//TEMP//DATABASES//SA_database.gpkg"
#     layers = fiona.listlayers(os.getcwd()+"//TEMP//DATABASES//SA_database.gpkg")
#     walous = ["WALOUS_2018_LB72_112", "WALOUS_2018_LB72_31", "WALOUS_2018_LB72_32", "WALOUS_2018_LB72_331",
#             "WALOUS_2018_LB72_332", "WALOUS_2018_LB72_333", "WALOUS_2018_LB72_34"]
#     data_type="GPKG"
#     PICC = gpd.read_file(os.getcwd()+"//TEMP//DATABASES//SA_PICC.gpkg", driver="GPKG", layer = 'CONSTR_BATIEMPRISE')
#     CaPa = gpd.read_file(os.getcwd()+"//TEMP//DATABASES//SA_CaPa.gpkg", driver='GPKG', layer= 'CaPa')
#     output_database = os.getcwd()+"//TEMP//DATABASES//SA_database_final.gpkg"
#     for i in range(len(layers)):
#         print(i)
#         func.data_modification(input_database, data_type, layers[i], walous, output_database, PICC, CaPa)
#     func.shp_to_raster(os.getcwd()+"//INPUT//DATABASE//CE_IGN_TOP10V/CE_IGN_TOP10V.shp", os.getcwd()+"//TEMP//DATABASES//CE_IGN_TOP10V.tiff")
#     #Pre-processing for Vulnerability
#     layers = fiona.listlayers(os.getcwd()+"//TEMP//DATABASES//SA_database_final.gpkg")
#     paths = pd.read_csv(os.getcwd()+"//INPUT//CSVs//Vulnerability_matrix_new1.csv", sep=",", encoding='latin-1')
#     paths[["name", "name1"]] = paths["Path"].str.split("/", expand=True)
#     names = paths["name1"].to_list()
#     list_shp = list(set(names).difference(layers))
#     print("Excluded layers due to no features in shapefiles:")
#     print(list_shp)
#     paths1 =paths[~paths["name1"].isin(list_shp)]
#     a,b = paths1.shape
#     print("STEP1: Saving the database for Vulnerability with attributes Vulne and Code")
#     for i in range(a):
#            shp = gpd.read_file(os.getcwd()+"//TEMP//DATABASES//SA_database_final.gpkg",
#                                             driver='GPKG',
#                                             layer=paths1["name1"][i])
#            x, y = shp.shape
#            if x > 0:
#              shp["Path"] = paths["name1"][i]
#              shp["Vulne"] = paths["Vulne"][i]
#              shp["Code"] = paths["Code"][i]
#              shp = shp[["geometry", "Path", "Vulne","Code"]]
#              shp.to_file(os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg",
#                                         driver='GPKG',
#                                         layer=paths["name1"][i])
#     print("STEP2: convert vectors to raster based on their vulnerability values")
#     layer = fiona.listlayers(os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg")
#     database = os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg"
#     extent = os.getcwd()+"//INPUT//STUDY_AREA//Bassin_SA.shp"
#     attribute = "Vulne"
#     Parallels.parallel_v2r(layer, database, extent, attribute)
#     attribute = "Code"
#     Parallels.parallel_v2r(layer, database, extent, attribute)    
# #
# def Vulnerability(main_dir,sc,AOI):
#     print("Starting VULNERABILITY computations at 1 m resolution")
#     os.chdir(main_dir)
# #    layers = fiona.listlayers(os.getcwd()+"//TEMP//DATABASES//SA_database_final.gpkg")
# #    # load the paths from csv with Vulne values
# #    paths = pd.read_csv(os.getcwd()+"//INPUT//CSVs//Vulnerability_matrix_new1.csv", sep=",", encoding='latin-1')
# #    paths[["name", "name1"]] = paths["Path"].str.split("/", expand=True)
# #    #names = paths["name1"].to_list()
# #    # loop for loading all shapefiles with the names matching with vulnerability matrix
# #    names = paths["name1"].to_list()
# #    list_shp = list(set(names).difference(layers))
# #    print("Excluded layers due to no features in shapefiles:")
# #    print(list_shp)
# #    paths1 =paths[~paths["name1"].isin(list_shp)]
# #    a,b = paths1.shape
# #    print("STEP1: Saving the database for Vulnerability with attributes Vulne and Code")
# #    for i in range(a):
# #           shp = gpd.read_file(os.getcwd()+"//TEMP//DATABASES//SA_database_final.gpkg",
# #                                            driver='GPKG',
# #                                            layer=paths1["name1"][i])
# #           x, y = shp.shape
# #           if x > 0:
# #             shp["Path"] = paths["name1"][i]
# #             shp["Vulne"] = paths["Vulne"][i]
# #             shp["Code"] = paths["Code"][i]
# #             shp = shp[["geometry", "Path", "Vulne","Code"]]
# #             shp.to_file(os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg",
# #                                        driver='GPKG',
# #                                        layer=paths["name1"][i])
# #    print("STEP2: convert vectors to raster based on their vulnerability values")
# #    layer = fiona.listlayers(os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg")
# #    database = os.getcwd()+"//TEMP//DATABASES//SA_database_final_V.gpkg"
# #    extent = os.getcwd()+"//INPUT//STUDY_AREA//Bassin_SA.shp"
# #    attribute = "Vulne"
# #    Parallels.parallel_v2r(layer, database, extent, attribute)
# #    attribute = "Code"
# #    Parallels.parallel_v2r(layer, database, extent, attribute)    
#     bu = glob.glob(os.getcwd()+"//INPUT//REMOVED_BUILDINGS//Scenario"+str(sc)+"//*.shp")
#     if len(bu)>0:
#          bu_PICC = os.getcwd()+"//INPUT//REMOVED_BUILDINGS//Scenario"+str(sc)+"//Removed_Buildings_PICC.shp" 
#          bu_CaBu = os.getcwd()+"//INPUT//REMOVED_BUILDINGS//Scenario"+str(sc)+"//Removed_Buildings_CaBu.shp"
#          func.shp_to_raster(bu_PICC, os.getcwd()+"//TEMP//REMOVED_BUILDINGS//Scenario"+str(sc)+"//Removed_Buildings_PICC.tiff")
#          func.shp_to_raster(bu_CaBu, os.getcwd()+"//TEMP//REMOVED_BUILDINGS//Scenario"+str(sc)+"//Removed_Buildings_CaBu.tiff")
#     else:
#          print("No buildings were removed in water depth analysis OR No shapefiles in INPUT/REMOVED_BUILDINGS/Scenario"+str(sc))
#     print("STEP3: Generate Vulnerability rasters 1m")
#     attribute="Vulne"
#     Output_tiff = os.getcwd()+"//TEMP//VULNERABILITY//Scenario"+str(sc)+"//Vulnerability_SA.tiff"
#     func.Comp_Vulnerability(Output_tiff, attribute,sc)
#     attribute = "Code"
#     Output_tiff = os.getcwd()+"//TEMP//VULNERABILITY//Scenario"+str(sc)+"//Vulnerability_Code_SA.tiff"
#     print(Output_tiff)
#     func.Comp_Vulnerability(Output_tiff, attribute,sc)
#     print("STEP4: Save Vulnerability files for the area of interest")
#     func.match_vuln_modrec(os.getcwd() + "//TEMP//DATABASES//CE_IGN_TOP10V/CE_IGN_TOP10V.tiff",
#                            os.getcwd() + "//TEMP//Masked/River_extent.tiff", os.getcwd()+"//INPUT//WATER_DEPTH//Scenario"+str(sc)+"//T1000.tif")
#     func.match_vuln_modrec(os.getcwd() + "//TEMP//VULNERABILITY//Scenario"+str(sc)+"//Vulnerability_SA.tiff",
#                            os.getcwd() + "//OUTPUT//VULNERABILITY//Scenario"+str(sc)+"Vulnerability_"+str(AOI)+".tiff", os.getcwd()+"//INPUT//WATER_DEPTH//Scenario"+str(sc)+"//T1000.tif")
#     func.match_vuln_modrec(os.getcwd() + "//TEMP//VULNERABILITY//Scenario"+str(sc)+"//Vulnerability_Code_SA.tiff",
#                            os.getcwd() + "//OUTPUT//VULNERABILITY//Scenario"+str(sc)+"//Vulnerability_Code"+str(AOI)+".tiff", os.getcwd()+"//INPUT//WATER_DEPTH//Scenario"+str(sc)+"//T1000.tif")

# def Vulnerability2(main_dir, attribute):
#     os.chdir(main_dir)
#     Output_tiff = os.getcwd()+"//OUTPUT//VULNERABILITY//Vulnerability_Code.tiff"
#     func.Comp_Vulnerability(Output_tiff, attribute)
#     #func.match_vuln_modrec(os.getcwd() + "//TEMP//DATABASES//CE_IGN_TOP10V/CE_IGN_TOP10V.tiff",
#     #                       os.getcwd() + "//TEMP//Masked/River_extent.tiff")
#     #func.match_vuln_modrec(os.getcwd() + "//OUTPUT//VULNERABILITY//Vulnerability.tiff",
#     #                       os.getcwd() + "//TEMP//Masked/Vulnerability_extent.tiff")
#     #func.match_vuln_modrec(os.getcwd() + "//OUTPUT//VULNERABILITY//Vulnerability_Code.tiff",
#     #                       os.getcwd() + "//TEMP//Masked/Vulnerability_Code_extent.tiff")

# def acceptability(main_dir,area_of_interest):
#     os.chdir(main_dir)
#     Vulne = gdal.Open(os.getcwd() + "//TEMP//Masked/Vulnerability_extent.tiff")
#     Vulne = Vulne.GetRasterBand(1).ReadAsArray()
#     riv = gdal.Open(os.getcwd() + "//TEMP//Masked/River_extent.tiff")
#     riv = riv.GetRasterBand(1).ReadAsArray()
#     list1 = ["2", "5", "15", "25", "50", "100", "1000"]
#     # sample for saving the raster
#     # mod1 = rasterio.open("G://00_GT_Resilience//Simulations_Theux//Scen_"+str(scen)+"//Theux_1.3K_sim_T1000_h.tif")
#     Qfile = pd.read_csv(os.getcwd() + "//INPUT//CSVs//Book2.csv")
#     # run vul-mod for 4 return intervals
#     x = glob.glob(os.getcwd() + "//INPUT//WATER_DEPTH//*.tiff")
#     Area_interest = area_of_interest
#     for i in range(len(list1)):
#         mod = gdal.Open(x[i])
#         mod = mod.GetRasterBand(1).ReadAsArray()
#         mod[mod == 0] = np.nan
#         mod[riv == 1] = np.nan
#         func.VulMod(Qfile, mod, Vulne, list1[i], Area_interest)
#     ax=locals()
#     list1=["2","5", "15","25", "50", "100", "1000"]
#     qs= glob.glob(os.getcwd()+"//TEMP//Q_files//*.tiff")
#     for i in range(len(list1)):
#         ax["vm"+str(i)] = gdal.Open(qs[i])
#         ax["vm"+str(i)]  = ax["vm"+str(i)].GetRasterBand(1).ReadAsArray()
#     #Remove nans from other Q files for final acceptability computation
#     for i in range(len(list1)-1):
#         ax["vm"+str(i)+str(1)] = np.nan_to_num(ax["vm"+str(i)], nan=0)
#         ax["vm"+str(i)+str(1)][np.isnan(ax["vm"+str(len(list1))])] = np.nan
#     pond = pd.read_csv(os.getcwd()+"//INPUT//CSVs//Ponderation.csv")
#     comb = vm6*float(pond.iloc[6,1]) + vm51*float(pond.iloc[5,1]) + vm41*float(pond.iloc[4,1]) + vm31*float(pond.iloc[3,1]) + vm21*float(pond.iloc[2,1]) + vm11*float(pond.iloc[1,1]) +vm01*float(pond.iloc[0,1])
#     dst_filename = os.getcwd()+"//OUTPUT//ACCEPTABILITY//Acceptability"+str(area_of_interest)+".tiff"
#     y_pixels, x_pixels = comb.shape  # number of pixels in x
#     driver = gdal.GetDriverByName('GTiff')
#     dataset = driver.Create(dst_filename, x_pixels, y_pixels, gdal.GDT_Float32, 1, options=["COMPRESS=LZW"])
#     dataset.GetRasterBand(1).WriteArray(comb.astype(np.float32))
#     input_raster = os.getcwd()+"//OUTPUT//ACCEPTABILITY//Acceptability"+str(area_of_interest)+".tiff"
#     output_raster = os.getcwd()+"//OUTPUT//ACCEPTABILITY//Acceptability"+str(area_of_interest)+"_100m.tiff"
#     Agg = gdal.Warp(output_raster, input_raster, xRes=100, yRes=100, resampleAlg='Average')
#     Agg = None
