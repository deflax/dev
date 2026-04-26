import os
from moviepy.editor import *
import youtube_dl

H = 720
W = 1280
SIZE = (W, H)
FPS = 24
VCODEC = 'libx264'
ACODEC = 'aac'
bold_font = 'Liberation-Sans-Bold'
plain_font = 'Liberation-Sans'

img_dir = "imgtest"

slideshow = []
for file in os.listdir(img_dir):
    if file.endswith(".jpg"):
        fullpath = os.path.join(img_dir, file)
        slideshow.append(fullpath)

startime = 0
clips = []

yt_url = input("please enter youtube video url:")
yt_info = youtube_dl.YoutubeDL().extract_info(
        url = yt_url,download=False
    )
#yt_filename = f"{yt_info['title']}.mp3"
yt_filename = f"tmpaudio.mp3"

yt_options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':yt_filename,
    }

with youtube_dl.YoutubeDL(yt_options) as ydl:
        ydl.download([yt_info['webpage_url']])

print("Download complete... {}".format(yt_filename))

audio_clip = AudioFileClip(yt_filename)
print('audio duration: ' + str(audio_clip.duration))
print('images found: ' + str(len(slideshow)))
step = int(audio_clip.duration) / int(len(slideshow))
print('calculated step: ' + str(step))

# Creating a list of ImageClip instances
for item in slideshow:
    duration = startime + step
    image = ImageClip(str(item)).set_duration(duration).set_start(startime).resize(height=H, width=W)
    text = TextClip("start: " + str(startime) + " duration: " + str(duration), font=bold_font, color='white', fontsize=48, interline=9).set_duration(duration - 2).set_start(startime + 1).set_pos(('left', 60)).crossfadein(.3)
    subtext = TextClip("File: " + str(item), font=plain_font, color='white', fontsize=32, interline=9).set_duration(duration - 4).set_start(startime + 2).set_pos(('left', 100)).crossfadein(.3)
    slide = CompositeVideoClip([image, text, subtext]).set_duration(duration)
    clips.append(slide)
    # increment next starttime with the step
    startime = startime + step

video_clip = CompositeVideoClip(clips, size=SIZE)
video_clip.set_duration(audio_clip.duration)
video_clip.write_videofile("tmpvideo.mp4", fps=FPS, codec=VCODEC)

print ('Muxing audio and video...')
final_audio = AudioFileClip('tmpaudio.mp3')
final_video = VideoFileClip('tmpvideo.mp4')
final_video = final_video.set_audio(final_audio.set_duration(final_audio.duration))
final_video.write_videofile('output.mp4', fps=FPS)

# Cleanup
os.unlink('tmpvideo.mp4')
os.unlink('tmpaudio.mp3')
print('Done.')
