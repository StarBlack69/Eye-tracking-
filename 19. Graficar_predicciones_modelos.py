import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import sys

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
ruta_archivo = r"C:\Ruta\Generica\RF_SVM_IVVT_IVDT_MO50.xlsx"
carpeta_salida = r"C:\Ruta\Generica\Predicion_modelos_RF_SVM_IVVT_IVDT"

COL_X = 'Point of Regard Right X [px]'
COL_Y = 'Point of Regard Right Y [px]'
COL_ETIQUETA_REAL = 'Etiqueta_A'
COL_RF = 'RF'
COL_SVM = 'SVM'
COL_IVVT = 'IVVT'
COL_IVDT = 'IVDT'

mapa_colores = {
    1: 'steelblue', 2: 'forestgreen', 3: 'blueviolet',
    4: 'red', 5: 'cyan', 6: 'gold', 7: 'saddlebrown'
}

nombres_etiquetas = {
    1: 'Fijación', 2: 'Sacada', 3: 'Seguimiento Suave',
    4: 'Ruido C I', 5: 'Ruido C II', 6: 'Ruido C III', 7: 'Parpadeo'
}

def obtener_intervalos(etiquetas, valor):
    """
    Encuentra los intervalos continuos de una etiqueta específica 
    para poder dibujar los bloques de color continuos en la gráfica.
    """
    intervalos = []
    inicio = None
    for i, v in enumerate(etiquetas):
        if v == valor and inicio is None:
            inicio = i
        elif v != valor and inicio is not None:
            intervalos.append((inicio, i - inicio))
            inicio = None
    if inicio is not None:
        intervalos.append((inicio, len(etiquetas) - inicio))
    return intervalos

def graficar_comparativa_modelos():
    """
    Genera gráficas comparativas que muestran las coordenadas de la mirada 
    junto a una barra de color apilada con las predicciones de distintos modelos 
    (Etiqueta Real, RF, SVM, I-VVT, I-VDT) para un análisis de concordancia visual.
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    try:
        df = pd.read_excel(ruta_archivo)
        grupos = df.groupby(['Participant', 'Stimulus'])
    except Exception as e:
        print(f"Error al cargar el archivo de entrada: {e}")
        sys.exit()

    for i, ((paciente, estimulo), df_paciente) in enumerate(grupos):
        
        subset = df_paciente.iloc[:119].copy()
        subset.columns = subset.columns.str.strip()

        datos_x = subset[COL_X].values
        datos_y = subset[COL_Y].values
        
        et_real = subset[COL_ETIQUETA_REAL].values
        et_rf   = subset[COL_RF].values
        et_svm  = subset[COL_SVM].values
        et_ivvt = subset[COL_IVVT].values
        et_ivdt = subset[COL_IVDT].values
        
        x_axis = np.arange(len(datos_x))
        
        fig, ax = plt.subplots(figsize=(13, 8))
        
        ax.plot(x_axis, datos_x, color='darkblue', label='Mirada X', linewidth=2, zorder=5, alpha=0.9)
        ax.plot(x_axis, datos_y, color='darkorange', label='Mirada Y', linewidth=2, zorder=5, alpha=0.9)

        series_a_graficar = [
            (et_real, 'Etiqueta A'),
            (et_rf,   'RF'),
            (et_svm,  'SVM'),
            (et_ivvt, 'I-VVT'),
            (et_ivdt, 'I-VDT')
        ]
        
        y_base = -350
        altura_fila = 50
        
        for valor_et, color in mapa_colores.items():
            for indice_fila, (datos_etiqueta, nombre) in enumerate(series_a_graficar):
                row_y = y_base + (4 - indice_fila) * altura_fila
                
                bloques = obtener_intervalos(datos_etiqueta, valor_et)
                if bloques:
                    ax.broken_barh(bloques, (row_y, altura_fila), 
                                   facecolors=color, edgecolor='black', linewidth=0.5, zorder=4)

        for indice_fila, (datos_etiqueta, nombre) in enumerate(series_a_graficar):
            row_y = y_base + (4 - indice_fila) * altura_fila
            ax.plot([0, 118], [row_y + altura_fila, row_y + altura_fila], color='black', lw=1.2, zorder=6)
            
            if indice_fila == len(series_a_graficar) - 1:
                ax.plot([0, 118], [row_y, row_y], color='black', lw=1.2, zorder=6)
                
            ax.text(120, row_y + (altura_fila * 0.5), nombre, fontsize=10, va='center', fontweight='bold')

        for x_val in range(0, 121, 10):
            ax.axvline(x=x_val, color='gray', linestyle='-', alpha=0.15, linewidth=0.8, zorder=1)

        handles_leyenda = []
        et_uniques = np.unique(np.concatenate([et_real, et_rf, et_svm, et_ivvt, et_ivdt]))
        for et in sorted(et_uniques):
            if et in mapa_colores:
                handles_leyenda.append(mpatches.Patch(color=mapa_colores[et], label=nombres_etiquetas.get(et, str(et))))
        
        ax.legend(handles=handles_leyenda, loc='upper right', frameon=False, fontsize='small')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5)
        ax.tick_params(width=2.5, length=8, labelsize=10)

        ax.set_xlim(-2, 128)
        ax.set_ylim(y_base - 50, 1900)
        
        ax.set_title(f"Registro - Sujeto {i + 1:02d}", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Muestras", fontweight='bold')
        ax.set_ylabel("Posición [px]", fontweight='bold')
        
        plt.tight_layout()
        
        nombre_archivo_img = f"Sujeto_{i + 1:02d}_Stacked_Colors.png"
        plt.savefig(os.path.join(carpeta_salida, nombre_archivo_img), dpi=150, bbox_inches='tight')
        plt.close()

    print(f"Proceso finalizado. Gráficas generadas exitosamente en: {carpeta_salida}")

if __name__ == "__main__":
    graficar_comparativa_modelos()