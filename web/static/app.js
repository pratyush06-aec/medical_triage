// async function sendMessage() {
//     const inputEl = document.getElementById("user-input");
//     const chat = document.getElementById("chat");

//     const msg = inputEl.value;
//     if (!msg.trim()) return;

//     chat.innerHTML += `<div class="text-right mb-2"><span class="inline-block bg-blue-200 p-2 rounded">${msg}</span></div>`;
//     inputEl.value = "";

//     const response = await fetch("/interact", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: msg })
//     });

//     const data = await response.json();

//     chat.innerHTML += `<div class="text-left mb-2"><span class="inline-block bg-gray-200 p-2 rounded">${data.reply}</span></div>`;
//     chat.scrollTop = chat.scrollHeight;
// }







async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    const response = await fetch("/interact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    // ✅ ALWAYS parse JSON
    const data = await response.json();

    // ✅ SAFETY CHECK (prevents null crash)
    if (!data || !data.reply) {
        addMessage("⚠️ Something went wrong. Please try again.", "bot");
        return;
    }

    // ✅ DISPLAY STRING (not object)
    addMessage(data.reply, "bot");
}


function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");

    const messageDiv = document.createElement("div");
    messageDiv.className = sender === "user" ? "user-message" : "bot-message";

    messageDiv.innerText = text;   // ✅ NOT innerHTML

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}