# 나의 python 버전
FROM python:3.11.4

# 작업 장소 지정
WORKDIR /code

RUN apt-get -y update
RUN apt install wget
RUN apt install unzip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb
RUN wget -O chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.92/linux64/chromedriver-linux64.zip
RUN mkdir chrome
RUN unzip chromedriver.zip
RUN mv chromedriver-linux64/chromedriver /usr/bin

# ./requirements.txt 를 /requirements.txt 로 복사
COPY ./requirements.txt /code/requirements.txt

# requirements.txt 를 보고 모듈 전체 설치(-r)
RUN pip install --no-cache-dir -r /code/requirements.txt

# 이제 app 에 있는 파일들을 code/app 에 복사
COPY ./app /code/app
COPY ./private /code/private
COPY ./chromedriver /code/chromedriver

EXPOSE 3000

# 실행
CMD ["uvicorn", "app.Crawling_app:app", "--host", "0.0.0.0", "--port", "3000"]