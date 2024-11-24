from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

# 크롬 시스템에 설치된 브라우저와 버전을 동일하게 하기 위해 버전에 맞는 크롬 드라이버 자동 다운
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# 지그재그 홈페이지 접속
# 지그재그 웹사이트를 열어서 원하는 데이터를 수집하기 위해 접속
driver.get("https://www.zigzag.kr/")

# '카테고리' 메뉴 클릭
category_menu = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/a[2]')
category_menu.click()
time.sleep(1)  # 페이지가 로드될 시간을 기다림

# '팬츠' 버튼 클릭
# 카테고리에서 팬츠 선택
subcategory_menu = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/section/section[2]/ul/li[1]/button[5]/p')
subcategory_menu.click()
time.sleep(1)  # 페이지 로딩을 기다림

# '와이드 팬츠' 버튼 클릭
# 팬츠에서 와이드 팬츠 선택
sort_option = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/nav[3]/ul/li[6]')
sort_option.click()
time.sleep(2)  # 정렬 옵션이 제대로 로드되도록 기다림

# 정렬 옵션을 바꾸기 위해 '필터' 버튼 클릭
# 리뷰 많은 순으로 바꾸기 위해 필터 버튼을 클릭해서 드롭다운메뉴 펼치기
recommend_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/section[1]/button')
recommend_button.click()
time.sleep(1)

# '리뷰 많은 순' 버튼 클릭
# 리뷰가 많은 순으로 정렬하는 버튼을 클릭하여 선택
review_option = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/section[1]/div[2]/div[2]/div/ul/li[3]')
review_option.click()
time.sleep(1)

##### 상품 정보 수집

# 함수 정의
def get_top_30_products(driver):
    name, prices, sale_ratio, review_rate, review_number, thumbnail, product_links = [], [], [], [], [], [], []

    # 현재 페이지에 로드된 상품 묶음 정보 가져오기
    while len(name) < 30:
        product_groups = driver.find_elements(By.CLASS_NAME, 'css-1y9zosf')

        # 개별 상품 정보 가져오기
        # 한 번에 최대 12개의 상품 정보만 수집 가능하므로 스크롤을 조금씩 내려서 다음 상품 정보를 수집해야 함
        for group in product_groups:
            items = group.find_elements(By.CLASS_NAME, 'css-5hci9z')

            for item in items:
                if len(name) == 30:
                    return name, prices, sale_ratio, review_rate, review_number, thumbnail, product_links

                # 상품 중복 방지
                product_name_candidate = item.find_element(By.XPATH, './/div/div[2]/div[1]/div/p').text
                if product_name_candidate in name:
                    continue

                # 상품 정보 추출
                # 상품 이름 추출
                try:
                    product_name = product_name_candidate
                    name.append(product_name)
                except:
                    name.append("")
                # 할인율 추출
                discount = item.find_element(By.XPATH, './/div/div[2]/div[2]/div/div/span[1]').text
                if '%' in discount:
                    sale_ratio.append(discount)
                else:
                    discount='0%'
                    sale_ratio.append(discount)
                # 가격 추출
                try:
                    price = item.find_element(By.XPATH, './/div/div[2]/div[2]/div/div/span[2]').text
                    prices.append(price)
                except:
                    price = item.find_element(By.XPATH, './/div/div[2]/div[2]/div/div/span[1]').text
                    prices.append(price)
                # 리뷰 평점 추출
                try:
                    rating = item.find_element(By.XPATH, './/div/div[2]/div[4]/div/div/span[2]').text
                    review_rate.append(rating)
                except:
                    rating = item.find_element(By.XPATH, './/div/div[2]/div[3]/div/div/span[2]').text
                    review_rate.append(rating)
                # 리뷰 수 추출
                try:
                    review = item.find_element(By.XPATH, './/div/div[2]/div[4]/div/div/span[3]').text.replace('(','').replace(')','')
                    review_number.append(review)
                except:
                    review = item.find_element(By.XPATH, './/div/div[2]/div[3]/div/div/span[3]').text.replace('(','').replace(')','')
                    review_number.append(review)
                # 썸네일 이미지 URL 추출
                try:
                    img_url = item.find_element(By.XPATH, './/div/div[1]/div/div/img').get_attribute('src')
                    thumbnail.append(img_url)
                except:
                    thumbnail.append("")

                # 상품 링크 추출
                # 스크롤 조금씩 내려며 상품 url 수집 함수
                try:
                    product_link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    product_links.append(product_link)
                except:
                    product_links.append("")

        # 추출한 상품 정보 30개가 안 되면 추가 스크롤 수행
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(4)  #충분한 로딩 시간

    return name, prices, sale_ratio, review_rate, review_number, thumbnail, product_links

