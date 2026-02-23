document.getElementById('checkBtn').addEventListener('click', async () => {
  const text = document.getElementById('msgInput').value;
  const resultDiv = document.getElementById('result');
  
  resultDiv.innerText = "Талдау жасалуда...";

  try {
    const response = await fetch('https://detect-ai-kennurken.vercel.app/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    
    const data = await response.json();
    
    if (data.verdict === "Қауіпті") {
      resultDiv.style.color = "red";
      resultDiv.innerText = "❌ ҚАУІПТІ: Алаяқтық белгілері бар!";
    } else {
      resultDiv.style.color = "green";
      resultDiv.innerText = "✅ ТАЗА: Қауіп анықталған жоқ.";
    }
  } catch (error) {
    resultDiv.innerText = "Қате орын алды!";
  }
});