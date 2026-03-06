import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# [DATO PRIVADO ELIMINADO - Ruta de archivo de origen]
RUTA_ARCHIVO = r"C:\Ruta\Generica\Datos_Participantes_Separados.xlsx"
NOMBRE_COLUMNA_ETIQUETA = "Etiqueta_A"

st.set_page_config(page_title="Clasificador Rápido", layout="wide")

COLORES_FIJOS = [
    "whitesmoke", "steelblue", "forestgreen", "blueviolet", 
    "red", "cyan", "gold", "saddlebrown"
]

st.sidebar.title("Panel de Control")

if not os.path.exists(RUTA_ARCHIVO):
    st.error(f"Error: No se encuentra el archivo en {RUTA_ARCHIVO}")
    st.stop()

if st.sidebar.button("REINICIAR MEMORIA", type="primary"):
    st.session_state.clear()
    st.rerun()

try:
    archivo_excel = pd.ExcelFile(RUTA_ARCHIVO)
    lista_participantes = archivo_excel.sheet_names
    
    if "indice_participante" not in st.session_state:
        st.session_state.indice_participante = 0

    col_nav1, col_nav2 = st.sidebar.columns(2)
    
    if col_nav1.button("Anterior"):
        if st.session_state.indice_participante > 0:
            st.session_state.indice_participante -= 1
            st.session_state["selector_participantes"] = lista_participantes[st.session_state.indice_participante]
            st.rerun()
            
    if col_nav2.button("Siguiente"):
        if st.session_state.indice_participante < len(lista_participantes) - 1:
            st.session_state.indice_participante += 1
            st.session_state["selector_participantes"] = lista_participantes[st.session_state.indice_participante]
            st.rerun()

    def actualizar_desde_selector():
        seleccion = st.session_state["selector_participantes"]
        if seleccion in lista_participantes:
            st.session_state.indice_participante = lista_participantes.index(seleccion)

    if "selector_participantes" not in st.session_state:
        st.session_state["selector_participantes"] = lista_participantes[st.session_state.indice_participante]

    participante_seleccionado = st.sidebar.selectbox(
        "Selecciona Participante:", 
        lista_participantes,
        key="selector_participantes", 
        on_change=actualizar_desde_selector
    )

    st.sidebar.divider()
    
    if st.sidebar.button("Recargar Datos"):
        st.rerun()

except Exception as e:
    st.error(f"Error cargando archivo: {e}")
    st.stop()

clave_memoria = f"datos_{participante_seleccionado}"

if clave_memoria not in st.session_state:
    df_temp = pd.read_excel(RUTA_ARCHIVO, sheet_name=participante_seleccionado)
    df_temp.index = pd.RangeIndex(start=1, stop=len(df_temp) + 1, step=1)
    if NOMBRE_COLUMNA_ETIQUETA not in df_temp.columns:
        df_temp[NOMBRE_COLUMNA_ETIQUETA] = 0
    st.session_state[clave_memoria] = df_temp

df_global = st.session_state[clave_memoria]
columnas = list(df_global.columns)

st.sidebar.divider()
st.sidebar.subheader("Edición Rápida")
with st.sidebar.expander("Desplegar herramienta", expanded=False):
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        fila_inicio = st.number_input("Desde Fila:", min_value=1, max_value=len(df_global), value=1)
    with col_r2:
        fila_fin = st.number_input("Hasta Fila:", min_value=1, max_value=len(df_global), value=min(10, len(df_global)))
    
    valor_masivo = st.number_input("Valor (0-7):", value=1, min_value=0, max_value=7)
    
    if st.button("Aplicar a Rango"):
        if fila_inicio <= fila_fin:
            st.session_state[clave_memoria].loc[fila_inicio:fila_fin, NOMBRE_COLUMNA_ETIQUETA] = valor_masivo
            st.success(f"Filas {fila_inicio}-{fila_fin} actualizadas a {valor_masivo}")
            st.rerun()

st.title(f"Participante: {participante_seleccionado}")

col1, col2 = st.columns(2)
with col1:
    idx_x = next((i for i, c in enumerate(columnas) if "Right X" in c or "Derecha X" in c), 0)
    col_x = st.selectbox("Eje X:", columnas, index=idx_x)
with col2:
    idx_y = next((i for i, c in enumerate(columnas) if "Right Y" in c or "Derecha Y" in c), 0)
    col_y = st.selectbox("Eje Y:", columnas, index=idx_y)

st.divider()

try:
    from streamlit import fragment
except ImportError:
    fragment = lambda func: func 

@fragment
def editor_interactivo():
    """
    Maneja la edición interactiva de la tabla de datos y actualiza la gráfica 
    de Plotly en tiempo real sin necesidad de recargar toda la página web.
    """
    df_local = st.session_state[clave_memoria]
    
    st.subheader("1. Tabla de Datos (Edición Directa)")
    
    config_cols = {col: st.column_config.Column(disabled=True) for col in columnas}
    config_cols[NOMBRE_COLUMNA_ETIQUETA] = st.column_config.NumberColumn(
        "Clasificación", step=1, disabled=False
    )

    df_editado = st.data_editor(
        df_local,
        column_config=config_cols,
        use_container_width=True, 
        height=400,
        key=f"editor_live_{participante_seleccionado}"
    )

    if not df_editado.equals(df_local):
        st.session_state[clave_memoria] = df_editado

    st.subheader("2. Gráfica en Tiempo Real")
    
    try:
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
            row_heights=[0.85, 0.15]
        )
        
        mis_indices = df_editado.index 

        fig.add_trace(go.Scatter(
            x=mis_indices, y=df_editado[col_x], 
            mode='lines', name='Eje X', line=dict(color='darkblue', width=1.5)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=mis_indices, y=df_editado[col_y], 
            mode='lines', name='Eje Y', line=dict(color='darkorange', width=1.5)
        ), row=1, col=1)

        etiquetas_z = df_editado[NOMBRE_COLUMNA_ETIQUETA].fillna(0)

        fig.add_trace(go.Heatmap(
            z=[etiquetas_z], x=mis_indices, y=[1], 
            colorscale=COLORES_FIJOS, zmin=0, zmax=7, showscale=False, name='Clase',
            hovertemplate='Muestra: %{x}<br>Etiqueta: %{z}<extra></extra>'
        ), row=2, col=1)

        fig.update_xaxes(range=[-1, 120]) 
        fig.update_yaxes(range=[-10, 1600], row=1, col=1)
        fig.update_yaxes(showticklabels=False, row=2, col=1) 
        fig.update_layout(height=500, margin=dict(t=30, b=10, l=0, r=0))
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as ex:
        st.warning(f"Error graficando: {ex}")

editor_interactivo()

st.divider()
if st.button("GUARDAR CAMBIOS EN EXCEL", type="primary"):
    try:
        with st.spinner("Guardando..."):
            with pd.ExcelWriter(RUTA_ARCHIVO, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                st.session_state[clave_memoria].to_excel(writer, sheet_name=participante_seleccionado, index=False)
            
            st.success(f"Guardado exitosamente. Hoja actualizada: {participante_seleccionado}")
            
    except PermissionError:
        st.error("Error: El archivo Excel está abierto. Ciérralo e intenta guardar de nuevo.")
    except Exception as e:
        st.error(f"Error al guardar: {e}")