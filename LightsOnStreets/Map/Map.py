# the Light(Safety) Map

# input_data : all_df.csv
# | point_ID  | 거리 | 밝기 | 총밝기 | 분류 | 명칭 | 위도 | 경도 | 경유여부 |

# 이관 대상 코드 :
# 3_save_score_on_the_loads_points.ipynb	lumos ver0	3 months ago
# 4_map.ipynb
# ver1 추가분 -> 각 시설물(road 좌표 제외) 표시하는 레이어 추가하기 ( map에서 레이어 개념 )

import os, settings
import numpy as np
import pandas as pd

class LightMap:
    def lux_on_link(self, road_df):
        node_df = road_df
        # 1_포인트(node) 연결하여 링크 만들기. & 링크 평균 밝기 계산
        link_df = pd.DataFrame(columns = [ 'LINK_NO','RDS_MAN_NO', 'RN', 'RN_CD', 'SP','EP', 'LUX']  )
        n = 0   # link_no

        for i in range(1, len(node_df)-1):
            # RDS_MAN_NO(도로관리코드)가 같다는 것은 서로 같은 도로, 이것을 연결해서 Link를 만들 수 있음.
            if node_df.loc[i, 'RDS_MAN_NO'] == node_df.loc[i+1, 'RDS_MAN_NO'] :
                tmp = { 'LINK_NO' : 'LINK_%d' % n                                   # 링크번호
                      ,'RDS_MAN_NO' : node_df.loc[i,'RDS_MAN_NO']                   # 도로관리번호
                      , 'RN' : node_df.loc[i,'RN']                                  # 도로명
                      , 'RN_CD' : node_df.loc[i,'RN_CD']                            # 도로코드
                      , 'SP' : [node_df.loc[i, 'LAT'], node_df.loc[i, 'LNG']]       # 시작점
                      , 'EP' : [node_df.loc[i+1, 'LAT'],node_df.loc[i+1, 'LNG']]    # 끝점
                       ##두 점의 평균값으로 링크의 밝기를 계산한다.
                      , 'LUX' : np.mean( [node_df.loc[i, '총밝기'], node_df.loc[i+1, '총밝기']] ) # 평균밝기
                      }

                link_df = link_df.append( link_df.from_dict(tmp, orient = 'index').T)
                n += 1

        # 원하는 정보만 가져와서 저장
        link_df = link_df.loc[:,['LINK_NO','RDS_MAN_NO', 'RN', 'RN_CD','SP','EP','LUX']].reset_index(drop = True)
        #link_df.to_csv(os.path.join(settings.BASE_DIR, 'output', 'links_with_lux.csv' ), mode='w', encoding='ms949') # edge(=link) list
        return link_df

    def display(self,road_df,link_df,isOpen = False):
        # display on Map
        import folium

        # 필요한 열만 가져오기
        nodes = road_df[['RN_CD', 'RN', 'RDS_MAN_NO', 'LAT', 'LNG']]
        links = link_df[['SP', 'EP', 'LUX']]

        std_point = (nodes.loc[0, 'LAT'], nodes.loc[0, 'LNG'])
        map_osm = folium.Map(location=std_point, width='100%', height='100%', zoom_start=17)

        # Draw Links
        for ix, row in links.iterrows():
            start = (row['SP'])  # 위도, 경도 튜플
            end = (row['EP'])
            kw = {'opacity': 1, 'weight': row['LUX'] / 10}

            # print(kw['weight']) #lux 범위가 0~16사이로 나옴.  우선 3등분 함
            if kw['weight'] < 5:
                folium.PolyLine(
                    locations=[start, end],
                    color='#FF00CC',  # 노락색(yellow)은 잘 안보임, 주황색(orange)도 그닥인듯
                    line_cap='round',
                    **kw,
                ).add_to(map_osm)
            elif kw['weight'] < 10:
                folium.PolyLine(
                    locations=[start, end],
                    color='#FF6633',
                    line_cap='round',
                    **kw,
                ).add_to(map_osm)
            else:
                folium.PolyLine(
                    locations=[start, end],
                    color='#FF0000',
                    line_cap='round',
                    **kw,
                ).add_to(map_osm)

        filepath = os.path.join(settings.BASE_DIR, 'output', 'map.html')
        map_osm.save(filepath)

        if isOpen:
            import webbrowser
            filepath = os.path.join(settings.BASE_DIR, 'output', 'map.html')
            webbrowser.open('file://' + filepath)

if  __name__ == '__main__':
    lm = LightMap()
    road_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'output', "road_with_light.csv"), encoding='ms949')
    res = lm.lux_on_link(road_df)
    lm.display(road_df, res)
    # print(res.head(4))