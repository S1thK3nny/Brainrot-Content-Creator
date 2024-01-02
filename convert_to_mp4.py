from moviepy.editor import ImageSequenceClip, ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip, CompositeAudioClip, VideoFileClip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.all import crop
from moviepy.audio.fx.all import audio_loop, volumex
import os
import random
from utils import sprint
from datetime import datetime


# YouTube Shorts are 1080x1920


def choose_random_file(dir):
    files = sorted(os.listdir(dir))
    return str(dir + random.choice([file for file in files]))

def post_to_clip(dir):
    # The post stuff will always be called post.mp3 and post.png, so let us simply turn it into an imageclip.
    audio_clip = AudioFileClip(dir + "/audio/post/post.mp3")
    img_clip = ImageClip(dir + "/images/post/post.png", duration=audio_clip.duration)
    img_clip = img_clip.set_audio(audio_clip)
    return img_clip, audio_clip.duration

def comments_to_clip(dir, post_clip_audio_duration):
    images_directory = dir + "/images/comments/"
    audio_directory = dir + "/audio/comments/"

    images = sorted(os.listdir(images_directory))
    audio_files = sorted(os.listdir(audio_directory))

    total_duration = post_clip_audio_duration
    clips = []

    for audio in audio_files:
        idx = int(audio.split('_')[0].replace('comment', ''))
        audio_clip = AudioFileClip(os.path.join(audio_directory, audio))
        img_clip = ImageSequenceClip([os.path.join(images_directory, images[idx])], durations=[audio_clip.duration])

        # Check if adding the current comment exceeds the maximum duration
        # TODO: Make sure it doesnt stop randomly somewhere in the image if it is too long.
        if total_duration + audio_clip.duration > 60:
            break

        img_clip = img_clip.set_audio(audio_clip)
        clips.append(img_clip)
        total_duration += audio_clip.duration

    return clips


def add_gameplay(final_clip_duration, list):
    # Choose random gameplay from the given resources
    rndfile = choose_random_file(os.getcwd() + "/resources/gameplay/")
    list.append(sprint(f"chosen gameplay is {rndfile}")) # Don't just print which gameplay file is chosen, but also save the print
    gameplay = VideoFileClip(rndfile)
    original_duration = gameplay.duration
    
    # Generate random start and end points
    max_start_time = original_duration - final_clip_duration
    start_time = random.uniform(0, max_start_time)
    end_time = start_time + final_clip_duration
    
    # Trim the original gameplay clip
    gameplay_clip = gameplay.subclip(start_time, end_time)
    gameplay_clip = gameplay_clip.without_audio()
    
    # Resize the clip to the desired height and crop the width
    gameplay_clip = resize(gameplay_clip, height=1920)
    if gameplay_clip.w >= 1080:
        gameplay_clip = crop(gameplay_clip, x_center=gameplay_clip.w/2, width=1080)  # Crop the width to 1080 from the center
    else:
        gameplay_clip = resize(gameplay_clip, (1080,1920))
    
    gameplay_clip = gameplay_clip.set_position(("center", "bottom"))  # Set the position to bottom
    return gameplay_clip

def add_bgmusic(final_clip_duration, list):
    # Choose random music from the given resources
    rndfile = choose_random_file(os.getcwd() + "/resources/music/")
    list.append(sprint(f"chosen music is {rndfile}")) # Don't just print which music file is chosen, but also save the print
    bgmusic = AudioFileClip(rndfile)

    # If the audio is longer than the video, trim it
    if bgmusic.duration > final_clip_duration:
        bgmusic = bgmusic.subclip(0, final_clip_duration)
    # If the video is longer than the audio, loop the audio
    else:
        bgmusic = audio_loop(bgmusic, duration=final_clip_duration)

    # Reduce the volume of the audio
    bgmusic = bgmusic.fx(volumex, 0.2)

    return bgmusic

def write_info_to_file(dir, list):
    # Write bgmusic and gameplay information to a text file
    sprint("Writing gameplay and bgmusic to info.txt!\n")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    info_filename = f"{dir}/info_{timestamp}.txt"
    with open(info_filename, 'w') as info_file:
        info_file.write(list[0] + '\n')
        info_file.write(list[1] + '\n')

def to_video(dir, open_file):
    print("\n--------------------------------------------------")
    sprint("Starting with the video conversion!\n")

    post_clips, post_clip_audio_duration = post_to_clip(dir)
    comment_clips = comments_to_clip(dir, post_clip_audio_duration)
    all_clips = [post_clips] + comment_clips

    final_clip = concatenate_videoclips(all_clips, method="compose")
    final_clip = resize(final_clip, width=1080)  # Maintain original aspect ratio while adjusting width
    
    background_clip = ColorClip(size=(1080, 1920), color=(255, 255, 255, 0), duration=final_clip.duration)  # Add alpha channel for transparency

    list = []

    # Merge gameplay and the transparent video clip with the reddit images we created
    final_clip = CompositeVideoClip([add_gameplay(final_clip.duration, list), background_clip.set_position(("center", "center")), final_clip.set_position(("center", "center"))], use_bgclip=True)

    # Add random background music
    final_clip.audio = CompositeAudioClip([final_clip.audio, add_bgmusic(final_clip.duration, list)])

    write_info_to_file(dir, list)

    sprint("Done with the conversion progress, saving to file now!\n--------------------------------------------------\n")
    final_clip.write_videofile(dir + "/result.mp4", codec='libx264', threads=16, fps=24, audio_codec='aac', logger=None, preset='ultrafast')
    
    if open_file:
        os.startfile(dir + "/result.mp4")