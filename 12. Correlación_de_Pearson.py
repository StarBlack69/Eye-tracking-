import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida de imagen]
RUTA_ARCHIVO = r"C:\Ruta\Generica\Metricas_x_y_finales.xlsx"
RUTA_IMAGEN_SALIDA = r"C:\Ruta\Generica\Mapa_Calor_Correlacion.png"

UMBRAL_CORRELACION = 0.90

def analizar_correlacion_pearson():
    """
    Calcula la matriz de correlación de Pearson (valor absoluto) para las métricas,
    genera un mapa de calor y sugiere la eliminación de características 
    redundantes basadas en un umbral establecido para optimizar modelos de ML.
    """
    try:
        df = pd.read_excel(RUTA_ARCHIVO)
        cols = df.columns.tolist()
        col_pivote = 'Point of Regard Right Y [px]'
        
        if col_pivote not in cols:
            raise ValueError(f"No se encontró la columna pivote: {col_pivote}")

        indice_inicio = cols.index(col_pivote) + 1
        columnas_metricas = cols[indice_inicio:]

        metricas_finales = [c for c in columnas_metricas if 'Etiqueta' not in c]
        
        df_corr = df[metricas_finales].corr().abs()

        # Parte 1: Generar mapa de calor
        figsize_calc = max(12, len(metricas_finales) * 0.5) 
        plt.figure(figsize=(figsize_calc, figsize_calc * 0.8))

        sns.heatmap(
            df_corr,
            vmin=0, vmax=1,
            cmap='YlOrRd',
            annot=False,
            square=True,
            cbar_kws={'label': 'Grado de Correlación Absoluta (0 a 1)'}
        )

        plt.title('Mapa de Calor de Correlación entre Métricas', fontsize=16)
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()

        plt.savefig(RUTA_IMAGEN_SALIDA, dpi=300)
        plt.close() 

        # Parte 2: Análisis de redundancia
        upper_tri = df_corr.where(np.triu(np.ones(df_corr.shape), k=1).astype(bool))

        pares_redundantes = []
        columnas_a_eliminar_sugeridas = set()

        for columna in upper_tri.columns:
            for fila_idx, valor_corr in upper_tri[columna].items():
                if valor_corr > UMBRAL_CORRELACION:
                    pares_redundantes.append((fila_idx, columna, valor_corr))
                    columnas_a_eliminar_sugeridas.add(columna)

        print(f"Análisis completado. Imagen guardada en: {RUTA_IMAGEN_SALIDA}")
        
        if not pares_redundantes:
            print("No se encontraron pares de métricas con correlación superior al umbral.")
        else:
            print(f"\nReporte de Redundancia (Umbral > {UMBRAL_CORRELACION}):")
            print(f"{'Métrica 1':<30} | {'Métrica 2':<30} | {'Correlación':<10}")
            print("-" * 75)
            for m1, m2, corr in pares_redundantes:
                print(f"{m1:<30} | {m2:<30} | {corr:.4f}")

            print("\nSugerencia: Eliminar las siguientes columnas antes de entrenar el modelo:")
            for col in sorted(list(columnas_a_eliminar_sugeridas)):
                print(f" - {col}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta: {RUTA_ARCHIVO}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    analizar_correlacion_pearson()