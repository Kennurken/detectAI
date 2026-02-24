const API_URL = "https://detect-ai-silk.vercel.app";

// Сайт жаңарған кезде іске қосылады
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
    checkUrlAutomatically(tab.url, tabId);
  }
});

async function checkUrlAutomatically(url, tabId) {
  try {
    const response = await fetch(`${API_URL}/analyze-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });
    
    const data = await response.json();

    if (data.verdict === "Қауіпті") {
      // 1. Белгішеге (Badge) қызыл леп белгісін қою
      chrome.action.setBadgeText({ text: "!", tabId: tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#FF0000" });

      // 2. Жүйелік хабарлама жіберу
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png', // Иконкаң болса
        title: '⚠️ ҚАУІПТІ САЙТ!',
        message: `Digital Trace алаяқтықты анықтады: ${data.reason}`,
        priority: 2
      });
    }
  } catch (error) {
    console.error("Background check error:", error);
  }
}