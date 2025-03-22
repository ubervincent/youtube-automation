import os
import time
from datetime import datetime
from pathlib import Path
import random
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Biblical topics with their key points and scriptures
BIBLICAL_TOPICS = {
    "God's Love": {
        "main_points": [
            "Unconditional Nature of God's Love",
            "Demonstrating God's Love Through Christ",
            "Experiencing God's Love Daily",
            "Sharing God's Love with Others"
        ],
        "key_scriptures": [
            "John 3:16",
            "1 John 4:7-8",
            "Romans 5:8",
            "Ephesians 3:17-19"
        ]
    },
    "Faith and Trust": {
        "main_points": [
            "Understanding Biblical Faith",
            "Building Trust in God",
            "Faith in Difficult Times",
            "Growing Your Faith Daily"
        ],
        "key_scriptures": [
            "Hebrews 11:1",
            "Proverbs 3:5-6",
            "James 1:2-4",
            "Romans 10:17"
        ]
    },
    "Prayer": {
        "main_points": [
            "The Power of Prayer",
            "Different Types of Prayer",
            "Developing a Prayer Life",
            "Praying with Purpose"
        ],
        "key_scriptures": [
            "Philippians 4:6-7",
            "1 Thessalonians 5:17",
            "James 5:16",
            "Matthew 6:9-13"
        ]
    },
    "Grace and Salvation": {
        "main_points": [
            "Understanding God's Grace",
            "The Gift of Salvation",
            "Living in Grace Daily",
            "Sharing the Message of Grace"
        ],
        "key_scriptures": [
            "Ephesians 2:8-9",
            "Romans 6:23",
            "Titus 2:11-12",
            "2 Corinthians 12:9"
        ]
    },
    "Spiritual Growth": {
        "main_points": [
            "The Process of Sanctification",
            "Developing Spiritual Disciplines",
            "Overcoming Spiritual Obstacles",
            "Bearing Spiritual Fruit"
        ],
        "key_scriptures": [
            "2 Peter 3:18",
            "Philippians 1:6",
            "Galatians 5:22-23",
            "Colossians 1:9-10"
        ]
    },
    "Biblical Community": {
        "main_points": [
            "The Importance of Fellowship",
            "Building Strong Relationships",
            "Serving One Another",
            "Unity in Christ"
        ],
        "key_scriptures": [
            "Hebrews 10:24-25",
            "Acts 2:42-47",
            "1 Corinthians 12:12-27",
            "Ephesians 4:11-16"
        ]
    },
    "Overcoming Trials": {
        "main_points": [
            "Understanding God's Purpose in Trials",
            "Finding Strength in Adversity",
            "The Role of Community in Trials",
            "Victory Through Christ"
        ],
        "key_scriptures": [
            "James 1:2-4",
            "Romans 8:28",
            "2 Corinthians 4:16-18",
            "1 Peter 5:10"
        ]
    },
    "Biblical Worship": {
        "main_points": [
            "Understanding True Worship",
            "Worship in Spirit and Truth",
            "Living a Life of Worship",
            "Corporate Worship"
        ],
        "key_scriptures": [
            "John 4:23-24",
            "Psalm 95:1-6",
            "Romans 12:1",
            "Hebrews 13:15-16"
        ]
    },
    "Spiritual Warfare": {
        "main_points": [
            "Understanding the Battle",
            "The Armor of God",
            "Strategies for Victory",
            "Standing Firm in Faith"
        ],
        "key_scriptures": [
            "Ephesians 6:10-18",
            "2 Corinthians 10:3-5",
            "1 Peter 5:8-9",
            "James 4:7"
        ]
    },
    "Biblical Stewardship": {
        "main_points": [
            "Managing God's Resources",
            "Time and Talent Stewardship",
            "Financial Stewardship",
            "Environmental Stewardship"
        ],
        "key_scriptures": [
            "Matthew 25:14-30",
            "1 Peter 4:10",
            "Malachi 3:10",
            "Genesis 1:28"
        ]
    },
    "The Holy Spirit": {
        "main_points": [
            "Understanding the Holy Spirit",
            "The Gifts of the Spirit",
            "Walking in the Spirit",
            "The Fruit of the Spirit"
        ],
        "key_scriptures": [
            "John 14:26",
            "Acts 1:8",
            "Galatians 5:22-23",
            "1 Corinthians 12:4-11"
        ]
    },
    "Biblical Leadership": {
        "main_points": [
            "Servant Leadership",
            "Developing Godly Character",
            "Leading by Example",
            "Empowering Others"
        ],
        "key_scriptures": [
            "Mark 10:42-45",
            "1 Timothy 3:1-7",
            "Titus 1:5-9",
            "1 Peter 5:1-4"
        ]
    }
}

