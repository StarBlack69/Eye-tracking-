import pandas as pd
import os

def calcular_dispersion_grados(df_ventana):
    """
    Calcula la dispersión sumando el rango máximo de movimiento 
    en ángulos (ejes X e Y) dentro de la ventana temporal actual.
    """
    disp_x = df_ventana['Angulo_X_[º]'].max() - df_ventana['Angulo_X_[º]'].min()
    disp_y = df_ventana['Angulo_Y_[º]'].max() - df_ventana['Angulo_Y_[º]'].min()
    return disp_x + disp_y

def aplicar_ivdt_por_grupo(df, t_v, t_d, t_w):
    """
    Aplica el algoritmo I-VDT (Identification by Velocity and Dispersion Threshold)
    para clasificar muestras en Fijaciones (1), Sacadas (2) y Seguimiento Suave (3).
    Aísla la ejecución por bloques de participante y estímulo.
    """
    df = df.copy()
    col_vel = 'Velocidad_[º/s]'
    
    df['IVDT'] = 0
    col_idx = df.columns.get_loc('IVDT')
    
    df.loc[df[col_vel] > t_v, 'IVDT'] = 2
    
    i = 0
    n = len(df)
    
    while i <= n - t_w:
        if df.iloc[i, col_idx] == 2:
            i += 1
            continue
            
        fin_ventana = i + t_w
        ventana = df.iloc[i:fin_ventana]
        
        if (ventana['IVDT'] == 2).any():
            df.iloc[i, col_idx] = 3
            i += 1
            continue
            
        dispersion = calcular_dispersion_grados(ventana)
        
        if dispersion < t_d:
            while fin_ventana <= n:
                disp_actual = calcular_dispersion_grados(df.iloc[i:fin_ventana])
                
                if disp_actual >= t_d or (fin_ventana < n and df.iloc[fin_ventana, col_idx] == 2):
                    break
                fin_ventana += 1
            
            df.iloc[i:fin_ventana-1, col_idx] = 1
            i = fin_ventana - 1 
        else:
            df.iloc[i, col_idx] = 3
            i += 1
            
    df.loc[df['IVDT'] == 0, 'IVDT'] = 3
    
    return df

def ejecutar_modelo_ivdt_excel():
    # [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
    ruta_archivo = r"C:\Ruta\Generica\IVDT.xlsx"
    archivo_salida = r"C:\Ruta\Generica\Resultados_IVDT.xlsx"
    
    try:
        df_original = pd.read_excel(ruta_archivo)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de entrada: {ruta_archivo}")
        return

    # Parámetros I-VDT
    t_v = 30.0  # Umbral de velocidad (30 º/s)
    t_d = 1.0   # Umbral de dispersión (1.0 Grado visual)
    t_w = 12    # Ventana temporal (12 muestras a 120Hz = ~100 ms)
    
    grupos = df_original.groupby(['Participant', 'Stimulus'])
    dfs_procesados = []
    
    for _, df_grupo in grupos:
        df_resultado_grupo = aplicar_ivdt_por_grupo(df_grupo, t_v, t_d, t_w)
        dfs_procesados.append(df_resultado_grupo)
        
    df_final = pd.concat(dfs_procesados, ignore_index=True)

    try:
        df_final.to_excel(archivo_salida, index=False)
        print(f"Clasificación I-VDT completada exitosamente. Archivo guardado en: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo Excel: {e}")

if __name__ == "__main__":
    ejecutar_modelo_ivdt_excel()