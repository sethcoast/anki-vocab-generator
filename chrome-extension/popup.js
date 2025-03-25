import { addNote, getDecks } from './anki_utils.js';

document.getElementById("generate-btn").addEventListener("click", async () => {
    const word = document.getElementById("vocab-word").value;
    const targetLang = document.getElementById("target-lang").value || "ja";
  
    const payload = {
      word,
      target_lang: targetLang,
      base_lang: "en" // for now
    };
  
    const resultDiv = document.getElementById("result");
    resultDiv.textContent = "Loading...";
  
    try {
      const response = await fetch("http://localhost:8000/generate-card", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
  
      if (!response.ok) {
        throw new Error(await response.text());
      }
  
      const data = await response.json();
      
      // Create audio elements for preview
      const vocabAudio = new Audio(`data:audio/mp3;base64,${data.vocab_audio}`);
      const exampleAudio = new Audio(`data:audio/mp3;base64,${data.example_sentence_translation_audio}`);
      
      // Fetch available decks
      const decks = await getDecks();
      const deckSelector = `
        <select id="deck-select">
          <option value="">Select a deck...</option>
          ${decks.map(deck => `<option value="${deck}">${deck}</option>`).join('')}
        </select>
      `;
      
      resultDiv.innerHTML = `
        <p><strong>Word:</strong> ${data.vocab_word} <button id="play-vocab">🔊</button></p>
        <p><strong>Translation:</strong> ${data.vocab_translation}</p>
        <p><strong>Example:</strong> ${data.example_sentence} <button id="play-example">🔊</button></p>
        <p><strong>Example Translation:</strong> ${data.example_sentence_translation}</p>
        <div style="margin: 10px 0;">
          ${deckSelector}
        </div>
        <button id="add-to-anki" disabled>Add to Anki</button>
      `;

      // Add hidden audio elements
      const vocabAudioElement = document.createElement('audio');
      vocabAudioElement.id = 'vocab-audio';
      vocabAudioElement.src = `data:audio/mp3;base64,${data.vocab_audio}`;
      
      const exampleAudioElement = document.createElement('audio');
      exampleAudioElement.id = 'example-audio';
      exampleAudioElement.src = `data:audio/mp3;base64,${data.example_sentence_translation_audio}`;
      
      resultDiv.appendChild(vocabAudioElement);
      resultDiv.appendChild(exampleAudioElement);

      // Add audio play button handlers
      document.getElementById("play-vocab").addEventListener("click", () => {
        vocabAudioElement.play();
      });

      document.getElementById("play-example").addEventListener("click", () => {
        exampleAudioElement.play();
      });

      // Enable/disable Add to Anki button based on deck selection
      const addButton = document.getElementById("add-to-anki");
      document.getElementById("deck-select").addEventListener("change", (e) => {
        addButton.disabled = !e.target.value;
      });

      // Add click handler for the "Add to Anki" button
      addButton.addEventListener("click", async () => {
        try {
          const selectedDeck = document.getElementById("deck-select").value;
          if (!selectedDeck) {
            throw new Error("Please select a deck first");
          }
          await addNote(data, selectedDeck);
          resultDiv.innerHTML += '<p style="color: green;">Successfully added to Anki!</p>';
        } catch (err) {
          resultDiv.innerHTML += `<p style="color: red;">Error adding to Anki: ${err.message}</p>`;
        }
      });
      
    } catch (err) {
      resultDiv.textContent = "Error: " + err.message;
    }
});
  