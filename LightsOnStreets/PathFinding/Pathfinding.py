# Find the safetest path
# 이관대상코드 : 3_find_way_Astar/finding_path_2.ipynb

# ver1 추가분
# -> https://www.redblobgames.com/grids/hexagons/#field-of-view redblobgames 이용해서 좌표변환 -> 길찾기 위한 Node간의 Edge(Link) 만들 수 있찌 않을까.
# -> 1차 속도 개선 위해서 dataframe 말고 기본 자료형 사용하기.

# 함수정리
# get_points_in_range : 중심점에서 범위 내 포함되는 점들 검색
# get_gf : G, H 구하기. return 은 F = G + H
# get_scaled_f : F scaling


import settings,os
import folium
import pandas as pd
import numpy as np
import heapq
from haversine import haversine #거리구하기
from sklearn.preprocessing import minmax_scale #정규화

##data 불러오기
class SafePath:
    sp = ()
    ep = ()
    closed_list = []
    closed_list_id = []
    closed_list_seq = []

    def set_destination(self,road_df,start,end):
        ##출발지, 도착지
        self.sp = start #출발지 37.506059, 127.036863
        self.ep = end   #도착지 37.509122, 127.043816

        def transform_road_df(road_df):
            road_df.drop(['SIG_CD', 'RDS_MAN_NO', 'RDS_MAN_NO2', 'RN_CD'], axis=1, inplace=True)

            # .csv 파일 직접 로드했을 시
            # if 'Unnamed: 0' in road_df.columns :
            #     road_df.drop(columns='Unnamed: 0', axis=1, inplace=True)

            road_df['ID'] = road_df.index
            road_df.rename(columns={'총밝기': '밝기',
                                    'RN': '명칭',
                                    'LAT': '위도',
                                    'LNG': '경도'}, inplace=True)
            road_df['분류'] = '도로'
            road_df['POINT_ID'] = road_df['ID'].apply(lambda x: 'POINT_' + str(x))
            return road_df

        # 필요한 정보만 가져오기
        df = transform_road_df(road_df)

        # 최대 밝기 정보 저장
        l_max = df['밝기'].max()
        print("1")

        # 도착점 추가 (가장 높은 밝기로 설정)
        df = df.append(df.from_dict({'ID' : len(df), 'POINT_ID':'POINT_EP', '위도':self.ep[0], '경도':self.ep[1]
                                        , '분류':'도착지', '명칭':'도착지', '밝기' : l_max}, orient = 'index').T)

        # 시작점 추가 (밝기는 가장 낮은 밝기로 설정)
        df = df.append(df.from_dict({'ID' : -1,'POINT_ID':'POINT_SP', '위도':self.sp[0], '경도':self.sp[1]
                                        , '분류':'출발지', '명칭':'출발지', '밝기' : -l_max }, orient = 'index').T)


        df = df.sort_values(by='ID').reset_index(drop=True)
        return df


    def find_path(self,df, radius=100):

        # 초기화
        point = self.sp
        sel_pointID = 'POINT_SP'

        # 반경 내 포함 points 검색
        def get_points_in_range(df, point, radius):
            point = self.sp
            rad = radius

            while True:
                # 1-1. 반경안에 포함된 모든 points 검색 => 후에 연결된 point로 바꿔야함.
                res = df[df.apply(lambda x: haversine(point, [x['위도'], x['경도']], unit='m'), axis=1) < rad]
                # 1-2. 이미 선택했던 point들 제외
                res = res[~res['POINT_ID'].isin(self.closed_list_id)]
                # 1-3. 반경안에 만족하는 포인트가 없다면 반경을 늘려서 재검색.
                if (len(res) == 0):
                    rad += 10
                else:
                    break
            return res

        # 가중치 구하기
            # 1. F구하기
        def get_f(df):
            g = np.array(df.apply(lambda x: haversine(self.sp, [x['위도'], x['경도']], unit='m'), axis=1)).reshape(-1, 1)
            h = np.array(df.apply(lambda x: haversine(self.ep, [x['위도'], x['경도']], unit='m'), axis=1)).reshape(-1, 1)
            return g + h

            # 2. Scaled_F : 밝기 0~100 에 맞추기
        def get_scaled_f(df):
            X_MinMax_scaled = 100 - minmax_scale(df['F'], axis=0, copy=True, feature_range=(0, 100))
            return X_MinMax_scaled

            # 3. 밝기 이용한 가중치 추가 W(weight = 4F(거리) + 6L(밝기))
        def get_w(df, w_lux=40, w_f=120):
            w = np.array(df.apply(lambda x: (x['밝기'] * w_lux) + (x['scaled_F'] * w_f), axis=1)).reshape(-1, 1)
            return w

        # 1. 해당 ID Close List에 추가
        n = 0
        heapq.heappush(self.closed_list_id, 'POINT_SP')
        heapq.heappush(self.closed_list_seq, n)
        heapq.heappush(self.closed_list, point)

        while (sel_pointID != 'POINT_EP'):
            #print("시작포인트 : " , point)
            points = pd.DataFrame()
            points = get_points_in_range(df, point, radius)     # 1. 반경 내 속하는 점들 검색
            points['F'] = get_f(points)                 # 2. F=G+H : F구하기
            points['scaled_F'] = get_scaled_f(points)   # 3. F를 밝기에 맞춰 스케일링
            points['W'] = get_w(points)                 # 4. 최종가중치 구하기

            points = points.sort_values('W', ascending=False).reset_index()  # 5. 정렬

            print(points.loc[0, 'POINT_ID'])
            sel_pointID = points.loc[0, 'POINT_ID']
            point = (points.loc[0, '위도'], points.loc[0, '경도'])

            # goodbye.append(points.loc[1:,'point_ID'].values)
            heapq.heappush(self.closed_list_id, sel_pointID)
            heapq.heappush(self.closed_list_seq, n)
            heapq.heappush(self.closed_list, (points.loc[0, '위도'], points.loc[0, '경도']))
            n += 1

        self.save_path()
        print("done, len : ", len(self.closed_list))


        # # 역삼동 중심 = 역삼역 /  좌표 : 37.500742, 127.036891
    def save_path(self,show=False):
        map = folium.Map(location= self.sp, zoom_start=18)
        path = self.closed_list

        for n in range(0, len(path)) :
              folium.CircleMarker([path[n][0], path[n][1]], popup= str(self.closed_list_seq[n]), radius = 3).add_to(map)

        # 구분하기 쉽게 스타팅 지역은 빨간색 마커로 표시
        folium.Marker(self.sp, popup= 'SP', icon=folium.Icon(color='red')).add_to(map)
        folium.Marker(self.ep, popup= 'EP', icon=folium.Icon(color='black')).add_to(map)

        filepath = os.path.join(settings.BASE_DIR, 'output', 'map_pathfinding.html')
        map.save(filepath)

        if show:
            import webbrowser
            webbrowser.open('file://' + filepath)

    def get_safe_path(self,road_df,start =(37.506059, 127.036863),  end =(37.509122, 127.043816) ):
        self.find_path(sp.set_destination(road_df, start, end))

if __name__ == '__main__':
    # 도로 정보이지만 시설물과 도로좌표를 합쳐서 더 촘촘한 정보를 얻을 수 있다.
    road_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'output', 'road_with_light.csv'), encoding = "EUC-KR" )
    import time
    print(time.time())
    sp = SafePath()
    sp.find_path(sp.set_destination(road_df, start = (37.506059, 127.036863),  end = (37.509122, 127.043816)))
    print(time.time())