def create_sermon_prompt(topic: str, topic_data: dict) -> str:
    """Create a detailed prompt for the OpenAI API."""
    prompt = f"""Write a 1000-word sermon on {topic}. The sermon must be EXACTLY 1000 words long.

Structure the sermon in this way:
1. Warm Personal Introduction (100 words)
   - Begin with "Dear friends in Christ, thank you for joining me today."
   - Introduce the topic personally and emotionally
   - Share why this topic matters in our daily lives

2. Main Teaching Points (700 words total, ~175 words each):
   {', '.join(f'- {point}' for point in topic_data['main_points'])}

3. Practical Application (100 words)
   - Real-life examples and solutions
   - Specific steps for daily implementation

4. Encouraging Conclusion (100 words)
   - Summarize key points
   - End with a prayer or blessing

Key Scriptures to Reference and Explain:
{', '.join(topic_data['key_scriptures'])}

Important Style Guidelines:
- Use a warm, conversational tone throughout
- Include personal anecdotes and real-life examples
- Address the audience directly using "you" and "we"
- Make deep theological concepts practical and accessible
- Provide specific, actionable guidance for daily life
- Use metaphors from everyday life
- Maintain a compassionate tone

Remember:
- The sermon MUST be exactly 1000 words
- Each section should flow naturally into the next
- Every scripture reference should be explained practically
- End with hope and encouragement

Format the text as a continuous sermon without section headers or numbers."""
    return prompt

def generate_sermon_with_openai(prompt: str) -> str:
    """Generate sermon content using OpenAI API."""
    try:
        # First attempt to generate the sermon
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable and compassionate biblical teacher creating engaging, scripture-based daily devotional messages. You MUST write exactly 1000 words - no more, no less."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        
        content = response.choices[0].message.content
        word_count = len(content.split())
        
        # If the content is too short, generate more in chunks
        while word_count < 950:  # Allow for some flexibility
            remaining_words = 1000 - word_count
            last_sentences = ' '.join(content.split()[-30:])
            
            continuation_prompt = f"""Continue this message to add approximately {remaining_words} more words.
            The current message ends with: "{last_sentences}"
            Continue naturally from this point, maintaining the same style and flow."""
            
            continuation = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are continuing a daily devotional message. Maintain the same style and flow."
                    },
                    {
                        "role": "user",
                        "content": continuation_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            additional_content = continuation.choices[0].message.content
            content = content + "\n\n" + additional_content
            word_count = len(content.split())
            print(f"Current sermon length: {word_count} words")
            
            # Prevent infinite loops
            if len(content.split()) >= 950:
                break
        
        # Final word count check
        final_word_count = len(content.split())
        if final_word_count < 950 or final_word_count > 1050:
            print(f"Warning: Final sermon length is {final_word_count} words (target: 1000)")
        
        return content
    except Exception as e:
        print(f"Error generating sermon: {str(e)}")
        return None

def ensure_data_directory():
    """Ensure the data directory exists."""
    Path("data").mkdir(parents=True, exist_ok=True)

def save_sermon(content: str, topic: str) -> str:
    """Save the generated sermon to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{topic.lower().replace(' ', '_')}.txt"
    
    ensure_data_directory()
    filepath = os.path.join("data", filename)  # Create path in data directory
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(filepath)  # Return full filepath instead of just filename

def generate_sermon():
    """Main function to generate a sermon."""
    # Pick a random topic
    topic = random.choice(list(BIBLICAL_TOPICS.keys()))
    topic_data = BIBLICAL_TOPICS[topic]
    
    # Create prompt and generate content
    prompt = create_sermon_prompt(topic, topic_data)
    sermon_content = generate_sermon_with_openai(prompt)
    
    if sermon_content:
        # Save the sermon
        filename = save_sermon(sermon_content, topic)
        return filename
    return None

def main():
    """Main execution function."""
    try:
        print("Generating sermon...")
        filename = generate_sermon()
        if filename:
            print(f"Sermon generated successfully and saved to: {filename}")
            return filename
        else:
            print("Failed to generate sermon.")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    main() 