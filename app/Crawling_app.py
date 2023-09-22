from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine,text
import uvicorn
import time
import openai
import sys
sys.path.append('C:/Users/Playdata/Desktop/git/Fast_api/Fast_api_private/')
from api_key import api_key
from db_connect import db_host, db_user, db_password, db_database, table_name

def main(Main_Page_Url):
    try:
        # headless option
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--headless")
        options.add_argument("--disable-setudid-sandbox")

        driver = webdriver.Chrome(options=options)
        driver.get(Main_Page_Url)
        time.sleep(2)

        region = driver.find_element(By.ID, "expand")
        region.click()
        time.sleep(2)

        title = driver.find_elements(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string')

        for i in title:
            title_text = i.text

        script = driver.find_elements(By.XPATH, '//*[@id="description-inline-expander"]')

        for i in script:
            scrpit_text = i.text

        scrpit_text = scrpit_text.replace('\n',' ')
        return title_text, scrpit_text
    
    except Exception as e:
        print('error:', e)
        quit()

def connect_db(Main_Page_Url):
    
    # MySQL 데이터베이스에 연결
    db_engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_database}')

    query = f"SELECT url FROM {table_name};"

    with db_engine.connect() as connection:
        result = connection.execute(text(query))
        # 쿼리 결과 처리
        for row in result:
            url = row['url']  # 'title'은 쿼리 결과의 컬럼 이름에 따라 조정
            if url == Main_Page_Url:
                db_title = False
                break
            else:
                db_title = True
    return db_title

def get_products(scrpit_text):
    openai.api_key = api_key
    query = """아래 주어진 글에서 재료만 뽑아서 아래 형태로 정리해줘. 요청한 정보외 다른글은 제거해줘.

                형태 : {양파 : 1개, 당근: 1개, ...}
                
                """ + f"""글 : {scrpit_text}"""
                
    messages = [
        {"role": "user",
         "content": query}
    ]

    # ChatGPT API 호출하기
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.4
    )
    answer = response['choices'][0]['message']['content']
    return answer

app = FastAPI()

@app.get("/{Main_Page_Url}")
def process(Main_Page_Url:str):
    Main_Page_Url = 'https://www.youtube.com/watch?v='+Main_Page_Url
    db_title = connect_db(Main_Page_Url)  
    if db_title:
        title_text, scrpit_text = main(Main_Page_Url)
        answer = get_products(scrpit_text)
        final = "{title: "+f"{title_text}, "+"script : " + f"{answer}" + "}"
        return final
    else:
      print("이미 등록된 자료.")
      return "이미 등록된 자료."

if __name__ == '__main__':
    uvicorn.run("Crawling_app:app", host='0.0.0.0', port=3000, reload=True)