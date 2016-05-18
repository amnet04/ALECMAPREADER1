import numpy as np
import os
import cv2
import funcionesCV_recurrentes as cvr
import georef
import localidad
from operator import add
import signos_convencionales as sc
from conf import RUTA_DEPARTAMENTOS, RUTA_PLANTILLAS, RUTA_LOCALIDADES, RUTA_SEXTANTES


class departamento(object):
    '''
    Clase para manejar los departamentos
    '''

    def __init__(self, template, mapa):
        '''
        Inicia el objeto departamento cargando una imagen
        '''
        self.mapa = mapa
        self.template = cv2.imread(template, 0)
        self.w, self.h = self.template.shape[::-1]
        self.ruta_archivo = template
        self.nombre_archivo = os.path.basename(template)
        self.id = os.path.basename(template)[:-4]
        self.puntos = template+".points"
        self.localidades = {k:v
                            for k,v in localidad.LOCALIDADES.items()
                            if (k[:2]==self.id and k[-1]=='_')
                            }
        for k,v in self.localidades.items():
            v['Plantilla'] = RUTA_LOCALIDADES+'/'+k+'.jpg'
        self.supi, self.infd, self.roi = cvr.detectar(self.template,
                                                      self.mapa,
                                                      99999999)
        self.sextantes = [x for x in os.listdir("Plantillas/Sextantes")
                         if x[:2]==self.id]

    def enmarcar(self, mapa, archivo):
        enmarcado = cv2.rectangle(mapa, self.supi, self.infd, (0, 0, 255), 2)
        cv2.imwrite(archivo, enmarcado)

    def georeferenciar(self):
        georef.georef_area(self.roi, self.puntos, 'Pruebas/'+self.id+'.tif')

    def detectar_localidades(self):
        for sextante in self.sextantes:
            id_sextante = sextante[2]
            template = cv2.imread(RUTA_SEXTANTES+'/'+sextante, 0)
            sup, inf, sroi = cvr.detectar(template,self.roi,999999)
            localidades = {k:v for k,v in self.localidades.items()
                           if ( k[2]==id_sextante
                               or (k[2:4]=='0'+id_sextante))
                          }
            for id, datos in localidades.items():
                if os.path.isfile(datos['Plantilla']):
                    img_loc = localidad.localidad(datos['Plantilla'],sroi)
                    new_sup = tuple(map(add, sup, img_loc.supi))
                    new_sup = tuple(map(add, new_sup, self.supi))
                    self.localidades[id]['supi']=new_sup
                else:
                    print('No existe plantilla para {0}'.format(id))

    def area_variantes(self):
        img = np.array(self.mapa)
        self.detectar_localidades()
        for id, datos in self.localidades.items():
            supi = (datos['supi'][0]-200,datos['supi'][1]+20)
            infd = (supi[0]+426,supi[1]+100)
            roiv = self.mapa[supi[1]:infd[1],supi[0]:infd[0]]
            roiv = sc.signos_convencionales(roiv)
            #cvr.ver_imagen(roiv, id)
            areas = cvr.detectar_area_contornos(roiv, 200, 255, (1,1), 1, 18,18)
            for area in areas:
                area_supi = tuple(map(add, area[0],supi))
                area_infd = tuple(map(add, area[1],supi))
                left = area_supi[0] < (supi[0]+infd[0])/2
                rigth = area_infd[0] > (supi[0]+infd[0])/2
                center = left and rigth
                top = area_supi[1] - 20 <  supi[1]
                no_marco = (area_infd[0] - area_supi[0]) < 424
                no_marco = no_marco and (area_infd[1] - area_supi[1]  < 80)
                color = (255,0,255)
                elegido = center and top and no_marco
                if elegido:
                    cv2.rectangle(img, area_supi, area_infd,color,2)
                    cv2.putText(img,
                                datos['localidadalec'],
                                area_supi,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,
                                (0, 0, 0),
                                2
                                )
        cv2.imwrite('Pruebas/col2.jpg',img)


mapa = departamento(RUTA_DEPARTAMENTOS+'/Bo.jpg',cv2.imread('../jpgs/alec_v4_044.jpg'))
mapa.area_variantes()
