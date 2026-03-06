import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
import sys

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
RUTA_ENTRADA = r"C:\Ruta\Generica\119_exacto_filas.xlsx"
RUTA_SALIDA = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6_NZ.xlsx"

if os.path.exists(RUTA_SALIDA):
    try:
        with open(RUTA_SALIDA, "a"): pass
    except PermissionError:
        print("Error: El archivo de salida está abierto en otro programa. Ciérralo antes de continuar.")
        sys.exit()

df = pd.read_excel(RUTA_ENTRADA)

cols_pixel = ['Point of Regard Right X [px]', 'Point of Regard Right Y [px]']
nuevas_cols = [
    'Point of Regard Right X (Z)', 
    'Point of Regard Right Y (Z)'
]

scaler = StandardScaler()
df[nuevas_cols] = scaler.fit_transform(df[cols_pixel])

if 'Etiqueta_A' in df.columns:
    idx = df.columns.get_loc('Etiqueta_A')
    
    columnas_restantes = [c for c in df.columns if c not in nuevas_cols]
    
    nuevo_orden = (
        columnas_restantes[:idx] + 
        nuevas_cols + 
        columnas_restantes[idx:]
    )
    
    df = df[nuevo_orden]
else:
    print("Advertencia: No se encontró la columna 'Etiqueta_A'. Las nuevas columnas estandarizadas se añadieron al final del archivo.")

df.to_excel(RUTA_SALIDA, index=False)
print(f"Archivo estandarizado guardado exitosamente en: {RUTA_SALIDA}")