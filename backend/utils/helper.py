import os, re
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document



def video_id(url: str) -> str:
    m = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    if not m: raise ValueError("Invalid YouTube URL")
    return m.group(1)




def fetch_transcript(url: str) -> str:
    vid = video_id(url)
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(vid)
    return " ".join([item.text for item in transcript])

def chunk(text: str, size=800, overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=size,chunk_overlap=overlap)
    return splitter.split_text(text)


