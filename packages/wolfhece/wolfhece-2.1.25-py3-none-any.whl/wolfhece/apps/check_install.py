
def main():
    # Check if installation is complete
    ret = 'Checking installation\n---------------------\n\n'
    try:
        from osgeo import ogr, gdal
        ret += 'GDAL/OGR installed\n\n'
    except:
        ret += 'GDAL/OGR not installed\n Please install GDAL from https://github.com/cgohlke/geospatial-wheels/releases\n\n'

    try:
        from ..PyGui import MapManager
        ret += 'Wolfhece installed\n\n'
    except:
        ret += 'Wolfhece not installed\n Retry installation : pip install wolfhece or pip install wolfhece --upgrade\n\n'

    print(ret)

if __name__=='__main__':
    main()