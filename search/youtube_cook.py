from langchain.document_loaders import YoutubeLoader
from googleapiclient.discovery import build
import requests
import json
import csv
import os
import traceback
from datetime import date
from search.youtube_video import search_videos_response

# ========= 유튜브로 요리 레시피 조회 ==========

#AIzaSyCMsyAYpQNJS3MwcxT4AfGTTZUVUdC_0Uw (dohchoi91)
#AIzaSyAkX8HZmKnOdh9RJ8FH7j84VMKllpZYXuw (dohchoi0118)
#AIzaSyCftV7VQwPTe88J9CWRIrEDzWODqsMmNYg (dhyun175)

youtube_api_key = 'AIzaSyCftV7VQwPTe88J9CWRIrEDzWODqsMmNYg'

# youtube = build('youtube', 'v3', developerKey=youtube_api_key)
directory_path = "../csv/cook"  # 하위 디렉토리 경로


# JSON 데이터를 CSV 파일로 저장하는 함수
def save_json_to_csv(json_data, file_name):
    file_path = os.path.join(directory_path, file_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # CSV 파일 열기
    with open(file_path, 'wt', encoding='utf8', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # 헤더 정보 작성
        headers = list(json_data[0].keys())
        writer.writerow(headers)

        # 데이터 작성
        for data in json_data:
            writer.writerow(list(data.values()))

            
def get_json_data(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 상태코드를 확인하고 오류가 발생하면 예외를 발생시킴
        data = response.json()  # JSON 데이터를 파이썬 객체로 변환
        return data
    except requests.exceptions.HTTPError as errh:
        print("HTTP 오류 발생:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("연결 오류 발생:", errc)
    except requests.exceptions.Timeout as errt:
        print("타임아웃 오류 발생:", errt)
    except requests.exceptions.RequestException as err:
        print("기타 오류 발생:", err)


def find_youtube_video(next_page_token):
    # 유튜브 동영상 검색
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': '뚝딱이형',
        'type': 'video',
        'maxResults': 25,
        'regionCode': 'kr',
        'key': youtube_api_key,
        'videoDuration':'short',
        'pageToken': next_page_token
    }
    return get_json_data(url, params=params)

def exist_caption(video_id, youtube):
    print('exist_caption_check?')
    captions_response = youtube.captions().list(
        part='snippet',
        videoId=video_id
    ).execute()
    return captions_response['items']


def extract_video(video_id):
    
    print('extract_video?')
    result = {
        'contents' : '',
        'view_count' : 0,
    }
    url = 'https://www.youtube.com/watch?v=%s' % video_id
    print(url)
    loader = YoutubeLoader.from_youtube_url(url, language = "ko", add_video_info=True)
    load_results = loader.load()
    print('extract_video?????')
    if load_results:
        load_results[0].page_content
        result['contents'] = load_results[0].page_content
        result['view_count'] = load_results[0].metadata['view_count']

    print('extract_video?????')
    return result

def youtube_cook_video(query:str, youtube:any):

    # 파일 이름 설정
    today = date.today().strftime("%Y-%m-%d")  # 오늘 날짜를 YYYY-MM-DD 형식으로 가져옴
    file_name = f"data_{today}.csv"  # 오늘 날짜를 포함한 파일 이름

    # 결과 설정
    cnt = 10
    idx = 0
    results = []

    video_results = search_videos_response(query, youtube)
    print('--------------------')
    print(video_results)
    print('--------------------')
    try:
        while (idx < cnt) and (video_results):
            print(video_results['pageInfo']['totalResults'])
            for item in video_results['items']:
                
                video_id = item['id']['videoId']
                print('[%d] %s .... 진행중 '% (idx + 1, video_id))
                if exist_caption(video_id, youtube):
                    print('check 됐고?')
                    idx = idx + 1
                    video_detail = extract_video(video_id)
                    new_item = {
                        'video_id' : video_id,
                        'thumbnails' : item['snippet']['thumbnails']['medium']['url'],
                        'video_url' : 'https://www.youtube.com/watch?v=%s' % video_id,
                        'title' : item['snippet']['title'],
                        'description' : item['snippet']['description'],
                        'contents' : video_detail['contents'],
                        'view_count' : video_detail['view_count']
                    }
                    print('append 직전')
                    results.append(new_item)
                if idx >= cnt:
                    break

            if video_results['nextPageToken']:
                video_results = find_youtube_video(video_results['nextPageToken']);
    
    except Exception as err: 
        print("오류 발생:", err)

        
    
    print(results)
    save_json_to_csv(results, file_name)
    print("=========================== Finish =========================== ")


