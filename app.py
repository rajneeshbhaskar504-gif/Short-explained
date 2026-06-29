import streamlit as st
import os
import whisper
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip
from transformers import pipeline

# Safe initialization
st.set_page_config(
    page_title="AI Movie Explainer", 
    page_icon="🎬", 
    layout="centered"
)

st.title("🎬 AI Movie Explainer 90-Sec Pro")
st.write("Ab aap 500 MB tak ki badi video clip se automatic 90-second ka viral short banayein!")

# Models Loader
@st.cache_resource
def load_models():
    whisper_model = whisper.load_model("tiny", device="cpu")
    script_pipe = pipeline("text-generation", model="Qwen/Qwen1.5-0.5B-Chat", device="cpu")
    return whisper_model, script_pipe

whisper_model, script_pipe = load_models()

# Video Uploader
uploaded_file = st.file_uploader("SABSE PEHLE MOVIE CLIP UPLOAD KAREIN 👇", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    st.video("input_video.mp4")
    
    if st.button("Generate Viral Short Video 🚀"):
        with st.status("💥 Processing Shuru Ho Gayi Hai (Do Not Close)...", expanded=True) as status:
            try:
                # Step 1: Audio/Text Extraction
                status.write("🎵 Video se audio alag karke transcript nikal raha hoon...")
                video = VideoFileClip("input_video.mp4")
                video.audio.write_audiofile("temp_audio.mp3", bitrate="64k", logger=None)
                
                result = whisper_model.transcribe("temp_audio.mp3", language="hi")
                transcript = result["text"]
                
                # Step 2: Script Generation
                status.write("🤖 AI ab viral Hindi script taiyar kar raha hai...")
                prompt = f"<|im_start|>system\nAap ek Facebook Reels aur YouTube Shorts creator hain. Niche di gayi movie transcript se ek lamba, suspenseful aur viral Hindi voiceover script likhein jo lagbhag 80 se 90 seconds tak chale.<|im_end|>\n<|im_start|>user\nTranscript: {transcript}<|im_end|>\n<|im_start|>assistant\n"
                outputs = script_pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)
                hindi_script = outputs[0]["generated_text"].split("<|im_start|>assistant\n")[-1]
                
                # Step 3: Voiceover
                status.write("🗣️ Voiceover file ban rahi hai...")
                tts = gTTS(text=hindi_script, lang='hi', slow=False)
                tts.save("ai_voiceover.mp3")
                
                # Step 4: Final Edit with Copyright Shield
                status.write("🎬 Video cut ho raha hai aur Copyright Shield apply ho raha hai...")
                audio_clip = AudioFileClip("ai_voiceover.mp3")
                duration = min(90, audio_clip.duration, video.duration)
                
                short_clip = video.subclip(0, duration)
                w, h = short_clip.size
                target_w = int(h * 9 / 16)
                x_center = w / 2
                
                # Crop + Zoom 5% + Mirror (Anti-Copyright)
                crop_clip = short_clip.crop(x_center=x_center, width=target_w, height=h)
                final_clip = crop_clip.fx(lambda c: c.resize(1.05)).fx(lambda c: c.mirrorx())
                final_clip = final_clip.set_audio(audio_clip.set_duration(duration))
                
                output_path = "viral_short_output.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None, threads=2)
                
                status.update(label="🎯 Video Taiyar Hai!", state="complete", expanded=False)
                
                # Output Show Karein
                st.success("🎉 Aapka Video Successfully Ban Gaya!")
                st.video(output_path)
                
            except Exception as e:
                status.update(label=f"❌ Error Aaya: {e}", state="error")


