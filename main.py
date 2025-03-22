import os
import time
import glob
from pathlib import Path
from src.sermon_generator import main as generate_sermon
from src.bible_tts import main as convert_to_speech
from src.mix_audio import process_all_sermons

def ensure_directories():
    """Ensure all necessary directories exist."""
    directories = ['data', 'audio', 'processed_audio', 'videos']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def check_ambience_file():
    """Check if the ambience file exists."""
    ambience_path = "processed_audio/trimmed_ambience.mp3"
    if not os.path.exists(ambience_path):
        raise FileNotFoundError(
            f"Ambience file not found at {ambience_path}. "
            "Please ensure you have placed your background ambience file at this location."
        )

def get_files_by_extension(directory, extension):
    """Get all files with the given extension in the directory."""
    return glob.glob(os.path.join(directory, f"*{extension}"))

def get_base_filename(filepath):
    """Get the base filename without extension and path."""
    return os.path.splitext(os.path.basename(filepath))[0]

def find_unprocessed_sermons():
    """
    Find sermons that haven't completed the full pipeline.
    Returns a dictionary with the status of each sermon.
    """
    # Get all files in each stage
    text_files = set(get_base_filename(f) for f in get_files_by_extension("data", ".txt"))
    audio_files = set(get_base_filename(f) for f in get_files_by_extension("audio", ".mp3"))
    final_files = set(get_base_filename(f).replace("_with_ambience", "") 
                     for f in get_files_by_extension("processed_audio", "_with_ambience.mp3"))
    
    unprocessed = {}
    
    # Check each sermon's status
    for sermon in text_files:
        status = {
            "text_exists": True,
            "audio_exists": sermon in audio_files,
            "final_exists": sermon in final_files,
            "text_path": os.path.join("data", f"{sermon}.txt"),
            "audio_path": os.path.join("audio", f"{sermon}.mp3"),
            "final_path": os.path.join("processed_audio", f"{sermon}_with_ambience.mp3")
        }
        
        # Only include if not fully processed
        if not all([status["text_exists"], status["audio_exists"], status["final_exists"]]):
            unprocessed[sermon] = status
    
    return unprocessed

def wait_for_file_modification(filepath, timeout=1200):
    """
    Wait for the specified file to be modified.
    Returns True if file was modified within timeout period.
    """
    if not filepath:
        return False
        
    start_time = time.time()
    initial_mtime = os.path.getmtime(filepath) if os.path.exists(filepath) else None
    
    while time.time() - start_time < timeout:
        if not os.path.exists(filepath):
            time.sleep(1)
            print(".", end="", flush=True)
            continue
            
        current_mtime = os.path.getmtime(filepath)
        if initial_mtime is None or current_mtime > initial_mtime:
            # Add a small safety delay to ensure file writing is complete
            time.sleep(2)
            return True
            
        time.sleep(1)
        print(".", end="", flush=True)
    
    return False

def monitor_audio_creation(audio_path, timeout=600):
    """
    Actively monitor for audio file creation and completion.
    Returns True if the file is created and stable (not being written to).
    """
    print(f"\nWaiting for audio file creation at: {audio_path}")
    start_time = time.time()
    last_size = 0
    size_stable_count = 0
    
    while time.time() - start_time < timeout:
        if os.path.exists(audio_path):
            current_size = os.path.getsize(audio_path)
            
            # If file size hasn't changed in 3 checks (3 seconds), consider it complete
            if current_size == last_size:
                size_stable_count += 1
                if size_stable_count >= 3:
                    print("\n✓ Audio file creation complete")
                    # Add a small safety delay
                    time.sleep(2)
                    return True
            else:
                size_stable_count = 0
                last_size = current_size
                print("+", end="", flush=True)  # Show progress when file is growing
        else:
            print(".", end="", flush=True)
            
        time.sleep(1)
    
    return False

