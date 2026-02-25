document.addEventListener('DOMContentLoaded', function() {
  const checkTextBtn = document.getElementById('checkTextBtn');
  const checkScreenBtn = document.getElementById('checkScreenBtn');
  const checkUrlBtn = document.getElementById('checkUrlBtn');
  const msgInput = document.getElementById('msgInput');
  const resultDiv = document.getElementById('result');
  const resultCard = document.getElementById('resultCard');
  const verdictLabel = document.getElementById('verdictLabel');
  const confidenceBadge = document.getElementById('confidenceBadge');
  const reasonText = document.getElementById('reasonText');
  const scanLine = document.getElementById('scanLine');

  const API_URL = "https://detect-ai-silk.vercel.app";

  function setLoading(isLoading) {
    [checkTextBtn, checkScreenBtn, checkUrlBtn].forEach(btn => {
      if (btn) {
        btn.disabled = isLoading;
        btn.style.opacity = isLoading ? "0.5" : "1";
      }
    });
    if (isLoading) {
      resultDiv.style.display = 'none';
      if (scanLine) scanLine.style.display = 'block';
    } else {
      if (scanLine) scanLine.style.display = 'none';
    }
  }

  function displayResult(data) {
    setLoading(false);
    resultDiv.style.display = 'block'; 
    
    if (data.error) {
      verdictLabel.innerText = "⚠️ ҚАТЕ";
      verdictLabel.style.color = "#f59e0b";
      reasonText.innerText = data.msg || data.error || "Сервер қатесі.";
      confidenceBadge.innerText = "0% Сенім";
      return;
    }

    const isDanger = data.verdict === "Қауіпті" || data.verdict === "ҚАУІПТІ";
    const score = data.scam_score !== undefined ? data.scam_score : (data.confidence || 0);
    
    resultCard.style.borderLeftColor = isDanger ? "#ef4444" : "#10b981";
    verdictLabel.style.color = isDanger ? "#f87171" : "#34d399";
    verdictLabel.innerText = isDanger ? "❌ ҚАУІПТІ" : "✅ ТАЗА";
    confidenceBadge.innerText = `${score}% Сенім`;
    reasonText.innerText = data.detail || data.reason || "Талдау аяқталды.";
  }

  // ЭКРАНДЫ ТЕКСЕРУ (Vision)
  if (checkScreenBtn) {
    checkScreenBtn.addEventListener('click', () => {
      setLoading(true);
      chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
        if (!dataUrl) {
          displayResult({ error: "Скриншот алу мүмкін болмады. Бетті жаңартып көріңіз." });
          return;
        }
        const base64Data = dataUrl.split(',')[1];
        try {
          const response = await fetch(`${API_URL}/analyze-screen`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: base64Data })
          });
          displayResult(await response.json());
        } catch (error) {
          displayResult({ error: "Сервермен байланыс үзілді." });
        }
      });
    });
  }

  // МӘТІНДІ ТЕКСЕРУ
  if (checkTextBtn) {
    checkTextBtn.addEventListener('click', async () => {
      const text = msgInput.value.trim();
      if (!text) return alert("Мәтінді жазыңыз");
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: text })
        });
        displayResult(await response.json());
      } catch (error) { displayResult({ error: "Қате кетті" }); }
    });
  }

  // URL ТЕКСЕРУ
  if (checkUrlBtn) {
    checkUrlBtn.addEventListener('click', () => {
      setLoading(true);
      chrome.tabs.query({active: true, currentWindow: true}, async (tabs) => {
        try {
          const response = await fetch(`${API_URL}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: tabs[0].url })
          });
          displayResult(await response.json());
        } catch (error) { displayResult({ error: "URL қатесі" }); }
      });
    });
  }
});