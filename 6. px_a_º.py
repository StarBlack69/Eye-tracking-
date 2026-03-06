import pandas as pd
import numpy as np
import os

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
archivo_entrada = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_NZ.xlsx"
nombre_archivo_salida = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_grados.xlsx"

# Constantes del monitor
RES_W_PX = 1600
RES_H_PX = 900
SIZE_W_MM = 352
SIZE_H_MM = 241

COL_X_PIXEL = 'Point of Regard Right X [px]'
COL_Y_PIXEL = 'Point of Regard Right Y [px]'
COL_Z_MM = 'Eye Position Right Z [mm]'
COL_REFERENCIA = 'Etiqueta_A'

def procesar_angulos_por_hojas():
    """
    Calcula los ángulos visuales (X e Y) a partir de coordenadas en píxeles y 
    la distancia del ojo al monitor (Z), utilizando las dimensiones físicas de la pantalla.
    Inserta las nuevas columnas trigonométricas antes de la columna de referencia.
    """
    if not os.path.exists(archivo_entrada):
        print(f"Error: No se encontró el archivo de entrada: {archivo_entrada}")
        return

    try:
        carpeta_base = os.path.dirname(archivo_entrada)
        ruta_salida_completa = os.path.join(carpeta_base, nombre_archivo_salida)

        diccionario_hojas = pd.read_excel(archivo_entrada, sheet_name=None)
        
        center_x_px = RES_W_PX / 2
        center_y_px = RES_H_PX / 2
        pixel_pitch_x = SIZE_W_MM / RES_W_PX
        pixel_pitch_y = SIZE_H_MM / RES_H_PX

        with pd.ExcelWriter(ruta_salida_completa, engine='openpyxl') as writer:
            for nombre_pestana, df in diccionario_hojas.items():
                columnas_necesarias = [COL_X_PIXEL, COL_Y_PIXEL, COL_Z_MM]
                
                if df.empty or not all(col in df.columns for col in columnas_necesarias):
                    df.to_excel(writer, sheet_name=nombre_pestana, index=False)
                    continue

                opuesto_x_mm = (df[COL_X_PIXEL] - center_x_px) * pixel_pitch_x
                opuesto_y_mm = (df[COL_Y_PIXEL] - center_y_px) * pixel_pitch_y
                adyacente_z_mm = df[COL_Z_MM]

                df['Angulo_X_[º]'] = np.degrees(np.arctan2(opuesto_x_mm, adyacente_z_mm)).round(2)
                df['Angulo_Y_[º]'] = np.degrees(np.arctan2(opuesto_y_mm, adyacente_z_mm)).round(2)

                columnas_nuevas = ['Angulo_X_[º]', 'Angulo_Y_[º]']
                
                if COL_REFERENCIA in df.columns:
                    cols_originales = [c for c in df.columns if c not in columnas_nuevas]
                    idx = cols_originales.index(COL_REFERENCIA)
                    nuevo_orden = cols_originales[:idx] + columnas_nuevas + cols_originales[idx:]
                    df = df[nuevo_orden]

                df.to_excel(writer, sheet_name=nombre_pestana, index=False)

        print(f"Cálculo de ángulos terminado exitosamente. Archivo guardado en: {ruta_salida_completa}")

    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")

if __name__ == "__main__":
    procesar_angulos_por_hojas()