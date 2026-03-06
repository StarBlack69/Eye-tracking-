import pandas as pd
import sys

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
nombre_archivo = 'C:/Ruta/Generica/1D_2D_RF_Idea_A_B_C.xlsx'
nombre_salida = 'C:/Ruta/Generica/Datos_para_random_forest.csv'

def preparar_datos_para_modelo():
    """
    Carga el conjunto de datos en formato Excel, elimina las columnas 
    de tiempo y coordenadas crudas, rellena valores vacíos con 0 
    y exporta el resultado como CSV para optimizar el entrenamiento de ML.
    """
    try:
        df = pd.read_excel(nombre_archivo)
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        print("Asegúrate de que el archivo no esté abierto en otra ventana.")
        sys.exit()

    columnas_a_eliminar = [
        'RecordingTime [ms]', 
        'Point of Regard Right X [px]', 
        'Point of Regard Right Y [px]', 
        'Eye Position Right Z [mm]', 
        'Angulo_X_[º]', 
        'Angulo_Y_[º]',
        'Point of Regard Right X (Z)',
        'Point of Regard Right Y (Z)'
    ]

    df_limpio = df.drop(columns=columnas_a_eliminar, errors='ignore')
    df_limpio = df_limpio.fillna(0)

    try:
        df_limpio.to_csv(nombre_salida, index=False)
        print(f"Archivo CSV preparado exitosamente en: {nombre_salida}")
        print(f"Dimensiones finales del dataset: {df_limpio.shape[0]} filas, {df_limpio.shape[1]} columnas")
    except Exception as e:
        print(f"Error al guardar el archivo CSV: {e}")

if __name__ == "__main__":
    preparar_datos_para_modelo()