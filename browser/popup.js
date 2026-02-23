// Текстовый анализ
document.getElementById('checkTextBtn').addEventListener('click', async () => {
  const text = document.getElementById('msgInput').value;
  const resultDiv = document.getElementById('result');
  
  if (!text.trim()) {
    resultDiv.innerText = "Мәтінді енгізіңіз!";
    return;
  }

  resultDiv.style.color = "black";
  resultDiv.innerText = "AI мәтінді талдау жасап жатыр...";

  try {
    const response = await fetch('https://your-vercel-link.app/analyze', { // Өз Vercel доменіңді жаз
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    
    const data = await response.json();
    
    if (data.error) {
      resultDiv.style.color = "orange";
      resultDiv.innerText = "⚠️ " + data.error;
      return;
    }

    if (data.verdict === "Қауіпті") {
      resultDiv.style.color = "#d9534f";
      resultDiv.innerHTML = `
        <strong>❌ ҚАУІПТІ: Алаяқтық белгілері бар!</strong><br>
        <small>Сенімділік: ${data.confidence}%</small><br>
        <p style="font-size: 12px; margin-top: 5px;">Себебі: ${data.reason}</p>
      `;
    } else {
      resultDiv.style.color = "#5cb85c";
      resultDiv.innerHTML = `
        <strong>✅ ТАЗА: Қауіп анықталған жоқ.</strong><br>
        <small>Сенімділік: ${data.confidence}%</small>
      `;
    }
  } catch (error) {
    console.error(error);
    resultDiv.style.color = "red";
    resultDiv.innerText = "Мәтіндік талдау кезінде қате орын алды!";
  }
});

// Экранды талдау (ЖАҢА БАТЫРМА)
document.getElementById('checkScreenBtn').addEventListener('click', async () => {
  const resultDiv = document.getElementById('result');
  resultDiv.style.color = "black";
  resultDiv.innerText = "AI экранды талдау жасап жатыр...";

  try {
    // 1. Белсенді тақтадан (visible tab) скриншот алу
    chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
      if (chrome.runtime.lastError) {
        resultDiv.style.color = "red";
        resultDiv.innerText = "⚠️ Экранды түсіру мүмкін емес: " + chrome.runtime.lastError.message;
        console.error("Capture error:", chrome.runtime.lastError.message);
        return;
      }
      if (!dataUrl) {
          resultDiv.style.color = "red";
          resultDiv.innerText = "⚠️ Бос скриншот алынды.";
          return;
      }
      
      const base64Image = dataUrl.split(',')[1]; // 'data:image/jpeg;base64,' префиксін алып тастау

      // 2. Backend-ке жіберу
      const response = await fetch('https://your-vercel-link.app/analyze-screen', { // Өз Vercel доменіңді жаз
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64Image })
      });
      
      const data = await response.json();

      if (data.error) {
        resultDiv.style.color = "orange";
        resultDiv.innerText = "⚠️ " + (data.details || data.error);
        return;
      }

      if (data.verdict === "Қауіпті") {
        resultDiv.style.color = "#d9534f";
        resultDiv.innerHTML = `
          <strong>❌ ҚАУІПТІ: Экранда алаяқтық белгілері бар!</strong><br>
          <small>Сенімділік: ${data.confidence}%</small><br>
          <p style="font-size: 12px; margin-top: 5px;">Себебі: ${data.reason}</p>
        `;
      } else {
        resultDiv.style.color = "#5cb85c";
        resultDiv.innerHTML = `
          <strong>✅ ТАЗА: Экранда қауіп анықталған жоқ.</strong><br>
          <small>Сенімділік: ${data.confidence}%</small>
        `;
      }
    });
  } catch (error) {
    console.error(error);
    resultDiv.style.color = "red";
    resultDiv.innerText = "Экранды талдау кезінде қате орын алды!";
  }
});