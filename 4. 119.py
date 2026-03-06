import pandas as pd

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ruta_entrada = "C:/Ruta/Generica/Archivo_Entrada.xlsx"
ruta_salida_datos_ajustados = "C:/Ruta/Generica/119_exacto_filas.xlsx"

TARGET_ROWS = 119

def ajustar_filas_por_grupo(grupo_df):
    """
    Ajusta cada grupo a un número exacto de filas (TARGET_ROWS).
    Si faltan filas, duplica la última. Si sobran, recorta el exceso.
    """
    current_rows = len(grupo_df)
    
    if current_rows == TARGET_ROWS:
        return grupo_df
    
    elif current_rows < TARGET_ROWS:
        n_missing = TARGET_ROWS - current_rows
        last_row_df = grupo_df.iloc[[-1]] 
        rows_to_add = pd.concat([last_row_df] * n_missing, ignore_index=True)
        return pd.concat([grupo_df, rows_to_add], ignore_index=True)
    
    else:
        return grupo_df.head(TARGET_ROWS)

try:
    df = pd.read_excel(ruta_entrada)
    
    df_ajustado = df.groupby(['Participant', 'Stimulus']).apply(ajustar_filas_por_grupo).reset_index(drop=True)
    
    df_ajustado.to_excel(ruta_salida_datos_ajustados, index=False)
    print(f"Datos ajustados exitosamente a {TARGET_ROWS} filas por grupo.")
    print(f"Archivo guardado en: {ruta_salida_datos_ajustados}")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo en: {ruta_entrada}")
except KeyError as e:
    print(f"Error de columnas: Faltan las columnas 'Participant' o 'Stimulus' -> {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")