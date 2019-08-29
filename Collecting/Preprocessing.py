import os, settings
import pandas as pd
from haversine import haversine


class Scoring:

    def light_score_on_facility(self, facility_df):
    #  Give each facility 'light(밝기)' score based on survey result.
        all_df = pd.DataFrame(columns=['밝기', '분류', '명칭', '위도', '경도'])
        for i in range(len(facility_df)):
            score = 0
            # 설문 결과
            if facility_df['분류'][i] == '파출소':
                score += 250 #25.471
            elif facility_df['분류'][i] == '보안등':
                score += 280 #28.397
            elif facility_df['분류'][i] == '편의점':
                score += 210 #21.774
            elif facility_df['분류'][i] == 'CCTV':
                score += 240 #24.357
            else :
                print('WARNING : Detected wrong category!! ')

            tmp = {'밝기': score,
                   '분류': facility_df.loc[i, '분류'], '명칭': facility_df.loc[i, '명칭'],
                   '위도': facility_df.loc[i, '위도'], '경도': facility_df.loc[i, '경도']
                   }
            all_df = all_df.append(all_df.from_dict(tmp, orient='index').T)

        all_df.reset_index(inplace=True, drop=True)
        all_df.to_csv(os.path.join(settings.BASE_DIR,'output',"total_with_light.csv"), mode='w', encoding='ms949')
        print("total_with_light : ",  len(all_df))
        return all_df


    def total_light_score_on_road(self, scored_facility_df, road_df, meter = 30):

        ### 도로 좌표의 밝기 구하기 = 오래걸림 -> 요부분을 spark로 가장 먼저 바꿔보자!
        scores = []
        for i in range(len(road_df)):
            score = 0
            s_point = (road_df.loc[i, 'LAT'], road_df.loc[i, 'LNG'])  # 시작점
            for n in range(len(scored_facility_df)):
                t_point = (scored_facility_df.loc[n, '위도'], scored_facility_df.loc[n, '경도'])  # 타겟
                d_m = haversine(s_point, t_point, unit='m')  # 시작점과 타겟의 거리  단위 미터
                # default 반경 30M 를 범위로 잡음
                if d_m <= meter:
                    score += scored_facility_df.loc[n, '밝기']
            # print(i, score) # 잘나옴
            scores.append(score)
        road_df['총밝기'] = scores
        road_df.to_csv(os.path.join(settings.BASE_DIR,'output',"road_with_light.csv"), mode='w', encoding='ms949')
        print("road_with_light : ", len(road_df))
        return road_df


    def get_scored_road(self,total_df, road_df, meter = 30):
        # 시설물에 점수주기
        scored_facility_df = self.light_score_on_facility(total_df)

        # 로드좌표에 점수주기
        scored_road = self.total_light_score_on_road(scored_facility_df, road_df)
        return scored_road


if __name__ == "__main__":

    base_dir = settings.BASE_DIR
    Scr = Scoring()

    ## total_df : facility coordinates
    ## road_df : road coordinates

    # 시설물에 점수주기
    facility_df = pd.read_csv(os.path.join(base_dir,'output', "total_without_road.csv") , encoding = 'ms949')
    facility_df.drop('Unnamed: 0', axis=1, inplace=True)
    scored_facility_df =Scr.light_score_on_facility(facility_df)
    print(scored_facility_df.head(5))

    # 로드좌표에 점수주기
    road_df = pd.read_csv(os.path.join(base_dir, 'output', "COORDS_IN_역삼동.csv"), encoding='ms949')
    road_df.drop('Unnamed: 0', axis=1, inplace=True)
    scored_road = Scr.total_light_score_on_road(scored_facility_df,road_df)
    print(scored_road.head(5))
