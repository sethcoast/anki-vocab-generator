const ANKI_CONNECT_URL = 'http://localhost:8765';

// Equivalent to Python's request function
function createRequest(action, params = {}) {
    return {
        action,
        version: 6,
        params
    };
}

// Equivalent to Python's invoke function
async function invoke(action, params = {}) {
    const response = await fetch(ANKI_CONNECT_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(createRequest(action, params))
    });

    if (!response.ok) {
        throw new Error(`Request failed with status code ${response.status}: ${await response.text()}`);
    }

    const responseJson = await response.json();
    if (!('error' in responseJson) || !('result' in responseJson)) {
        throw new Error('Invalid response structure');
    }
    if (responseJson.error) {
        throw new Error(responseJson.error);
    }

    return responseJson.result;
}

// Equivalent to Python's store_audio_file function, but modified to work with base64 data directly
async function storeAudioFile(filename, audioData) {
    const response = await invoke('storeMediaFile', {
        filename,
        data: audioData
    });
    console.log(`Stored ${filename}:`, response);
    return response;
}

// New version of add_note that takes the data object from the backend
async function addNote(data, deckName = "Vocabulary") {
    // Store the audio files
    const vocabAudioFilename = `${data.vocab_word}_word.mp3`;
    const exampleAudioFilename = `${data.vocab_word}_sentence.mp3`;

    await storeAudioFile(vocabAudioFilename, data.vocab_audio);
    await storeAudioFile(exampleAudioFilename, data.example_sentence_translation_audio);

    const note = {
        deckName,
        modelName: "Vocab Mining",
        fields: {
            "Target Word": data.vocab_word,
            "Source Translation": data.vocab_translation,
            "Target Sentence": data.example_sentence,
            "Source Sentence Translation": data.example_sentence_translation,
            "Word Audio": `[sound:${vocabAudioFilename}]`,
            "Sentence Audio": `[sound:${exampleAudioFilename}]`
        },
        options: {
            allowDuplicate: false,
            duplicateScope: "deck",
            duplicateScopeOptions: {
                deckName,
                checkChildren: false,
                checkAllModels: false
            }
        },
        tags: ["chrome_extension"]
    };

    return invoke("addNote", { note });
}

// Add this function before the export statement
async function getDecks() {
    return invoke('deckNames');
}

// Export the functions to be used in other files
export {
    invoke,
    storeAudioFile,
    addNote,
    getDecks
}; 