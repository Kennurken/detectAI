document.addEventListener('DOMContentLoaded', function() {
  // Элементтерді алу
  const checkTextBtn = document.getElementById('checkTextBtn');
  const checkScreenBtn = document.getElementById('checkScreenBtn');
  const msgInput = document.getElementById('msgInput');
  const resultDiv = document.getElementById('result');
  const resultCard = document.getElementById('resultCard');
  const verdictLabel = document.getElementById('verdictLabel');
  const confidenceBadge = document.getElementById('confidenceBadge');
  const reasonText = document.getElementById('reasonText');
  const scanLine = document.getElementById('scanLine');

  const API_URL = "https://detect-ai-kennurken.vercel.app";

  function showLoading() {
    resultDiv.classList.add('hidden');
    if (scanLine) scanLine.style.display = 'block';
  }

  function displayResult(data) {
    if (scanLine) scanLine.style.display = 'none';
    resultDiv.classList.remove('hidden');
    
    // Егер серверден қате келсе
    if (data.error) {
      verdictLabel.innerText = "⚠️ ҚАТЕ";
      reasonText.innerText = data.details || data.error;
      resultCard.style.borderLeftColor = "#f59e0b";
      return;
    }

    const isDanger = data.verdict === "Қауіпті";
    
    if (isDanger) {
      resultCard.style.borderLeftColor = "#ef4444";
      verdictLabel.className = "font-extrabold text-base text-red-400";
      verdictLabel.innerText = "❌ ҚАУІПТІ";
      confidenceBadge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-400";
    } else {
      resultCard.style.borderLeftColor = "#10b981";
      verdictLabel.className = "font-extrabold text-base text-emerald-400";
      verdictLabel.innerText = "✅ ТАЗА";
      confidenceBadge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400";
    }

    confidenceBadge.innerText = `${data.confidence || 0}% SENIM`;
    reasonText.innerText = data.reason || "Талдау аяқталды.";
  }

  // 1. Мәтінді талдау батырмасы
  checkTextBtn.addEventListener('click', async () => {
    const text = msgInput.value.trim();
    if (!text) return alert("Мәтінді енгізіңіз!");

    showLoading();

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
      });
      const data = await response.json();
      displayResult(data);
    } catch (error) {
      displayResult({ error: "Серверге қосылу мүмкін болмады", details: error.message });
    }
  });

  // 2. Экранды талдау батырмасы (Vision)
  checkScreenBtn.addEventListener('click', () => {
    showLoading();

    // Chrome API арқылы скриншот алу
    chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
      if (!dataUrl) {
        displayResult({ error: "Скриншот алу мүмкін болмады" });
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
        displayResult({ error: "Vision API қатесі", details: error.message });
      }
    });
  });
});