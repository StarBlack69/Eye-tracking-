import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import warnings

# Configuración de alertas
warnings.filterwarnings('ignore')

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y ARCHIVOS
# ==========================================
# Asegúrate de que estas rutas sean correctas en tu ordenador
NUEVO_ARCHIVO = r"C:\Users\david\Desktop\EYE TRACKING\PYTHON\1D_2D_RF_MO_50.csv"
NOMBRE_MODELO = r'C:/Users/david/Desktop/EYE TRACKING/PYTHON/modelo_rf_optimizado.pkl'
RUTA_SALIDA_IMG = r'C:\Users\david\Desktop\EYE TRACKING\PYTHON\matriz_confusion_MO_50_RF_1_1.png'
ARCHIVO_EXCEL_FINAL = r'C:\Users\david\Desktop\EYE TRACKING\PYTHON\Reporte_RF_MO50.xlsx'

print(" Iniciando proceso: Cargando cerebro (RF) y datos de Kiara...")

try:
    df_nuevo = pd.read_csv(NUEVO_ARCHIVO) 
    df_nuevo.columns = df_nuevo.columns.str.strip()
    
    modelo = joblib.load(NOMBRE_MODELO)
    print(" Modelo Random Forest y dataset cargados con éxito.")
except Exception as e:
    print(f" Error crítico al cargar archivos: {e}")
    exit()

# Validación de estructura mínima para el groupby
if not {'Participant', 'Stimulus'}.issubset(df_nuevo.columns):
    print(" ERROR: El archivo debe contener las columnas 'Participant' y 'Stimulus'.")
    exit()

# ==========================================
# 2. RECREAR CONTEXTO TEMPORAL (VENTANA ±3)
# ==========================================
features_dinamicas = [
    'Media_V3_X', 'Media_V3_Y', 'RMS_V3_X', 'RMS_V3_Y', 
    'Ceros_V3_X', 'Ceros_V3_Y', 'Velocidad_[º/s]', 'Dispersion_[º]', 
    'Aceleracion_[º/s2]', 'Curtosis', 'Energia', 'Jerk_[º/s3]', 
    'Residuo_Mediana_X', 'Residuo_Mediana_Y', 'Residuo_Mediana_V'
]

print(" Reconstruyendo memoria temporal (Ventana ±3)...")
for i in range(1, 4):  
    for col in features_dinamicas:
        if col in df_nuevo.columns:
            df_nuevo[f'{col}_Prev{i}'] = df_nuevo.groupby(['Participant', 'Stimulus'])[col].shift(i)
            df_nuevo[f'{col}_Next{i}'] = df_nuevo.groupby(['Participant', 'Stimulus'])[col].shift(-i)

print(" Aplicando limpieza y relleno de nulos...")
df_nuevo.replace([np.inf, -np.inf], np.nan, inplace=True)

# Definimos columnas que no son features de entrenamiento
columnas_no_entrenamiento = [
    'Participant', 'Stimulus', 'Etiqueta_A', 'RecordingTime [ms]', 
    'Point of Regard Right X [px]', 'Point of Regard Right Y [px]',
    'Etiqueta_Real_Texto', 'Prediccion_RF', 'Prediccion_Texto_RF'
]
columnas_a_rellenar = [c for c in df_nuevo.columns if c not in columnas_no_entrenamiento]

# Relleno inteligente por grupo para no contaminar entre sujetos
df_nuevo[columnas_a_rellenar] = df_nuevo.groupby(['Participant', 'Stimulus'])[columnas_a_rellenar].ffill()
df_nuevo[columnas_a_rellenar] = df_nuevo.groupby(['Participant', 'Stimulus'])[columnas_a_rellenar].bfill()
df_nuevo.fillna(0, inplace=True)

# ==========================================
# 3. ALINEACIÓN CON EL MODELO
# ==========================================
print(" Alineando variables con la estructura del Random Forest...")
try:
    # Extraer el orden exacto de columnas que espera el modelo guardado
    columnas_entrenadas = modelo.feature_names_in_
    X_nuevos = df_nuevo[columnas_entrenadas].astype(np.float32)
    X_nuevos = np.clip(X_nuevos, -1e10, 1e10)
except Exception as e:
    print(f" ERROR: Las columnas generadas no coinciden con el modelo: {e}")
    exit()

# ==========================================
# 4. PREDICCIÓN E INFERENCIA (RF)
# ==========================================
print(" Ejecutando inferencia con Random Forest (RF)...")
df_nuevo['Prediccion_RF'] = modelo.predict(X_nuevos)

# Diccionario de traducción de etiquetas
nombres_etiquetas = {
    1: 'Fijación', 
    2: 'Sacada', 
    4: 'Ruido I', 
    5: 'Ruido II', 
    6: 'Ruido III'
}

df_nuevo['Prediccion_Texto_RF'] = df_nuevo['Prediccion_RF'].map(nombres_etiquetas)

# ==========================================
# 5. EVALUACIÓN Y MÉTRICAS
# ==========================================
if 'Etiqueta_A' in df_nuevo.columns:
    print("\n" + "═"*50)
    print(" RESULTADOS FINALES DEL MODELO RF")
    print("═"*50)
    
    df_nuevo['Etiqueta_Real_Texto'] = df_nuevo['Etiqueta_A'].map(nombres_etiquetas)
    
    # 1. Precisión Global
    acc = accuracy_score(df_nuevo['Etiqueta_A'], df_nuevo['Prediccion_RF'])
    print(f" PRECISIÓN GLOBAL (ACCURACY RF): {acc * 100:.2f}%")
    print("-" * 50)
    
    # 2. Reporte Detallado
    presentes = sorted(list(set(df_nuevo['Etiqueta_A']) | set(df_nuevo['Prediccion_RF'])))
    target_names = [nombres_etiquetas.get(k, f'Clase {k}') for k in presentes]
    
    print(" DETALLE POR CATEGORÍA:")
    print(classification_report(df_nuevo['Etiqueta_A'], df_nuevo['Prediccion_RF'], 
                                labels=presentes, target_names=target_names))

    # 3. Matriz de Confusión Visual
    plt.figure(figsize=(11, 8))
    cm = confusion_matrix(df_nuevo['Etiqueta_A'], df_nuevo['Prediccion_RF'], labels=presentes)
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                xticklabels=target_names, yticklabels=target_names)
    
    plt.title(f'Matriz de Confusión RF - Precisión: {acc:.2%}', fontsize=14)
    plt.ylabel('Etiqueta_A', fontsize=12)
    plt.xlabel('Random Forest', fontsize=12)
    
    plt.savefig(RUTA_SALIDA_IMG, bbox_inches='tight')
    print(f" Matriz visual guardada en: {RUTA_SALIDA_IMG}")
    plt.show()

# ==========================================
# 6. EXPORTACIÓN A EXCEL
# ==========================================
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

# Filtrar solo las que existen para evitar errores
columnas_finales = [c for c in columnas_export if c in df_nuevo.columns]
df_excel = df_nuevo[columnas_finales]

print(f"\n Generando reporte Excel final...")
try:
    df_excel.to_excel(ARCHIVO_EXCEL_FINAL, index=False, engine='openpyxl')
    print(f" ¡PROCESO COMPLETADO!")
    print(f" Archivo disponible en: {ARCHIVO_EXCEL_FINAL}")
except Exception as e:
    print(f" Error al guardar Excel: {e}")