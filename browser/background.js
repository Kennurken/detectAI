const API_URL = "https://detect-ai-silk.vercel.app";

console.log("Digital Trace: Background Service Worker іске қосылды");

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Бет толық жүктелгенде ғана тексереміз
  if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
    console.log("Жаңа сайт ашылды, тексеру басталды:", tab.url);
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
    console.log("Background талдау нәтижесі:", data);

    if (data.verdict === "Қауіпті") {
      console.warn("⚠️ ҚАУІПТІ САЙТ АНЫҚТАЛДЫ!");
      
      // Иконкаға белгі қою
      chrome.action.setBadgeText({ text: "!", tabId: tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#FF0000" });

      // Хабарлама шығару
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png', 
        title: 'Digital Trace AI: Қауіп!',
        message: `Бұл сайт күмәнді: ${data.reason}`,
        priority: 2
      });
    } else {
      // Егер таза болса, белгіні алып тастаймыз
      chrome.action.setBadgeText({ text: "", tabId: tabId });
    }
  } catch (error) {
    console.error("Автоматты тексеру қатесі:", error);
  }
}