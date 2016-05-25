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
        self.sextantes = [x for x in os.listdir("Plantillas/Sextantes")
                          if x[:2] == self.id]
        self.localidades = {k: v for k, v in localidad.LOCALIDADES.items()
                            if (k[:2] == self.id and k[-1] == '_')
                            }
        for k, v in self.localidades.items():
                        v['Plantilla'] = RUTA_LOCALIDADES+'/'+k+'.jpg'
        thresh = 100000000
        while cvr.detectar(self.template, self.mapa, thresh)[0] is None:
            thresh = cvr.detectar(self.template, self.mapa, thresh)[1]
            print('''Departamento no identificado en el mapa, intentando con un
            menor valor de match''')
        if cvr.detectar(self.template, self.mapa, thresh) is not None:
                self.supi, self.infd, self.roi = cvr.detectar(self.template,
                                                          self.mapa,
                                                          thresh)




    def enmarcar(self, img = None):
        if img is None:
            img = self.mapa
        cv2.rectangle(img, self.supi, self.infd, (222, 0, 255), 2)

    def georeferenciar(self):
        georef.georef_area(self.roi, self.puntos, 'Pruebas/'+self.id+'.tif')

    def detectar_localidades(self):

        for sextante in self.sextantes:
            id_sextante = sextante[2]
            template = cv2.imread(RUTA_SEXTANTES+'/'+sextante, 0)
            if (cvr.detectar(template, self.roi, 999999) is not None):
                sup, inf, sroi = cvr.detectar(template,self.roi,999999)
                localidades = {k : v for k,v in self.localidades.items()
                               if ( k[2]==id_sextante
                               or (k[2:4]=='0'+id_sextante))
                              }
                for id, datos in localidades.items():
                    if os.path.isfile(datos['Plantilla']):
                        img_loc = localidad.localidad(datos['Plantilla'],
                                                      sroi,
                                                      id)
                        # cvr.ver_imagen(img_loc.roi, id)
                        new_sup = tuple(map(add, sup, img_loc.supi))
                        new_sup = tuple(map(add, new_sup, self.supi))
                        h, w, _ = img_loc.roi.shape
                        if self.id != 'Am': #Caso especial amazonas
                            centro_inf = (new_sup[0]+int(w/2), new_sup[1] + h)
                        else:
                            centro_inf = (new_sup[0]+ w + 30, new_sup[1]+15)
                        self.localidades[id]['supi'] = new_sup
                        self.localidades[id]['centro_inf'] = centro_inf
            else:
                print('No se detecta el sextante {0} en el mapa'.format(sextante))

    def area_variantes(self):
        img = np.array(self.mapa)
        # llamando un np.array se evita modificar la imagen original (así se
        # crea una copia)
        self.detectar_localidades()
        for id, datos in self.localidades.items():
            print(id)
            supi = (datos['centro_inf'][0]-201,datos['centro_inf'][1]-7)
            infd = (datos['centro_inf'][0]+201,datos['centro_inf'][1]+105)
            roiv = np.array(self.mapa[supi[1]:infd[1],supi[0]:infd[0]])
            roiv = sc.signos_convencionales(roiv)
            cv2.imwrite('Pruebas/'+id+'.jpg',roiv)
            #cv2.rectangle(img, supi, infd,(0,255,255),2)
            #cv2.line(img, (datos['centro_inf'][0],datos['centro_inf'][1]-6), (datos['centro_inf'][0],datos['centro_inf'][1]+105), (255,0,0),1)
            areas = cvr.detectar_area_contornos(roiv, 250, 255, (0,0), 1, 20, 20)
            print (areas)
            for area in areas:
                x1 = area[0]-2
                y1 = area[1]-2
                x2 = area[2]+2
                y2 = area[3]+2
                area_supi = tuple(map(add, (x1,y1),supi))
                area_infd = tuple(map(add, (x2,y2),supi))
                left = area_supi[0] < (supi[0]+infd[0])/2
                rigth = area_infd[0] > (supi[0]+infd[0])/2
                center = left and rigth
                top = area_supi[1] - 20 <  supi[1]
                no_marco = (area_infd[0] - area_supi[0]) < 398
                no_marco = no_marco and (area_infd[1] - area_supi[1]  < 100)
                color = (0,0,255)
                elegido = center and no_marco and top
                #if not elegido and no_marco:
                #    cv2.rectangle(img, area_supi, area_infd,(0,255,0),2)
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
                    variantes = np.array(self.mapa[area_supi[1]:area_infd[1],
                                         area_supi[0]:area_infd[0]])
                    cv2.imwrite('Proceso/'+id+'.jpg', variantes)
        cv2.imwrite('Pruebas/col2.jpg',img)

mapa = departamento(RUTA_DEPARTAMENTOS+'/Bo.jpg',cv2.imread('../jpgs/mapas/alec_v4_044.jpg'))
mapa.area_variantes()
