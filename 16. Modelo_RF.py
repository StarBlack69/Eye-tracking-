import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import warnings
import sys

warnings.filterwarnings('ignore')

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada, modelo y salida]
NUEVO_ARCHIVO = r"C:\Ruta\Generica\1D_2D_RF_MO_50.csv"
NOMBRE_MODELO = r"C:\Ruta\Generica\modelo_rf_optimizado.pkl"
RUTA_SALIDA_IMG = r"C:\Ruta\Generica\matriz_confusion_MO_50_RF.png"
ARCHIVO_EXCEL_FINAL = r"C:\Ruta\Generica\Reporte_RF_MO50.xlsx"

def ejecutar_inferencia_rf():
    """
    Carga un modelo Random Forest pre-entrenado, recrea el contexto temporal
    sobre datos nuevos, ejecuta la inferencia (predicción de clases de 
    movimientos oculares y ruido) y genera reportes de evaluación.
    """
    try:
        df_nuevo = pd.read_csv(NUEVO_ARCHIVO) 
        df_nuevo.columns = df_nuevo.columns.str.strip()
        modelo = joblib.load(NOMBRE_MODELO)
    except Exception as e:
        print(f"Error crítico al cargar archivos: {e}")
        sys.exit()

    if not {'Participant', 'Stimulus'}.issubset(df_nuevo.columns):
        print("Error: El archivo de entrada debe contener las columnas 'Participant' y 'Stimulus'.")
        sys.exit()

    features_dinamicas = [
        'Media_V3_X', 'Media_V3_Y', 'RMS_V3_X', 'RMS_V3_Y', 
        'Ceros_V3_X', 'Ceros_V3_Y', 'Velocidad_[º/s]', 'Dispersion_[º]', 
        'Aceleracion_[º/s2]', 'Curtosis', 'Energia', 'Jerk_[º/s3]', 
        'Residuo_Mediana_X', 'Residuo_Mediana_Y', 'Residuo_Mediana_V'
    ]

    for i in range(1, 4):  
        for col in features_dinamicas:
            if col in df_nuevo.columns:
                df_nuevo[f'{col}_Prev{i}'] = df_nuevo.groupby(['Participant', 'Stimulus'])[col].shift(i)
                df_nuevo[f'{col}_Next{i}'] = df_nuevo.groupby(['Participant', 'Stimulus'])[col].shift(-i)

    df_nuevo.replace([np.inf, -np.inf], np.nan, inplace=True)

    columnas_no_entrenamiento = [
        'Participant', 'Stimulus', 'Etiqueta_A', 'RecordingTime [ms]', 
        'Point of Regard Right X [px]', 'Point of Regard Right Y [px]',
        'Etiqueta_Real_Texto', 'Prediccion_RF', 'Prediccion_Texto_RF'
    ]
    
    columnas_a_rellenar = [c for c in df_nuevo.columns if c not in columnas_no_entrenamiento]

    df_nuevo[columnas_a_rellenar] = df_nuevo.groupby(['Participant', 'Stimulus'])[columnas_a_rellenar].ffill()
    df_nuevo[columnas_a_rellenar] = df_nuevo.groupby(['Participant', 'Stimulus'])[columnas_a_rellenar].bfill()
    df_nuevo.fillna(0, inplace=True)

    try:
        columnas_entrenadas = modelo.feature_names_in_
        X_nuevos = df_nuevo[columnas_entrenadas].astype(np.float32)
        X_nuevos = np.clip(X_nuevos, -1e10, 1e10)
    except Exception as e:
        print(f"Error: Las columnas generadas no coinciden con las del modelo: {e}")
        sys.exit()

    df_nuevo['Prediccion_RF'] = modelo.predict(X_nuevos)

    nombres_etiquetas = {
        1: 'Fijación', 
        2: 'Sacada', 
        4: 'Ruido I', 
        5: 'Ruido II', 
        6: 'Ruido III'
    }

    df_nuevo['Prediccion_Texto_RF'] = df_nuevo['Prediccion_RF'].map(nombres_etiquetas)

    if 'Etiqueta_A' in df_nuevo.columns:
        df_nuevo['Etiqueta_Real_Texto'] = df_nuevo['Etiqueta_A'].map(nombres_etiquetas)
        
        acc = accuracy_score(df_nuevo['Etiqueta_A'], df_nuevo['Prediccion_RF'])
        
        presentes = sorted(list(set(df_nuevo['Etiqueta_A']) | set(df_nuevo['Prediccion_RF'])))
        target_names = [nombres_etiquetas.get(k, f'Clase {k}') for k in presentes]
        
        print("\nReporte de Clasificación (Inferencia):")
        print(f"Precisión Global (Accuracy): {acc * 100:.2f}%\n")
        print(classification_report(df_nuevo['Etiqueta_A'], df_nuevo['Prediccion_RF'], 
                                    labels=presentes, target_names=target_names))

        plt.figure(figsize=(11, 8))
        cm = confusion_matrix(df_nuevo['Etiqueta_A'], df_nuevo['Prediccion_RF'], labels=presentes)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                    xticklabels=target_names, yticklabels=target_names)
        
        plt.title(f'Matriz de Confusión RF - Inferencia (Acc: {acc:.2%})', fontsize=14)
        plt.ylabel('Etiqueta Real', fontsize=12)
        plt.xlabel('Predicción del Modelo', fontsize=12)
        
        plt.savefig(RUTA_SALIDA_IMG, bbox_inches='tight')
        plt.close()

    columnas_export = [
        'RecordingTime [ms]', 
        'Participant', 
        'Stimulus', 
        'Point of Regard Right X [px]',  
        'Point of Regard Right Y [px]',  
        'Etiqueta_A', 
        'Etiqueta_Real_Texto', 
        'Prediccion_RF', 
        'Prediccion_Texto_RF'
    ]

    columnas_finales = [c for c in columnas_export if c in df_nuevo.columns]
    df_excel = df_nuevo[columnas_finales]

    try:
        df_excel.to_excel(ARCHIVO_EXCEL_FINAL, index=False, engine='openpyxl')
        print(f"Reporte de inferencia generado exitosamente en: {ARCHIVO_EXCEL_FINAL}")
        print(f"Matriz de confusión guardada en: {RUTA_SALIDA_IMG}")
    except Exception as e:
        print(f"Error al guardar el reporte Excel: {e}")

if __name__ == "__main__":
    ejecutar_inferencia_rf()