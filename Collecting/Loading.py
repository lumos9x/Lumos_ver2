import pandas as pd
import settings
import os

## shp 컬럼 정보
##


class LoadingCSV:
    def preprocessing(self, df, category_nm):
        # 공통 전처리 부분 / df 넘기기 전에 df 컬럼 [명칭,주소, 위도, 경도] 로 통일할 것.
        df1 = df.dropna()                               # 1. NaN 값이 하나라도 들어가 있는 행은 그 행 전체를 제거
        df1['분류'] = category_nm                        # 2. 분류 추가하기.
        df2 = df1.drop_duplicates(keep='first')         # 3. 중복되는 행 하나만 남기고 제거하기(부정확한 데이터)
        # ex) [1599 rows x 4 columns] => [1231 rows x 4 columns]

        res = df2.reset_index(drop=True)                # 4. reset index를 통해 index를 0부터 새롭게 지정.
        return res

    def load_light(self, prvd_code,dong):
        ### 보안등 - 원본 자료 부정확
        ### 정확한 보안등 데이터를 위해서 실제로 돌아보며 정확한 위치 기록하는 수작업 필요함.
        file = os.path.join(settings.BASE_DIR, 'data', '전국보안등정보표준데이터.csv')
        light_df = pd.read_csv(file, encoding='ms949', engine='python')

        # 2-1. 지역필터링 gu > dong
        # prvd_name_df = light_df[light_df.제공기관명.str.contains(gu)] # gu = 강남구
        gu_df = light_df[light_df.제공기관코드 == prvd_code]          # prvd_code = '3220000'
        dong_df = gu_df[gu_df.보안등위치명.str.contains(dong)]        # dong='역삼1동'

        # 2-2. 위도,경도 결측치 확인하고 결측치 제거.
        # print(dong_df.isnull().sum())     # Null 값 20개
        # dong_df[dong_df.위도.isnull()]
        dong_df2 = pd.DataFrame()
        dong_df2['명칭'] = dong_df['보안등위치명']
        dong_df2['주소'] = dong_df['소재지지번주소']
        dong_df2['위도'] = dong_df['위도']
        dong_df2['경도'] = dong_df['경도']
        return self.preprocessing(dong_df2,'보안등')

    def load_cctv(self, dong):
        file = os.path.join(settings.BASE_DIR, 'data', '서울특별시_강남구_CCTV_20190312.csv')
        gucc_df = pd.read_csv(file, encoding='ms949', engine='python')
        dongcc_df = gucc_df[gucc_df.소재지지번주소.str.contains(dong)]
        dong_df2 = pd.DataFrame()
        dong_df2['명칭'] = dongcc_df['소재지지번주소']
        dong_df2['주소'] = dongcc_df['소재지지번주소']
        dong_df2['위도'] = dongcc_df['위도']
        dong_df2['경도'] = dongcc_df['경도']

        # 명칭은 동부터 기록하기
        address = []
        for name in dong_df2['명칭']:
            nm = name[10:]
            address.append(nm)
        dong_df2['명칭'] = address

        return self.preprocessing(dong_df2,'CCTV')


