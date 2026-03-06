import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# [DATO PRIVADO ELIMINADO - Lista real de nombres de participantes y estímulos]
PLAN_INYECCION = [
    {'Participante': 'Participante_01', 'Estimulo': 'MO 27'},
    {'Participante': 'Participante_01', 'Estimulo': 'MO 9'},
    {'Participante': 'Participante_02', 'Estimulo': 'MO 27'},
    # ... Agrega aquí el resto de tu diccionario de forma anonimizada
]

# [DATO PRIVADO ELIMINADO - Rutas de archivos de entrada y salida]
RUTA_ENTRADA = r"C:\Ruta\Generica\1D_2D_Dep_RF.xlsx" 
RUTA_SALIDA = r"C:\Ruta\Generica\1D_2D_RF_Ruido_6.xlsx"

NUM_COPIAS = 10 

def inyectar_ruido_total(df_orig, plan, num_copias):
    """
    Genera clones de los datos originales e inyecta anomalías sintéticas.
    Simula Ruido I (Picos aislados) y Ruido III (Ráfagas sostenidas)
    en variantes Micro y Macro sobre las muestras etiquetadas como fijación.
    """
    cols_base = ['RecordingTime [ms]', 'Stimulus', 'Participant', 
                 'Point of Regard Right X [px]', 'Point of Regard Right Y [px]', 
                 'Eye Position Right Z [mm]', 'Etiqueta_A']
    
    cols_presentes = [c for c in cols_base if c in df_orig.columns]
    df_resultado = df_orig[cols_presentes].copy()
    lista_copias = []
    
    count_r4_micro = 0
    count_r4_macro = 0
    count_r6_micro = 0
    count_r6_macro = 0

    for num_ronda in range(1, num_copias + 1):
        for tarea in plan:
            sujeto_orig = tarea['Participante']
            stim = tarea['Estimulo']
            
            copia = df_resultado[(df_resultado['Participant'] == sujeto_orig) & 
                                 (df_resultado['Stimulus'] == stim)].copy()
            if copia.empty: continue
            
            copia['Participant'] = copia['Participant'] + f"_Clon{num_ronda}"
            
            n_eventos = np.random.randint(10, 18) 
            indices_fijacion = copia[copia['Etiqueta_A'] == 1].index.tolist()
            candidatos = indices_fijacion.copy()
            
            for _ in range(n_eventos):
                if not candidatos: break 
                idx = np.random.choice(candidatos)
                
                # 60% Ruido I, 40% Ruido III
                tipo_evento = np.random.choice([4, 6], p=[0.6, 0.4])
                
                if tipo_evento == 4:
                    # Lógica Ruido I (75% Micro, 25% Macro)
                    duracion = np.random.choice([1, 2, 3]) 
                    tipo_tamano_r4 = np.random.choice(['Micro', 'Macro'], p=[0.75, 0.25])
                    
                    if tipo_tamano_r4 == 'Micro':
                        salto_base_x = np.random.uniform(10, 45) * np.random.choice([1, -1])
                        salto_base_y = np.random.uniform(10, 30) * np.random.choice([1, -1])
                    else:
                        salto_base_x = np.random.uniform(50, 500) * np.random.choice([1, -1])
                        salto_base_y = np.random.uniform(40, 350) * np.random.choice([1, -1])
                    
                    for f in range(duracion):
                        cur_idx = idx + f
                        if cur_idx in copia.index:
                            jitter = np.random.uniform(0.5, 1.5) 
                            copia.at[cur_idx, 'Point of Regard Right X [px]'] += (salto_base_x * jitter)
                            copia.at[cur_idx, 'Point of Regard Right Y [px]'] += (salto_base_y * jitter)
                            copia.at[cur_idx, 'Etiqueta_A'] = 4
                            
                            if tipo_tamano_r4 == 'Micro':
                                count_r4_micro += 1
                            else:
                                count_r4_macro += 1
                                
                    distancia = 10 
                
                else:
                    # Lógica Ruido III (50% Micro, 50% Macro)
                    duracion = np.random.randint(5, 15) 
                    tipo_tamano_r6 = np.random.choice(['Micro', 'Macro'], p=[0.5, 0.5])
                    
                    for f in range(duracion):
                        cur_idx = idx + f
                        if cur_idx in copia.index:
                            if tipo_tamano_r6 == 'Micro':
                                salto_caotico_x = np.random.uniform(10, 45) * np.random.choice([1, -1])
                                salto_caotico_y = np.random.uniform(10, 30) * np.random.choice([1, -1])
                            else:
                                salto_caotico_x = np.random.uniform(60, 550) * np.random.choice([1, -1])
                                salto_caotico_y = np.random.uniform(50, 350) * np.random.choice([1, -1])
                                
                            copia.at[cur_idx, 'Point of Regard Right X [px]'] += salto_caotico_x
                            copia.at[cur_idx, 'Point of Regard Right Y [px]'] += salto_caotico_y
                            copia.at[cur_idx, 'Etiqueta_A'] = 6
                            
                            if tipo_tamano_r6 == 'Micro':
                                count_r6_micro += 1
                            else:
                                count_r6_macro += 1
                                
                    distancia = 20 

                candidatos = [x for x in candidatos if abs(x - idx) > distancia]
            lista_copias.append(copia)

    df_final = pd.concat([df_resultado] + lista_copias, ignore_index=True)
    
    print("\nReporte de inyección de ruido:")
    print(f" - Ruido I (Micro): {count_r4_micro} frames")
    print(f" - Ruido I (Macro): {count_r4_macro} frames")
    print(f" - Ruido III (Micro): {count_r6_micro} frames")
    print(f" - Ruido III (Macro): {count_r6_macro} frames")
    
    return df_final


try:
    df_original = pd.read_excel(RUTA_ENTRADA)
    df_aumentado = inyectar_ruido_total(df_original, PLAN_INYECCION, NUM_COPIAS)
    df_aumentado.to_excel(RUTA_SALIDA, index=False)
    print(f"\nArchivo guardado exitosamente en: {RUTA_SALIDA}")
except Exception as e:
    print(f"Ocurrió un error: {e}")