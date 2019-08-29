import os
import settings
from Collecting.Crawling import MapCrawling   # Crawling을 class로 묶지 않으면 import하는 순간에 크롬이 실행된다.
from Collecting.Loading import LoadingCSV, LoadingSHP
from Collecting.Preprocessing import Scoring
from LightsOnStreets.Map.Map import LightMap
from LightsOnStreets.PathFinding.Pathfinding import SafePath


import pandas as pd


def collect_data():
    # ## 1. Collecting
    #     # 1-1. 크롤링으로 데이터 수집
    # mcr = MapCrawling()  # 한 화면 당 페이지수
    # polices = mcr.crawling("역삼1동", "파출소")
    # polices.to_csv("polices.csv", mode='w', encoding='ms949')
    # stores = mcr.crawling("역삼1동", "편의점")
    # stores.to_csv("stores.csv", mode='w', encoding='ms949')
    #
    # ## 2. 파일 로드해서 데이터 수집
    #     # 2-1. csv
    # ld_csv = LoadingCSV()
    # lights = ld_csv.load_light('3220000', '역삼1동')  # code, 동이름
    # lights.to_csv("lights.csv", mode='w', encoding='ms949')
    # cctvs = ld_csv.load_cctv('역삼동')  # 동이름
    # cctvs.to_csv("cctvs.csv", mode='w', encoding='ms949')
    #
    #     # 2-2. shp
    # file = os.path.join(settings.BASE_DIR, 'data', '서울특별시_강남구_도로정보', '11680', 'TL_SPRD_MANAGE.shp')
    # rd_shp = LoadingSHP()
    # road_coords = rd_shp.load_shp_by_region(file, '역삼동')
    # print(road_coords.head(30))
    # road_coords.to_csv(f"COORDS_IN_역삼동.csv", mode='w', encoding='ms949')  # edge(=link) list
    #
    # ## 3. Total Table 만들기.
    #     # 3-1.total_facilities
    # total_without_road = pd.concat([polices, stores, lights, cctvs]).reset_index(drop=True)
    # total_without_road.to_csv("total_without_road.csv", mode='w', encoding='ms949')


    total_without_road = pd.read_csv(os.path.join(base_dir, 'output', "total_without_road.csv"), encoding='ms949')
    total_without_road.drop('Unnamed: 0', axis=1, inplace=True)
    print(total_without_road.head(4))

    road_coords = pd.read_csv(os.path.join(base_dir, 'output', "COORDS_IN_역삼동.csv"), encoding='ms949')
    road_coords.drop('Unnamed: 0', axis=1, inplace=True)
    print(road_coords.head(4))

    return total_without_road, road_coords




if __name__ == "__main__":

    ############################# 공통 #############################
    print(__name__)
    base_dir = settings.BASE_DIR

    ############################# 기능 구현 #############################
    ## 1. collecting
    facility_df, road_df = collect_data()

    ## 2. Scoring
    scr = Scoring()
    scored_road = scr.get_scored_road(facility_df, road_df)
    print(scored_road.head(3))

    ## 3. Map
    # lm = LightMap()
    # res = lm.lux_on_link(road_df)
    # lm.display(road_df, res, True)

    ## 4. PathFinding
    sp = SafePath()
    sp.find_path(sp.set_destination(road_df, start=(37.506059, 127.036863), end=(37.509122, 127.043816)))

    print(road_df)