def process_sermon(sermon_name, status, is_new=False):
    """Process a single sermon through the remaining steps in the pipeline."""
    try:
        # If this is a new sermon, we need to generate it first
        if is_new:
            print("\n=== Step 1: Generating New Sermon Text ===")
            generated_file = generate_sermon()
            if not generated_file or not os.path.exists(generated_file):
                raise Exception("Failed to generate sermon text")
            
            # Update status with actual file paths
            base_name = os.path.splitext(os.path.basename(generated_file))[0]
            status = {
                "text_exists": True,
                "audio_exists": False,
                "final_exists": False,
                "video_exists": False,
                "text_path": generated_file,
                "audio_path": os.path.join("audio", f"{base_name}.mp3"),
                "final_path": os.path.join("processed_audio", f"{base_name}_with_ambience.mp3"),
                "video_path": os.path.join("videos", f"{base_name}_with_ambience.mp4")
            }
            sermon_name = base_name
            print(f"✓ Generated new sermon: {os.path.basename(generated_file)}")
        
        # Convert to speech if needed (10 minute timeout)
        if not status["audio_exists"]:
            print(f"\n=== Converting '{sermon_name}' to Speech ===")
            convert_to_speech()
            if not monitor_audio_creation(status["audio_path"], timeout=600):
                raise Exception("Failed to convert sermon to speech (timeout after 10 minutes)")
            print(f"✓ Created audio: {os.path.basename(status['audio_path'])}")
        
        # Mix with ambience if needed (3 minute timeout)
        if not status["final_exists"]:
            print(f"\n=== Mixing '{sermon_name}' with Ambience ===")
            process_all_sermons(
                audio_dir="audio",
                ambience_file="processed_audio/trimmed_ambience.mp3",
                output_dir="processed_audio"
            )
            if not monitor_audio_creation(status["final_path"], timeout=180):
                raise Exception("Failed to mix audio with ambience (timeout after 3 minutes)")
            print(f"✓ Created final mix: {os.path.basename(status['final_path'])}")
        
        # Create video with subtitles if needed
        if not status["video_exists"]:
            print(f"\n=== Creating Video for '{sermon_name}' ===")
            create_videos(processed_audio_dir="processed_audio", output_dir="videos")
            if not os.path.exists(status["video_path"]):
                raise Exception("Failed to create video")
            print(f"✓ Created video: {os.path.basename(status['video_path'])}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error processing '{sermon_name}': {str(e)}")
        return False

def main(force_new=False):
    """Main execution function that coordinates all processes."""
    try:
        print("\n=== Starting Sermon Production System ===\n")
        
        # Step 0: Setup
        print("Setting up directories...")
        ensure_directories()
        check_ambience_file()
        print("✓ Setup complete")
        
        # Find unprocessed sermons
        unprocessed = find_unprocessed_sermons()
        
        if force_new or not unprocessed:
            print("\nGenerating new sermon...")
            # Create a placeholder status for the new sermon
            new_sermon_status = {
                "text_exists": False,
                "audio_exists": False,
                "final_exists": False,
                "video_exists": False,
                "text_path": None,  # Will be set after generation
                "audio_path": None,
                "final_path": None,
                "video_path": None
            }
            process_sermon("new_sermon", new_sermon_status, is_new=True)
        else:
            print(f"\nFound {len(unprocessed)} unprocessed sermons:")
            for sermon_name, status in unprocessed.items():
                print(f"\nProcessing: {sermon_name}")
                print("Status:")
                print(f"  - Text file: {'✓' if status['text_exists'] else '✗'}")
                print(f"  - Audio file: {'✓' if status['audio_exists'] else '✗'}")
                print(f"  - Final mix: {'✓' if status['final_exists'] else '✗'}")
                print(f"  - Video: {'✓' if status['video_exists'] else '✗'}")
                
                process_sermon(sermon_name, status)
        
        print("\n=== Sermon Production Complete ===")
        print("✓ All steps completed successfully!")
        print("Your final sermons can be found in the 'videos' directory.")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {str(e)}")
    except Exception as e:
        print(f"\n✗ An unexpected error occurred: {str(e)}")
    finally:
        print("\nProcess finished.")

if __name__ == "__main__":
    main(force_new=True)  # Force generation of a new sermon 