document.getElementById('checkBtn').addEventListener('click', async () => {
  const text = document.getElementById('msgInput').value;
  const resultDiv = document.getElementById('result');
  
  if (!text.trim()) {
    resultDiv.innerText = "Мәтінді енгізіңіз!";
    return;
  }

  resultDiv.style.color = "black";
  resultDiv.innerText = "AI талдау жасап жатыр...";

  try {
    const response = await fetch('https://detect-ai-silk.vercel.app/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    
    const data = await response.json();
    
    // Егер Backend-тен қате келсе
    if (data.error) {
      resultDiv.style.color = "orange";
      resultDiv.innerText = "⚠️ " + data.error;
      return;
    }

    // Нәтижені шығару
    if (data.verdict === "Қауіпті") {
      resultDiv.style.color = "#d9534f"; // Қызыл түс
      resultDiv.innerHTML = `
        <strong>❌ ҚАУІПТІ: Алаяқтық белгілері бар!</strong><br>
        <small>Сенімділік: ${data.confidence}%</small><br>
        <p style="font-size: 12px; margin-top: 5px;">Себебі: ${data.reason}</p>
      `;
    } else {
      resultDiv.style.color = "#5cb85c"; // Жасыл түс
      resultDiv.innerHTML = `
        <strong>✅ ТАЗА: Қауіп анықталған жоқ.</strong><br>
        <small>Сенімділік: ${data.confidence}%</small>
      `;
    }
  } catch (error) {
    console.error(error);
    resultDiv.style.color = "red";
    resultDiv.innerText = "Серверге қосылу мүмкін болмады!";
  }
});