import pandas as pd
import numpy as np
from sklearn.cluster import KMeans



class FindWay:

    def __init__(self,data):
        # 데이터 불러오기
        print("findWay: ", data['boundary'])

        self.left = data['boundary']['left']
        self.right = data['boundary']['right']
        self.bottom = data['boundary']['bottom']
        self.top = data['boundary']['top']

        self.intersection = pd.read_csv("3_1_all_light.csv", encoding='CP949')

        # 필요한 열 이름 바꾸기
        self.intersection = self.intersection.rename(columns={'위도': 'lat', '경도': 'lon', '밝기': 'lux'})
        self.intersection_unique = self.intersection.drop(columns="Unnamed: 0")

        # 드디어 좌표 범위 필터링 방법을 찾음. 파이썬은 참 직관적인 언어인 것 같음. tmi) 나한텐 컴파일 언어가 더 잘 맞는 것 같음.
        self.filteredDF = self.intersection_unique[(self.bottom <= self.intersection_unique.lat) & (self.intersection_unique.lat <= self.top )]
        # 경도도 필터링 해주고~
        self.filteredDF = self.filteredDF[(self.left <= self.filteredDF.lon) & (self.filteredDF.lon <= self.right )]
        # 번호도 다시 붙이고~
        self.filteredDF = self.filteredDF.reset_index(drop=True)

        # 위도 기준으로 분포 고려하여 3등분하기
        self.latClusterDF = pd.qcut(self.filteredDF.lat, 3)
        # 경도 기준으로 분포 고려하여 3등분하기
        self.lonClusterDF = pd.qcut(self.filteredDF.lon, 3)

        # 필요없는 열 정리해버림.
        self.df = self.filteredDF.drop(['feature_ID', '명칭', '분류','lux'], 1)

        self.model = KMeans(n_clusters=3, algorithm='auto')
        self.model.fit(self.df)
        self.predict = pd.DataFrame(self.model.predict(self.df))
        self.predict.columns = ['predict']

        r = pd.concat([self.df, self.predict], axis=1)

        self.data_points = np.array(self.df.values)
        self.kmeans = KMeans(n_clusters=3).fit(self.data_points)

        self.ps_list = self.kmeans.cluster_centers_
        self.ps = str(self.ps_list[0][1]) + "," + str(self.ps_list[0][0]) + "_" + str(self.ps_list[1][1]) + "," + str(self.ps_list[1][0]) + "_" + str(self.ps_list[2][1]) + "," + str(self.ps_list[2][0])

    def get_ps(self):
        return self.ps





