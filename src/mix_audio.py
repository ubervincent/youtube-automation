from pydub import AudioSegment
import os
import time

def mix_sermon_with_ambience(sermon_path, ambience_path, output_path, sermon_volume=0, ambience_volume=-10):
    """
    Mix a sermon audio with background ambience.
    
    Args:
        sermon_path (str): Path to the sermon audio file
        ambience_path (str): Path to the ambience audio file
        output_path (str): Path where the mixed audio will be saved
        sermon_volume (int): Volume adjustment for sermon in dB (0 means no change)
        ambience_volume (int): Volume adjustment for ambience in dB (negative means reduce volume)
    """
    try:
        # Load the audio files
        print(f"Loading sermon audio from {sermon_path}...")
        sermon = AudioSegment.from_mp3(sermon_path)
        
        print(f"Loading ambience audio from {ambience_path}...")
        ambience = AudioSegment.from_mp3(ambience_path)
        
        # Adjust volumes
        print("Adjusting volumes...")
        sermon = sermon + sermon_volume
        ambience = ambience + ambience_volume
        
        # Loop ambience if it's shorter than sermon
        if len(ambience) < len(sermon):
            print("Extending ambience to match sermon length...")
            times_to_loop = (len(sermon) // len(ambience)) + 1
            ambience = ambience * times_to_loop
        
        # Trim ambience to match sermon length
        ambience = ambience[:len(sermon)]
        
        # Overlay the tracks
        print("Mixing audio...")
        mixed = sermon.overlay(ambience)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export the result
        print(f"Exporting mixed audio to {output_path}...")
        mixed.export(output_path, format="mp3")
        
        # Verify the file was created
        if os.path.exists(output_path):
            print(f"Successfully created mixed audio: {output_path}")
            return True
        else:
            print(f"Failed to create mixed audio: {output_path}")
            return False
            
    except Exception as e:
        print(f"Error mixing audio: {str(e)}")
        return False

def is_already_mixed(filename):
    """Check if a file has already been mixed with ambience."""
    return "_with_ambience" in filename or "mixed" in filename.lower()

def process_all_sermons(audio_dir, ambience_file, output_dir):
    """
    Process all MP3 files in the audio directory that haven't been mixed yet.
    
    Args:
        audio_dir (str): Directory containing sermon audio files
        ambience_file (str): Path to the ambience audio file
        output_dir (str): Directory where mixed files will be saved
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Verify ambience file exists
        if not os.path.exists(ambience_file):
            raise FileNotFoundError(f"Ambience file not found: {ambience_file}")
        
        # Get all MP3 files in the audio directory that haven't been mixed
        sermon_files = [f for f in os.listdir(audio_dir) 
                       if f.endswith('.mp3') and not is_already_mixed(f)]
        
        if not sermon_files:
            print("No new sermons to process - all files have already been mixed")
            return True
        
        print(f"Found {len(sermon_files)} unmixed sermon files to process")
        
        success = True
        # Process each unmixed sermon file
        for sermon_file in sermon_files:
            sermon_path = os.path.join(audio_dir, sermon_file)
            output_path = os.path.join(output_dir, f"{os.path.splitext(sermon_file)[0]}_with_ambience.mp3")
            
            # Check if output already exists
            if os.path.exists(output_path):
                print(f"Skipping {sermon_file} - mixed version already exists")
                continue
                
            print(f"\nProcessing: {sermon_file}")
            if not mix_sermon_with_ambience(sermon_path, ambience_file, output_path):
                print(f"Failed to mix {sermon_file}")
                success = False
            
            # Small delay between files
            time.sleep(1)
        
        return success
        
    except Exception as e:
        print(f"Error in process_all_sermons: {str(e)}")
        return False

if __name__ == "__main__":
    audio_dir = "audio"
    ambience_file = "processed_audio/trimmed_ambience.mp3"
    output_dir = "processed_audio"
    
    # Process all sermons in the audio directory
    process_all_sermons(audio_dir, ambience_file, output_dir) 