#1.LIBRERIAS

import numpy as np
import pandas as pd
import pickle

#2.FUNCIONES DE SOPORTE
def eliminar_duplicados(df):
    df.drop_duplicates(inplace = True)
    return(df)
                     
def calidad_datos(df):
    ### Gestionamos imputación de nulos por la media ###
    
    var_imputar_media = ['price']
    def imputar_media(variable):
        if pd.api.types.is_integer_dtype(variable):
            return(variable.fillna(int(variable.mean())))
        else:
            return(variable.fillna(variable.mean()))
    df[var_imputar_media] = df[var_imputar_media].apply(imputar_media)

    ### Gestionamos imputación de nulos por un valor ###
    
    var_imputar_valor = ['beds','bathrooms','bedrooms']
    #Beds
    def imputar_beds(registro):
        #Lista de condiciones
        condiciones = [(registro.accommodates <= 2),
                      (registro.accommodates > 2) & (registro.accommodates <= 4),
                      (registro.accommodates > 4) & (registro.accommodates <=6),
                      (registro.accommodates > 6)]
        #lista de resultados
        resultados = [1,2,3,4]
        #Salida
        return (np.select(condiciones,resultados, default = -999))
    df.loc[df.beds.isna(), 'beds'] = df.loc[df.beds.isna()].apply(imputar_beds, axis = 1).astype('int64')
    #Bedrooms
    def imputar_bedrooms(registro):
        #Lista de condiciones
        condiciones = [(registro.beds <= 2),
                      (registro.beds > 2) & (registro.beds <= 4),
                      (registro.beds > 4) & (registro.beds <=6),
                      (registro.beds > 6)]
        #lista de resultados
        resultados = [1,2,3,4]
        #Salida
        return (np.select(condiciones,resultados, default = -999))
    df.loc[df.bedrooms.isna(), 'bedrooms'] = df.loc[df.bedrooms.isna()].apply(imputar_bedrooms, axis = 1).astype('float64')
    #bathrooms
    def imputar_bathrooms(registro):
        #Lista de condiciones
        condiciones = [(registro.bedrooms <= 2),
                      (registro.bedrooms > 2) & (registro.bedrooms <= 4),
                      (registro.bedrooms >= 5)]
        #lista de resultados
        resultados = [1,2,3]
        #Salida
        return (np.select(condiciones,resultados, default = -999))
    df.loc[df.bathrooms.isna(), 'bathrooms'] = df.loc[df.bathrooms.isna()].apply(imputar_bathrooms, axis = 1).astype('float64')

    ### Gestionamos los atípicos por winsorizacion automática ###
    
    var_winsorizar = ['price','minimum_nights','accommodates','bathrooms','bedrooms','beds']
    p_min = 0.01
    p_max = 0.99
    for variable in var_winsorizar:
          
        # Calcula los cuantiles para cada variable
        lower_quantile = df[variable].quantile(p_min)
        upper_quantile = df[variable].quantile(p_max)
        
        # Si la columna es de tipo Int64, redondea los cuantiles a enteros
        if pd.api.types.is_integer_dtype(df[variable]):
            lower_quantile = int(round(lower_quantile))
            upper_quantile = int(round(upper_quantile))
                
        # Aplica la winsorización utilizando los cuantiles como límites
        df[variable].clip(lower=lower_quantile, upper=upper_quantile, inplace=True)

    ###  Creamos la target ###
    
    df['ocupacion'] = (((365 - df.availability_365)/ 365) * 100).astype('int64')
    #Eliminar variable availability
    df = df.drop(columns = 'availability_365')

    ### Creamos variable distancia pdi ###

    #importamos el modulo de matematicas
    from math import radians, cos, sin, asin, sqrt

    #Hacemos una función personalinada llamada haversine que necesitas que le pases la latitud y longitud del punto 1 (Las Setas) y del punto 2 (inmueble)
    def haversine(lat1, lon1, lat2, lon2):

      R = 6372.8 #En km, si usas millas tienes que cambiarlo por 3959.87433
      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)
      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c
    #Ahora lo que hacemos es meter la latitud y longitud del punto de interés
    lat1 = 37.3771699330896
    lon1 = -5.9870810323649035
    df['pdi_plazaesp'] = df.apply(lambda registro : haversine(lat1,lon1,registro.latitude, registro.longitude), axis = 1) #Ponemos el axis = 1 para que entieda que debe coger los registros y no las columnas
    
    ### Creamos variable precio compra de la vivienda  ###
    #Definimos condiciones
    condiciones = [(df.bedrooms >=0) & (df.bedrooms <= 1),
              (df.bedrooms == 2),
              (df.bedrooms == 3),
              (df.bedrooms == 4),
              (df.bedrooms >4)]

    #Definimos resultados
    resultados = [50,70,90,120,150]
    df['m2'] = np.select(condiciones, resultados, default = -999)
    #Ahora que ya tenemos los m2, simplemente hacemos el cálculo directo y lo guardamos en una nueva variable
    df['precio_compra'] = df.m2 * df.precio_m2
    #Eliminamos la variable de precio del m2 ya que hemos calculado el valor final
        
    return(df)

#3. EJECUTAR MODELOS
def ejecutar_modelos(df):
    x = eliminar_duplicados(calidad_datos(df))
                     
    #3.CARGA PIPE DE EJECUCION
    with open('C:/Users/tania.camacho/Desktop/Master/EstructuraDirectorio/04_PORTAFOLIO/01_PORTAFOLIO_INMO/03_Notebooks/03_Sistema/app_ocupacion/pipe_ejecucion.pickle', mode='rb') as file:
        pipe_ejecucion = pickle.load(file)

    #EJECUCION
    scoring = pipe_ejecucion.predict(x)

    #4.RESULTADO
    precio = df.price
    ocupacion = scoring

    RE = pd.DataFrame({'precio_alquiler_noche':precio,
                   'ocupacion':scoring})

    RE['beneficio'] = round((365 * RE.ocupacion)/100 * RE.precio_alquiler_noche,2)
    RE['rentabilidad_esperada'] = round(RE.beneficio * 0.70,2) # Se espera que un 30% de los beneficios obtenidos se incurran en gastos de la vivienda
    return (RE)



