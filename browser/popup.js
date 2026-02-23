const resultDiv = document.getElementById('result');
const API_URL = "https://detect-ai-silk.vercel.app";

function showLoading(msg) {
  resultDiv.classList.remove('hidden');
  resultDiv.innerHTML = `<div class="flex items-center"><svg class="animate-spin h-4 w-4 mr-2 text-blue-400" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> ${msg}</div>`;
}

// 1. Мәтінді тексеру
document.getElementById('checkTextBtn').addEventListener('click', async () => {
  const text = document.getElementById('msgInput').value;
  if (!text.trim()) return;

  showLoading("AI талдап жатыр...");

  try {
    const res = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    displayResult(data);
  } catch (e) {
    resultDiv.innerText = "Қате: Сервер жауап бермеді.";
  }
});

// 2. Экранды тексеру (CV)
document.getElementById('checkScreenBtn').addEventListener('click', async () => {
  showLoading("Экран түсірілуде...");

  chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, async (dataUrl) => {
    if (!dataUrl) {
      resultDiv.innerText = "Қате: Скриншот алынбады.";
      return;
    }
    
    showLoading("AI кескінді көріп отыр...");
    const base64Image = dataUrl.split(',')[1];

    try {
      const res = await fetch(`${API_URL}/analyze-screen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64Image })
      });
      const data = await res.json();
      displayResult(data);
    } catch (e) {
      resultDiv.innerText = "Қате: CV талдау сәтсіз аяқталды.";
    }
  });
});

function displayResult(data) {
  resultDiv.classList.remove('hidden');
  const isDanger = data.verdict === "Қауіпті";
  const color = isDanger ? "text-red-400" : "text-green-400";
  const icon = isDanger ? "⚠️" : "✅";

  resultDiv.innerHTML = `
    <div class="font-bold ${color}">${icon} ${data.verdict.toUpperCase()}</div>
    <div class="text-xs text-gray-400 mt-1">Сенімділік: ${data.confidence}%</div>
    <div class="mt-2 text-xs leading-relaxed">${data.reason}</div>
  `;
}