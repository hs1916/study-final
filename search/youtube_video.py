from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)


# Youtube Video 검색
def search_videos(keyword: str, youtube: any, max_results: int = 10) -> any:
    search_response = (
        youtube.search()
        .list(q=keyword, part="id,snippet", maxResults=max_results)
        .execute()
    )

    videos = []
    for res in search_response["items"]:
        if res["id"]["kind"] == "youtube#video":
            videos.append(
                {
                    "title": res["snippet"]["title"],
                    "description": res["snippet"]["description"],
                    "channelTitle": res["snippet"]["channelTitle"],
                    "videoId": res["id"]["videoId"],
                }
            )
    return videos

# Youtube Video 검색
def search_videos_response(keyword: str, youtube: any, max_results: int = 10) -> any:
    search_response = (
        youtube.search()
        .list(q=keyword, part="id,snippet", maxResults=max_results)
        .execute()
    )

    videos = []
    for res in search_response["items"]:
        if res["id"]["kind"] == "youtube#video":
            videos.append(
                {
                    "title": res["snippet"]["title"],
                    "description": res["snippet"]["description"],
                    "channelTitle": res["snippet"]["channelTitle"],
                    "videoId": res["id"]["videoId"],
                }
            )
    return search_response



# 자막 저장 및 document split
def youtube_caption_load(video_id: str) -> any:
    loader = YoutubeLoader.from_youtube_url(
        youtube_url="https://youtu.be/" + video_id, language="ko", add_video_info=True
    )
    # document = loader.load_and_split(text_splitter=text_splitter)
    document = loader.load()
    return document
