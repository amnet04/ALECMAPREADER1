import numpy as np
import re
import os
import cv2
import csv
import funcionesCV_recurrentes as cvr
import georef
from conf import RUTA_PLANTILLAS

numeros = re.compile('\D')
espacios = re.compile('\s')

with open(RUTA_PLANTILLAS+'/localidades.csv') as localidades:
    reader = csv.DictReader(localidades)
    err_msg = ', no es un código válido. '
    err_no0 = 'El tercer caractér no corresponde con el patrón.'
    err_spa = 'el código contiene espacios.'
    err_tail = ' Lo corregiré automáticamente pero es conveniente que lo'
    err_tail = err_tail + ' verifique en el archivo "localidades.cvs"'
    LOCALIDADES = {}
    for row in reader:
        Localidad = dict(row)
        Localidad.pop('Idlocalidad')
        Localidad.pop('Comentarios')
        err = '{0}'.format(row['Idlocalidad']) + err_msg
        if espacios.match(row['Idlocalidad']):
            err = err + err_spa + err_tail
            print(err)
            row['Idlocalidad'] = ''.join(row['Idlocalidad'].split())
        if numeros.match(row['Idlocalidad'][2]):
            err = err + err_no0 + err_tail
            print(err)
            id_as_list = list(row['Idlocalidad'])
            id_as_list[2] = '0'
            row['Idlocalidad'] = ''.join(id_as_list)
            print(row['Idlocalidad'])
        LOCALIDADES[row['Idlocalidad']] = Localidad


class localidad(object):
    '''
    Clase para manejar los departamentos
    '''
    def __init__(self, template, imagen, id):
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
        if cvr.detectar(self.template, imagen, 400000)[0] is not None:
            self.supi, self.infd, self.roi = cvr.detectar(self.template,
                                                          imagen,
                                                          400000)
        else:
            self.supi, self.infd, self.roi = (None, None, None)
            print('No se encontraron coincidencias para {0}'.format(id))

    def enmarcar(self, color):
        if (self.supi is not None and
            self.infd is not None and
            self.roi is not None):
            enmarcado = cv2.rectangle(self.imagen,
                                      self.supi,
                                      self.infd,
                                      color,
                                      1)
            return(enmarcado)

    def escribir_nombre(self, color, imagen=[], supi=[]):
        if supi == []:
            supi = self.supi
        if imagen == []:
            imagen = self.imagen
        if supi is not None:
            nombre_en_mapa = cv2.putText(imagen,
                                         self.id,
                                         supi,
                                         cv2.FONT_HERSHEY_SIMPLEX,
                                         0.5,
                                         color,
                                         1
                                         )
            return(nombre_en_mapa)
