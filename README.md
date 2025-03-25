# YouTube Sermon Automation

This project automatically generates and creates engaging sermon videos using AI. It combines sermon generation, text-to-speech conversion, and video creation capabilities to produce high-quality religious content.

## Features

- **AI Sermon Generation**: Creates biblically-sound sermons on various topics using OpenAI's GPT-4
- **Text-to-Speech Conversion**: Converts generated sermons to natural-sounding speech
- **Automated Video Creation**: Produces engaging videos with background visuals and captions
- **Multiple Biblical Topics**: Supports 20+ predefined biblical topics with key points and scriptures
- **Structured Content**: Generates sermons with consistent structure:
  - Loving Greeting
  - Main Teaching Points
  - Heart-to-Heart Application
  - Blessing and Commission

## Project Structure

```
youtube-automation/
├── src/                # Source code
│   ├── sermon_generator.py    # Sermon generation logic
│   ├── audio_utils.py        # Audio processing utilities
│   ├── create_captioned_videos.py  # Video creation
│   └── main.py              # Main execution script
├── data/               # Generated sermons
├── assets/            # Static assets
├── backgrounds/       # Video background images
├── videos/            # Output video files
├── .env              # Environment variables
└── requirements.txt   # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

1. Generate a new sermon:
```bash
python src/sermon_generator.py
```

2. Create a video from the generated sermon:
```bash
python src/create_captioned_videos.py
```

## Available Topics

The system includes various biblical topics such as:
- God's Love
- Faith and Trust
- Prayer
- Grace and Salvation
- Spiritual Growth
- Biblical Community
- Overcoming Trials
- And many more...

Each topic comes with predefined main points and key scriptures to ensure theological accuracy and comprehensive coverage.

## Output

- **Sermons**: Generated as text files in the `data/` directory
- **Videos**: Created in the `videos/` directory with:
  - Professional voice narration
  - Beautiful background visuals
  - Synchronized captions
  - Background music (optional)

## Requirements

- Python 3.8+
- OpenAI API key
- FFmpeg (for video processing)
- Required Python packages (see requirements.txt)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 