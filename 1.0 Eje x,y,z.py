import pandas as pd
import os

# --- 1. CONFIGURACIÓN ---
input_path = "C:/Users/Irazu/Desktop/Python/Residencia/Datos crudos/VPT 5.txt"
output_folder = "C:/Users/Irazu/Desktop/Python/Residencia/Excel 2"
output_filename = "VPT 5.xlsx"
output_path = os.path.join(output_folder, output_filename)

columnas_deseadas = [
    "RecordingTime [ms]",
    "Stimulus",
    "Participant",
    "Point of Regard Right X [px]",
    "Point of Regard Right Y [px]",
    "Point of Regard Left X [px]",
    "Point of Regard Left Y [px]",
    "Eye Position Left Z [mm]",
    "Eye Position Right Z [mm]"
]

columnas_numericas = [
    "RecordingTime [ms]",
    "Point of Regard Right X [px]",
    "Point of Regard Right Y [px]",
    "Point of Regard Left X [px]",
    "Point of Regard Left Y [px]",
    "Eye Position Left Z [mm]",
    "Eye Position Right Z [mm]"
]

def procesar_datos():
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("1. Leyendo el archivo...")
    try:
        # Leemos el archivo
        df = pd.read_csv(input_path, sep=',', low_memory=False)

        # Seleccionamos columnas
        cols_existentes = [c for c in columnas_deseadas if c in df.columns]
        df = df[cols_existentes]

        # --- DIAGNÓSTICO (Para que veas qué está leyendo) ---
        print(f"   -> Filas totales leídas: {len(df)}")
        if 'Stimulus' in df.columns:
            print(f"   -> Estímulos encontrados en tu archivo: {df['Stimulus'].unique()}")

        # --- CORRECCIÓN 1: FILTRO AMPLIADO ---
        # Agregamos variaciones con y sin espacio para asegurar que encuentre los datos
        print("2. Filtrando por Estímulo (MO 69, MO 96)...")
        estimulos_validos = ['MO 96', 'MO 69'] 
        df = df[df['Stimulus'].isin(estimulos_validos)]

        if df.empty:
            print("ERROR CRÍTICO: El filtro borró todo. Revisa los nombres de los estímulos impresos arriba.")
            return

        # --- CORRECCIÓN 2: CONVERTIR NUMÉRICOS ---
        print("3. Convirtiendo datos a números...")
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')


        print("4. Eliminando filas que solo tienen nombre (sin coordenadas)...")
        columna_clave = "Point of Regard Right X [px]"
        
        if columna_clave in df.columns:
            filas_antes = len(df)
            df = df.dropna(subset=[columna_clave])
            filas_despues = len(df)
            print(f"   -> Se eliminaron {filas_antes - filas_despues} filas vacías/basura.")

        # --- GUARDAR ---
        print(f"5. Guardando Excel con {len(df)} filas útiles...")
        df.to_excel(output_path, index=False)
        print(f"¡Listo! Archivo guardado en: {output_path}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    procesar_datos()