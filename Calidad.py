import numpy as np
import pandas as pd
from Tkinter import Tk		# Ventana para seleccionar archivo
from tkFileDialog import askopenfilename

def main():
    Tk().withdraw()		# No queremos GUI completa
    path = askopenfilename()
    path2 = askopenfilename()

    # Nombre de las columnas
    headers_estaciones = ['COD_EMPRESA', 'PERIODO', 'CODIGO_SITIO', 'TECNOLOGIA', 'TIPO_SITIO', 'REGION', 'COMUNA', 'LATITUD_GRADOS', 'LATITUD_MINUTOS', 'LATITUD_SEGUNDOS', 'LONGITUD_GRADOS', 'LONGITUD_MINUTOS', 'LONGITUD_SEGUNDOS', 'DIRECCION']
    headers_mediciones = ['CODIGO_EMPRESA', 'AAAAMMDD', 'CODIGO_SITIO', 'RANGO_HORARIO', 'ESTABLECIDAS', 'INTENTOS', 'INTERRUMPIDAS', 'DOWNTIME']

    # Importa las tablas de mediciones y estaciones
    mediciones = pd.read_csv(path, sep = ';', dtype = str, names = headers_mediciones) # Antes venia con 4 lineas blancas skiprows = 4
    estaciones = pd.read_csv(path2, sep = ';', dtype = str, names = headers_estaciones)

    print "Mediciones: %.0f" % len(mediciones)
    print "Estaciones: %.0f" % len(estaciones)
    # Cruza mediciones con estaciones
    mediciones['CODIGO_SITIO'] = mediciones['CODIGO_SITIO'].str.upper()
    estaciones['CODIGO_SITIO'] = estaciones['CODIGO_SITIO'].str.upper()
    mediciones = pd.merge(left = mediciones, right = estaciones, left_on = 'CODIGO_SITIO', right_on = 'CODIGO_SITIO')
    mediciones.drop(['COD_EMPRESA', 'PERIODO', 'TECNOLOGIA', 'TIPO_SITIO', 'REGION', 'COMUNA', 'LATITUD_GRADOS', 'LATITUD_MINUTOS', 'LATITUD_SEGUNDOS', 'LONGITUD_GRADOS', 'LONGITUD_MINUTOS', 'LONGITUD_SEGUNDOS', 'DIRECCION'], axis = 1, inplace = True)

    # Reordena las columnas de la tabla mediciones

    print "Mediciones: %.0f" % len(mediciones)
    mediciones.to_csv('exportar.txt', sep = ';', header = False, index = False)
    

    #######################################################################
    # Finalmente calcula las estadisticas de cumplimiento de la normativa #
    #######################################################################

    mediciones_hora_cargada = mediciones.copy()
    mediciones_hora_cargada = mediciones_hora_cargada[mediciones_hora_cargada['RANGO_HORARIO'] == '1213']
    est = estaciones[['CODIGO_SITIO', 'TIPO_SITIO']]
    mediciones_hora_cargada = pd.merge(mediciones_hora_cargada, est, left_on = 'CODIGO_SITIO', right_on = 'CODIGO_SITIO', how = 'inner')
    mediciones_hora_cargada[['ESTABLECIDAS', 'INTENTOS', 'INTERRUMPIDAS', 'DOWNTIME']] = mediciones_hora_cargada[['ESTABLECIDAS', 'INTENTOS', 'INTERRUMPIDAS', 'DOWNTIME']].astype(float)
    print "mediciones_hora_cargada: %.0f" % len(mediciones_hora_cargada)

    meds = mediciones_hora_cargada.groupby(['CODIGO_SITIO', 'TIPO_SITIO'])
    meds = meds.sum().reset_index()

    print "Mediciones despues de filtrar: %f.0" % len(meds)
    rurales = len(estaciones[estaciones['TIPO_SITIO'] == 'R'])
    urbanas = len(estaciones[estaciones['TIPO_SITIO'] == 'U'])
    print "Rurales: {}".format(rurales)
    print "Urbanas: {}".format(urbanas)


    meds['PEE'] = meds['ESTABLECIDAS']/meds['INTENTOS']
    meds['PFE'] = (meds['ESTABLECIDAS'] - meds['INTERRUMPIDAS'])/meds['ESTABLECIDAS']

    ppee_rural = 1.0 * len(meds[np.logical_and(meds['PEE'] < 0.9, meds['TIPO_SITIO'] == 'R')]['PEE'])/rurales
    ppee_urbano =  1.0 * len(meds[np.logical_and(meds['PEE'] < 0.97, meds['TIPO_SITIO'] == 'U')]['PEE'])/urbanas
    ppfe_rural = 1.0 * len(meds[np.logical_and(meds['PFE'] < 0.9, meds['TIPO_SITIO'] == 'R')]['PFE'])/rurales
    ppfe_urbano =  1.0 * len(meds[np.logical_and(meds['PFE'] < 0.97, meds['TIPO_SITIO'] == 'U')]['PFE'])/urbanas

    rural_no_cumple_ppee = len(meds[np.logical_and(meds['PEE'] < 0.9, meds['TIPO_SITIO'] == 'R')]['PEE'])
    urbano_no_cumple_ppee = len(meds[np.logical_and(meds['PEE'] < 0.97, meds['TIPO_SITIO'] == 'U')]['PEE'])
    rural_no_cumple_ppfe = len(meds[np.logical_and(meds['PFE'] < 0.9, meds['TIPO_SITIO'] == 'R')]['PFE'])
    urbano_no_cumple_ppfe = len(meds[np.logical_and(meds['PFE'] < 0.97, meds['TIPO_SITIO'] == 'U')]['PFE'])

    print "PPEE urbano no cumpliendo %.0f" % (urbano_no_cumple_ppee)
    print "PPEE rural no cumpliendo %.0f" % (rural_no_cumple_ppee)
    print "PPFE urbano no cumpliendo %.0f" % (urbano_no_cumple_ppfe)
    print "PPFE rural no cumpliendo %.0f" % (rural_no_cumple_ppfe)
    print "PPFE urbano: %.2f%%" % (ppfe_urbano*100)
    print "PPEE urbano: %.2f%%" % (ppee_urbano*100)
    print "PPEE rural: %.2f%%" % (ppee_rural*100)
    print "PPFE rural: %.2f%%" % (ppfe_rural*100)

    print "PPFE y PPEE deben ser menor o igual a 5%"
    #meds.to_csv('agrupados.txt', sep = ';', header = True, index = False)

if __name__ == "__main__":
    main()