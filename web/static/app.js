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

    // ❌ OLD AUTH CHECK (CAUSES 404 — DO NOT DELETE)
    // await checkAuth();

    // ✅ NEW: Directly show chat (session handled backend-side)
    showChat();

    // ✅ Profile toggle binding
    const profileBtn = document.getElementById("profile-toggle");
    if (profileBtn) {
        profileBtn.addEventListener("click", toggleProfile);
    }
});

/*************************************************
 * ❌ OLD AUTH CHECK (COMMENTED — DO NOT DELETE)
 *************************************************/
/*
async function checkAuth() {
    let res;
    try {
        res = await fetch("/auth/profile/me", {
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
*/

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
 * 👤 PROFILE PANEL LOGIC (FINAL)
 *************************************************/
async function toggleProfile() {
    const panel = document.getElementById("profile-panel");

    // Toggle close
    if (!panel.classList.contains("hidden")) {
        panel.classList.add("hidden");
        return;
    }

    const res = await fetch("auth/profile/appointments", {
        credentials: "same-origin"
    });

    if (!res.ok) {
        console.error("Failed to load profile appointments");
        return;
    }

    const data = await res.json();

    renderAppointments("upcoming-appointments", data.upcoming);
    renderAppointments("past-appointments", data.past);

    panel.classList.remove("hidden");
}

function renderAppointments(elementId, appointments) {
    const ul = document.getElementById(elementId);
    ul.innerHTML = "";

    if (!appointments || appointments.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No appointments";
        ul.appendChild(li);
        return;
    }

    appointments.forEach(a => {
        const li = document.createElement("li");

        // ✅ FIX: backend does NOT return specialty
        li.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;

        ul.appendChild(li);
    });
}

/*************************************************
 * ✅ LOGOUT
 *************************************************/
async function logout() {
    await fetch("/auth/logout", {
        method: "POST",
        credentials: "same-origin"
    });
    showAuth();
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
    credentials: "same-origin", // ✅ ADD THIS
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
