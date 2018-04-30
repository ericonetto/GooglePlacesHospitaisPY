import logging

from flask import request
from flask import Flask, make_response  
import csv
from googleplaces import GooglePlaces, types, lang
import requests
import pandas as pd
import json
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=str(env_path))
 


YOUR_API_KEY = os.getenv('PLACES_KEY')
google_places = GooglePlaces(YOUR_API_KEY)



app = Flask(__name__)







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





@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    try:
        df = hospitalsSP({'lat':request.args.get('lat'),'lng':request.args.get('lon')})
        df.to_csv(sys.path[0] +'/saida.csv', sep=',')

        with open('saida.csv', 'rb') as file: 
            csv = file.read()
        response = make_response(csv)
        cd = 'attachment; filename=saida.csv'
        response.headers['Content-Disposition'] = cd 
        response.mimetype='text/csv'

        return response
    except:
        message='<br><br>Script em Python feito por Érico Netto<br>'
        message=message+'Cliente do WORKANA: Alex Braga<br>'
        message=message+'Data de criação: 08/04/2018<br><br><br>'

        message=message+'Modo de uso<br><br>'
        message=message+'Na URL adicionar uma interrogação e passar 2 parâmetros separados por um & entre si, necessariamente nesta ordem:<br>'
        message=message+'Latitude do ponto GPS de procura (usar ponto para separar casa decimal)<br>'
        message=message+'Longitude do ponto GPS de procura (usar ponto para separar casa decimal)<br>'
        message=message+'Exemplo<br>'
        message=message+'?lat=-22.1367345&lon=-51.4201818<br>'
        message=message+'http://localhost:8080/?lat=-22.1367345&lon=-51.4201818'
        return message


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)