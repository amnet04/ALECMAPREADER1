import numpy as np
import pandas
import cv2
import departamento
import georef
import funcionesCV_recurrentes as cvr
import textdetector


class mapa(object):
    '''
    Clase para manejar y manipular los mapas del alec
    '''
    def __init__(self, image):
        '''
        Inicia el objeto mapa cargando una imagen y comprueba que la imagen
        contenga departamentos para garantizar que si sea un mapa del ALEC
        '''
        self.mapa = cv2.imread(image)
        self.puntos = 'geo/ColombiALEC.jpg.points'
        self.template = cv2.imread('geo/ColombiALEC.jpg', 0)
        self.supi, self.infd, self.roi = cvr.detectar(self.template,
                                                      self.mapa,
                                                      99999999)

    def georeferenciar(self):
        georef.georef_area(self.roi, self.puntos, 'Pruebas/mapa.tif')

    def textos_sup_izquierdo(self):
        mapa = np.array(self.mapa)


map = mapa('../jpgs/alec_v4_044.jpg')
map.georeferenciar()
