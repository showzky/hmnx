export function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${minutes}:${secs}`;
  }
  
  export function getRandomPanicMessage() {
    const messages = [
      "HVORFOR ER HIMMELEN BLÅ?!",
      "Hvem stjæler alltid sokker mine?",
      "Hvor er katten min?!",
      "PANIKK!!"
    ];
    return `04:${Math.floor(Math.random() * 59).toString().padStart(2, '0')} - Random User: ${messages[Math.floor(Math.random() * messages.length)]}`;
  }
