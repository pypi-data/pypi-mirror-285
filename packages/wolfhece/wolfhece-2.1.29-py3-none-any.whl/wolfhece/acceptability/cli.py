"""
The command-line interface for the acceptability
"""
import argparse
from .acceptability import Base_data_creation, Vulnerability, Acceptability, Accept_Manager

def main():

    parser = argparse.ArgumentParser(
        description="A tool to obtain vulnerability and acceptability for regions in Walloon Region and particularly in Vesdre valley.")

    parser.add_argument("function",
                        nargs="?",
                        choices=['base_data_creation', 'vulnerability', 'acceptability', 'check'],
                        default='acceptability',
                        )
    args:argparse.Namespace
    args, sub_args = parser.parse_known_args()

    if args.function == "check":

        parser.add_argument("dir",
                            type=str,
                            help="Add path to the main directory with all folders. This sets the path of all outputs and inputs",
                            default='Data')
        parser.add_argument("GDB",
                            type=str,
                            help="Add the name of the main gdb like GT_Resilence_dataRisques202010.gdb",
                            default='GT_Resilence_dataRisques202010.gdb')
        parser.add_argument("CaPa",
                            type=str,
                            help="Add the name of the Cadaster geopackage, like Cadastre_Walloon.gpkg",
                            default='Cadastre_Walloon.gpkg')
        parser.add_argument("PICC",
                            type=str,
                            help="Add the name of the PICC gdb, like PICC_vDIFF.gdb",
                            default='PICC_vDIFF.gdb')
        parser.add_argument("CE",
                            type=str,
                            help="Add the name of the river extent from IGN, like CE_IGN_top10v.shp",
                            default='CE_IGN_TOP10V/CE_IGN_TOP10V.shp')

        parser.add_argument("scenario",
                            type=str,
                            help="scenario name",
                            default='Scenario1')
        parser.add_argument("study_area",
                            type=str,
                            help="Add the area of interest, like Theux, Chaufontaine, Eupen, etc.",
                            default='Bassin_Vesdre')

        args = parser.parse_args()

        manager = Accept_Manager(main_dir=args.dir,
                                 Study_area=args.study_area,
                                 scenario=args.scenario,
                                 Original_gdb=args.GDB,
                                 CaPa_Walloon=args.CaPa,
                                 PICC_Walloon=args.PICC,
                                 CE_IGN_top10v=args.CE)


    elif args.function == "base_data_creation":

        parser.add_argument("dir",
                            type=str,
                            help="Add path to the main directory with all folders. This sets the path of all outputs and inputs",
                            default='Data')
        parser.add_argument("GDB",
                            type=str,
                            help="Add the name of the main gdb like GT_Resilence_dataRisques202010.gdb",
                            default='GT_Resilence_dataRisques202010.gdb')
        parser.add_argument("study_area",
                            type=str,
                            help="Add the name of the study area shapefile, Vesdre Valley like Bassin_SA.shp",
                            default='Bassin_Vesdre.shp')
        parser.add_argument("CaPa",
                            type=str,
                            help="Add the name of the Cadaster geopackage, like Cadastre_Walloon.gpkg",
                            default='Cadastre_Walloon.gpkg')
        parser.add_argument("PICC",
                            type=str,
                            help="Add the name of the PICC gdb, like PICC_vDIFF.gdb",
                            default='PICC_vDIFF.gdb')
        parser.add_argument("CE",
                            type=str,
                            help="Add the name of the river extent from IGN, like CE_IGN_top10v.shp",
                            default='CE_IGN_TOP10V/CE_IGN_TOP10V.shp')
        parser.add_argument("resolution",
                            type=float,
                            help="Add the resolution of water_depth files. If water_depth files have resolution 1 meter, you can put it as 1",
                            default=1.)
        parser.add_argument("number_procs",
                            type=int,
                            help="Add the number of processors to use",
                            default=1)
        args = parser.parse_args()

        Base_data_creation(main_dir=args.dir,
                            Original_gdb=args.GDB,
                            Study_area=args.study_area,
                            CaPa_Walloon=args.CaPa,
                            PICC_Walloon=args.PICC,
                            CE_IGN_top10v=args.CE,
                            resolution=args.resolution,
                            number_procs=args.number_procs)

    elif args.function == "vulnerability":

        parser.add_argument("dir",
                            type=str,
                            help="Add path to the main directory with all folders.This sets the path of all outputs and inputs",
                            default='Data')
        parser.add_argument("scenario",
                            type=str,
                            help="scenario name",
                            default='Scenario1')
        parser.add_argument("study_area",
                            type=str,
                            help="Add the area of interest, like Theux, Chaufontaine, Eupen, etc.",
                            default='Bassin_Vesdre')
        args = parser.parse_args()

        Vulnerability(main_dir=args.dir,
                      scenario=args.scenario,
                      Study_area=args.study_area)

    elif args.function == "acceptability":

        parser.add_argument("dir",
                            type=str,
                            help="Add path to the main directory with all folders.This sets the path of all outputs and inputs",
                            default='Data')
        parser.add_argument("study_area",
                            type=str,
                            help="Add the name of area, like Theux, Chaudfontaine, Eupen, etc.",
                            default='Bassin_Vesdre')
        parser.add_argument("scenario",
                            type=str,
                            help="Scenario number",
                            default='Scenario1')

        args = parser.parse_args()

        Acceptability(main_dir=args.dir,
                      scenario=args.scenario,
                      Study_area=args.study_area)

if __name__ == '__main__':
    main()
