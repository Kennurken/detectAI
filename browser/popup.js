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

  // URL соңында қиғаш сызық (/) болмағаны дұрыс
  const API_URL = "https://detect-ai-kennurken.vercel.app";

  console.log("Digital Trace: Скрипт іске қосылды");

  // Жүктеу күйін басқару функциясы
  function setLoading(isLoading) {
    if (isLoading) {
      console.log("Талдау басталды...");
      checkTextBtn.disabled = true;
      checkScreenBtn.disabled = true;
      checkTextBtn.style.opacity = "0.5";
      checkScreenBtn.style.opacity = "0.5";
      checkTextBtn.style.cursor = "not-allowed";
      checkScreenBtn.style.cursor = "not-allowed";
      resultDiv.style.display = 'none';
      if (scanLine) scanLine.style.display = 'block';
    } else {
      checkTextBtn.disabled = false;
      checkScreenBtn.disabled = false;
      checkTextBtn.style.opacity = "1";
      checkScreenBtn.style.opacity = "1";
      checkTextBtn.style.cursor = "pointer";
      checkScreenBtn.style.cursor = "pointer";
      if (scanLine) scanLine.style.display = 'none';
    }
  }

  function displayResult(data) {
    setLoading(false);
    resultDiv.style.display = 'block'; 
    
    if (data.error) {
      console.error("Көрсетілетін қате:", data.error);
      verdictLabel.innerText = "⚠️ ҚАТЕ";
      verdictLabel.style.color = "#f59e0b";
      reasonText.innerText = data.details || data.error;
      resultCard.style.borderLeftColor = "#f59e0b";
      confidenceBadge.innerText = "0% SENIM";
      return;
    }

    const isDanger = data.verdict === "Қауіпті";
    
    resultCard.style.borderLeftColor = isDanger ? "#ef4444" : "#10b981";
    verdictLabel.style.color = isDanger ? "#f87171" : "#34d399";
    verdictLabel.innerText = isDanger ? "❌ ҚАУІПТІ" : "✅ ТАЗА";
    
    confidenceBadge.innerText = `${data.confidence || 0}% SENIM`;
    confidenceBadge.style.background = isDanger ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)";
    confidenceBadge.style.color = isDanger ? "#f87171" : "#34d399";
    
    reasonText.innerText = data.reason || "Талдау аяқталды.";
  }

  // 1. Мәтінді талдау батырмасы
  checkTextBtn.addEventListener('click', async () => {
    const text = msgInput.value.trim();
    if (!text) return alert("Мәтінді жазыңыз");

    console.log("1. Талдау басталды, мәтін:", text);
    setLoading(true); // Мұнда showLoading емес, setLoading болуы керек!

    try {
        console.log("2. Серверге сұраныс кетті...");
        
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            mode: 'cors', // CORS рұқсаты үшін маңызды
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        console.log("3. Статус:", response.status);
        const data = await response.json();
        console.log("4. Деректер алынды:", data);

        displayResult(data);
    } catch (error) {
        console.error("!!! FETCH ҚАТЕСІ:", error);
        displayResult({ error: "Байланыс үзілді", details: "Сервер жауап бермеді немесе CORS қатесі." });
    }
  });

  // 2. Экранды талдау батырмасы (Vision)
  checkScreenBtn.addEventListener('click', () => {
    console.log("Экранды түсіру басталды...");
    setLoading(true);

    chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
      if (!dataUrl) {
        displayResult({ error: "Скриншот алу мүмкін болмады. Расширениеге рұқсат берілгенін тексеріңіз." });
        return;
      }

      console.log("Скриншот алынды, серверге жіберілуде...");
      const base64Data = dataUrl.split(',')[1];

      try {
        const response = await fetch(`${API_URL}/analyze-screen`, {
          method: 'POST',
          mode: 'cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_base64: base64Data })
        });

        if (!response.ok) throw new Error(`Сервер қатесі: ${response.status}`);

        const data = await response.json();
        displayResult(data);
      } catch (error) {
        console.error("Vision Error:", error);
        displayResult({ error: "Vision API қатесі", details: error.message });
      }
    });
  });
});