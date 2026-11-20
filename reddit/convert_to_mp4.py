from moviepy.editor import ImageSequenceClip, ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips, ColorClip, CompositeVideoClip, CompositeAudioClip, VideoFileClip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.all import crop
from moviepy.audio.fx.all import audio_loop, volumex
import os
import random
import winsound
from utils import sprint, choose_random_file, write_to_info_file


# YouTube Shorts are 1080x1920


def post_to_clip(out_dir):
    # The post stuff will always be called post.mp3 and post.png, so let us simply turn it into an imageclip.
    audio_clip = AudioFileClip(out_dir + "/audio/post/post.mp3")
    img_clip = ImageClip(out_dir + "/images/post/post.png", duration=audio_clip.duration)
    img_clip = img_clip.set_audio(audio_clip)

    return img_clip, audio_clip.duration

def comments_to_clip(out_dir, post_clip_audio_duration):
    images_directory = os.path.join(out_dir, "images/comments/")
    audio_directory = os.path.join(out_dir, "audio/comments/")

    images = sorted(os.listdir(images_directory))
    audio_files = sorted(os.listdir(audio_directory))

    total_duration = post_clip_audio_duration
    clips = []

    for image in images:
        image_id = int(image.split('-')[1].split('.')[0])

        audio_clips_for_image = [audio for audio in audio_files if audio.startswith(f"comment-{image_id}_")]

        if not audio_clips_for_image:
            sprint(f"Image: {image}, Image ID: {image_id}")
            sprint(f"No audio clips found for image {image}. Skipping.")
            continue

        combined_audio = concatenate_audioclips([AudioFileClip(os.path.join(audio_directory, audio)) for audio in audio_clips_for_image])

        # Check if this comment/image and its audio will make our short longer than a minute
        if total_duration + combined_audio.duration >= 60:
            sprint(f"Skipping Image {image} due to length...")
            continue

        img_clip = ImageSequenceClip([os.path.join(images_directory, image)], durations=[combined_audio.duration])
        img_clip = img_clip.set_audio(combined_audio)

        clips.append(img_clip)
        total_duration += combined_audio.duration

    return clips

def add_gameplay(final_clip_duration, info_lines, height):
    # Choose random gameplay from the given resources
    rndfile = choose_random_file(os.getcwd() + "/resources/gameplay/")
    info_lines.append(sprint(f"chosen gameplay is {rndfile}")) # Don't just print which gameplay file is chosen, but also save the print
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
    gameplay_clip = resize(gameplay_clip, height=height)
    if gameplay_clip.w >= 1080:
        gameplay_clip = crop(gameplay_clip, x_center=gameplay_clip.w/2, width=1080)  # Crop the width to 1080 from the center
    else:
        gameplay_clip = resize(gameplay_clip, (1080,height))
    
    gameplay_clip = gameplay_clip.set_position(("center", "bottom"))  # Set the position to bottom

    return gameplay_clip

def add_bgmusic(final_clip_duration, info_lines):
    # Choose random music from the given resources
    rndfile = choose_random_file(os.getcwd() + "/resources/music/")
    info_lines.append(sprint(f"chosen music is {rndfile}")) # Don't just print which music file is chosen, but also save the print
    bgmusic = AudioFileClip(rndfile)

    # If the audio is longer than the video, trim it
    if bgmusic.duration > final_clip_duration:
        bgmusic = bgmusic.subclip(0, final_clip_duration)
    # If the video is longer than the audio, loop the audio
    else:
        bgmusic = audio_loop(bgmusic, duration=final_clip_duration)

    # Reduce the volume of the audio
    bgmusic = bgmusic.fx(volumex, 0.1)

    return bgmusic

def to_video(out_dir):
    print("\n--------------------------------------------------")
    sprint("Starting with the video conversion!\n")

    post_clips, post_clip_audio_duration = post_to_clip(out_dir)
    comment_clips = comments_to_clip(out_dir, post_clip_audio_duration)
    all_clips = [post_clips] + comment_clips

    final_clip = concatenate_videoclips(all_clips, method="compose")
    # NOTE : Width is 1060 instead of 1080 to leave just a little space at the sides
    final_clip = resize(final_clip, width=1060)  # Maintain original aspect ratio while adjusting width
    
    background_clip = ColorClip(size=(1080, 1920), color=(255, 255, 255, 0), duration=final_clip.duration)  # Add alpha channel for transparency

    info_lines = []

    gameplay = add_gameplay(final_clip.duration, info_lines, 1920)
    music = add_bgmusic(final_clip.duration, info_lines)

    final_clip = CompositeVideoClip([gameplay, background_clip.set_position(("center", "center")), final_clip.set_position(("center", "top"))], use_bgclip=True) # Merge gameplay and the transparent video clip with the reddit images we created
    final_clip.audio = CompositeAudioClip([final_clip.audio, music])

    sprint("Writing gameplay and bgmusic to info.txt!\n")
    write_to_info_file(out_dir, info_lines[0])
    write_to_info_file(out_dir, info_lines[1])

    sprint("Done with the conversion progress, saving to file now!\n--------------------------------------------------\n")
    final_clip.write_videofile(out_dir + "/result.mp4", codec='libx264', threads=16, fps=24, audio_codec='aac', logger=None, remove_temp=True)
    winsound.PlaySound("SystemExit", winsound.SND_ALIAS)