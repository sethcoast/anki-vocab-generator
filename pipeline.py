# pipeline.py
import openai
import requests
from gtts import gTTS

from constants import (
    OPENAI_API_KEY,
    ANKI_CONNECT_URL    
)


# Function to call the LLM for translations and example sentences
def generate_language_data(vocab_word, target_language="Japanese"):
    """
    Given a {target_language} vocabulary word, generate:
    - English translation of the word
    - Example sentence in {target_language}
    - English translation of the example sentence
    """
    prompt = f"""
    Please provide the following details for the {target_language} vocabulary word "{vocab_word}":
    1. English translation of the word
    2. An example sentence in {target_language} using the word
    3. English translation of the example sentence
    
    Provide them exactly as specified, separated by newline characters.
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY) 
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for learning Japanese."},
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
def generate_audio(text, language="ja", filename="output.mp3"):
    """
    Generate TTS audio for a given text in the specified language.
    """
    try:
        tts = gTTS(text=text, lang=language)
        tts.save(filename)
        return filename
    except Exception as e:
        return f"Error generating audio: {e}"

# Complete workflow
def process_vocab_word(vocab_word, target_language="Japanese"):
    """
    Generates all components for an English-{target_language} Anki card from a {target_language} word.
    """
    print(f"Processing vocabulary word: {vocab_word}\n")
    
    # Generate text data
    language_data = generate_language_data(vocab_word, target_language=target_language)
    if len(language_data) < 3:
        print("Error: LLM output malformed.")
        return None
    
    vocab_translation, example_sentence, example_sentence_translation = language_data[:3]
    
    # Generate TTS audio
    vocab_filename = f"{vocab_word}_word.mp3"
    sentence_filename = f"{vocab_word}_sentence.mp3"
    generate_audio(vocab_word, filename=vocab_filename)
    generate_audio(example_sentence, filename=sentence_filename)
    
    return {
        "vocab_word": vocab_word,
        "vocab_translation": vocab_translation,
        "example_sentence": example_sentence,
        "example_sentence_translation": example_sentence_translation,
        "vocab_audio_filename": vocab_filename,
        "example_sentence_translation_audio_filename": sentence_filename
    }

# Function to send the card to Anki
def add_card_to_anki(deck_name, vocab_data):
    """
    Sends the formatted Anki card to Anki using AnkiConnect API.
    """
    note = {
        "deckName": deck_name,
        "modelName": "Basic", 
        "fields": {
            "Front": f"{vocab_data['vocab_word']}\n\n{vocab_data['example_sentence']}",
            "Back": f"{vocab_data['vocab_translation']}\n\n{vocab_data['example_sentence_translation']}",
        },
        "audio": [
            {"url": vocab_data["vocab_audio"], "filename": "vocab_word.mp3", "fields": ["Front"]},
            {"url": vocab_data["example_sentence_translation_audio"], "filename": "example_sentence.mp3", "fields": ["Back"]}
        ]
    }
    
    payload = {"action": "addNote", "version": 6, "params": {"note": note}}
    
    response = requests.post(ANKI_CONNECT_URL, json=payload).json()
    return response
