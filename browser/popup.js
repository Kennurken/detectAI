const resultDiv = document.getElementById('result');
const resultCard = document.getElementById('resultCard');
const verdictLabel = document.getElementById('verdictLabel');
const confidenceBadge = document.getElementById('confidenceBadge');
const reasonText = document.getElementById('reasonText');
const scanLine = document.getElementById('scanLine');

function showLoading() {
  resultDiv.classList.add('hidden');
  scanLine.style.display = 'block';
}

function displayResult(data) {
  scanLine.style.display = 'none';
  resultDiv.classList.remove('hidden');
  
  const isDanger = data.verdict === "Қауіпті";
  
  // Түстерді динамикалық орнату
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

  confidenceBadge.innerText = `${data.confidence}% SENIM`;
  reasonText.innerText = data.reason;
}