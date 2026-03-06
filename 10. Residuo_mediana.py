import pandas as pd
import numpy as np
import sys

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ruta_entrada = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_Met.xlsx"
ruta_salida = r"C:\Ruta\Generica\1D_2D_RF_Base_Final.xlsx"

def calcular_residuos_mediana(grupo):
    """
    Calcula el residuo de la mediana móvil (ventana=5, centrada) para las 
    coordenadas X, Y y la Velocidad. Útil para resaltar picos anómalos (Ruido I).
    """
    ventana = 5
    
    mediana_x = grupo['Point of Regard Right X [px]'].rolling(window=ventana, center=True).median()
    mediana_y = grupo['Point of Regard Right Y [px]'].rolling(window=ventana, center=True).median()
    mediana_v = grupo['Velocidad_[º/s]'].rolling(window=ventana, center=True).median()
    
    grupo['Residuo_Mediana_X'] = (grupo['Point of Regard Right X [px]'] - mediana_x).abs()
    grupo['Residuo_Mediana_Y'] = (grupo['Point of Regard Right Y [px]'] - mediana_y).abs()
    grupo['Residuo_Mediana_V'] = (grupo['Velocidad_[º/s]'] - mediana_v).abs()
    
    return grupo

def procesar_residuos():
    try:
        df = pd.read_excel(ruta_entrada)
    except Exception as e:
        print(f"Error al cargar el archivo de entrada: {e}")
        sys.exit()

    df = df.groupby('Participant', group_keys=False).apply(calcular_residuos_mediana)
    
    # Rellenamos los extremos de la ventana (NaN) con 0
    df.fillna(0, inplace=True)

    columnas = df.columns.tolist()
    nuevas_cols = ['Residuo_Mediana_X', 'Residuo_Mediana_Y', 'Residuo_Mediana_V']

    if 'Etiqueta_A' in columnas:
        for c in nuevas_cols:
            if c in columnas:
                columnas.remove(c)
                
        indice_etiqueta = columnas.index('Etiqueta_A')
        for i, c in enumerate(nuevas_cols):
            columnas.insert(indice_etiqueta + i, c)
            
        df = df[columnas]
    else:
        print("Advertencia: No se encontró la columna 'Etiqueta_A'. Las columnas quedarán al final.")

    try:
        df.to_excel(ruta_salida, index=False)
        print(f"Archivo con residuos calculado exitosamente. Guardado en: {ruta_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo de salida: {e}")

if __name__ == "__main__":
    procesar_residuos()