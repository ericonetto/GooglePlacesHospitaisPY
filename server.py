#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
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
load_dotenv(dotenv_path=env_path)
 


YOUR_API_KEY = os.getenv('PLACES_KEY')
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


# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

  # GET
  def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers

        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))

        try:
            df = hospitalsSP({'lat':query_components['lat'],'lng':query_components['lon']})
            df.to_csv(sys.path[0] +'/saida.csv', sep=',')



            self.send_header('Content-type','file/csv')
            self.send_header('Content-Disposition', 'attachment; filename="saida.csv')
            self.end_headers()

            with open('saida.csv', 'rb') as file: 
                self.wfile.write(file.read())

        except:
            self.send_header('Content-type','text/html')
            self.end_headers()
            message='<br><br>Script em Python feito por Érico Netto<br>'
            message=message+'Cliente do WORKANA: Alex Braga<br>'
            message=message+'Data de criação: 08/04/2018<br><br><br>'

            message=message+'Modo de uso<br><br>'
            message=message+'Na URL adicionar uma interrogação e passar 2 parâmetros separados por um & entre si, necessariamente nesta ordem:<br>'
            message=message+'Latitude do ponto GPS de procura (usar ponto para separar casa decimal)<br>'
            message=message+'Longitude do ponto GPS de procura (usar ponto para separar casa decimal)<br>'
            message=message+'Exemplo<br>'
            message=message+'?lat=-22.1367345&lon=-51.4201818'
            message=message+'http://localhost:8080/?lat=-22.1367345&lon=-51.4201818'

            # Write content as utf-8 data
            self.wfile.write(bytes(message, "utf8"))
        return

def run():
  print('starting server...')

  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8080)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()


run()