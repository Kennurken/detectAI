document.addEventListener('DOMContentLoaded', function() {
  const checkTextBtn = document.getElementById('checkTextBtn');
  const checkScreenBtn = document.getElementById('checkScreenBtn');
  const msgInput = document.getElementById('msgInput');
  const resultDiv = document.getElementById('result');
  const resultCard = document.getElementById('resultCard');
  const verdictLabel = document.getElementById('verdictLabel');
  const confidenceBadge = document.getElementById('confidenceBadge');
  const reasonText = document.getElementById('reasonText');
  const scanLine = document.getElementById('scanLine');

  const API_URL = "https://detect-ai-silk.vercel.app";

  console.log("Digital Trace: Скрипт іске қосылды");

  function setLoading(isLoading) {
    if (isLoading) {
      console.log("Жүктелуде...");
      checkTextBtn.disabled = true;
      checkScreenBtn.disabled = true;
      checkTextBtn.style.opacity = "0.5";
      checkScreenBtn.style.opacity = "0.5";
      resultDiv.style.display = 'none';
      if (scanLine) scanLine.style.display = 'block';
    } else {
      checkTextBtn.disabled = false;
      checkScreenBtn.disabled = false;
      checkTextBtn.style.opacity = "1";
      checkScreenBtn.style.opacity = "1";
      if (scanLine) scanLine.style.display = 'none';
    }
  }

  function displayResult(data) {
    setLoading(false);
    resultDiv.style.display = 'block'; 
    
    if (data.error) {
      console.error("Сервер қатесі:", data.error);
      verdictLabel.innerText = "⚠️ ҚАТЕ";
      verdictLabel.style.color = "#f59e0b";
      reasonText.innerText = data.details || data.error;
      resultCard.style.borderLeftColor = "#f59e0b";
      confidenceBadge.innerText = "0% Қауіп";
      return;
    }

    const isDanger = data.verdict === "Қауіпті";
    
    // Түстерді және белгілерді баптау
    resultCard.style.borderLeftColor = isDanger ? "#ef4444" : "#10b981";
    verdictLabel.style.color = isDanger ? "#f87171" : "#34d399";
    verdictLabel.innerText = isDanger ? "❌ ҚАУІПТІ" : "✅ ТАЗА";
    
    // Сенімділік пайызын көрсету (егер сандар ретінде келсе)
    const confidence = data.confidence || 0;
    confidenceBadge.innerText = `${confidence}% Қауіп`;
    confidenceBadge.style.background = isDanger ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)";
    confidenceBadge.style.color = isDanger ? "#f87171" : "#34d399";
    
    reasonText.innerText = data.reason || "Талдау аяқталды.";
  }

  // 1. Мәтінді талдау
  checkTextBtn.addEventListener('click', async () => {
    const text = msgInput.value.trim();
    if (!text) return alert("Мәтінді жазыңыз");

    setLoading(true);
    try {
        console.log("Мәтін жіберілуде...");
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();
        console.log("Жауап келді:", data);
        displayResult(data);
    } catch (error) {
        console.error("Fetch Error:", error);
        displayResult({ error: "Байланыс үзілді", details: "Сервер жауап бермеді." });
    }
  });

  // 2. Экранды талдау (Vision)
  checkScreenBtn.addEventListener('click', () => {
    setLoading(true);
    console.log("Скриншот жасалуда...");

    chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
      if (!dataUrl) {
        displayResult({ error: "Скриншот алу мүмкін болмады. Рұқсаттарды тексеріңіз." });
        return;
      }

      const base64Data = dataUrl.split(',')[1];
      
      try {
        console.log("Скриншот серверге кетті...");
        const response = await fetch(`${API_URL}/analyze-screen`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_base64: base64Data })
        });

        if (!response.ok) {
            throw new Error(`Сервер қатесі: ${response.status}`);
        }

        const data = await response.json();
        console.log("Vision жауабы:", data);
        displayResult(data);
      } catch (error) {
        console.error("Vision API қатесі:", error);
        displayResult({ error: "Талдау сәтсіз аяқталды", details: error.message });
      }
    });
  });
});