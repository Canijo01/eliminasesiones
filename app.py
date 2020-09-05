import datetime
import configparser
import os
import sys
from funciones import *

### Inicio del programa
config = configparser.ConfigParser()
### Esta linea es para conservar las mayusculas. Normalmente convierte a minusculas
config.optionxform = str

leer_parametros = config.read("config.ini")

### Acceso a la API
if "TOKEN" in os.environ:
    token = os.environ['TOKEN']
    # print ("Token:%s"%token)
else:
    print ("No esta definido el Token. Cerrando el programa")
    sys.exit("No esta definido el Token en la variable de ambiente TOKEN")

### Revisa si hay mas de una sesion de usuario en awingu y cierra todas menos la mas reciente
### la prioridad es primero la variable de ambiente y despues la definida en config.ini
### Las variables que se utilizan son:
###URL : dominio donde esta el appliance ej. https://awingu.edgecapital.tech/
### domain: tenant que se est utilizando ej. EDGEOS
###n VERIFY para verificar si la conexion es segura. false si hay problema con el certificado
### Numero de dias hacia atras para solicitar la información de las sesiones
### DAYS : Numero de dias anteriores para cargar los registros ej. 5
### IDLE #Seconds without open RDP apps before Awingu assumes session is idle
### DELAY ## Seconds between interactions ej. 60


for secciones in config.sections():
    for variable in config.items(secciones):
        print(variable)
        dato = variable[1]
        if variable[0] in os.environ:
            dato = os.environ[variable[0]]
        exec("%s=\"%s\"" % (variable[0], dato))
        print("%s=\"%s\"" % (variable[0], dato))
VERIFY=bool(VERIFY)
user="%s\\%s"%(DOMAIN,USERNAME)
duplicados =[]

### Headers para los restful API
headers = {
    'Accept': 'application/json',
    'Authorization': "Token %s" % (token)
}
### Obtener el uri del dominio
domain_uri = getdomainuri(headers, url, DOMAIN)

### Inicio del programa
### Obtener las sesiones abiertas en el dominio
print ("Verificado no hay sesiones duplicadas para %s:"%(user))
sessions_list = usersessionslist(headers,url, DOMAIN,VERIFY)
if sessions_list.status_code == requests.codes.ok:
    #print(json.dumps(json.loads(sessions_list.text),indent=4,sort_keys=True))
    sesionesabiertas=json.loads(sessions_list.text)
    if sesionesabiertas["count"] > 1:
        for s in sesionesabiertas["results"]:
            #print (s)
            if s["username"].lower() == user.lower():
                duplicados.append(s)
        if len (duplicados) > 1:
            print(duplicados)
            print ("Usuario: %s tienen %s sesiones abiertas"%(username,len(duplicados)))
            duplicadosSorteados=sorted(duplicados,key=lambda date: datetime.datetime.strptime(date["start"] + "Z", "%Y-%m-%dT%H:%M:%S.%f%z"),reverse=1)
            for i in range (1,len(duplicadosSorteados)):
                print ("borrando sesion:%s"% duplicadosSorteados[i]["session_id"])
                closesession(headers,url,duplicadosSorteados[i]["session_id"],VERIFY)
        else:
            print("Usuario % solo tiene una sesion abiertas")



