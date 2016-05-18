import numpy as np
import gdal
import cv2
import osr
import cv2
import os


def georef_area(imagen, puntos, outtif):
    #imagen = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)
    if os.path.isfile(puntos):
        coordenadas = np.genfromtxt(puntos,
                                    delimiter=',',
                                    skip_header=1
                                    )
        lon_max = coordenadas[:, 0].max()
        lon_min = coordenadas[:, 0].min()
        lat_max = coordenadas[:, 1].max()
        lat_min = coordenadas[:, 1].min()
        rows, cols, _ = imagen.shape
        b,g,r = cv2.split(imagen)
        xres = (lon_max-lon_min)/float(cols)
        yres = (lat_max-lat_min)/float(rows)
        geotransform = (lon_min, xres, 0, lat_max, 0, -yres)
        output_raster = gdal.GetDriverByName('GTiff').Create(
                        outtif,
                        cols,
                        rows,
                        3,
                        gdal.GDT_Byte
                        )
        output_raster.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        output_raster.SetProjection(srs.ExportToWkt())
        output_raster.GetRasterBand(1).WriteArray(r)
        output_raster.GetRasterBand(2).WriteArray(g)
        output_raster.GetRasterBand(3).WriteArray(b)


def georef_puntos(imagen, puntos, outtif):
    #imagen = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)
    if os.path.isfile(puntos):
        coordenadas = np.genfromtxt(puntos,
                                    delimiter=',',
                                    skip_header=1
                                    )
        lon_max = coordenadas[:, 0].max()
        lon_min = coordenadas[:, 0].min()
        lat_max = coordenadas[:, 1].max()
        lat_min = coordenadas[:, 1].min()
        rows, cols = imagen.shape
        xres = (lon_max-lon_min)/float(cols)
        yres = (lat_max-lat_min)/float(rows)
        geotransform = (lon_min, xres, 0, lat_max, 0, -yres)
        output_raster = gdal.GetDriverByName('GTiff').Create(
                        outtif,
                        cols,
                        rows,
                        1,
                        gdal.GDT_Float32
                        )
        output_raster.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        output_raster.SetProjection(srs.ExportToWkt())
        output_raster.GetRasterBand(1).WriteArray(imagen[0])
        output_raster.GetRasterBand(2).WriteArray(imagen[1])
        output_raster.GetRasterBand(3).WriteArray(imagen[2])
