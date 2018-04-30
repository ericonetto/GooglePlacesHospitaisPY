from googleplaces import GooglePlaces, types, lang
import requests
import pandas as pd
import json
import sys


print('\n\nScript em Python feito por Érico Netto')
print('Cliente do WORKANA: Alex Braga')
print('Data de criação: 08/04/2018\n\n\n')

print('Modo de uso\n')
print('Passar 4 parâmetros separados por espaço entre si, necessariamente nesta ordem:')
print('Chave do google')
print('Latitude do ponto GPS de procura (usar ponto para separar casa decimal)')
print('Longitude do ponto GPS de procura (usar ponto para separar casa decimal)')
print('Caminho completo do arquivo CSV de saída (deverá ter o caminho E O NOME do arquivo COM A TERMINAÇÂO csv\n')
print('Exemplo')
print('GPhospitais.py AIzaSyCgi56Nnki5iNorSfTHjvj3Q08LwuM6rs2 -22.1367345 -51.4201818 saida.csv')


if not len(sys.argv)==5:
    print('\n>Parâmetros incorretos ou faltando, o arquivo não foi gerado!')
    sys.exit()


print('\n\nIncio do script!\n')

print('>Parâmetros passados: \n')
print(' chave_google: ' + sys.argv[1] +"\n")
print(' latitude: ' + sys.argv[2] +"\n")
print(' longitude: ' + sys.argv[3] +"\n")
print(' caminho_completo_csv: ' + sys.argv[4] +"\n")

chave_google = sys.argv[1]
latitude = float(sys.argv[2])
longitude = float(sys.argv[3])
caminho_completo_csv = sys.argv[4]


YOUR_API_KEY = chave_google
google_places = GooglePlaces(YOUR_API_KEY)




#retorna resultados pq está dentro do estado de sp
#{'lat':-22.1367345,'lng':-51.4201818}

#zero resultados pq está fora do estado de sp
#{'lat':-22.9832447,'lng':-51.4532838}
def hospitalsSP(nearByLocation, next_page_token=None):
    placesdf=pd.DataFrame([])
    if next_page_token==None:
        result= google_places.nearby_search(location='São Paulo', lat_lng=nearByLocation,types=[types.TYPE_HOSPITAL]) 
    else:
        result= google_places.nearby_search(location='São Paulo', lat_lng=nearByLocation,types=[types.TYPE_HOSPITAL], pagetoken=next_page_token) 
    if not len(result.places)==0:
        for place in result.places:
            newdf=pd.DataFrame([getPlaceDetails(place.place_id)])
            placesdf=placesdf.append(newdf)
            
    return placesdf


def getPlaceDetails(placeId):
    url = "https://maps.googleapis.com/maps/api/place/details/json"

    querystring = {"placeid":placeId ,"key":YOUR_API_KEY}

    headers = {
        'cache-control': "no-cache"
        }

    response=requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == requests.codes.ok:
        jsondetails=json.loads(response.text)
        place= jsondetails['result']
        return place
        return {"name":place['name'], "rating":place['rating'], 'formatted_address':place['formatted_address']}
    else:
        return None


df = hospitalsSP({'lat':latitude,'lng':longitude})
df.to_csv(caminho_completo_csv, sep=',', encoding='UTF-8' )
print("Script executado, seu arquivo CSV se encontra em " + caminho_completo_csv)