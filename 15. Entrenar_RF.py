import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ARCHIVO_CSV = r"C:\Ruta\Generica\1D_2D_RF_Base_Final.csv" 
RUTA_BASE = r"C:\Ruta\Generica\\"

def entrenar_modelo_random_forest():
    """
    Entrena un clasificador Random Forest para datos de Eye Tracking.
    Incluye generación de contexto temporal (ventana ±3), split por grupos 
    (Participante-Estímulo), balanceo de clases (Under/Over sampling) y 
    exportación del modelo, matriz de confusión y feature importance.
    """
    print("Cargando el dataset principal...")
    df = pd.read_csv(ARCHIVO_CSV)
    df.columns = df.columns.str.strip()

    # 1. CONTEXTO TEMPORAL (VENTANA ±3)
    features_dinamicas = [
        'Media_V3_X', 'Media_V3_Y', 'RMS_V3_X', 'RMS_V3_Y', 
        'Ceros_V3_X', 'Ceros_V3_Y', 'Velocidad_[º/s]', 'Dispersion_[º]', 
        'Aceleracion_[º/s2]', 'Curtosis', 'Energia', 'Jerk_[º/s3]', 
        'Residuo_Mediana_X', 'Residuo_Mediana_Y', 'Residuo_Mediana_V'
    ]

    print("Generando memoria temporal profunda (Ventana ±3)...")
    for i in range(1, 4):
        for col in features_dinamicas:
            if col in df.columns:
                df[f'{col}_Prev{i}'] = df.groupby(['Participant', 'Stimulus'])[col].shift(i)
                df[f'{col}_Next{i}'] = df.groupby(['Participant', 'Stimulus'])[col].shift(-i)

    print("Aplicando relleno para evitar valores nulos (NaN/Inf)...")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    cols_a_eliminar = [
        'Participant', 'Stimulus', 'Etiqueta_A', 'RecordingTime [ms]', 
        'Point of Regard Right X [px]', 'Point of Regard Right Y [px]', 
        'Point of Regard Binocular X [px]', 'Point of Regard Binocular Y [px]',
        'Angulo_X_[º]', 'Angulo_Y_[º]', 'Sujeto_Estimulo'
    ]

    columnas_a_rellenar = [c for c in df.columns if c not in cols_a_eliminar]
    df[columnas_a_rellenar] = df.groupby(['Participant', 'Stimulus'])[columnas_a_rellenar].ffill()
    df[columnas_a_rellenar] = df.groupby(['Participant', 'Stimulus'])[columnas_a_rellenar].bfill()
    df.fillna(0, inplace=True)

    # 2. SPLIT POR PARTICIPANTE Y ESTÍMULO
    print("Dividiendo datos por grupos únicos (Participante-Estímulo)...")
    df['Sujeto_Estimulo'] = df['Participant'].astype(str) + "_" + df['Stimulus'].astype(str)
    grupos_unicos = df['Sujeto_Estimulo'].nunique()

    if grupos_unicos > 1:
        gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
        train_idx, test_idx = next(gss.split(df, groups=df['Sujeto_Estimulo']))
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]
    else:
        split_point = int(len(df) * 0.8)
        train_df = df.iloc[:split_point]
        test_df = df.iloc[split_point:]

    total_muestras = len(df)
    muestras_train = len(train_df)
    muestras_test = len(test_df)
    pct_train = (muestras_train / total_muestras) * 100
    pct_test = (muestras_test / total_muestras) * 100

    print(f"Total de muestras originales: {total_muestras}")
    print(f"Muestras para Entrenamiento:  {muestras_train} ({pct_train:.2f}%)")
    print(f"Muestras para Prueba (Test):  {muestras_test} ({pct_test:.2f}%)")

    X_train_raw = train_df.drop(columns=[c for c in cols_a_eliminar if c in train_df.columns], errors='ignore').astype(np.float32)
    y_train_raw = train_df['Etiqueta_A']
    X_test = test_df.drop(columns=[c for c in cols_a_eliminar if c in test_df.columns], errors='ignore').astype(np.float32)
    y_test = test_df['Etiqueta_A']

    # 3. BALANCEO
    print("Balanceando las clases del conjunto de entrenamiento...")
    META_ALTA = 4000 
    META_BAJA = 4000 

    under = RandomUnderSampler(sampling_strategy={c: META_ALTA for c in y_train_raw.value_counts()[y_train_raw.value_counts() > META_ALTA].index}, random_state=42)
    X_under, y_under = under.fit_resample(X_train_raw, y_train_raw)

    over = RandomOverSampler(sampling_strategy={c: META_BAJA for c in y_under.value_counts()[y_under.value_counts() < META_BAJA].index}, random_state=42)
    X_bal, y_bal = over.fit_resample(X_under, y_under)

    # 4. ENTRENAMIENTO
    print("Entrenando el modelo Random Forest...")
    pesos = {1: 1, 2: 3, 4: 15, 5: 2, 6: 5}
    rf_definitivo = RandomForestClassifier(n_estimators=500, max_depth=30, min_samples_leaf=2, class_weight=pesos, random_state=42, n_jobs=-1)
    rf_definitivo.fit(X_bal, y_bal)

    # 5. EVALUACIÓN Y MATRIZ
    print("\nEvaluando el modelo...")
    y_pred = rf_definitivo.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"PRECISIÓN GLOBAL (ACCURACY): {acc * 100:.2f}%")

    mapa_nombres = {
        1: "Fijación",
        2: "Sacada",
        4: "Ruido I",
        5: "Ruido II",
        6: "Ruido III"
    }

    labels_presentes = sorted(list(set(y_test) | set(y_pred)))
    nombres_labels = [mapa_nombres.get(l, f"E{l}") for l in labels_presentes]

    print("\nREPORTE POR CATEGORÍA:")
    print(classification_report(y_test, y_pred, target_names=nombres_labels))

    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_test, y_pred, labels=labels_presentes)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=nombres_labels, 
                yticklabels=nombres_labels)

    plt.title(f'Matriz de Confusión - Precisión Global: {acc:.2%}')
    plt.xlabel('Predicción del Modelo')
    plt.ylabel('Etiqueta Real')

    ruta_matriz = RUTA_BASE + 'Matriz_Confusion.png'
    plt.savefig(ruta_matriz, bbox_inches='tight')
    plt.close()

    # 6. GUARDAR MODELO
    joblib.dump(rf_definitivo, RUTA_BASE + 'modelo_rf_optimizado.pkl')
    joblib.dump(X_train_raw.columns.tolist(), RUTA_BASE + 'columnas_modelo_definitivo.pkl')
    print(f"Modelo y columnas guardados en: {RUTA_BASE}")

    # 7. IMPORTANCIA DE VARIABLES
    print("Calculando importancia de variables (Feature Importance)...")
    importancias = rf_definitivo.feature_importances_
    nombres_columnas = X_train_raw.columns

    df_importancias = pd.DataFrame({
        'Variable': nombres_columnas,
        'Importancia': importancias
    }).sort_values(by='Importancia', ascending=False)

    print("\nTop 10 Variables Más Importantes:")
    print(df_importancias.head(10).to_string(index=False))

    plt.figure(figsize=(10, 8))
    sns.barplot(x='Importancia', y='Variable', data=df_importancias.head(10), palette='mako')
    plt.title('Importancia Relativa de Variables - Random Forest')
    plt.xlabel('Importancia Relativa')
    plt.ylabel('Variable')
    plt.tight_layout()

    ruta_importancia = RUTA_BASE + 'Importancia_Variables_Top10.png'
    plt.savefig(ruta_importancia, bbox_inches='tight')
    plt.close()

    ruta_csv_importancias = RUTA_BASE + 'Importancia_Todas_Las_Variables.csv'
    df_importancias.to_csv(ruta_csv_importancias, index=False)
    print(f"Gráficos y CSV de importancias generados exitosamente.")

if __name__ == "__main__":
    entrenar_modelo_random_forest()