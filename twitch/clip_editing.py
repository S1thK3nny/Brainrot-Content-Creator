import moviepy.editor as mp
import whisper_timestamped
from moviepy.video.fx.resize import resize
from moviepy.video.fx.all import crop
from reddit.convert_to_mp4 import add_gameplay, add_bgmusic
from utils import sprint
import winsound
import os

def generate_subtitles(dir, language: str):
    generated_audio = dir + '/final_audio.wav'
    existing_clip = dir + '/clip.mp4'

    # Load the model and decoding options
    model = whisper_timestamped.load_model('base')
    whisper_timestamped.DecodingOptions(language=language, fp16='false')

    # Specify the video file
    video = mp.VideoFileClip(existing_clip)

    # Extract audio from the video
    video.audio.write_audiofile(generated_audio)
    result = whisper_timestamped.transcribe(model, generated_audio)

    # Generate and add subtitles
    subtitles = []
    for segment in result["segments"]:
        for word in segment["words"]:
            text = word["text"]
            start = word["start"]
            end = word["end"]
            duration = end - start
            text_clip = mp.TextClip(txt=text, fontsize=160, font="Arial-Bold", stroke_width=4, stroke_color="black", color='white')
            text_clip = text_clip.set_start(start).set_duration(duration).set_pos(("center", "bottom"))
            subtitles.append(text_clip)

    # Overlay the subtitles on the video
    final_video = mp.CompositeVideoClip([video] + subtitles)

    # Part 1 fix for when CompositeVideoClip somehow screws up the duration. Why? I don't know. How? I don't know.
    final_video.duration = video.duration

    final_video = resize(final_video, height=960)
    if final_video.w >= 1080:
        final_video = crop(final_video, x_center=final_video.w/2, width=1080)  # Crop the width to 1080 from the center
    else:
        final_video = resize(final_video, (1080,960))
    
    final_video = final_video.set_position(("center", "bottom"))  # Set the position to bottom

    return final_video, generated_audio, existing_clip

# TODO: Fix bug that lets you not remove existing_clip.
def initialize_editing(dir, open_when_done, language):
    list = []
    clip, generated_audio, existing_clip = generate_subtitles(dir, language)
    gameplay = add_gameplay(clip.duration, list, 960)
    bgmusic = add_bgmusic(clip.duration, list)
    final_video = mp.ColorClip(size=(1080, 1920), color=(255, 255, 255, 0), duration=clip.duration)  # Add alpha channel for transparency
    final_video = resize(final_video, (1080, 1920))

    try:
        final_video = mp.CompositeVideoClip([final_video, gameplay.set_position(("center", "bottom")), clip.set_position(("center", "top"))], use_bgclip=True)  # Merge gameplay and the transparent video clip with the reddit images we created
        final_video.audio = mp.CompositeAudioClip([final_video.audio, bgmusic])

        # Part 2 fix for when CompositeVideoClip somehow screws up the duration. Why? I don't know. How? I don't know.
        final_video.duration = clip.duration

        final_video.write_videofile(dir + "/result.mp4", codec='libx264', threads=16, fps=24, audio_codec='aac', remove_temp=True)
        winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

        if open_when_done:
            if os.path.isfile(dir + "/result.mp4"):
                os.startfile(dir + "/result.mp4")
    finally:
        # Close the video clip objects to release resources
        clip.close()
        final_video.close()

    if os.path.isfile(generated_audio):
        os.remove(generated_audio)

    if os.path.isfile(existing_clip):
        os.remove(existing_clip)