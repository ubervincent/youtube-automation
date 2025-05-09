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
    },
    "Overcoming Sin": {
        "main_points": [
            "Understanding the Nature of Sin",
            "The Power of Christ's Redemption",
            "Practical Steps for Victory",
            "Living in Freedom"
        ],
        "key_scriptures": [
            "Romans 6:23",
            "1 John 1:9",
            "James 1:14-15",
            "Romans 8:1-2"
        ]
    },
    "Sexual Purity": {
        "main_points": [
            "God's Design for Sexuality",
            "Battling Temptation",
            "Healing from Past Wounds",
            "Walking in Holiness"
        ],
        "key_scriptures": [
            "1 Thessalonians 4:3-5",
            "Matthew 5:27-28",
            "1 Corinthians 6:18-20",
            "Hebrews 13:4"
        ]
    },
    "Repentance": {
        "main_points": [
            "True Biblical Repentance",
            "God's Heart for Restoration",
            "Steps to Genuine Change",
            "Living a Transformed Life"
        ],
        "key_scriptures": [
            "2 Corinthians 7:10",
            "Acts 3:19",
            "Psalm 51:1-12",
            "Ezekiel 36:26"
        ]
    },
    "Identity in Christ": {
        "main_points": [
            "Understanding Your New Nature",
            "Living as God's Child",
            "Overcoming False Identity",
            "Walking in Your Calling"
        ],
        "key_scriptures": [
            "2 Corinthians 5:17",
            "Galatians 2:20",
            "Ephesians 1:3-6",
            "1 Peter 2:9"
        ]
    },
    "Biblical Marriage": {
        "main_points": [
            "God's Design for Marriage",
            "Love and Respect",
            "Navigating Challenges",
            "Building a Christ-Centered Home"
        ],
        "key_scriptures": [
            "Ephesians 5:21-33",
            "Genesis 2:24",
            "1 Corinthians 13:4-7",
            "Colossians 3:18-19"
        ]
    },
    "Spiritual Disciplines": {
        "main_points": [
            "The Power of God's Word",
            "Developing Prayer Life",
            "Fasting and Meditation",
            "Worship as a Lifestyle"
        ],
        "key_scriptures": [
            "Joshua 1:8",
            "Psalm 119:105",
            "Matthew 6:16-18",
            "Colossians 3:16"
        ]
    },
    "Dealing with Anger": {
        "main_points": [
            "Understanding Righteous Anger",
            "Overcoming Sinful Anger",
            "Practical Steps for Peace",
            "Restoration and Reconciliation"
        ],
        "key_scriptures": [
            "Ephesians 4:26-27",
            "James 1:19-20",
            "Proverbs 15:1",
            "Matthew 5:21-24"
        ]
    },
    "Biblical Contentment": {
        "main_points": [
            "Finding Peace in Christ",
            "Overcoming Comparison",
            "Gratitude in All Circumstances",
            "Eternal Perspective"
        ],
        "key_scriptures": [
            "Philippians 4:11-13",
            "1 Timothy 6:6-8",
            "Hebrews 13:5",
            "Matthew 6:33"
        ]
    },
    "Spiritual Warfare": {
        "main_points": [
            "Understanding the Enemy",
            "The Armor of God",
            "Prayer and Warfare",
            "Victory in Christ"
        ],
        "key_scriptures": [
            "Ephesians 6:10-18",
            "2 Corinthians 10:3-5",
            "James 4:7",
            "1 John 4:4"
        ]
    }
}

