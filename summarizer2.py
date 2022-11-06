from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

def yt_summarizer(video_link):

    #splitting of video link
    video_id = video_link.split("v=")[-1]
    trans_json = YouTubeTranscriptApi.get_transcript(video_id)
    print(trans_json[:5])

    trans_list = []
    for i in range(len(trans_json)):
        txt = trans_json[i]['text']
        #Filtering if it is a closed caption
        if txt[0]=="[":
            continue
        if ":" in txt:
            txt = ":".split(txt)[-1]
        print(txt)
        trans_list.append(txt)
    trans_para = (" ").join(trans_list)

    model = "t5-base"

    summarizer = pipeline("summarization",model=model)
    summarized = summarizer(trans_para,min_length=80)
    return summarized[0]['summary_text']