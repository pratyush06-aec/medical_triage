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







// async function sendMessage() {
//     const input = document.getElementById("user-input");
//     const message = input.value.trim();
//     if (!message) return;

//     addMessage(message, "user");
//     input.value = "";

//     const response = await fetch("/interact", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message })
//     });

//     // ✅ ALWAYS parse JSON
//     const data = await response.json();

//     // ✅ SAFETY CHECK (prevents null crash)
//     if (!data || !data.reply) {
//         addMessage("⚠️ Something went wrong. Please try again.", "bot");
//         return;
//     }

//     // ✅ DISPLAY STRING (not object)
//     addMessage(data.reply, "bot");
// }


/*************************************************
 * ❌ OLD (COMMENTED — DO NOT DELETE)
 *************************************************/
// window.onload = checkAuth;

/*************************************************
 * ✅ BOOTSTRAP
 *************************************************/
document.addEventListener("DOMContentLoaded", async () => {
    const authView = document.getElementById("auth-view");
    const chatView = document.getElementById("chat-view");

    authView.style.display = "none";
    chatView.style.display = "none";

    await checkAuth();
});

/*************************************************
 * ✅ AUTH CHECK
 *************************************************/
async function checkAuth() {
    let res;
    try {
        res = await fetch("/profile/me", {
            credentials: "same-origin"
        });
    } catch {
        showAuth();
        return;
    }

    const data = await res.json();
    if (data.error) {
        showAuth();
    } else {
        showChat();
    }
}

function showAuth() {
    document.getElementById("chat-view").style.display = "none";
    document.getElementById("auth-view").style.display = "flex";

    fetch("/static/auth.html")
        .then(res => res.text())
        .then(html => {
            document.getElementById("auth-view").innerHTML = html;
        });
}

function showChat() {
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("chat-view").style.display = "block";
}

/*************************************************
 * ✅ LOGOUT (NEW)
 *************************************************/
async function logout() {
    await fetch("/auth/logout", {
        method: "POST",
        credentials: "same-origin"
    });

    // Reload to re-trigger auth gate
    location.reload();
}

/*************************************************
 * ✅ CHAT LOGIC (UNCHANGED)
 *************************************************/
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

    const data = await response.json();
    if (data?.reply) {
        addMessage(data.reply, "bot");
    }
}

function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = sender === "user" ? "user-message" : "bot-message";
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}
