import numpy as np
import pandas as pd
import folium
import os, settings
# from selenium import webdriver



## folium 띄우기!

#
# driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
# driver = webdriver.Chrome(driver_path)
#
#
# # folium 띄우기 : https://github.com/python-visualization/folium/issues/946
#
# LDN_COORDINATES = (51.5074, 0.1278)
# filepath = os.path.join(settings.BASE_DIR, 'output', 'map.html')
# m = folium.Map(location=LDN_COORDINATES, zoom_start=19)
# m.save(filepath)
# driver.get('file://' + filepath)

#
# map_co = [35.689872, 139.694406]
# map = folium.Map(location=map_co, zoom_start=13)
# folium.CircleMarker(location=map_co, radius=200, color = '#000000', fill_color = '#000000' ).add_to(map)
# map.save('test.html')

# import webbrowser
# filepath = os.path.join(settings.BASE_DIR, 'output', 'map.html')
# webbrowser.open('file://' + filepath)

# total_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'output', 'road_with_light.csv'), encoding="EUC-KR")
#
# total_df.rename(columns={"Unnamed: 0": "POINT_ID"}, inplace=True)
# total_df['POINT_ID'] = total_df['POINT_ID'].apply(lambda x: 'POINT_' + str(x))
#

# 글자수 맞추기
print("3".zfill(5))
print("3".rjust(5,'0'))

#숫자에
print ('{0:05d}'.format(3)) #2.6이상
print ("%05d"% 3)
print (format(30,'05')) #2.6이상

# list에서 한번에 적용
# >>> mylis = ['this is test', 'another test']
# >>> [item.upper() for item in mylis]
# ['THIS IS TEST', 'ANOTHER TEST']


total_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'output', 'road_with_light.csv'), encoding="EUC-KR")
if 'Unnamed: 0' in total_df.columns :
    total_df.drop(columns='Unnamed: 0', axis=1, inplace=True)
total_df['ID'] = total_df.index


print(total_df.head(5))