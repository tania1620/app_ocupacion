from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts  # Esto es para los gráficos
import pandas as pd
import locale

# Establecer la configuración regional para el formateo de moneda
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajusta la configuración según tu localización

# Definir una función para formatear números a formato de moneda
def formato_moneda(numero):
    return locale.currency(numero, grouping=True)

#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'Análisis mercado inmobiliario',
     page_icon = 'logo.png',
     layout = 'wide')

#SIDEBAR
with st.sidebar:
     st.image('vivienda_01.jpg')
     
     # Diccionario para mapear distritos con precios por metro cuadrado
     precios_m2_por_distrito = {'Casco Antiguo': 3601,'Cerro - Amate': 1218,'Este - Alcosa - Torreblanca': 2025,'Los Remedios': 3145,'Macarena': 1671,'Macarena - Norte': 1398,'Nervión': 2953,
    'Palmera - Bellavista': 2814,'San Pablo - Santa Justa': 2392,'Sur': 3294,'default': 3118}  # Valor por defecto en caso de que no coincida ningún distrito
    
    # Para latitud y longitud, ajustamos el rango para permitir hasta 8 decimales
     min_lat, max_lat = -90.0, 90.0
     min_lon, max_lon = -180.0, 180.0
     step_lat, step_lon = 0.00000001, 0.00000001  # Esto permite hasta 8 decimales
     
     #INPUTS DE LA APLICACION
     accommodates = st.number_input('Máximo huéspedes permitidos', int(1), int(8))
     bathrooms = st.radio('Baños en la vivienda :bath:',["1", "2", "3","4"], horizontal=True)
     bedrooms = st.radio('Habitaciones en la vivienda ',["1", "2", "3","4"], horizontal=True)
     beds = st.radio('Camas disponibles :bed:',["1", "2", "3","4"], horizontal=True)
     room_type = st.selectbox('Tipo de alquiler 	:house:', ['Entire home/apt','Private room','Shared room'])
     latitude = st.number_input('Latitud. Busca la ubicación de tu vivienda en google maps y pulsa con el botón derecho sobre el icono de la app para copiar la latitud y longitud :world_map:', min_value=min_lat, max_value=max_lat, value=None, step=step_lat)
     longitude = st.number_input('Longitud :world_map:', min_value=min_lon, max_value=max_lon, value=None, step=step_lon)
     neighbourhood = st.selectbox('Barrio :cityscape:', ['no asignado','Aeropuerto Viejo', 'Avda. de la Paz', 'Bda. Pino Montano', 'Cruz Roja, Capuchinos', 'El Cano, Los Bermejales', 'El Porvenir','El Tardón, El Carmen','Encarnación, Regina','Felipe II, Los Diez Mandamientos',
               'Feria','Giralda Sur','Heliópolis','Hermandades, La Carrasca','Huerta de Santa Teresa','Huerta del Pilar','Juan XXIII','La Barzola','La Buhaira','La Calzada','La Corza','La Plata','Las Avenidas','Las Huertas',
               'Las Letanías','León XIII, Los Naranjos','Los Carteros','Macarena 3 Huertas, Macarena 5','Museo','Nervión','Palacio Congresos, Urbadiez, Entrepuentes, Jardines del Eden','Parque Alcosa','Pino Flores',
               'Polígono Norte','Prado, Parque María Luisa','Retiro Obrero','Rochelambert','San Diego','San Gil','San Jerónimo','San Pablo A y B','San Pablo C','San Pablo D y E','San Vicente','Santa Aurelia, Cantábrico, Atlántico, La Romería',
               'Santa Catalina',  'Santa Clara','Santa Cruz','Sector Sur, La Palmera, Reina Mercedes','Triana Oeste','San Roque'])
     neighbourhood_group = st.selectbox('Distrito :cityscape:', ['Casco Antiguo','Triana','Nervión','Macarena','San Pablo - Santa Justa','Sur','Los Remedios','Palmera - Bellavista','Cerro - Amate','Este - Alcosa - Torreblanca','Macarena - Norte'])
    # Obtener el distrito seleccionado
     distrito_seleccionado = neighbourhood_group
    # Obtener el precio_m2 correspondiente al distrito seleccionado
     precio_m2 = precios_m2_por_distrito.get(distrito_seleccionado, precios_m2_por_distrito['default'])
    # Mostrar el text_input para precio_m2
     precio_m2 = st.text_input('Precio_m2 por zona "NO RELLENAR" indicado automáticamente:dollar:', value=precio_m2)
     m2 = st.slider('M2 que tiene la vivienda', min_value = int(50), max_value = int(150))
     price = st.number_input('Precio de alquiler por noche :dollar:', min_value = float(20), max_value = float(1300))
     precio_compra = st.number_input('Precio de compra de la vivienda :dollar:', int(60000), int(450000))
     minimum_nights = st.slider('Mínimo de noches a reservar', min_value = int(1), max_value = int(7))
     availability_365 = st.slider('Días disponibles al año para alquilar :calendar:', int(1), int(365))


#MAIN
st.title(':violet[CALCULADORA RENTABILIDAD VIVIENDA]')

#CALCULAR

#Crear el registro
registro = pd.DataFrame({'accommodates':int(accommodates),
                         'bathrooms':float(bathrooms),
                         'bedrooms':float(bedrooms),
                         'beds': float(beds),
                         'latitude':latitude,
                         'longitude':longitude,
                         'm2':int(m2),
                         'minimum_nights':int(minimum_nights),
                         'neighbourhood':str(neighbourhood),
                         'neighbourhood_group':str(neighbourhood_group),
                         'price':float(price),
                         'precio_compra':int(precio_compra),
                         'room_type':str(room_type),
                         'availability_365':int(availability_365),
                         'precio_m2': int(precio_m2)}
                        ,index=[0])

#CALCULAR RIESGO

if st.sidebar.button('CALCULAR OCUPACION'):
    #Ejecutar el scoring
    RE = ejecutar_modelos(registro)
    precio_alquiler_noche = int(RE.precio_alquiler_noche)
    ocupacion = float(RE.ocupacion)
    beneficio = float(RE.beneficio)
    rentabilidad = float(RE.rentabilidad_esperada)
    #Velocimetro para ocupacion
    ocupacion_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "Ocupación esperada",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,},
                    },
                    "progress": {"show": "true", "width": 15},
                    "detail": {"valueAnimation": "false", "formatter": '{value}%', "color": "violet"},
                    "data": [{"value": ocupacion, "name": "Ocupación"}],
                }
            ],
        }

    
    #Crear dos columnas para las métricas
    col1,col2 = st.columns(2)
    with col1:
        st.write('La rentabilidad esperada teniendo en cuenta un 30% de gastos de los beneficios:')
        st.metric(label="RENTABILIDAD", value=formato_moneda(rentabilidad))
    with col2:
        st.write('Los beneficios obtenidos del alquiler de la vivienda con la ocupación esperada es de:')
        st.metric(label="BENEFICIO", value=formato_moneda(beneficio))
    
    #Añadir el velocímetro
    st_echarts(options=ocupacion_options, width="120%", height="400px", key=1)
else:
    st.write('DEFINE LAS CARACTERÍSTICAS DE LA VIVIENDA Y HAZ CLICK EN CALCULAR OCUPACIÓN')