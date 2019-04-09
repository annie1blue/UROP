import json
with open('Parcels_2016_Data_Full.geojson', 'w') as geojson_file:
    data = json.load(geojson_file)
    # data is now a dict,
    # you can do whatever you want with it
    


""" import pandas as pd 
import numpy as np 

fields = ['OBJECTID','PTYPE','U_NUM_PARK','GIS_ID','FULL_ADDRESS','SHAPESTArea','SHAPESTLength']
df = pd.read_csv('Parcels_2016_Data_Full.csv', delimiter=',', usecols=fields)
""" 
for prop in df.PTYPE:
    if prop>=0 and prop<200:
        df.drop([0, 1])
for parking in df.U_NUM_PARK: """

print (df) """
