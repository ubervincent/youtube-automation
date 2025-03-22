import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import subprocess
import sys

# Load environment variables
load_dotenv()

class BibleTTS:
    def __init__(self):
        # Initialize OpenAI client with API key from environment variables
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def text_to_speech(self, text, output_file, voice="ash"):
        """
        Convert text to speech using OpenAI's TTS API
        Available voices: alloy, echo, fable, onyx, nova, shimmer
        """
        try:
            # Create speech from text
            response = self.client.audio.speech.create(
                model="gpt-4o-mini-tts", 
                voice=voice,
                speed=0.75,
                instructions="Speak in a slow and reverent tone, as if you are reading from a sacred text.",
                input=text
            )
            
            # Save to file
            response.stream_to_file(output_file)
            return True
            
        except Exception as e:
            print(f"Error creating audio: {str(e)}")
            return False

    def combine_audio_parts(self, audio_parts, final_output):
        """
        Combine multiple audio parts into a single file using ffmpeg
        """
        try:
            # Create a text file listing all audio parts
            list_file = "temp_file_list.txt"
            with open(list_file, "w") as f:
                for part in sorted(audio_parts):
                    f.write(f"file '{part}'\n")
            
            # Use ffmpeg to concatenate the files
            cmd = [
                "ffmpeg", "-y",  # -y to overwrite output file if it exists
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",  # Copy audio streams without re-encoding
                final_output
            ]
            
            # Run ffmpeg command
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Clean up
            os.remove(list_file)
            for part in audio_parts:
                os.remove(part)
                
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error running ffmpeg: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Error combining audio parts: {str(e)}")
            return False

    def process_text_file(self, text_file_path, output_dir):
        """
        Process a single text file and convert it to audio
        Splits the text into smaller chunks to handle API limitations
        """
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            with open(text_file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except FileNotFoundError:
            print(f"Error: File '{text_file_path}' not found.")
            return False
        
        # Get the base filename without extension
        base_name = Path(text_file_path).stem
        final_output = os.path.join(output_dir, f"{base_name}.mp3")
        
        # Split text into chunks (approximately 4000 characters each)
        chunk_size = 4000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # If there's only one chunk, create a single audio file
        if len(chunks) == 1:
            return self.text_to_speech(chunks[0], final_output)
        
        # If multiple chunks, create temporary part files
        temp_files = []
        success = True
        
        try:
            # Process each chunk
            for i, chunk in tqdm(enumerate(chunks), total=len(chunks), desc=f"Converting {base_name}"):
                temp_file = os.path.join(output_dir, f"_temp_{base_name}_part_{i+1}.mp3")
                temp_files.append(temp_file)
                if not self.text_to_speech(chunk, temp_file):
                    success = False
                    break
            
            # If all chunks were processed successfully, combine them
            if success and temp_files:
                print(f"Combining audio parts for {base_name}...")
                if not self.combine_audio_parts(temp_files, final_output):
                    success = False
            
            # Clean up temp files if they still exist
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
        except Exception as e:
            print(f"Error processing {text_file_path}: {str(e)}")
            success = False
            # Clean up temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        return success

    def process_directory(self, input_dir, output_dir):
        """
        Scan directory for text files and process only new or modified ones
        """
        # Get all text files in input directory
        text_files = []
        for ext in ['.txt']:
            text_files.extend(Path(input_dir).glob(f'*{ext}'))
        
        if not text_files:
            print(f"No text files found in {input_dir}")
            return
        
        # Process each text file
        for text_file in text_files:
            # Check if audio file already exists and is newer than text file
            base_name = text_file.stem
            audio_file = Path(output_dir) / f"{base_name}.mp3"
            
            # Skip if audio file exists and is newer than text file
            if audio_file.exists() and audio_file.stat().st_mtime > text_file.stat().st_mtime:
                print(f"Skipping {text_file.name} - audio is up to date")
                continue
            
            print(f"Processing {text_file.name}...")
            self.process_text_file(str(text_file), output_dir)

def main():
    input_directory = "data"
    output_directory = "audio"
    
    # Initialize and run the converter
    converter = BibleTTS()
    converter.process_directory(input_directory, output_directory)

if __name__ == "__main__":
    main() 