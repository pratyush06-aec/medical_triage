let recognition;

function startVoiceInput() {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
        alert("Voice input is not supported in this browser.");
        return;
    }

    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    recognition = new SpeechRecognition();
    recognition.lang = "en-IN";        // Indian English
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById("user-input");
        input.value = transcript;
        input.focus();
    };

    recognition.onerror = (event) => {
        console.error("Voice recognition error:", event.error);
    };
}
