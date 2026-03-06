import pandas as pd
import os

def procesar_multiples_archivos(lista_archivos, carpeta_destino):
   
    columnas_deseadas = [
        'RecordingTime [ms]', 
        'Stimulus', 
        'Participant', 
        'Point of Regard Right X [px]', 
        'Point of Regard Right Y [px]', 
        'Eye Position Right Z [mm]'
    ]

    os.makedirs(carpeta_destino, exist_ok=True)

    for archivo in lista_archivos:
        chunks_filtrados = []
        nombre_base = os.path.basename(archivo).replace('.txt', '')
        archivo_salida = os.path.join(carpeta_destino, f"{nombre_base}_MO50.xlsx")

        try:
            with pd.read_csv(archivo, sep=',', chunksize=100000, usecols=columnas_deseadas) as reader:
                for chunk in reader:
                    chunk_filtrado = chunk[chunk['Stimulus'] == 'MO 50']
                    
                    if not chunk_filtrado.empty:
                        chunks_filtrados.append(chunk_filtrado)

            if chunks_filtrados:
                df_final = pd.concat(chunks_filtrados, ignore_index=True)
                
                columnas_a_limpiar = [
                    'Point of Regard Right X [px]', 
                    'Point of Regard Right Y [px]', 
                    'Eye Position Right Z [mm]'
                ]
                
                for col in columnas_a_limpiar:
                    df_final[col] = pd.to_numeric(df_final[col].astype(str).str.strip(), errors='coerce')
                
                df_final = df_final.dropna(subset=columnas_a_limpiar)
                
                with pd.ExcelWriter(archivo_salida) as writer:
                    for participante, datos_participante in df_final.groupby('Participant'):
                        nombre_hoja = str(participante)[:31]
                        datos_participante.to_excel(writer, sheet_name=nombre_hoja, index=False)
                        
            else:
                print(f"Estímulo 'MO 50' no encontrado en: {archivo}")

        except FileNotFoundError:
            print(f"Error: No se encontró la ruta '{archivo}'")
        except ValueError as ve:
            print(f"Error de columnas en {archivo}: {ve}")
        except Exception as e:
            print(f"Error inesperado al procesar {archivo}: {e}")


# [DATO PRIVADO ELIMINADO - Ruta de carpeta destino]
carpeta_destino = r"C:\Ruta\Generica\Carpeta_Destino"

# [DATO PRIVADO ELIMINADO - Rutas de archivos txt]
archivos_txt = [
    r"C:\Ruta\Generica\Archivo_1.txt",
    r"C:\Ruta\Generica\Archivo_2.txt",
    r"C:\Ruta\Generica\Archivo_3.txt",
    r"C:\Ruta\Generica\Archivo_4.txt",
    r"C:\Ruta\Generica\Archivo_5.txt",
    r"C:\Ruta\Generica\Archivo_6.txt"
]

procesar_multiples_archivos(archivos_txt, carpeta_destino)