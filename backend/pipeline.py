# pipeline.py
import openai
import io
import base64
from gtts import gTTS

from backend.constants import (
    OPENAI_API_KEY,
    ANKI_CONNECT_URL    
)


# Function to call the LLM for translations and example sentences
def generate_language_data(vocab_word, target_language, base_language):
    """
    Given a {target_language} vocabulary word, generate:
    - {base_language} translation of the word
    - Example sentence in {target_language}
    - {base_language} translation of the example sentence
    """
    prompt = f"""
    Please provide the following details for the {target_language} vocabulary word "{vocab_word}":
    1. {base_language} translation of the word, by itself no other text
    2. An example sentence in {target_language} using the word, by itself no other text
    3. {base_language} translation of the example sentence, by itself no other text
    
    Provide them exactly as specified, separated by newline characters.
    
    EXAMPLE: If the target language is Japanese, base language is English, and vocab word = 猫 you would output:
    Cat
    猫は魚が大好きです
    Cats love fish
    
    EXAMPLE: If the target language is Spanish, base language is English, and vocab word = perro
    perro
    El perro es un animal de cuatro patas
    The dog is a four-legged animal
    
    EXAMPLE: If the target language is Swedish, base language is English, and vocab word = vatten
    vatten
    Vatten är en vätska
    Water is a liquid
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY) 
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for learning languages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        output = response.choices[0].message.content.strip()
        return output.split("\n")
    except Exception as e:
        return ["Error", str(e), ""]

# Function to generate TTS audio
def generate_audio(text, language="ja"):
    """
    Generate TTS audio for a given text and return base64-encoded audio data
    """
    try:
        # Generate audio in memory
        audio_buffer = io.BytesIO()
        tts = gTTS(text=text, lang=language)
        tts.write_to_fp(audio_buffer)
        
        # Convert to base64
        audio_data = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
        return audio_data
    except Exception as e:
        return f"Error generating audio: {e}"

def get_language_code(language_name):
    """Map language names to IETF language tags"""
    mapping = {
        "Arabic": "ar",
        "Bulgarian": "bg",
        "Chinese": "zh",
        "Croatian": "hr",
        "Czech": "cs",
        "Dutch": "nl",
        "English": "en",
        "French": "fr",
        "German": "de",
        "Greek": "el",
        "Hebrew": "he",
        "Hindi": "hi",
        "Hungarian": "hu",
        "Indonesian": "id",
        "Italian": "it",
        "Japanese": "ja",
        "Korean": "ko",
        "Malay": "ms",
        "Polish": "pl",
        "Portuguese": "pt",
        "Romanian": "ro",
        "Russian": "ru",
        "Slovak": "sk",
        "Spanish": "es",
        "Swedish": "sv",
        "Thai": "th",
        "Turkish": "tr",
        "Vietnamese": "vi"
    }
    return mapping.get(language_name, "en")

# Complete workflow
def process_vocab_word(vocab_word, target_language, base_language="English"):
    """
    Generates all components for an {base_language}-{target_language} Anki card from a {target_language} word.
    """
    print(f"Processing vocabulary word: {vocab_word}")
    print(f"Target language: {target_language}")
    print(f"Base language: {base_language}")
    # Generate text data
    language_data = generate_language_data(vocab_word, target_language=target_language, base_language=base_language)
    if len(language_data) < 3:
        print("Error: LLM output malformed.")
        return None
    
    vocab_translation, example_sentence, example_sentence_translation = language_data[:3]
    
    # Generate TTS audio
    language_code = get_language_code(target_language)
    vocab_audio = generate_audio(vocab_word, language_code)
    example_sentence_translation_audio = generate_audio(example_sentence, language_code)
    
    return {
        "vocab_word": vocab_word,
        "vocab_translation": vocab_translation,
        "example_sentence": example_sentence,
        "example_sentence_translation": example_sentence_translation,
        "vocab_audio": vocab_audio,
        "example_sentence_translation_audio": example_sentence_translation_audio
    }

