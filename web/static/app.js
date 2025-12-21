



// /*************************************************
//  * 🔴 OLD CODE (COMMENTED — DO NOT DELETE)
//  *************************************************/

// // async function sendMessage() {
// //     ...
// // }

// // window.onload = checkAuth;


// /*************************************************
//  * ✅ BOOTSTRAP (PROOF + SAFETY)
//  *************************************************/
// console.log("app.js loaded");

// /*************************************************
//  * ✅ AUTH GATE (STABLE, ORDER-SAFE)
//  *************************************************/
// document.addEventListener("DOMContentLoaded", async () => {
//     console.log("DOM ready");

//     // Always hide both views first (prevents flicker)
//     const authView = document.getElementById("auth-view");
//     const chatView = document.getElementById("chat-view");

//     if (!authView || !chatView) {
//         console.error("Auth or Chat view missing in HTML");
//         return;
//     }

//     authView.style.display = "none";
//     chatView.style.display = "none";

//     await checkAuth();
// });

// async function checkAuth() {
//     console.log("Checking auth...");

//     let res;
//     try {
//         res = await fetch("/profile/me", {
//             credentials: "same-origin"
//         });
//     } catch (err) {
//         console.error("Network error during auth check", err);
//         showAuth();
//         return;
//     }

//     let data;
//     try {
//         data = await res.json();
//     } catch (err) {
//         console.error("Invalid JSON from /profile/me");
//         showAuth();
//         return;
//     }

//     console.log("Auth response:", data);

//     if (data.error) {
//         showAuth();
//     } else {
//         showChat();
//     }
// }

// function showAuth() {
//     console.log("Showing auth UI");

//     document.getElementById("chat-view").style.display = "none";
//     document.getElementById("auth-view").style.display = "flex";

//     fetch("/static/auth.html")
//         .then(res => res.text())
//         .then(html => {
//             document.getElementById("auth-view").innerHTML = html;
//         })
//         .catch(err => {
//             console.error("Failed to load auth.html", err);
//         });
// }

// function showChat() {
//     console.log("Showing chat UI");

//     document.getElementById("auth-view").style.display = "none";
//     document.getElementById("chat-view").style.display = "block";
// }

// /*************************************************
//  * ✅ CHAT LOGIC (UNCHANGED BEHAVIOR)
//  *************************************************/
// async function sendMessage() {
//     const input = document.getElementById("user-input");
//     const message = input.value.trim();
//     if (!message) return;

//     addMessage(message, "user");
//     input.value = "";

//     let response;
//     try {
//         response = await fetch("/interact", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ message })
//         });
//     } catch (err) {
//         addMessage("⚠️ Server not reachable.", "bot");
//         return;
//     }

//     if (!response.ok) {
//         addMessage("⚠️ Server error.", "bot");
//         return;
//     }

//     const data = await response.json();

//     if (!data || !data.reply) {
//         addMessage("⚠️ Invalid response.", "bot");
//         return;
//     }

//     addMessage(data.reply, "bot");
// }

// function addMessage(text, sender) {
//     const chatBox = document.getElementById("chat-box");
//     if (!chatBox) return;

//     const div = document.createElement("div");
//     div.className = sender === "user" ? "user-message" : "bot-message";
//     div.innerText = text;

//     chatBox.appendChild(div);
//     chatBox.scrollTop = chatBox.scrollHeight;
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
