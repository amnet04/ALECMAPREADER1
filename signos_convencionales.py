import numpy as np
import cv2
import funcionesCV_recurrentes as cvr

def unir_separadores(imagen):
    imagen = imagen
    separadores = ['polimorfismo.jpg',
                   'polimorfismo_frecuencia.jpg',
                   'no_equivalente.jpg',
                   'mismo_genero.jpg',
                   'hombre_mujer.jpg']
    lineas = []
    for separador in separadores:
        elevacion = 10
        if separador == 'mismo_genero.jpg' or   separador == 'hombre_mujer.jpg':
            elevacion = -5
        template = cv2.imread('Signos_Convencionales/'+separador, 0)
        puntos, h, w = cvr.detectar_recursivo(template, imagen, 0.75)
        for punto in puntos:
            centro = (int(punto[0]+h/2), int(punto[1]+w/2))
            izquierdo = (centro[0]-40, centro[1]-elevacion)
            derecho = (centro[0]+40, centro[1]-elevacion)
            lineas.append((izquierdo, derecho, (0, 0, 0), 20))
    return(lineas)

def asterisco(mapa):
    template = cv2.imread('Signos_Convencionales/uso_arcaico.jpg', 0)
    puntos, h, w = cvr.detectar_recursivo(template, mapa, 0.7)
    lineas = []
    for punto in puntos:
        centro = (int(punto[0]+h/2), int(punto[1]+w/2))
        izquierdo = (centro[0]-5, punto[1]+20)
        derecho = (centro[0]+5, punto[1]+20)
        lineas.append((izquierdo, derecho, (0, 0, 0), 20))
    return(lineas)

def adiciones(mapa):
    template = cv2.imread('Signos_Convencionales/adiciones.jpg', 0)
    puntos, h, w = cvr.detectar_recursivo(template, mapa, 0.7)
    lineas = []
    for punto in puntos:
        centro = (int(punto[0]+h/2), int(punto[1]+w/2))
        izquierdo = (centro[0]-40, punto[1]+10)
        lineas.append((centro, izquierdo, (0, 0, 0), 20 ))
    return(lineas)

def mascara_contener(mapa):
    template_der = cv2.imread('Signos_Convencionales/salto_de_linea_der.jpg',0)
    template_izq = cv2.imread('Signos_Convencionales/salto_de_linea_izq.jpg',0)
    puntos_der, h_der, w_der = cvr.detectar_recursivo(template_der, mapa, 0.7)
    puntos_izq, h_izq, w_izq = cvr.detectar_recursivo(template_izq, mapa, 0.7)
    lineas = []
    for punto in puntos_der:
        top = (punto[0] + int(w_der/2), punto[1])
        bottom = (punto[0] + int(w_der/2), punto[1]+h_der)
        center = (punto[0], punto[1] + int(h_der/2))
        antena_sup = (center[0]-40, center[1] -20)
        antena_inf = (center[0]-40, center[1] +20)
        lineas.append((top, bottom, (255, 255, 255), w_der))
        lineas.append((center, antena_sup, (0, 0, 0), 10))
        lineas.append((center, antena_inf, (0, 0, 0), 10))
    for punto in puntos_izq:
        top = (punto[0] + int(w_izq/2), punto[1])
        bottom = (punto[0] + int(w_izq/2), punto[1]+h_izq)
        center = (punto[0]+w_izq, punto[1] + int(h_izq/2))
        antena_sup = (center[0]+40, center[1] -20)
        antena_inf = (center[0]+40, center[1] +20)
        lineas.append((top, bottom, (255, 255, 255), w_izq))
        lineas.append((center, antena_sup, (0, 0, 0), 10))
        lineas.append((center, antena_inf, (0, 0, 0), 10))
    return(lineas)


def signos_convencionales(mapa):
    lines = unir_separadores (mapa)
    lines = lines+asterisco(mapa)
    lines = lines+adiciones(mapa)
    lines = lines+mascara_contener(mapa)
    for line in lines:
        print (line)
        pt1, pt2, color, ancho = line
        cv2.line(mapa, pt1, pt2, color, ancho)
    mapa = cv2.cvtColor(mapa, cv2.COLOR_RGB2GRAY)
    ret, mapa = cv2.threshold(mapa, 200, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite('Pruebas/col1.jpg', mapa)
    return(mapa)

mapa = cv2.imread('../jpgs/alec_v4_044.jpg')
signos_convencionales(mapa)
