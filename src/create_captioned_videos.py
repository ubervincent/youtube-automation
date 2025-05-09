import os
import logging
import whisper
import subprocess
from datetime import timedelta, datetime
import glob
import atexit
from openai import OpenAI
import requests
from PIL import Image
import io
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
if not client.api_key:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

def cleanup_temp_files():
    """Clean up all temporary files created during processing."""
    try:
        # Patterns for temp files
        temp_patterns = [
            '*.srt',           # Subtitle files
            '*TEMP*',          # FFmpeg temp files
            '*.log',           # Log files
            '*.mbtree',        # x264 temp files
            '*.ffindex',       # FFmpeg index files
            '*.lwi',           # LAV Filters index files
            'ffmpeg*.txt',     # FFmpeg text files
            '*.part'           # Partial downloads/processing
        ]
        
        # Get current directory
        current_dir = os.getcwd()
        
        # Clean up each pattern
        for pattern in temp_patterns:
            for file_path in glob.glob(os.path.join(current_dir, pattern)):
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {file_path}: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# Register cleanup function to run on script exit
atexit.register(cleanup_temp_files)

def create_srt_from_segments(segments):
    """Create an SRT file from transcription segments."""
    try:
        print("📝 Creating SRT subtitle file...")
        # Generate a unique SRT filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        srt_path = f"temp_{timestamp}.srt"
        
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                # Convert start and end times to SRT format (HH:MM:SS,mmm)
                start = str(timedelta(seconds=int(segment["start"]))) + f",{int((segment['start'] % 1) * 1000):03d}"
                end = str(timedelta(seconds=int(segment["end"]))) + f",{int((segment['end'] % 1) * 1000):03d}"
                
                # Write SRT entry
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        
        print("✅ SRT file created successfully")
        return srt_path
    except Exception as e:
        print(f"❌ Error creating SRT file: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper."""
    print("🎤 Transcribing audio...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        print("✅ Audio transcription completed")
        return result["segments"]
    except Exception as e:
        print(f"❌ Error transcribing audio: {e}")
        return None

def generate_background_image(base_name=None):
    """Generate a background image using DALL-E 3.
    Args:
        base_name (str, optional): Base name for the image file. If not provided, uses timestamp.
    """
    try:
        print("🎨 Generating background image with DALL-E 3...")
        # Configure image generation parameters
        image_params = {
            "model": "dall-e-3",
            "n": 1,
            "size": "1792x1024",  # 16:9 widescreen aspect ratio
            "quality": "standard",
            "style": "natural",
            "prompt": (
               "A serene and ethereal portrait of Jesus Christ in a contemplative pose, "
                "inspired by classical Renaissance masters. The composition should be "
                "centered with soft, divine lighting illuminating the figure against a "
                "subtle, atmospheric background. The style should blend traditional "
                "religious iconography with contemporary artistic sensibilities. "
                "The color palette should be warm and inviting, with golden light "
                "and deep, rich shadows. The overall mood should be peaceful and spiritual."
            )
        }
        
        # Generate the image
        response = client.images.generate(**image_params)
        print("✅ Background image generated successfully")
        
        # Get the image URL from the response
        image_url = response.data[0].url
        
        # Create backgrounds directory if it doesn't exist
        os.makedirs("backgrounds", exist_ok=True)
        
        # Download and save the image
        print("📥 Downloading background image...")
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Use provided base_name or generate timestamp
            if base_name:
                image_path = f"backgrounds/{base_name}_background.png"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"backgrounds/background_{timestamp}.png"
                
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            print(f"✅ Background image saved to: {image_path}")
            return image_path
        else:
            print(f"❌ Failed to download image: {image_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating background image: {e}")
        return None

def create_video_with_subtitles(audio_file, output_path, use_generated_bg=True, base_name=None):
    """Create a video with subtitles using FFmpeg."""
    try:
        # Generate background image if enabled
        background_path = generate_background_image(base_name) if use_generated_bg else "assets/default_background.png"
        if not background_path:
            print("⚠️  Failed to generate background image, using default background")
            background_path = "assets/default_background.png"
            
        # Create SRT file from transcription
        segments = transcribe_audio(audio_file)
        if not segments:
            print("❌ Failed to transcribe audio")
            return False
            
        srt_path = create_srt_from_segments(segments)
        if not srt_path:
            print("❌ Failed to create SRT file")
            return False
            
        # Construct FFmpeg command
        print("🎬 Creating video with FFmpeg...")
        ffmpeg_cmd = (
            f'ffmpeg -y -loop 1 -i "{background_path}" -i "{audio_file}" '
            f'-vf "subtitles={srt_path}:force_style=\'FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,OutlineWidth=2,BorderStyle=4,BackColour=&H80000000,Alignment=2\'" '
            f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p '
            f'-shortest "{output_path}"'
        )
        
        # Run FFmpeg command
        result = subprocess.run(ffmpeg_cmd, shell=True, capture_output=True, text=True)
        
        # Clean up temporary files
        print("🧹 Cleaning up temporary files...")
        if os.path.exists(srt_path):
            os.remove(srt_path)
        if use_generated_bg and os.path.exists(background_path):
            os.remove(background_path)
            
        if result.returncode == 0:
            print(f"✅ Video created successfully: {output_path}")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return False

def main():
    """Main function to process all untreated audio files."""
    try:
        print("🎥 Starting video creation process...")
        
        # Create output directories
        os.makedirs("videos", exist_ok=True)
        
        # Get list of all audio files
        audio_files = glob.glob("processed_audio/*.mp3")
        
        # Get list of existing videos
        existing_videos = set(os.path.splitext(os.path.basename(v))[0] 
                            for v in glob.glob("videos/*.mp4"))
        
        # Filter for untreated files
        untreated_files = [
            audio_file for audio_file in audio_files
            if os.path.splitext(os.path.basename(audio_file))[0] not in existing_videos
        ]
        
        if not untreated_files:
            print("\n📝 No new audio files to process!")
            return
            
        print(f"\n🎯 Found {len(untreated_files)} files to process")
        
        # Process each untreated file
        for audio_file in untreated_files:
            try:
                print(f"\n📂 Processing: {os.path.basename(audio_file)}")
                output_path = os.path.join("videos", 
                                         os.path.basename(audio_file).replace(".mp3", ".mp4"))
                
                if create_video_with_subtitles(audio_file, output_path):
                    print(f"✅ Successfully created video: {os.path.basename(output_path)}")
                else:
                    print(f"❌ Failed to create video for: {os.path.basename(audio_file)}")
                    
            except Exception as e:
                print(f"❌ Error processing {os.path.basename(audio_file)}: {str(e)}")
                continue
        
        print("\n🎉 Video creation process completed!")
        
    except Exception as e:
        print(f"\n❌ Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 