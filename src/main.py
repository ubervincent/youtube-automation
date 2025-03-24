import os
import shutil
from pathlib import Path
from datetime import datetime
import logging
from sermon_generator import generate_sermon, BIBLICAL_TOPICS
from create_captioned_videos import create_video_with_subtitles
from audio_utils import text_to_audio, mix_audio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories if they don't exist."""
    directories = ['data', 'videos', 'backgrounds', 'processed_audio', 'temp', 'assets/music']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created/verified directory: {directory}")

def cleanup_temp_files():
    """Clean up temporary files while keeping specified files."""
    try:
        # Clean up temp directory
        if os.path.exists('temp'):
            shutil.rmtree('temp')
            logger.info("Cleaned up temp directory")

        # Clean up processed_audio
        if os.path.exists('processed_audio'):
            shutil.rmtree('processed_audio')
            logger.info("Cleaned up processed_audio directory")

        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def get_unprocessed_sermons():
    """Get list of sermons that haven't been processed into videos yet."""
    # Get all sermon files
    sermon_files = [f for f in os.listdir('data') if f.endswith('.txt')]
    
    # Get all existing video files
    video_files = set(os.path.splitext(f)[0] for f in os.listdir('videos') if f.endswith('.mp4'))
    
    # Filter out sermons that already have videos
    unprocessed = []
    for sermon_file in sermon_files:
        sermon_id = '_'.join(sermon_file.split('_')[:2])  # Get timestamp part of filename
        if not any(video.startswith(sermon_id) for video in video_files):
            unprocessed.append(os.path.join('data', sermon_file))
    
    return unprocessed

def main():
    """Main execution function that orchestrates the entire workflow."""
    try:
        logger.info("Starting automated sermon video creation workflow...")
        
        # Setup required directories
        setup_directories()
        
        # Get unprocessed sermons
        unprocessed_sermons = get_unprocessed_sermons()
        
        if not unprocessed_sermons:
            logger.info("No unprocessed sermons found.")
            return
            
        logger.info(f"Found {len(unprocessed_sermons)} unprocessed sermons")
        
        for sermon_file in unprocessed_sermons:
            try:
                logger.info(f"Processing sermon: {os.path.basename(sermon_file)}")
                
                # Extract topic from filename
                topic = os.path.basename(sermon_file).split('_', 2)[2].replace('.txt', '')
                timestamp = '_'.join(os.path.basename(sermon_file).split('_')[:2])
                
                # Read sermon content
                with open(sermon_file, 'r', encoding='utf-8') as f:
                    sermon_text = f.read()
                
                # Create voice audio file
                voice_path = os.path.join('temp', f'voice_{timestamp}_{topic}.mp3')
                os.makedirs('temp', exist_ok=True)
                
                if not text_to_audio(sermon_text, voice_path):
                    logger.error("Failed to create voice audio file")
                    continue
                
                # Mix audio with background music
                logger.info("Mixing audio with background music...")
                audio_path = os.path.join('processed_audio', f'{timestamp}_{topic}.mp3')
                os.makedirs('processed_audio', exist_ok=True)
                
                if not mix_audio(voice_path, audio_path):
                    logger.error("Failed to mix audio")
                    continue
                
                # Create video with subtitles
                video_output = os.path.join('videos', f'{timestamp}_{topic}.mp4')
                if not create_video_with_subtitles(audio_path, video_output, use_generated_bg=True):
                    logger.error("Failed to create video")
                    continue
                
                # Move the background image to match video name if it exists
                background_files = [f for f in os.listdir('backgrounds') if f.startswith('background_')]
                if background_files:
                    latest_background = max(background_files, key=lambda x: os.path.getctime(os.path.join('backgrounds', x)))
                    new_background_name = f'{timestamp}_{topic}_background.png'
                    os.rename(
                        os.path.join('backgrounds', latest_background),
                        os.path.join('backgrounds', new_background_name)
                    )
                
                # Clean up temporary files for this sermon
                cleanup_temp_files()
                
                logger.info(f"Successfully created video: {video_output}")
                
            except Exception as e:
                logger.error(f"Error processing sermon {sermon_file}: {str(e)}")
                # Continue with next sermon
                continue
        
        logger.info("Workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")
        # Attempt cleanup even if there's an error
        cleanup_temp_files()

if __name__ == "__main__":
    main() 