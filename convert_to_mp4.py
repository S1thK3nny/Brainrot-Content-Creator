from moviepy.editor import ImageSequenceClip, ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip
from moviepy.video.fx.resize import resize
import os

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

def to_video(dir):
    post_clips = post_to_clip(dir)
    comment_clips = comments_to_clip(dir)
    all_clips = [post_clips] + comment_clips

    final_clip = concatenate_videoclips(all_clips, method="compose")
    final_clip = resize(final_clip, (1080,960))
    
    background_clip = ColorClip(size=(1080,1920), color=(255,255,255), duration=final_clip.duration)
    
    # Pass the clips as a list to CompositeVideoClip
    final_clip = CompositeVideoClip([background_clip, final_clip])

    final_clip.write_videofile(dir + "/result.mp4", codec='h264', fps=24)
