import numpy as np
import pandas
import cv2
import funcionesCV_recurrentes as cvr
from ocr import ocr

def detectar_area_variantes(mapa):
    '''
    Detecta las zonas de texto de la parte superior izquierda correspondientes al
    título del mapa, las variantes y las traducciones.
    '''
    mapa = cvr.cargar_imagen(mapa)
    height, width = img['gris'].shape[:2]
    img_dilatada = cvr.dilatar_imagen(img['gris'], 127, 255, (13,13), 5)
    img2, contours, hierarchy = cv2.findContours(img_dilatada,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    areas_de_texto = []
    for contour in contours:
        [x,y,w,h] = cv2.boundingRect(contour)
        if (60 < w < width/2) or (60 < h <  height/2):
            if ( x < width/3 and y <  height/7 and w > 16 and h > 16):
                areas_de_texto.append((x,y,x+w,y+h))
    areas_de_texto = pandas.DataFrame(areas_de_texto, columns=('x1','y1','x2','y2'))
    areas_ordenadas = areas_de_texto.sort_values(by=['y1'])
    are_tit = areas_ordenadas.iloc[0,:]
    are_int = areas_ordenadas.iloc[1:,:]
    are_int = are_int.sort_values(by=['x1'])
    are_var = are_int.iloc[0,:]
    are_tra = are_int.iloc[1,:]
    im = {}
    im['tit'] = cvr.cortar_imagen(img['gris'],are_tit.x1,are_tit.x2,are_tit.y1,are_tit.y2)
    im['var'] = cvr.cortar_imagen(img['gris'],are_var.x1,are_var.x2,are_var.y1,are_var.y2)
    im['tra'] = cvr.cortar_imagen(img['gris'],are_tra.x1,are_tra.x2,are_tra.y1,are_tra.y2)
    return(im)

def obtener_titulo(mapa):
    img = detectar_area_variantes(mapa)['tit']['im']
    img_mejorada = cvr.preprocesar_texto_adapta(img, 255,71,30)
    text = ocr(img_mejorada,'spa')
    titulo = {}
    titulo['numero']=text[0].replace(' ','')
    titulo['ententrada']=[' '.join(text[1:])][0]
    return(titulo)

def obtener_traducciones(mapa):
    img = detectar_area_variantes(mapa)['tra']['im']
    img_mejorada = cvr.preprocesar_texto_otsu(img,127,255,(3,7),3)
    text_eng = ocr(img_mejorada,'eng')
    text_fra = ocr(img_mejorada,'fra')
    traducciones = {}
    traducciones['frances']=text_fra[0]
    traducciones['ingles']=text_eng[1]
    return(traducciones)

def preparar_sub_carpeta(mapa):
    volumen = mapa[5:7]
    carpeta_mapa = 'm'+str(obtener_titulo(mapa)['num_mapa'])
    path ="datos_procesados/"+volumen+"/"+carpeta_mapa
    if not os.path.exists(path):
        os.makedirs (path)
    return(path)

def buscar_variantes(mapa):
    titulo = obtener_titulo(mapa)
    traducciones = obtener_traducciones(mapa)
    departamentos = detectar_departamentos(mapa)
    variantes = obtener_variantes(mapa)
    imagenes_variantes={}
    for variante in variantes.iterrows():
        variante_nombre = variante[0].replace(' ','_')
        x = variante[1].iloc[0]
        y = variante[1].iloc[1]
        w = variante[1].iloc[2]
        h = variante[1].iloc[3]
        imagen_variante = img_gray[y:h,x:w]
        w_variante,h_variante=imagen_variante.shape[::-1]
        cv2.imwrite(carpeta+variante_nombre+'.jpg',imagen_variante)
        for key, value in departamentos.items():
            x_dep = value[0][0]
            y_dep = value[0][1]
            w_dep= value[1][0]
            h_dep = value[1][1]
            imagen_departamento_gray = img_gray[y_dep:h_dep,x_dep:w_dep]
            imagen_departamento = img[y_dep:h_dep,x_dep:w_dep]
            concidencias = cv2.matchTemplate (imagen_departamento_gray, imagen_variante, cv2.TM_CCOEFF_NORMED)
            loc = np.where( concidencias >= 0.9)

            #colorcitos solo pa ve
            i=0
            for pt in zip(*loc[::-1]):
                cv2.rectangle(imagen_departamento, pt, (pt[0] + w_variante, pt[1] + h_variante), (0,0,255), 1)
                cv2.putText(imagen_departamento, variante_nombre, pt, cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 1)
                i+=1
            cv2.imwrite(carpeta+key+'.jpg',imagen_departamento)
