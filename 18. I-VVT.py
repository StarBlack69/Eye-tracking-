import pandas as pd
import os

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ruta_archivo = r"C:\Ruta\Generica\IVVT.xlsx" 
archivo_salida = r"C:\Ruta\Generica\Resultados_Unicos_IVVT_Numeros.xlsx"

def aplicar_modelo_ivvt_numeros_excel():
    """
    Aplica el algoritmo I-VVT (Identification by Velocity and Velocity Threshold)
    para clasificar muestras en Fijaciones (1), Sacadas (2) y Seguimiento Suave (3)
    utilizando dos umbrales de velocidad estáticos.
    """
    try:
        df = pd.read_excel(ruta_archivo)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de entrada: {ruta_archivo}")
        return

    # Umbrales del modelo I-VVT (en Grados por segundo)
    t_vs = 30.0  # Umbral superior para Sacadas
    t_vp = 10.0  # Umbral inferior para Seguimiento Suave (menor a esto es Fijación)

    df['IVVT'] = 0

    # Lógica de clasificación por velocidad
    df.loc[df['Velocidad_[º/s]'] > t_vs, 'IVVT'] = 2
    df.loc[(df['IVVT'] == 0) & (df['Velocidad_[º/s]'] < t_vp), 'IVVT'] = 1
    df.loc[df['IVVT'] == 0, 'IVVT'] = 3

    try:
        df.to_excel(archivo_salida, index=False)
        print(f"Clasificación I-VVT completada exitosamente. Archivo guardado en: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo Excel: {e}")

if __name__ == "__main__":
    aplicar_modelo_ivvt_numeros_excel()