# 상위 30개 상품 추출
name, prices, sale_ratio, review_rate, review_number, thumbnail, product_links = get_top_30_products(driver)


# 데이터프레임 생성 및 ID 추가
data = pd.DataFrame({
    'id': range(1, len(name) + 1),
    'name': name,
    'price': prices,
    'sale_ratio': sale_ratio,
    'review_rate': review_rate,
    'review_number': review_number,
    'thumbnail': thumbnail
})

# CSV 파일로 저장 (utf-8-sig 인코딩 사용)
df_products = pd.DataFrame(data)
df_products.to_csv('products.csv', index=False, encoding='utf-8-sig')


##### 리뷰 정보 수집

# 각 상품 링크는 위에서 상품 정보 수집과 함께 product_links로 수집함
# 리뷰에 대한 정보 수집 함수
def get_reviews():
    reviews = [] # 리뷰 수집 정보 저장할 리스트
    review_id = 1  # 리뷰 번호 초기값 설정

    for product_index, product_url in enumerate(product_links, start=1):  # 첫 번째 항목의 번호를 1로 시작하게 바꿔줌 # 상품번호 매길때 사용하기 위함
        driver.get(product_url + "?tab=review") # 리뷰 페이지로 바로 접속 # 여기서 시행 착오 적으면 좋을듯
        time.sleep(7)  # 페이지 로드 대기

        # 리뷰 정보 수집 (5개 리뷰) # 리뷰어 id, 날짜, 텍스트 등이 다 나와있는 하나의 리뷰 묶음 > 사진으로 보여주면 좋을듯
        review_elements = driver.find_elements(By.CSS_SELECTOR, ".css-u0gd1c.e1hradnr0")[:5]

        for review_element in review_elements:
            reviewer_id = review_element.find_element(By.CSS_SELECTOR, ".BODY_14.SEMIBOLD.css-v0z0bg.e1oql6860").text # 리뷰어 id 텍스트 수집
            review_date = review_element.find_element(By.CSS_SELECTOR, ".BODY_17.REGULAR.CAPTION_12.SEMIBOLD.css-e9zz9.e1oql6860").text # 리뷰 날짜 텍스트 수집

            review_text_element = review_element.find_element(By.CLASS_NAME, "BODY_14.REGULAR.css-epr5m6.e1loaqv40") # 리뷰 텍스트 부분 찾기

            # 리뷰 텍스트에서 더보기 버튼 있는 경우 클릭 # 더보기 버튼을 눌러야 전체 리뷰 text가 보이기 때문
            try:
                more_button = review_text_element.find_element(By.CSS_SELECTOR, ".BODY_13.BOLD.css-1aa4nqt.e1loaqv41") # 더보기 버튼 찾기
                driver.execute_script("arguments[0].click();", more_button) # 셀레니움에서 자바스크립트 실행해서 버튼 누르기 # 셀레니움 클릭으로는 더보기가 실행되지 않는 경우가 있음, html요소가 동적 생성이기 때문 # 하나하나 무슨 뜻인지 적으면 좋을듯
                time.sleep(1) # 로딩 대기 시간
            except Exception:
                pass # 더보기 버튼이 없다면 지나가기

            # 리뷰 텍스트 추출
            review_text = review_text_element.text

            # 리스트에 리뷰 내용 저장
            reviews.append({
                "id": review_id,
                "product_id": product_index,
                "reviewer": reviewer_id,
                "date": review_date,
                "text": review_text
            })

            review_id += 1  # 리뷰 번호 1 증가 (다음 리뷰로 넘어갔다는 뜻)

    return reviews # 결과 리스트 반환

reviews_elements = get_reviews() # 리뷰 내용 저장

# CSV로 저장
df_reviews = pd.DataFrame(reviews_elements)
df_reviews.to_csv('reviews.csv', index=False, encoding='utf-8-sig')

# 드라이버 종료
driver.quit()