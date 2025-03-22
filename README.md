# Bible Text-to-Speech Converter

This project converts biblical texts to audio using OpenAI's Text-to-Speech API.

## Project Structure

```
bible_tts_project/
├── src/           # Source code
│   └── bible_tts.py
├── data/          # Input text files
│   └── bible_text.txt
├── output/        # Generated audio files
│   └── bible_part_*.mp3
├── venv/          # Virtual environment
├── .env           # Environment variables (API keys)
└── requirements.txt
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

1. Place your biblical text in `data/bible_text.txt`
2. Run the script:
```bash
python src/bible_tts.py
```
3. Find the generated audio files in the `output/` directory

## Available Voices

- alloy (default)
- echo
- fable
- onyx
- nova
- shimmer

To change the voice, modify the `voice` parameter in `src/bible_tts.py`. 