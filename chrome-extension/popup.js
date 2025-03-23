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
      resultDiv.innerHTML = `
        <p><strong>Word:</strong> ${data.vocab_word}</p>
        <p><strong>Translation:</strong> ${data.vocab_translation}</p>
        <p><strong>Example:</strong> ${data.example_sentence}</p>
        <p><strong>Example Translation:</strong> ${data.example_sentence_translation}</p>
      `;
    } catch (err) {
      resultDiv.textContent = "Error: " + err.message;
    }
  });
  