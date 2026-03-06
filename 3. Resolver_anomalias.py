import pandas as pd
import numpy as np

def clean_eye_tracking_final(df):
    
    cols_to_average = [
        'Point of Regard Right X [px]', 'Point of Regard Right Y [px]', 
        'Point of Regard Left X [px]', 'Point of Regard Left Y [px]', 
        'Eye Position Left Z [mm]', 'Eye Position Right Z [mm]'
    ]
    
    df['RecordingTime [ms]'] = pd.to_numeric(df['RecordingTime [ms]'], errors='coerce')
    df['RecordingTime [ms]'] = df['RecordingTime [ms]'].round(4)
    
    if 'Correction_Type' in df.columns:
        df.rename(columns={'Correction_Type': 'Historial_Previo'}, inplace=True)
    
    df = df.sort_values(by=['Participant', 'Stimulus', 'RecordingTime [ms]']).reset_index(drop=True)
    
    if 'Original_Row_Index' not in df.columns:
        df['Original_Row_Index'] = df.index
    
    corrected_rows = []
    stats = {'split': 0, 'merge': 0, 'duplicate_fix': 0}

    grouped = df.groupby(['Participant', 'Stimulus'])

    for (participant, stimulus), group in grouped:
        rows = group.to_dict('records')
        n = len(rows)
        i = 0
        
        while i < n:
            current_row = rows[i]
            
            # Primera fila del bloque
            if i == 0:
                current_row['Correction_Type'] = 'Inicio_Bloque' if 'Historial_Previo' not in current_row else 'Normal'
                current_row['Debug_Delta_ms'] = 0
                corrected_rows.append(current_row)
                i += 1
                continue
            
            prev_row = corrected_rows[-1]
            prev_time = prev_row['RecordingTime [ms]']
            curr_time = current_row['RecordingTime [ms]']
            
            dt = round(curr_time - prev_time, 4)
            current_row['Debug_Delta_ms'] = dt 
            
            # Caso 0: Error de tiempo (duplicados o retrocesos)
            if dt <= 0.001: 
                stats['duplicate_fix'] += 1
                current_row['RecordingTime [ms]'] = prev_time + 0.1
                current_row['Correction_Type'] = 'Time_Shift_Fix'
                corrected_rows.append(current_row)
                i += 1

            # Caso 1: Hueco grande (> 14ms)
            elif dt > 14.0:
                stats['split'] += 1
                # Aseguramos al menos 2 divisiones
                num_splits = max(2, int(round(dt / 8.333))) 
                new_interval = dt / num_splits
                
                for k in range(num_splits):
                    new_row = current_row.copy()
                    new_row['RecordingTime [ms]'] = prev_time + (new_interval * (k + 1))
                    new_row['Correction_Type'] = f'Split_Expansion ({k+1}/{num_splits})'
                    corrected_rows.append(new_row)
                i += 1

            # Caso 2: Muestras muy juntas (< 6ms)
            elif dt < 6.0 and i < (n - 1):
                stats['merge'] += 1
                next_row = rows[i+1]
                merged_row = current_row.copy()
                
                merged_row['RecordingTime [ms]'] = next_row['RecordingTime [ms]']
                
                for col in cols_to_average:
                    val1 = current_row.get(col, np.nan)
                    val2 = next_row.get(col, np.nan)
                    if pd.notnull(val1) and pd.notnull(val2):
                        merged_row[col] = (val1 + val2) / 2
                    elif pd.notnull(val1):
                        merged_row[col] = val1
                    else:
                        merged_row[col] = val2
                
                merged_row['Correction_Type'] = 'Merge_Compression'
                idx1 = str(current_row.get('Original_Row_Index',''))
                idx2 = str(next_row.get('Original_Row_Index',''))
                merged_row['Original_Row_Index'] = f"{idx1}&{idx2}"
                
                corrected_rows.append(merged_row)
                i += 2
                
            # Caso 3: Normal
            else:
                current_row['Correction_Type'] = 'Normal'
                corrected_rows.append(current_row)
                i += 1

    df_clean = pd.DataFrame(corrected_rows)
    
    print("\nReporte de anomalías resueltas:")
    print(f"Filas entrada:  {len(df)}")
    print(f"Filas salida:   {len(df_clean)}")
    print(f"Splits (>14ms): {stats['split']}")
    print(f"Merges (<6ms):  {stats['merge']}")
    print(f"Fix Duplicados: {stats['duplicate_fix']}")
    
    return df_clean

# [DATO PRIVADO ELIMINADO - Ruta y nombre de archivo]
input_path = r"C:\Ruta\Generica\Archivo_Entrada_MO50.xlsx"
output_path = input_path.replace(".xlsx", "_Corregido.xlsx")

try:
    df_original = pd.read_excel(input_path)
    df_final = clean_eye_tracking_final(df_original)
    df_final.to_excel(output_path, index=False)
    print(f"\nArchivo guardado exitosamente en: {output_path}")

except Exception as e:
    print(f"Ocurrió un error: {e}")