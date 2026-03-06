import pandas as pd
import os
import glob

def consolidar_excels_y_contar(carpeta_origen):
   
    archivo_salida = os.path.join(carpeta_origen, "Consolidado_MO50.xlsx")
    patron_busqueda = os.path.join(carpeta_origen, "*_MO50.xlsx")
    archivos_excel = glob.glob(patron_busqueda)

    if not archivos_excel:
        print("Error: No se encontraron archivos Excel en la carpeta para consolidar.")
        return

    datos_participantes = {}

    for archivo in archivos_excel:
        hojas = pd.read_excel(archivo, sheet_name=None)
        
        for nombre_hoja, df in hojas.items():
            if nombre_hoja not in datos_participantes:
                datos_participantes[nombre_hoja] = df
            else:
                datos_participantes[nombre_hoja] = pd.concat([datos_participantes[nombre_hoja], df], ignore_index=True)

    with pd.ExcelWriter(archivo_salida) as writer:
        for participante, df in datos_participantes.items():
            nombre_hoja_seguro = str(participante)[:31]
            df.to_excel(writer, sheet_name=nombre_hoja_seguro, index=False)

    total_participantes = len(datos_participantes)
    
    print(f"Archivo guardado exitosamente: {archivo_salida}")
    print(f"Total de participantes únicos procesados: {total_participantes}")

# [DATO PRIVADO ELIMINADO - Ruta de carpeta origen]
carpeta_origen = r"C:\Ruta\Generica\Carpeta_Origen"

consolidar_excels_y_contar(carpeta_origen)