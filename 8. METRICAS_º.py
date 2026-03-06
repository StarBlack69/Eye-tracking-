import pandas as pd
import numpy as np
import os
import sys

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ruta_entrada = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_metricas.xlsx"
ruta_salida = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_Met_Cinematicas.xlsx"

def calcular_metricas_cinematicas():
    """
    Calcula características cinemáticas y físicas (Velocidad, Aceleración, 
    Jerk, Dispersión, Curtosis y Energía) basándose en los ángulos visuales 
    y el tiempo de grabación. Mantiene la estructura de 119 muestras.
    """
    if os.path.exists(ruta_salida):
        try:
            with open(ruta_salida, "a"): pass
        except PermissionError:
            print("Error: El archivo de salida está abierto. Ciérralo antes de ejecutar.")
            sys.exit()

    try:
        df = pd.read_excel(ruta_entrada)

        columnas_agrupacion = ['Participant', 'Stimulus']
        col_referencia = 'Etiqueta_A'
        
        df = df.sort_values(by=['Participant', 'Stimulus', 'RecordingTime [ms]']).reset_index(drop=True)

        dt = df.groupby(columnas_agrupacion)['RecordingTime [ms]'].diff() / 1000.0

        dx = df.groupby(columnas_agrupacion)['Angulo_X_[º]'].diff()
        dy = df.groupby(columnas_agrupacion)['Angulo_Y_[º]'].diff()
        distancia = np.sqrt(dx**2 + dy**2)
        
        df['Velocidad_[º/s]'] = (distancia / dt).replace([np.inf, -np.inf], np.nan)
        df['Velocidad_[º/s]'] = df.groupby(columnas_agrupacion)['Velocidad_[º/s]'].bfill().fillna(0).round(4)

        d_vel = df.groupby(columnas_agrupacion)['Velocidad_[º/s]'].diff()
        df['Aceleracion_[º/s2]'] = (d_vel / dt).replace([np.inf, -np.inf], np.nan)
        df['Aceleracion_[º/s2]'] = df.groupby(columnas_agrupacion)['Aceleracion_[º/s2]'].bfill().fillna(0).round(4)

        d_acc = df.groupby(columnas_agrupacion)['Aceleracion_[º/s2]'].diff()
        df['Jerk_[º/s3]'] = (d_acc / dt).replace([np.inf, -np.inf], np.nan)
        df['Jerk_[º/s3]'] = df.groupby(columnas_agrupacion)['Jerk_[º/s3]'].bfill().fillna(0).round(4)

        VENTANA_DISPERSION = 3
        VENTANA_CINETICA = 10
        
        df['max_x'] = df.groupby(columnas_agrupacion)['Angulo_X_[º]'].transform(lambda x: x.rolling(VENTANA_DISPERSION).max())
        df['min_x'] = df.groupby(columnas_agrupacion)['Angulo_X_[º]'].transform(lambda x: x.rolling(VENTANA_DISPERSION).min())
        df['max_y'] = df.groupby(columnas_agrupacion)['Angulo_Y_[º]'].transform(lambda x: x.rolling(VENTANA_DISPERSION).max())
        df['min_y'] = df.groupby(columnas_agrupacion)['Angulo_Y_[º]'].transform(lambda x: x.rolling(VENTANA_DISPERSION).min())
        
        df['Dispersion_[º]'] = (df['max_x'] - df['min_x']) + (df['max_y'] - df['min_y'])
        df['Dispersion_[º]'] = df.groupby(columnas_agrupacion)['Dispersion_[º]'].bfill().fillna(0).round(4)
        df.drop(columns=['max_x', 'min_x', 'max_y', 'min_y'], inplace=True)

        df['Curtosis'] = df.groupby(columnas_agrupacion)['Velocidad_[º/s]'].transform(
            lambda x: x.rolling(window=VENTANA_CINETICA, min_periods=4).kurt()
        ).bfill().fillna(0).round(4)

        df['Energia'] = df.groupby(columnas_agrupacion)['Velocidad_[º/s]'].transform(
            lambda x: (x**2).rolling(window=VENTANA_CINETICA).mean()
        ).bfill().fillna(0).round(4)

        columnas_nuevas = [
            'Velocidad_[º/s]', 'Dispersion_[º]', 'Aceleracion_[º/s2]', 
            'Curtosis', 'Energia', 'Jerk_[º/s3]'
        ]
        
        cols_originales = [c for c in df.columns if c not in columnas_nuevas]

        if col_referencia in cols_originales:
            idx = cols_originales.index(col_referencia)
            nuevo_orden = cols_originales[:idx] + columnas_nuevas + cols_originales[idx:]
            df = df[nuevo_orden]
        else:
            print(f"Advertencia: No se encontró la columna '{col_referencia}'. Quedarán al final.")

        df.to_excel(ruta_salida, index=False)
        print(f"Características cinemáticas calculadas exitosamente. Archivo guardado en: {ruta_salida}")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    calcular_metricas_cinematicas()