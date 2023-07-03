from django.shortcuts import render
import pytube as pyt
from youtubesearchpython import *
from pydub import AudioSegment
import os
import shutil
from django.core.mail import EmailMessage

def send_audio_file_email(to, subject, audio_file_path):
    email = EmailMessage(
        subject,
        'Audio file attached',
        to=to
    )
    with open(audio_file_path, 'rb') as f:
        email.attach('audio.mp3', f.read(), 'audio/mp3')
    email.send()

def get_urls(singer, count):
    count=int(count)
    search = CustomSearch(singer + "songs", VideoSortOrder.viewCount, limit=count)
    urls = []
    while (len(urls) < count):
        for i in search.result()['result']:
            urls.append(i['link'])
            if (len(urls) >= count):
                break
        search.next()
    return urls

def download_video(urls):
    for u in urls:
        youtube = pyt.YouTube(u , use_oauth=True, allow_oauth_cache=True)
        video = youtube.streams.get_lowest_resolution()
        video.download(r'videos')

def convert_to_audio(video_folder, audio_folder):
    for filename in os.listdir(video_folder):
        if filename.endswith(".mp4"):
            video_path = os.path.join(video_folder, filename)
            audio = AudioSegment.from_file(video_path, format="mp4")
            audio_filename = os.path.splitext(filename)[0] + ".wav"
            audio_path = os.path.join(audio_folder, audio_filename)
            audio.export(audio_path, format="wav")

def cut_audio(audio_folder, cut_audio_folder, time):
    time=int(time)
    for filename in os.listdir(audio_folder):
        if filename.endswith(".wav"):
            audio_path = os.path.join(audio_folder, filename)
            audio = AudioSegment.from_file(audio_path, format="wav")
            cut_audio = audio[0:time*1000]
            cut_audio_path = os.path.join(cut_audio_folder, "cut_" + filename)
            cut_audio.export(cut_audio_path, format="wav")

def merge_audio_files(audio_folder, merged_audio_folder, output_file):
    merged_audio = AudioSegment.silent(duration=0)
    for filename in os.listdir(audio_folder):
        if filename.endswith(".wav"):
            audio_path = os.path.join(audio_folder, filename)
            audio = AudioSegment.from_file(audio_path, format="mp3")
            merged_audio = merged_audio + audio
    os.makedirs(merged_audio_folder, exist_ok=True)
    merged_audio_path = os.path.join(merged_audio_folder, output_file + ".mp3")
    merged_audio.export(merged_audio_path, format="mp3")









# Create your views here.
def index(request):
    print("Homepage")
    if(request.method=="POST"):

        # GET DATA FROM FORM
        singerName=request.POST['singerName']
        numberOfVideos=request.POST['numberOfVideos']
        duration=request.POST['duration']
        email = request.POST['email']
        # print(singerName,numberOfVideos,duration,email)
        singerName=str(singerName)
        numberOfVideos=str(numberOfVideos)
        duration=str(duration)

        if not os.path.exists('videos'):
            os.mkdir('videos')
        if not os.path.exists('audios'):
            os.mkdir('audios')
        if not os.path.exists('cut_audios'):
            os.mkdir('cut_audios')

        urls = get_urls(singerName, numberOfVideos)
        download_video(urls)
        convert_to_audio("videos", "audios")
        cut_audio("audios", "cut_audios", duration)
        merge_audio_files("cut_audios", "merged_output", "output")
        print(os.getcwd())
        
        shutil.rmtree('videos')
        shutil.rmtree('audios')
        shutil.rmtree('cut_audios')

        audio_file_path="merged_output/output.mp3"
        subject="Congratulations Mashup Of your songs is ready!!"
        email=[email]
        send_audio_file_email(email, subject, audio_file_path)
        shutil.rmtree('merged_output')

    return render(request,'index.html')