def create_sermon_prompt(topic: str, topic_data: dict) -> str:
    """Create a detailed prompt for the OpenAI API."""
    prompt = f"""Write an 1100-word sermon from Jesus Christ's perspective, speaking directly to a modern audience. The sermon must be EXACTLY 1100 words long.

Structure the sermon in this way:
1. Loving Greeting (110 words)
   - Begin with "My beloved children,"
   - Speak with divine authority yet tender compassion
   - Connect the eternal truth with present-day relevance

2. Main Teaching Points (770 words total, ~192 words each):
   {', '.join(f'- {point}' for point in topic_data['main_points'])}
   For each point:
   - Draw parallels between biblical parables and modern situations
   - Reference both ancient wisdom and contemporary challenges
   - Speak with divine insight while remaining accessible

3. Heart-to-Heart Application (110 words)
   - Provide guidance with divine wisdom
   - Share eternal principles for daily living
   - Speak to both individual and communal transformation

4. Blessing and Commission (110 words)
   - Affirm your eternal love and presence
   - Give specific encouragement for the journey ahead
   - End with a blessing that bridges heaven and earth

Key Scriptures to Weave In Naturally:
{', '.join(topic_data['key_scriptures'])}

Essential Style Elements:
- Maintain Jesus' unique voice - authoritative yet deeply compassionate
- Use "I" statements that reflect divine perspective
- Include modern metaphors while preserving timeless truth
- Reference your earthly ministry and teachings where relevant
- Speak with both divine wisdom and human understanding
- Address both personal and communal aspects of faith
- Balance eternal truth with present-day application

Voice Guidelines:
- Use phrases like "As I told my disciples then, I tell you now..."
- Draw parallels: "Just as I walked with my followers in Galilee, I walk with you today..."
- Connect past and present: "The truth I spoke on the mountainside remains true in your modern world..."
- Show continuity: "My words to the woman at the well speak to your heart today..."

Remember:
- The sermon MUST be exactly 1100 words
- Maintain Jesus' unique voice throughout
- Blend biblical authority with contemporary relevance
- Every scripture should feel personally delivered
- End with divine blessing and commissioning

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
                    "content": "You are channeling the voice and perspective of Jesus Christ speaking to a modern audience. Follow this structure strictly:\n1. Opening (110 words)\n2. Main Teaching (770 words)\n3. Application (110 words)\n4. Single Closing Blessing (110 words)\nDo not repeat the closing or add multiple endings. The sermon must be exactly 1100 words total."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2500,
            presence_penalty=0.6,  # Penalize topic repetition
            frequency_penalty=0.8   # Strongly penalize word repetition
        )
        
        content = response.choices[0].message.content
        word_count = len(content.split())
        
        # If the content is too short, generate more in chunks
        while word_count < 1050:  # Allow for some flexibility
            remaining_words = 1100 - word_count
            last_sentences = ' '.join(content.split()[-150:])
            
            continuation_prompt = f"""Continue this sermon to add approximately {remaining_words} more words.
            Here's the current ending for context: "{last_sentences}"
            
            Important:
            - You may modify the last few sentences of the previous content to ensure smooth flow
            - Maintain the same style, tone, and thematic consistency
            - Ensure natural transitions between ideas
            - Keep building toward a SINGLE conclusion
            - Do not add multiple endings or blessings"""
            
            continuation = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are continuing a sermon. Focus on maintaining flow and coherence with the previous content. Do not add multiple endings or repeat the blessing. End with a single, powerful closing blessing."
                    },
                    {
                        "role": "assistant",
                        "content": content  # Provide full context
                    },
                    {
                        "role": "user",
                        "content": continuation_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                presence_penalty=0.6,
                frequency_penalty=0.8
            )
            
            additional_content = continuation.choices[0].message.content
            last_period = content.rfind('.')
            if last_period != -1:
                content = content[:last_period + 1] + "\n\n" + additional_content
            else:
                content = content + "\n\n" + additional_content
                
            word_count = len(content.split())
            print(f"Current sermon length: {word_count} words")
            
            # Prevent infinite loops
            if len(content.split()) >= 1050:
                break
        
        # Final word count check
        final_word_count = len(content.split())
        if final_word_count < 1050 or final_word_count > 1150:
            print(f"Warning: Final sermon length is {final_word_count} words (target: 1100)")
        
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