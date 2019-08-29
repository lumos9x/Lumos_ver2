# naver에서 편의점 목록을 크롤링하고, 해당 목록으로 google에서 경위도 좌표를 가져온다.
import os, settings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import pandas as pd

# 재사용성 생각해서 다시 로직 짜보기
class MapCrawling:

    def processing(self, df, category_nm):
        # 공통 전처리 부분 / df 넘기기 전에 df 컬럼 [명칭,주소, 위도, 경도] 로 통일할 것.
        df1 = df.dropna()  # 1. NaN 값이 하나라도 들어가 있는 행은 그 행 전체를 제거
        df1['분류'] = category_nm  # 2. 분류 추가하기.
        df2 = df1.drop_duplicates(keep='first')  # 3. 중복되는 행 하나만 남기고 제거하기(부정확한 데이터)
        # ex) [1599 rows x 4 columns] => [1231 rows x 4 columns]
        res = df2.reset_index(drop=True)  # 4. reset index를 통해 index를 0부터 새롭게 지정.
        return res


    def crawling_naver(self, dong, facility, num = 5):
        numPages = num  # 세트 하나당 page수

        def preprocessingForGoogle(cs_name, cs_address):
            # '서울특별시 강남구 테헤란로 201 아주빌딩 지번' 형태로 출력되어 오른쪽의 지번을 제거해준다.
            li1 = []
            for i in range(0, len(cs_address)):
                li1.append(cs_address[i].rstrip(' 지번'))

            # '서울특별시 강남구 논현로95길 29-13 1층 (역삼동 644-3)'와 같은 형태는 '(' 뒤로 모두 삭제해야 google맵에서 좌표 찾을때 제대로 찾음.
            li2 = []
            for i in li1:
                if i.find("(") > 0:
                    li2.append(i[0:i.find("(")])
                else:
                    li2.append(i)

            data = {'명칭': cs_name,
                    '주소': li2}

            res_df = pd.DataFrame(data)
            return res_df

        # 1. driver setting: This version of ChromeDriver supports Chrome version 76
        # driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver.exe')
        driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
        driver = webdriver.Chrome(driver_path)
        driver.get('https://map.naver.com/')
        wait = WebDriverWait(driver, 20)   # 명시적 대기. 명시된 시간까지 기다리고 아니면 TimeoutException. cf) time.sleep(10): loading 여부와 상관없이 항상 정해진 시간을 기다림)

        # 2. Researching
        driver.find_element_by_id('search-input').send_keys(dong + " " + facility) # '역삼1동 편의점'
        driver.find_element_by_css_selector('#header > div.sch > fieldset > button').click()

        page, cs_name, cs_address  = 1, [], []

        #.3. Crawling
        while( True ):
            ###############################################################################################################################
            # [ https://seleniumhq.github.io/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.expected_conditions.html ]  #
            # presence_of_element_located: An expectation for checking that an element is present on the DOM of a page. 올라갔는지 확인      #
            # staleness_of : returns False if the element is still attached to the DOM, true otherwise. 아직 올리고 있는지 확인.              #
            # 의문점 : staleness_of와 presence_of_element_located 중복해서 쓸 필요가 있을까?                                                    #
            #   I Guess......                                                                                                             #
            #   click하기전에 element를 저장해두고 click후에 해당 element가 여전히 있는지 확인. 없다면 그것은 click하고 새로운 페이지가 load됐다는 뜻이야.  #
            #   그담에 presence_of_element_located로 내가 원하는 애가 정상적으로 올라와있는지 확인하고 다음 코드를 진행하는 것!                          #
            ###############################################################################################################################
            # 3-1. Get a new list
            try:
                cs_list = wait.until( expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "lsnx_det")))

            except TimeoutException:
                print("해당 페이지에 lsnx_det 을 ID 로 가진 태그가 존재하지 않거나, 해당 페이지가 10초 안에 열리지 않았습니다.")


            # 3-2. Store the addresses
            for data in cs_list:
                title = data.find_element_by_tag_name('a').text
                address = data.find_element_by_class_name('addr').text
                cs_name.append(title)
                cs_address.append(address[:100])

            # 3-2. Move to the next page
            # print(page)
            page = page + 1
            page_mod = page % numPages

            if page_mod == 1: #다음 페이지가 새로운 묶음이면
                try:
                    element = driver.find_element_by_class_name("lst_site")
                    driver.find_element_by_class_name('next').click()
                    wait.until(expected_conditions.staleness_of(element)) # returns False if the element is still attached to the DOM, true otherwise.

                except:
                    break
            else:
                # css selector에서 페이지 클릭을 위한 nth-child는 2,3,4,5,6 이다. 따라서 다음에 클릭할 페이지가 묶음의 마지막이라면 0+1 = 1이 아닌 6이되어야한다.
                num=numPages+1 if page_mod==0 else page_mod + 1

                try :
                    element = driver.find_element_by_class_name("lst_site")
                    driver.find_element_by_css_selector(f'div.search_result > div > div > a:nth-child({str(num)})').click()
                    wait.until(expected_conditions.staleness_of(element))

                except:
                    break

        driver.close() # 드라이버 닫아주기
        print('naver_done')

        # 데이터 전처리
        res_df = preprocessingForGoogle(cs_name, cs_address)
        return res_df

    def crawling_google(self, input_df):
        # Get a dataframe of convenience store's coordinates.
        import googlemaps
        import settings

        gmaps_key = settings.get_secret("GOOGLE_MAP_KEY")
        gmaps = googlemaps.Client(key = gmaps_key)

        cs_lat = []
        cs_lng = []
        cs_address = input_df['주소'].values.tolist()
        cs_name = input_df['명칭'].values.tolist()

        for i in range(0,len(cs_address)):
            # 위의 코드에서 'geometry'가 가지고 데이터('location'의 'lat', 'lng')를 모두 가져옴
            e = gmaps.geocode(cs_address[i], language = 'ko')[0].get('geometry')
            cs_lat.append(e['location']['lat'])
            cs_lng.append(e['location']['lng'])

        cs_df = pd.DataFrame()
        cs_df['명칭'] = cs_name
        cs_df['주소'] = cs_address
        cs_df['위도'] = cs_lat
        cs_df['경도'] = cs_lng
        return cs_df

    def crawling(self, dong, facility ):
        df = self.crawling_naver(dong, facility)
        coords_df = self.crawling_google(df)
        res_df = self.processing(coords_df, facility)
        return res_df

## 저장소에 연결/저장 코드 추가 필요
if __name__ == '__main__':
    cr = MapCrawling()
    print(cr.crawling("역삼1동", "편의점"))
