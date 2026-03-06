import pandas as pd
import os
import sys

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ruta_entrada = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_grados.xlsx"
ruta_salida = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_metricas.xlsx"

def calcular_metricas():
    """
    Calcula la Media, RMS y cantidad de Ceros usando una ventana móvil de 3 
    sobre las coordenadas estandarizadas (Z). Verifica la integridad de 
    119 muestras por grupo antes de guardar.
    """
    if os.path.exists(ruta_salida):
        try:
            with open(ruta_salida, "a"): pass
        except PermissionError:
            print("Error: El archivo de salida está abierto. Ciérralo antes de ejecutar.")
            sys.exit()

    try:
        df = pd.read_excel(ruta_entrada)

        col_x = 'Point of Regard Right X (Z)'
        col_y = 'Point of Regard Right Y (Z)'
        columnas_agrupacion = ['Stimulus', 'Participant']
        col_referencia = 'Etiqueta_A'

        df['Media_V3_X'] = df.groupby(columnas_agrupacion)[col_x].transform(
            lambda x: x.rolling(window=3).mean().bfill()
        ).round(4)
        
        df['Media_V3_Y'] = df.groupby(columnas_agrupacion)[col_y].transform(
            lambda x: x.rolling(window=3).mean().bfill()
        ).round(4)

        df['Derivada_X'] = df.groupby(columnas_agrupacion)[col_x].diff().bfill()
        df['Derivada_Y'] = df.groupby(columnas_agrupacion)[col_y].diff().bfill()

        df['RMS_V3_X'] = df.groupby(columnas_agrupacion)['Derivada_X'].transform(
            lambda x: (x**2).rolling(window=3).mean() ** 0.5
        ).bfill().round(4)
        
        df['RMS_V3_Y'] = df.groupby(columnas_agrupacion)['Derivada_Y'].transform(
            lambda x: (x**2).rolling(window=3).mean() ** 0.5
        ).bfill().round(4)

        df.drop(columns=['Derivada_X', 'Derivada_Y'], inplace=True)

        df['Ceros_V3_X'] = df.groupby(columnas_agrupacion)[col_x].transform(
            lambda x: (x == 0).rolling(window=3).sum().bfill()
        )

        df['Ceros_V3_Y'] = df.groupby(columnas_agrupacion)[col_y].transform(
            lambda x: (x == 0).rolling(window=3).sum().bfill()
        )

        columnas_nuevas = ['Media_V3_X', 'Media_V3_Y', 'RMS_V3_X', 'RMS_V3_Y', 'Ceros_V3_X', 'Ceros_V3_Y']
        cols_originales = [c for c in df.columns if c not in columnas_nuevas]

        if col_referencia in cols_originales:
            idx = cols_originales.index(col_referencia)
            nuevo_orden = cols_originales[:idx] + columnas_nuevas + cols_originales[idx:]
            df = df[nuevo_orden]
        else:
            print(f"Advertencia: No se encontró la columna '{col_referencia}'. Las columnas se añadieron al final.")

        tamanos_grupos = df.groupby(columnas_agrupacion).size()
        no_119 = tamanos_grupos[tamanos_grupos != 119]
        
        if not no_119.empty:
            print("\nAdvertencia: Se encontraron grupos que no tienen exactamente 119 muestras:")
            print(no_119)
        else:
            print("Verificación exitosa: Todos los grupos tienen exactamente 119 muestras.")

        df.to_excel(ruta_salida, index=False)
        print(f"Archivo guardado exitosamente en: {ruta_salida}")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    calcular_metricas()