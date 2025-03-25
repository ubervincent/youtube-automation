"""Audio processing utilities for sermon generation."""
import os
import shutil
import logging
import subprocess
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

def text_to_audio(text, output_path):
    """Convert text to audio using OpenAI's text-to-speech."""
    try:
        client = OpenAI()
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Split text into chunks of 4000 characters (leaving some buffer)
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        temp_files = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            temp_file = os.path.abspath(f"temp/chunk_{i}.mp3")
            temp_files.append(temp_file)
            
            # Create the speech file for this chunk
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="ash",  # Using a deep, authoritative voice
                speed=0.78,
                instructions="Speak in a slow and reverent tone, as if you are reading from a sacred text.",
                input=chunk
            )
            
            # Save the chunk
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            logger.info(f"Created audio chunk {i+1} of {len(chunks)}")
        
        # If we only have one chunk, just move it to the output path
        if len(temp_files) == 1:
            shutil.move(temp_files[0], output_path)
            return True
            
        # Combine all chunks using FFmpeg
        concat_file = os.path.abspath("temp/concat.txt")
        with open(concat_file, 'w') as f:
            for temp_file in temp_files:
                f.write(f"file '{temp_file}'\n")
        
        # FFmpeg command to concatenate files
        ffmpeg_cmd = (
            f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" '
            f'-c copy "{output_path}"'
        )
        
        result = subprocess.run(ffmpeg_cmd, shell=True, capture_output=True, text=True)
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(concat_file):
            os.remove(concat_file)
        
        if result.returncode == 0:
            logger.info(f"Audio file created successfully: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating audio file: {str(e)}")
        return False

def mix_audio(voice_path, output_path, background_music=None):
    """Mix voice audio with background music."""
    try:
        # Use provided background music or default
        if not background_music:
            background_music = "assets/music/ambient_worship.mp3"
        
        if not os.path.exists(background_music):
            logger.warning("Background music file not found. Using voice track only.")
            shutil.copy2(voice_path, output_path)
            return True
        
        # Simple mix command with volume adjustment and audio normalization
        ffmpeg_cmd = (
            f'ffmpeg -y '
            f'-i "{voice_path}" '
            f'-i "{background_music}" '
            f'-filter_complex "'
            f'[0:a]volume=1.0[voice];'
            f'[1:a]volume=0.1[music];'
            f'[voice][music]amix=inputs=2:duration=first:normalize=0[aout]" '
            f'-map "[aout]" '
            f'-ar 44100 '
            f'-ab 192k '
            f'"{output_path}"'
        )
        
        result = subprocess.run(ffmpeg_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Audio mixing completed successfully")
            return True
        else:
            logger.error(f"FFmpeg error during mixing: {result.stderr}")
            # If mixing fails, use voice track only
            logger.warning("Falling back to voice track only")
            shutil.copy2(voice_path, output_path)
            return True
            
    except Exception as e:
        logger.error(f"Error mixing audio: {str(e)}")
        # If any error occurs, use voice track only
        shutil.copy2(voice_path, output_path)
        return True 