class LoadingSHP:
    import json

    def load_shp(self,file):
        import shapefile  # pip install pyshp
        print('load_SHP')
        # 좌표 추출 함수
        def get_coordninates(load_points, inCoords='epsg:5179', outCoords='epsg:4326'):
            print('get_coordninates')
            from pyproj import Proj, transform  # pip install pyproj

            # 1. 좌표 체계 설정
            inProj = Proj(init=inCoords)
            outProj = Proj(init=outCoords)  # wgs84

            # 2. 좌표 변환/추출 #########매~~~~~~~~우느림 원인파악하기.)  --> 이부분 애초에 lat, lan으로 저장하도록 수정하자.
            COORDS = []
            for i in range(0, len(load_points)):
                a = load_points[i]
                b = list(map(lambda x: transform(inProj, outProj, x[0], x[1]), a))
                COORDS.append(b)

            return COORDS

        # 1. 파일 읽기
        shape = shapefile.Reader( file , encoding="euc-kr") # TL_SPRD_MANAGE.shp -> 강남구
        # print("\n 1. type : ", shape.shapeType)   # type :  3 - polyline

        # 2. 레코드 가져오기
        fields_node = [x[0] for x in shape.fields][1:]                  # 필드 데이터
        records_node = [list(x.record) for x in shape.shapeRecords()]   # 데이터
        load_points = [s.points for s in shape.shapes()]                # 좌표 데이터

        # 3. DataFrame으로 만들기
        record_df = pd.DataFrame(columns=fields_node, data=records_node)
        record_df['COORDS']  = get_coordninates(load_points)            # 좌표 정보 추가

        # 4. *************** 중간 결과 저장 (좌표변환이 느리므로 저장해두자!) *******************
        # record_df.to_csv("all_records_raw.csv", mode='w', encoding='ms949')
        return record_df

    def filter_region(self, record_df, region='역삼동'):
        print('filter_region')
        df = record_df[(record_df.RBP_CN.str.contains(region)) | (record_df.REP_CN.str.contains(region))]
        region_df = df.reset_index(drop=True)
        # df.to_csv(f"1_2_{region}_all_records_raw.csv", mode='w', encoding='ms949')  # edge(=link) list
        return region_df

    def preprocessing(self, df):
        print('preprocessing')
        # COORDS에 묶여있는 Node정보 Row로 저장
        # 'SIG_CD' , 'RDS_MAN_NO', 'RN', 'RN_CD', 'ROAD_BT', 'ROAD_LT', 'LAT', 'LNG'
        # '시군구코드','도로구간일련번호','도로명','도로명코드','도로폭','도로길이','위도', '경도'
        all_coords = pd.DataFrame(columns=['SIG_CD', 'RDS_MAN_NO', 'RN', 'RN_CD', 'ROAD_BT', 'ROAD_LT', 'LAT', 'LNG'])
        tmp = pd.DataFrame( columns=['SIG_CD', 'RDS_MAN_NO', 'RN', 'RN_CD', 'RDS_MAN_NO2', 'ROAD_BT', 'ROAD_LT', 'COORDS'])

        for i in range(0, len(df)):
            tmp = df.loc[i, ['SIG_CD', 'RDS_MAN_NO', 'RN', 'RN_CD', 'ROAD_BT', 'ROAD_LT', 'COORDS']]
            for j in range(0, len(tmp.COORDS)):
                all_coords = all_coords.append(all_coords.from_dict({'SIG_CD': tmp.SIG_CD
                                                                        , 'RDS_MAN_NO': tmp.RDS_MAN_NO
                                                                        , 'RN': tmp.RN
                                                                        , 'RN_CD': tmp.RN_CD
                                                                        , 'RDS_MAN_NO2': j
                                                                        , 'ROAD_BT': tmp.ROAD_BT
                                                                        , 'ROAD_LT': tmp.ROAD_LT
                                                                        , 'LAT': tmp.COORDS[j][1]
                                                                        , 'LNG': tmp.COORDS[j][0]}, orient='index').T)

        sorted_all_coords = all_coords.sort_values(by=['RN_CD', 'RDS_MAN_NO', 'RDS_MAN_NO2']).reset_index(drop=True)
        # all_coords.to_csv(f"1_3_COORDS_IN_{region}.csv", mode='w', encoding='ms949')  # edge(=link) list
        res_df = sorted_all_coords.loc[:, ['SIG_CD', 'RDS_MAN_NO', 'RDS_MAN_NO2', 'RN_CD', 'RN', 'LAT', 'LNG']]    #KEY : SIG_CD,RDS_MAN_NO,RDS_MAN_NO2

        # 2_save_total_load_points.ipynb => 추가해야함.

        return res_df

    def load_shp_by_region(self, file, region):
        # 다양한 지역 구성할때 경로 및 파일명 수정 필요
        region_df = self.filter_region(self.load_shp(file), region)
        res = self.preprocessing(region_df)
        # res.to_csv(f"COORDS_IN_역삼동.csv", mode='w', encoding='ms949')  # edge(=link) list
        return res

if __name__ == '__main__':
    # rd = LadingCSV()
    # print(rd.load_Light('3220000', '역삼1동').head(5)) #code, 동이름
    # print(rd.load_CCTV('역삼동').head(5))  # 동이름    # rd = RoadingCSV()
    # print(rd.load_Light('3220000', '역삼1동').head(5)) #code, 동이름
    # print(rd.load_CCTV('역삼동').head(5))  # 동이름

    ## SHP
    rd_shp = LoadingSHP()
    file = os.path.join(settings.BASE_DIR , 'data', '서울특별시_강남구_도로정보', '11680', 'TL_SPRD_MANAGE.shp' )
    res = rd_shp.load_shp_by_region(file, '역삼동')
    # res.to_csv(f"COORDS_IN_역삼동.csv", mode='w', encoding='ms949')  # edge(=link) list
    print(res.head(5))




