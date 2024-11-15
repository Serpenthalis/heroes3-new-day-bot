import tweepy
import datetime
import os
import random
import glob
import natsort
import creature_lists

from PIL import Image
from pathlib import Path
from moviepy.editor import *
from http.client import HTTPException

# Twitter Init
api_key = 
api_key_secret = 
access_token = 
access_token_secret = 
bearer_token = 
client_id = 
client_secret = 

auth = tweepy.OAuth1UserHandler(consumer_key=api_key,
                                consumer_secret=api_key_secret,
                                access_token=access_token,
                                access_token_secret=access_token_secret)
client = tweepy.Client(consumer_key=api_key,
                       consumer_secret=api_key_secret,
                       access_token=access_token,
                       access_token_secret=access_token_secret)
api = tweepy.API(auth)


# Init some vars
frame_count = 0
temp_rel_path = Path("/temp")
temp_frame_rel_path = Path(str(temp_rel_path) + "/result_")
clips = []
temp_files = glob.glob(os.getcwd() + str(temp_frame_rel_path) + "*.png")
normal_week = creature_lists.normal_week
normal_month = creature_lists.normal_month
special_week = creature_lists.special_week
special_month = creature_lists.special_month


# Get current date
today = datetime.datetime.today()
day_in_week = today.weekday() + 1
day_in_month = today.day


# Get picture frame of random color
picture_frame = Path(random.choice(glob.glob(os.getcwd() + "/Images/frames/frame_*.png")))


# Get assets based on current date
text = Path(os.getcwd() + "/Images/words/day_" + str(day_in_week) + ".png")
audio = Path(os.getcwd() + "/Sounds/NewDay_less_noise.wav")
bgs = glob.glob(os.getcwd() + "/Images/new_day/new_day_*.png")
message = ""

if day_in_week == 1:
    audio = Path(os.getcwd() + "/Sounds/NewWeek_less_noise.wav")
    bgs = glob.glob(os.getcwd() + "/Images/new_week/new_week_*.png")
    week_roll = random.randrange(0, 100, 1)
    if week_roll <= 25: # Special week
        monster_of_the_week = random.choice(special_week)
        population_increase = 5
        if monster_of_the_week == "Imp and Familiar":
            population_increase = 15
        message = "Astrologers proclaim week of the " + str(monster_of_the_week) + ".\n\n" + str(monster_of_the_week) + " growth +" + str(population_increase) + ".\n\nAll dwellings increase population."
    else: # Normal week
        message = "Astrologers proclaim week of the " + str(random.choice(normal_week)) + ".\n\nAll dwellings increase population."

if day_in_month == 1:
    audio = Path(os.getcwd() + "/Sounds/NEWMONTH_less_noise.wav")
    month_roll = random.randrange(0, 100, 1)
    if month_roll >= 50: # Normal month
        message = "Astrologers proclaim month of the " + str(random.choice(normal_month)) + ".\n\nAll dwellings increase population."
    elif month_roll <= 10: # Plague month
        message = "Astrologers proclaim month of the PLAGUE!\n\nAll populations are halved."
    else: # Special month
        monster_of_the_month = random.choice(special_month)
        message = "Astrologers proclaim month of the " + str(monster_of_the_month) + ".\n\n" + str(monster_of_the_month) + " population doubles!\n\nAll dwellings increase population."


# Create audio clip from file
audio_clip = AudioFileClip(str(audio))
audio_clip = audio_clip.set_duration(audio_clip.duration - 0.1) # This fixes an audio bug (blip at the very end)


# Remove leftover temp files from last time
for file in temp_files:
    os.remove(file)


# Create frames for the video
for bg in bgs:
    image1 = Image.open(fp=bg, mode="r", formats=["PNG"])
    image2 = Image.open(fp=picture_frame, mode="r", formats=["PNG"])
    image3 = Image.open(fp=text, mode="r", formats=["PNG"])

    # Stack the images on top of each other
    result = Image.alpha_composite(im1=image1, im2=image2)
    result = Image.alpha_composite(im1=result, im2=image3)

    result.save(fp=Path(os.getcwd() + str(temp_frame_rel_path) + str(frame_count) + ".png"), format="PNG")
    frame_count += 1


# Get and sort frames from files
temp_frames = glob.glob(os.getcwd() + str(temp_frame_rel_path) + "*.png")
temp_frames = natsort.natsorted(temp_frames)


# Create image clips
for i, temp_frame in enumerate(temp_frames):
    clip_duration = 0.13
    if i == len(temp_frames) - 1:
        # Calculate length of last frame
        clip_duration = max(audio_clip.duration - len(clips) * clip_duration, clip_duration)
    clips.append(ImageClip(temp_frame, ismask=False, duration=clip_duration))


# Create video clip from image clips and audio clip
video_clip = concatenate_videoclips(clips, method="compose")
video_clip = video_clip.set_audio(audio_clip)
video_clip.write_videofile("video-output.avi", fps=20, codec="png", audio_codec="aac")


# Upload media (Twitter API v1, OAuth 1)
media = api.media_upload("video-output.avi", media_category="amplify_video")


# Send Tweet (Twitter API v1, OAuth 1)
response = client.create_tweet(text=message, media_ids=[media.media_id])