from moviepy.editor import ImageSequenceClip, ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip, VideoFileClip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.all import crop
import os
import random

# YouTube Shorts are 1080x1920

def post_to_clip(dir):
    audio_clip = AudioFileClip(dir + "/audio/post/post.mp3")
    img_clip = ImageClip(dir + "/images/post/post.png", duration=audio_clip.duration)
    img_clip = img_clip.set_audio(audio_clip)
    return img_clip

def comments_to_clip(dir):
    images_directory = dir + "/images/comments/"
    audio_directory = dir + "/audio/comments/"

    images = sorted(os.listdir(images_directory))
    audio_files = sorted(os.listdir(audio_directory))

    clips = []
    for audio in audio_files:
        idx = int(audio.split('_')[0].replace('comment', ''))
        audio_clip = AudioFileClip(os.path.join(audio_directory, audio))
        img_clip = ImageSequenceClip([os.path.join(images_directory, images[idx])], durations=[audio_clip.duration])
        img_clip = img_clip.set_audio(audio_clip)
        clips.append(img_clip)
    return clips

def add_gameplay(final_clip_duration):
    dir = os.getcwd() + "/resources/gameplay/"
    videos = sorted(os.listdir(dir))
    gameplay = VideoFileClip(str(dir + random.choice([video for video in videos])))
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
    gameplay_clip = crop(gameplay_clip, x_center=gameplay_clip.w/2, width=1080)  # Crop the width to 1080 from the center
    
    gameplay_clip = gameplay_clip.set_position(("center", "bottom"))  # Set the position to bottom
    return gameplay_clip


def to_video(dir):
    post_clips = post_to_clip(dir)
    comment_clips = comments_to_clip(dir)
    all_clips = [post_clips] + comment_clips

    final_clip = concatenate_videoclips(all_clips, method="compose")
    final_clip = resize(final_clip, width=1080)  # Maintain original aspect ratio while adjusting width
    
    background_clip = ColorClip(size=(1080, 1920), color=(255, 255, 255, 0), duration=final_clip.duration)  # Add alpha channel for transparency
    
    # Position the final_clip at the bottom half
    final_clip = CompositeVideoClip([background_clip.set_position(("center", "bottom")), final_clip], use_bgclip=True)

    final_clip = CompositeVideoClip([add_gameplay(final_clip.duration), final_clip], use_bgclip=True)
    final_clip.write_videofile(dir + "/result.mp4", codec='libx264', fps=24, audio_codec='aac')