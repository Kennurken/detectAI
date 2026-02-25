document.addEventListener('DOMContentLoaded', function() {
  // Элементтерді алу
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

  // Апелляция элементтері
  const appealSection = document.getElementById('appealSection');
  const appealReasonInput = document.getElementById('appealReasonInput');
  const sendAppealBtn = document.getElementById('sendAppealBtn');

  const API_URL = "https://detect-ai-silk.vercel.app";
  let lastScannedUrl = "";

  console.log("Digital Trace: Скрипт іске қосылды");

  function setLoading(isLoading) {
    const buttons = [checkTextBtn, checkScreenBtn, checkUrlBtn];
    buttons.forEach(btn => {
      if (btn) {
        btn.disabled = isLoading;
        btn.style.opacity = isLoading ? "0.5" : "1";
      }
    });

    if (isLoading) {
      resultDiv.style.display = 'none';
      if (appealSection) appealSection.style.display = 'none';
      if (scanLine) scanLine.style.display = 'block';
    } else {
      if (scanLine) scanLine.style.display = 'none';
    }
  }

  function displayResult(data) {
    setLoading(false);
    resultDiv.style.display = 'block'; 
    console.log("Серверден келген деректер:", data); // Консольден тексеру үшін

    if (data.error) {
      verdictLabel.innerText = "⚠️ ҚАТЕ";
      verdictLabel.style.color = "#f59e0b";
      reasonText.innerText = data.msg || data.error || "Сервермен байланыс жоқ.";
      confidenceBadge.innerText = "0%";
      return;
    }

    // Бэкэндтен келетін деректерді өңдеу (scam_score мен detail-ге басымдық береміз)
    const isDanger = data.verdict === "Қауіпті" || data.verdict === "ҚАУІПТІ";
    const score = data.scam_score !== undefined ? data.scam_score : (data.confidence || 0);
    const detail = data.detail || data.reason || "Талдау аяқталды.";

    resultCard.style.borderLeftColor = isDanger ? "#ef4444" : "#10b981";
    verdictLabel.style.color = isDanger ? "#f87171" : "#34d399";
    verdictLabel.innerText = isDanger ? "❌ ҚАУІПТІ" : "✅ ТАЗА";
    
    confidenceBadge.innerText = `${score}% Сенім`;
    confidenceBadge.style.background = isDanger ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)";
    confidenceBadge.style.color = isDanger ? "#f87171" : "#34d399";
    reasonText.innerText = detail;

    // Қауіпті болса апелляцияны көрсету
    if (isDanger && appealSection) {
      appealSection.style.display = 'block';
    }
  }

  // 1. МӘТІНДІ ТАЛДАУ (Бэкэндтегі /check-ке жібереміз)
  if (checkTextBtn) {
    checkTextBtn.addEventListener('click', async () => {
      const text = msgInput.value.trim();
      if (!text) return alert("Мәтінді жазыңыз");
      lastScannedUrl = text.substring(0, 50) + "..."; // Апелляция үшін сақтаймыз
      setLoading(true);
      try {
          const response = await fetch(`${API_URL}/check`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ url: text }) // Бэкэнд SiteRequest(url: str) күтіп тұр
          });
          displayResult(await response.json());
      } catch (error) {
          displayResult({ error: "Байланыс үзілді" });
      }
    });
  }

  // 2. СІЛТЕМЕНІ ТАЛДАУ (URL)
  if (checkUrlBtn) {
    checkUrlBtn.addEventListener('click', () => {
      setLoading(true);
      chrome.tabs.query({active: true, currentWindow: true}, async (tabs) => {
        if (!tabs[0]) return;
        lastScannedUrl = tabs[0].url;
        try {
          const response = await fetch(`${API_URL}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: tabs[0].url })
          });
          displayResult(await response.json());
        } catch (error) {
          displayResult({ error: "URL қатесі" });
        }
      });
    });
  }

  // 3. АПЕЛЛЯЦИЯ ЖІБЕРУ
  if (sendAppealBtn) {
    sendAppealBtn.addEventListener('click', async () => {
      const reason = appealReasonInput.value.trim();
      if (!reason) return alert("Себебін жазыңыз");
      
      try {
        const response = await fetch(`${API_URL}/appeal`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: lastScannedUrl, reason: reason })
        });
        const data = await response.json();
        if (data.status === "success") {
          alert("Апелляция жіберілді!");
          appealSection.style.display = 'none';
          appealReasonInput.value = "";
        }
      } catch (e) {
        alert("Қате кетті");
      }
    });
  }
});