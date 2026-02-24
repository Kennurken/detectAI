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

  console.log("Digital Trace: Скрипт іске қосылды");

  // Жүктеу күйін басқару (барлық батырмалар үшін)
  function setLoading(isLoading) {
    const buttons = [checkTextBtn, checkScreenBtn, checkUrlBtn];
    
    buttons.forEach(btn => {
      if (btn) {
        btn.disabled = isLoading;
        btn.style.opacity = isLoading ? "0.5" : "1";
        btn.style.cursor = isLoading ? "not-allowed" : "pointer";
      }
    });

    if (isLoading) {
      console.log("Талдау басталды...");
      resultDiv.style.display = 'none';
      if (scanLine) scanLine.style.display = 'block';
    } else {
      if (scanLine) scanLine.style.display = 'none';
    }
  }

  // Нәтижені экранға шығару
  function displayResult(data) {
    setLoading(false);
    resultDiv.style.display = 'block'; 
    
    if (data.error) {
      console.error("Сервер қатесі:", data.error);
      verdictLabel.innerText = "⚠️ ҚАТЕ";
      verdictLabel.style.color = "#f59e0b";
      reasonText.innerText = data.details || data.error;
      resultCard.style.borderLeftColor = "#f59e0b";
      confidenceBadge.innerText = "0% Сенім";
      return;
    }

    const isDanger = data.verdict === "Қауіпті";
    
    resultCard.style.borderLeftColor = isDanger ? "#ef4444" : "#10b981";
    verdictLabel.style.color = isDanger ? "#f87171" : "#34d399";
    verdictLabel.innerText = isDanger ? "❌ ҚАУІПТІ" : "✅ ТАЗА";
    
    const confidence = data.confidence || 0;
    confidenceBadge.innerText = `${confidence}% Сенім`;
    confidenceBadge.style.background = isDanger ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)";
    confidenceBadge.style.color = isDanger ? "#f87171" : "#34d399";
    
    reasonText.innerText = data.reason || "Талдау аяқталды.";
  }

  // 1. МӘТІНДІ ТАЛДАУ
  if (checkTextBtn) {
    checkTextBtn.addEventListener('click', async () => {
      const text = msgInput.value.trim();
      if (!text) return alert("Мәтінді жазыңыз");

      setLoading(true);
      try {
          const response = await fetch(`${API_URL}/analyze`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: text })
          });
          const data = await response.json();
          displayResult(data);
      } catch (error) {
          console.error("Fetch Error:", error);
          displayResult({ error: "Байланыс үзілді", details: "Сервер жауап бермеді." });
      }
    });
  }

  // 2. ЭКРАНДЫ ТАЛДАУ (Vision)
  if (checkScreenBtn) {
    checkScreenBtn.addEventListener('click', () => {
      setLoading(true);
      chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
        if (!dataUrl) {
          displayResult({ error: "Скриншот алу мүмкін болмады." });
          return;
        }

        const base64Data = dataUrl.split(',')[1];
        try {
          const response = await fetch(`${API_URL}/analyze-screen`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: base64Data })
          });
          const data = await response.json();
          displayResult(data);
        } catch (error) {
          displayResult({ error: "Vision қатесі", details: error.message });
        }
      });
    });
  }

  // 3. СІЛТЕМЕНІ ТАЛДАУ (URL)
  if (checkUrlBtn) {
    checkUrlBtn.addEventListener('click', () => {
      setLoading(true);
      chrome.tabs.query({active: true, currentWindow: true}, async (tabs) => {
        const currentUrl = tabs[0].url;
        try {
          const response = await fetch(`${API_URL}/analyze-url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: currentUrl })
          });
          const data = await response.json();
          displayResult(data);
        } catch (error) {
          displayResult({ error: "URL қатесі", details: error.message });
        }
      });
    });
  }
});