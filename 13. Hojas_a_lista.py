import pandas as pd
import os

# [DATO PRIVADO ELIMINADO - Ruta de archivo origen]
ruta_archivo = r"C:\Ruta\Generica\Datos_Participantes_Separados.xlsx"

def combinar_hojas_a_lista():
    """
    Lee todas las hojas de un archivo Excel, limpia los nombres de las columnas,
    combina los datos en un solo DataFrame, filtra las primeras 119 muestras
    por grupo (Participante, Estímulo) y guarda el resultado consolidado.
    """
    try:
        diccionario_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
        lista_dataframes = []

        if not diccionario_hojas:
            print("Error: El archivo Excel no contiene datos.")
            return

        for nombre_hoja, df_hoja in diccionario_hojas.items():
            df_hoja.columns = df_hoja.columns.str.strip()
            lista_dataframes.append(df_hoja)
            
        df_combinado = pd.concat(lista_dataframes, ignore_index=True)
        
        df_combinado = df_combinado.loc[:, ~df_combinado.columns.str.contains('^Unnamed')]
        
        col_tiempo = 'RecordingTime [ms]'
        if col_tiempo in df_combinado.columns:
            df_combinado = df_combinado.sort_values(by=['Participant', 'Stimulus', col_tiempo])
        
        df_final = df_combinado.groupby(['Participant', 'Stimulus']).head(119)
        
        nulos_x = df_final['Point of Regard Right X [px]'].isnull().sum()
        if nulos_x > 0:
            print(f"Advertencia: Se encontraron {nulos_x} datos vacíos en la columna X.")
        
        carpeta_salida = os.path.dirname(ruta_archivo)
        
        # [DATO PRIVADO ELIMINADO - Nombre de archivo de salida]
        nombre_salida = "Lista_Consolidada.xlsx" 
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)
        
        df_final.to_excel(ruta_salida, index=False)
        
        print(f"Proceso completado exitosamente.")
        print(f"Archivo consolidado guardado en: {ruta_salida}")
        print(f"Total de filas en el archivo final: {len(df_final)}")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en: {ruta_archivo}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    combinar_hojas_a_lista()