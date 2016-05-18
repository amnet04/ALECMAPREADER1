import numpy as np
import os
import cv2
import csv
import funcionesCV_recurrentes as cvr
import georef
from conf import RUTA_PLANTILLAS

with open(RUTA_PLANTILLAS+'/localidades.csv') as localidades:
    reader = csv.DictReader(localidades)
    LOCALIDADES = {}
    for row in reader:
        Localidad = dict(row)
        Localidad.pop('Idlocalidad')
        LOCALIDADES[row['Idlocalidad']] = Localidad


class localidad(object):
    '''
    Clase para manejar los departamentos
    '''
    def __init__(self, template, imagen):
        '''
        Inicia el objeto departamento cargando una imagen
        '''
        self.template = cv2.imread(template, 0)
        self.w, self.h = self.template.shape[::-1]
        self.ruta_archivo = template
        self.nombre_archivo = os.path.basename(template)
        self.id = os.path.basename(template)[:-4]
        self.nombre = LOCALIDADES[self.id]['Nombre']
        self.imagen = imagen
        self.supi, self.infd, self.roi = cvr.detectar(self.template,
                                                      imagen,
                                                      400000)

    def enmarcar(self):
        enmarcado = cv2.rectangle(self.imagen,
                                  self.supi,
                                  self.infd,
                                  (0, 0, 255),
                                  1)
        return(enmarcado)

    def escribir_nombre(self, imagen = [], supi = []):
        if supi == []:
            supi = self.supi
        if imagen == []:
            imagen = self.imagen
        nombre_en_mapa = cv2.putText(imagen,
                                     self.id,
                                     supi,
                                     cv2.FONT_HERSHEY_SIMPLEX,
                                     0.5,
                                     (0, 255, 0),
                                     1
                                     )
        return(nombre_en_mapa)


# un = localidad('Departamentos/Municipios/G_05_.jpg')
# un.escribir_nombre(cv2.imread('../jpgs/alec_v1_287.jpg'),'Pruebas/ghtil.jpg')
