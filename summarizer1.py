from googleapiclient.discovery import build
import aniso8601
import re
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from datetime import datetime,date,time
import math

def yt_summarizer(video_link):
    api_key = "AIzaSyCeGYBIo3mvMTpCfiuSa-HzAmpQALk4GC4"

    #Getting youtube resource
    youtube = build('youtube','v3',developerKey=api_key)

    #Splitting video link
    #video_link = "https://www.youtube.com/watch?v=Qr4QMBUPxWo"
    video_id = video_link.split("v=")[-1]

    #Getting description
    l = youtube.videos().list(part="snippet",id=video_id).execute()
    items = l.get("items")[0]
    snippet=items["snippet"]
    desc = snippet["description"]

    #Getting duration
    d = youtube.videos().list(part="contentDetails",id=video_id).execute()
    items1 = d.get("items")[0]
    contentDetails = items1["contentDetails"]
    dur = contentDetails["duration"]  

    #converting duration
    rdur = aniso8601.parse_duration(dur)
    duration = str(rdur)

    #finding the chapter times in description
    match = re.finditer(r'(?P<time>\d{2}:\d{2}:\d{2}|\d{2}:\d{2}|\d{1}:\d{2}:\d{2})\)?\s(\-)?(\s)?(?P<chapterTitle>.*)',desc)
    l = []
    for i in match:
      x = re.compile(r'\d{1}:\d{2}:\d{2}')
      z = x.match(i.group('time'))
      x2 = re.compile(r'\d{2}:\d{2}') 
      z2 = x2.match(i.group('time'))
      if z:
        t = '0' + i.group('time')
        print(t)
        dict = {'time' : '0'+ i.group('time'),
              'chapterTitle': i.group('chapterTitle')}
      elif x2:
        dict = {'time' : '00:'+ i.group('time'),
          'chapterTitle': i.group('chapterTitle')}
      else:
        dict = {'time' : i.group('time'),
              'chapterTitle': i.group('chapterTitle')}
      l.append(dict)

    #Getting transcript
    trans_json = YouTubeTranscriptApi.get_transcript(video_id)
    print(trans_json[:5])

    #Splitting into dialouges
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

    #Dividing the transcript into summaries of chapters
    trans_list=[]
    paragraph = []
    tracker=0
    for index,elem in enumerate(l):
      print(aniso8601.parse_time(l[index]['time']))
      st = datetime.combine(date.min,aniso8601.parse_time(l[index]['time'])) - datetime.min
      if(index+1 < len(l)-1):
        en = datetime.combine(date.min,aniso8601.parse_time(l[index+1]['time'])) - datetime.min
      else:
        en = datetime.combine(date.min,aniso8601.parse_time('0' + duration)) - datetime.min
      trans_list=[]
      print(st.total_seconds())
      j=0
      print("index: ",index)
      print(en.total_seconds())
      for j in range(tracker,len(trans_json)):
        print("start: ",trans_json[j]['start'])
        print("endtime: ",trans_json[j]['start'] + trans_json[j]['duration'])
        tracker = tracker + 1 
        if trans_json[j]['start'] >= st.total_seconds():
          if trans_json[j]['start'] + trans_json[j]['duration'] > en.total_seconds() + 1:
            break
          else:
            txt = trans_json[j]['text']
            #Filtering if it is a closed caption
            print(txt)
            trans_list.append(txt) 
            print(st.total_seconds())
      print("tracker: ",tracker)
      paragraph.append(trans_list)

    summaries = [] #transcript without chapter titles

    #Initializing summarizer t5 transformer
    model = "t5-base"

    summarizer = pipeline("summarization",model=model)

    #chunking and summarizing
    chunk = []

    chunk.append("")
    cur_ch = 0
    for item in paragraph:
      for i in item:
        if ( len(chunk[cur_ch].split()) > 400):
          cur_ch = cur_ch + 1
          chunk.append("")
        else:
          chunk[cur_ch] = chunk[cur_ch] + " " + i
      summarized = summarizer(chunk,min_length = 5,max_length = 20,do_sample=False)
      s = ' '.join([summ['summary_text'] for summ in summarized])
      print(s)
      summaries.append(s)
      chunk = [""]
      cur_ch = 0

    #storing the summary
    summary=[]
    print("hello")
    for i,item in enumerate(summaries):
      print(l[i]['chapterTitle'])
      print(item)
      d = {'title':l[i]['chapterTitle'],'item' : item}
      summary.append(d)
    return summary