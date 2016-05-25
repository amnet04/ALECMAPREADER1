import numpy as np
import pandas
import cv2

def cargar_imagen(archivo):
    '''
    Carga en  variables dos matrices de la imágen, una gris y otra a color,
    devuelve un diccionario con las dos versiones.
    '''
    imagen = {}
    imagen['gris'] = cv2.imread(archivo,0)
    imagen['color'] = cv2.imread(archivo)
    return(imagen)

def dilatar_imagen(img, umbral_blanco, umbral_negro, dim_kernel, iteraciones):
    ret,thresh = cv2.threshold(img, umbral_blanco,umbral_negro,cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, dim_kernel)
    dilatada= cv2.dilate(thresh,kernel,iterations = iteraciones)
    return(dilatada)

def erosionar_imagen(img, umbral_blanco, umbral_negro, dim_kernel, iteraciones):
    ret,thresh = cv2.threshold(img, umbral_blanco,umbral_negro,cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, dim_kernel)
    erosionada = cv2.erode(thresh,kernel,iterations = iteraciones)
    return(erosionada)

def dibujar_rectangulos(img,x1,y1,x2,y2,color,ancho_bordes,archivo=''):
    cv2.rectangle(img,(x1,y1),(x2,y2),(color),ancho_bordes)
    # if archivo !='':
    #     cv2.imwrite(archivo,img)

def cortar_imagen(img,x1,x2,y1,y2):
    corte = img[y1:y2,x1:x2]
    img_cortada = {}
    img_cortada['im'] = corte
    img_cortada['x1'] = x1
    img_cortada['y1'] = y1
    img_cortada['x2'] = x2
    img_cortada['y2'] = y2
    return(img_cortada)

def bw_otsu(img, umbral_blanco,limite,blur=0,blur_ori =0):
    '''
    blur es el shape del blur en tupla por ejemplo (5,5)
    blur_ori es un entero. Si no se ponen valores no hace el blur
    '''
    if blur == (0,0):
        blureada = img
    else:
        blureada = cv2.GaussianBlur(img,blur,blur_ori)
    ret,th = cv2.threshold(blureada,umbral_blanco,limite,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return (th)

def bw_adapta(img,limite,tam,sh):
    th = cv2.adaptiveThreshold(img,limite,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,tam,sh)
    return (th)

def ver_imagen(img,title='solo pa vé'):
    cv2.imshow(title, img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def detectar(template, imagen, max_var_thresh):
    '''
    Detacta si el la imagen tiene coincidencias en el mapa y devuelve la
    coordenada superior izquierda de la coincidencia, su altura y su  ancho
    en la imagen del mapa general
    '''
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)
    imagen_bw = bw_adapta(imagen_gris, 255, 71, 30)
    h, w = template.shape
    coincidencia = cv2.matchTemplate(template, imagen_bw, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(coincidencia)
    x1 = max_loc[0]
    x2 = max_loc[0] + w
    y1 = max_loc[1]
    y2 = max_loc[1] + h
    if max_val < max_var_thresh:
        #cv2.imwrite('Pruebas/tast.jpg',imagen[y1:y2,x1:x2])
        return(None, max_val)
    else:
        #print (max_val)
        sup_izq = (x1,y1)
        inf_der = (x2,y2)
        roi = imagen[y1:y2,x1:x2]
        return(sup_izq, inf_der, roi)

def detectar_recursivo(template, imagen, thresh):
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)
    imagen_bw = bw_adapta(imagen_gris, 255, 71, 30)
    h, w = template.shape
    res = cv2.matchTemplate(imagen_bw,template,cv2.TM_CCOEFF_NORMED)
    loc = np.where(res>=thresh)
    puntos = []
    for punto in zip(*loc[::-1]):
        puntos.append(punto)
    return (puntos, h, w)

def detectar_area_contornos(imagen,
                            umbral_blanco,
                            umbral_negro,
                            dim_kernel,
                            iteraciones,
                            w, h):
    if dim_kernel != (0,0):
        imagen_dilatada = dilatar_imagen(imagen,
                                         umbral_blanco,
                                         umbral_negro,
                                         dim_kernel,
                                         iteraciones)
    else:
        imagen_dilatada = imagen
    imagen, contours, hierarchy = cv2.findContours(imagen_dilatada,
                                                   cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)
    areas = []
    for contour in contours:
        [x,y,wc,hc] = cv2.boundingRect(contour)
        x1 = x
        y1 = y
        x2 = x+wc
        y2 = y+hc
        if (wc > w) and (hc >  h):
            areas.append((x1, y1 , x2, y2))

    return (areas)
